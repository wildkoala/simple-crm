"""
SAM.gov collection endpoints.

Fetches opportunities from the SAM.gov API and imports them as contracts
using the existing import pipeline.
"""

import asyncio
import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user_or_api_key
from app.database import get_db
from app.models.models import Contact, Contract, User
from app.schemas.schemas import (
    SAMGovCollectRequest,
    SAMGovCollectResponse,
)
from app.services.sam_gov import collect_opportunities
from app.utils import generate_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sam-gov", tags=["sam-gov"])


def _import_opportunities(
    opportunities: list[dict],
    auto_create_contacts: bool,
    current_user: User,
    db: Session,
) -> SAMGovCollectResponse:
    """Import fetched SAM.gov opportunities as contracts, reusing the existing import logic."""
    contracts_created = 0
    contracts_skipped = 0
    contacts_created = 0
    errors: list[str] = []

    for opp in opportunities:
        savepoint = db.begin_nested()
        try:
            notice_id = opp.get("noticeId")
            if not notice_id:
                savepoint.rollback()
                continue

            # Deduplicate
            existing = (
                db.query(Contract).filter(Contract.sam_gov_notice_id == notice_id).first()
            )
            if existing:
                contracts_skipped += 1
                savepoint.rollback()
                continue

            # Parse deadline
            deadline = None
            raw_deadline = opp.get("responseDeadLine") or ""
            if raw_deadline:
                for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
                    try:
                        deadline = datetime.strptime(
                            raw_deadline.replace("Z", "+00:00")[:25], fmt
                        )
                        break
                    except ValueError:
                        continue

            if not deadline:
                errors.append(f"No valid deadline for: {opp.get('title', notice_id)}")
                savepoint.rollback()
                continue

            title = (opp.get("title") or "Untitled Opportunity")[:300]

            # Auto-create contacts from point of contact
            contact_ids: list[str] = []
            if auto_create_contacts:
                for poc in opp.get("pointOfContact") or []:
                    poc_email = poc.get("email")
                    poc_name = poc.get("fullName")
                    if poc_email and poc_name:
                        existing_contact = (
                            db.query(Contact).filter(Contact.email == poc_email).first()
                        )
                        if existing_contact:
                            contact_ids.append(existing_contact.id)
                        else:
                            name_parts = poc_name.strip().split()
                            new_contact = Contact(
                                id=generate_id(),
                                first_name=name_parts[0] if name_parts else "Unknown",
                                last_name=(
                                    " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                                ),
                                email=poc_email,
                                phone=poc.get("phone") or "",
                                organization=title[:100],
                                contact_type="government",
                                status="warm",
                                needs_follow_up=True,
                                notes=f"Auto-imported from SAM.gov opportunity: {title}",
                                assigned_user_id=current_user.id,
                            )
                            db.add(new_contact)
                            db.flush()
                            contact_ids.append(new_contact.id)
                            contacts_created += 1

            # Build notes
            notes_parts = [f"SAM.gov Notice ID: {notice_id}"]
            if opp.get("solicitationNumber"):
                notes_parts.append(f"Solicitation #: {opp['solicitationNumber']}")
            if opp.get("naicsCode"):
                notes_parts.append(f"NAICS Code: {opp['naicsCode']}")

            new_contract = Contract(
                id=generate_id(),
                title=title[:200],
                description=opp.get("description") or "",
                source="SAM.gov",
                deadline=deadline,
                status="prospective",
                sam_gov_notice_id=notice_id,
                submission_link=opp.get("uiLink"),
                notes="\n".join(notes_parts),
                created_by_user_id=current_user.id,
            )

            if contact_ids:
                contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()
                new_contract.assigned_contacts = contacts

            db.add(new_contract)
            savepoint.commit()
            contracts_created += 1

        except Exception as e:
            savepoint.rollback()
            errors.append(f"Error importing {opp.get('title', '?')}: {e}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save imports: {e}",
        )

    return SAMGovCollectResponse(
        contracts_created=contracts_created,
        contracts_skipped=contracts_skipped,
        contacts_created=contacts_created,
        opportunities_fetched=len(opportunities),
        errors=errors,
    )


@router.post("/collect", response_model=SAMGovCollectResponse)
async def collect_samgov_opportunities(
    request: SAMGovCollectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    """
    Fetch opportunities from SAM.gov API and import them as contracts.

    Requires SAM_GOV_API_KEY environment variable to be set.
    Searches by NAICS codes over the specified date range, deduplicates,
    and imports new opportunities as prospective contracts.
    """
    api_key = os.getenv("SAM_GOV_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAM_GOV_API_KEY not configured",
        )

    naics_codes = request.naics_codes

    try:
        # Run the synchronous API calls in a thread to avoid blocking
        opportunities = await asyncio.to_thread(
            collect_opportunities,
            api_key=api_key,
            naics_codes=naics_codes,
            days_back=request.days_back,
            solicitations_only=request.solicitations_only,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("SAM.gov collection failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SAM.gov API error: {e}",
        )

    return _import_opportunities(
        opportunities=opportunities,
        auto_create_contacts=request.auto_create_contacts,
        current_user=current_user,
        db=db,
    )
