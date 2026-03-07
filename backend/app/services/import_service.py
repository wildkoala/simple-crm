"""
Shared import logic for SAM.gov opportunities.

Used by both the manual import endpoint (contracts router)
and the automated collection endpoint (sam_gov router).
"""

import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.models import Contact, Contract, User
from app.utils import generate_id

logger = logging.getLogger(__name__)


def _parse_deadline(raw_deadline: str | None) -> datetime | None:
    """Parse a deadline string into a datetime, trying multiple formats."""
    if not raw_deadline:
        return None
    # Try ISO format with timezone
    try:
        return datetime.fromisoformat(raw_deadline.replace("Z", "+00:00"))
    except ValueError:
        pass
    # Try date-only format
    try:
        return datetime.strptime(raw_deadline[:10], "%Y-%m-%d")
    except ValueError:
        pass
    return None


def import_opportunities(
    opportunities: list[dict],
    auto_create_contacts: bool,
    current_user: User,
    db: Session,
) -> dict:
    """
    Import SAM.gov opportunities as contracts.

    Accepts a list of opportunity dicts with keys:
        noticeId, title, description, responseDeadLine, solicitationNumber,
        naicsCode, uiLink, pointOfContact, source, notes

    Returns a dict with contracts_created, contracts_skipped, contacts_created, errors.
    """
    contracts_created = 0
    contracts_skipped = 0
    contacts_created = 0
    errors: list[str] = []

    # Batch-load existing notice IDs to avoid per-item queries
    notice_ids = [
        opp.get("noticeId") or getattr(opp, "noticeId", None)
        for opp in opportunities
    ]
    notice_ids = [nid for nid in notice_ids if nid]
    existing_notice_ids = set()
    if notice_ids:
        existing_rows = (
            db.query(Contract.sam_gov_notice_id)
            .filter(Contract.sam_gov_notice_id.in_(notice_ids))
            .all()
        )
        existing_notice_ids = {row[0] for row in existing_rows}

    # Batch-load existing contact emails to avoid O(n*m) queries
    all_poc_emails: set[str] = set()
    if auto_create_contacts:
        for opp in opportunities:
            pocs = _get_field(opp, "pointOfContact") or []
            for poc in pocs:
                email = _get_field(poc, "email")
                if email:
                    all_poc_emails.add(email)

    existing_contacts_by_email: dict[str, Contact] = {}
    if all_poc_emails:
        existing_contacts = (
            db.query(Contact).filter(Contact.email.in_(all_poc_emails)).all()
        )
        existing_contacts_by_email = {c.email: c for c in existing_contacts}

    for opp in opportunities:
        notice_id = _get_field(opp, "noticeId")
        if not notice_id:
            continue

        savepoint = db.begin_nested()
        try:
            # Deduplicate
            if notice_id in existing_notice_ids:
                contracts_skipped += 1
                savepoint.rollback()
                continue

            title = (_get_field(opp, "title") or "Untitled Opportunity")[:300]

            # Parse deadline
            raw_deadline = _get_field(opp, "responseDeadLine")
            deadline = _parse_deadline(raw_deadline)
            if not deadline:
                errors.append(f"No valid deadline for: {title}")
                savepoint.rollback()
                continue

            # Auto-create contacts from point of contact
            contact_ids: list[str] = []
            if auto_create_contacts:
                pocs = _get_field(opp, "pointOfContact") or []
                for poc in pocs:
                    poc_email = _get_field(poc, "email")
                    poc_name = _get_field(poc, "fullName")
                    if poc_email and poc_name:
                        existing_contact = existing_contacts_by_email.get(poc_email)
                        if existing_contact:
                            contact_ids.append(existing_contact.id)
                        else:
                            name_parts = poc_name.strip().split()
                            first_name = name_parts[0] if name_parts else "Unknown"
                            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                            new_contact = Contact(
                                id=generate_id(),
                                first_name=first_name,
                                last_name=last_name,
                                email=poc_email,
                                phone=_get_field(poc, "phone") or "",
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
                            # Add to cache so subsequent POCs with same email are reused
                            existing_contacts_by_email[poc_email] = new_contact

            # Build notes
            notes_parts = [f"SAM.gov Notice ID: {notice_id}"]
            sol_num = _get_field(opp, "solicitationNumber")
            if sol_num:
                notes_parts.append(f"Solicitation #: {sol_num}")
            naics = _get_field(opp, "naicsCode")
            if naics:
                notes_parts.append(f"NAICS Code: {naics}")
            extra_notes = _get_field(opp, "notes")
            if extra_notes:
                notes_parts.append(extra_notes)

            source = _get_field(opp, "source") or "SAM.gov"

            new_contract = Contract(
                id=generate_id(),
                title=title[:200],
                description=_get_field(opp, "description") or "",
                source=source,
                deadline=deadline,
                status="prospective",
                sam_gov_notice_id=notice_id,
                submission_link=_get_field(opp, "uiLink"),
                notes="\n".join(notes_parts),
                created_by_user_id=current_user.id,
            )

            if contact_ids:
                contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()
                new_contract.assigned_contacts = contacts

            db.add(new_contract)
            savepoint.commit()
            contracts_created += 1
            # Track so duplicates in the same batch are caught
            existing_notice_ids.add(notice_id)

        except Exception as e:
            savepoint.rollback()
            errors.append(f"Error importing {_get_field(opp, 'title') or '?'}: {e}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save imports: {e}",
        )

    return {
        "contracts_created": contracts_created,
        "contracts_skipped": contracts_skipped,
        "contacts_created": contacts_created,
        "errors": errors,
    }


def _get_field(obj, field: str):
    """Get a field from either a dict or a Pydantic model / object."""
    if isinstance(obj, dict):
        return obj.get(field)
    return getattr(obj, field, None)
