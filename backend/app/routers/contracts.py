from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.models import Contract, Contact, User
from app.schemas.schemas import (
    Contract as ContractSchema,
    ContractCreate,
    ContractUpdate,
    ContractPatch,
    SAMGovImportRequest,
    SAMGovImportResponse
)
from app.auth import get_current_user, get_current_user_or_api_key
from app.utils import generate_id

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=List[ContractSchema])
def get_contracts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key)
):
    """Get all contracts - contracts are shared across all users"""
    return db.query(Contract).options(
        selectinload(Contract.assigned_contacts)
    ).offset(skip).limit(limit).all()


@router.get("/{contract_id}", response_model=ContractSchema)
def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contract"""
    contract = db.query(Contract).options(
        selectinload(Contract.assigned_contacts)
    ).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return contract


def _check_contract_authorization(contract: Contract, current_user: User):
    """Check if user is authorized to modify/delete a contract."""
    if contract.created_by_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this contract"
        )


def _resolve_owned_contacts(contact_ids: List[str], current_user: User, db: Session) -> list:
    """Resolve contact IDs, filtering to only contacts owned by the current user."""
    if not contact_ids:
        return []
    return db.query(Contact).filter(
        Contact.id.in_(contact_ids),
        Contact.assigned_user_id == current_user.id
    ).all()


@router.post("", response_model=ContractSchema, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contract"""
    new_contract = Contract(
        id=generate_id(),
        title=contract.title,
        description=contract.description,
        source=contract.source,
        deadline=contract.deadline,
        status=contract.status,
        submission_link=contract.submission_link,
        notes=contract.notes,
        created_by_user_id=current_user.id
    )

    # Add assigned contacts (only those owned by current user)
    new_contract.assigned_contacts = _resolve_owned_contacts(
        contract.assigned_contact_ids, current_user, db
    )

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract


@router.put("/{contract_id}", response_model=ContractSchema)
def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contract - only creator or admin can modify"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    _check_contract_authorization(contract, current_user)

    # Update fields
    contract.title = contract_update.title
    contract.description = contract_update.description
    contract.source = contract_update.source
    contract.deadline = contract_update.deadline
    contract.status = contract_update.status
    contract.submission_link = contract_update.submission_link
    contract.notes = contract_update.notes

    # Update assigned contacts (only those owned by current user)
    if contract_update.assigned_contact_ids is not None:
        contract.assigned_contacts = _resolve_owned_contacts(
            contract_update.assigned_contact_ids, current_user, db
        )

    db.commit()
    db.refresh(contract)
    return contract


@router.patch("/{contract_id}", response_model=ContractSchema)
def patch_contract(
    contract_id: str,
    updates: ContractPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partially update a contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    _check_contract_authorization(contract, current_user)

    update_data = updates.model_dump(exclude_unset=True)

    # Handle assigned_contact_ids separately (relationship, not a column)
    if "assigned_contact_ids" in update_data:
        contact_ids = update_data.pop("assigned_contact_ids")
        contract.assigned_contacts = _resolve_owned_contacts(
            contact_ids, current_user, db
        )

    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contract - only creator or admin can delete"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    _check_contract_authorization(contract, current_user)

    db.delete(contract)
    db.commit()
    return None


@router.post("/import/samgov", response_model=SAMGovImportResponse)
def import_samgov_opportunities(
    import_request: SAMGovImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key)
):
    """
    Import contract opportunities from SAM.gov

    This endpoint accepts opportunities scraped from SAM.gov and creates:
    - Contract records for each opportunity
    - Contact records from point-of-contact information (if auto_create_contacts is True)

    Duplicate opportunities (by noticeId) are skipped automatically.
    Uses savepoints so individual failures don't roll back the entire batch.
    """
    contracts_created = 0
    contracts_skipped = 0
    contacts_created = 0
    errors = []

    for opp in import_request.opportunities:
        savepoint = db.begin_nested()
        try:
            # Check if contract already exists by noticeId
            existing_contract = db.query(Contract).filter(
                Contract.sam_gov_notice_id == opp.noticeId
            ).first()

            if existing_contract:
                contracts_skipped += 1
                savepoint.rollback()
                continue

            # Parse deadline
            deadline = None
            if opp.responseDeadLine:
                try:
                    deadline = datetime.fromisoformat(opp.responseDeadLine.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        deadline = datetime.strptime(opp.responseDeadLine[:10], "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Could not parse deadline for {opp.title}")
                        savepoint.rollback()
                        continue

            if not deadline:
                errors.append(f"No deadline provided for {opp.title}")
                savepoint.rollback()
                continue

            # Create contacts from point of contact if requested
            contact_ids = []
            if import_request.auto_create_contacts and opp.pointOfContact:
                for poc in opp.pointOfContact:
                    if poc.email and poc.fullName:
                        # Check if contact already exists
                        existing_contact = db.query(Contact).filter(
                            Contact.email == poc.email
                        ).first()

                        if existing_contact:
                            contact_ids.append(existing_contact.id)
                        else:
                            # Parse name
                            name_parts = poc.fullName.strip().split()
                            first_name = name_parts[0] if name_parts else "Unknown"
                            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                            new_contact = Contact(
                                id=generate_id(),
                                first_name=first_name,
                                last_name=last_name,
                                email=poc.email,
                                phone=poc.phone or "",
                                organization=opp.title[:100] if opp.title else "SAM.gov Contact",
                                contact_type="government",
                                status="warm",
                                needs_follow_up=True,
                                notes=f"Auto-imported from SAM.gov opportunity: {opp.title}",
                                assigned_user_id=current_user.id
                            )
                            db.add(new_contact)
                            db.flush()
                            contact_ids.append(new_contact.id)
                            contacts_created += 1

            # Build notes with SAM.gov metadata
            notes_parts = [f"SAM.gov Notice ID: {opp.noticeId}"]
            if opp.solicitationNumber:
                notes_parts.append(f"Solicitation #: {opp.solicitationNumber}")
            if opp.naicsCode:
                notes_parts.append(f"NAICS Code: {opp.naicsCode}")
            if opp.notes:
                notes_parts.append(opp.notes)

            # Create contract
            new_contract = Contract(
                id=generate_id(),
                title=opp.title[:200],
                description=opp.description or "",
                source=opp.source,
                deadline=deadline,
                status="prospective",
                sam_gov_notice_id=opp.noticeId,
                submission_link=opp.uiLink,
                notes="\n".join(notes_parts),
                created_by_user_id=current_user.id
            )

            # Assign contacts
            if contact_ids:
                contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()
                new_contract.assigned_contacts = contacts

            db.add(new_contract)
            savepoint.commit()
            contracts_created += 1

        except Exception as e:
            savepoint.rollback()
            errors.append(f"Error importing {opp.title}: {str(e)}")
            continue

    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save imports: {str(e)}"
        )

    return SAMGovImportResponse(
        contracts_created=contracts_created,
        contracts_skipped=contracts_skipped,
        contacts_created=contacts_created,
        errors=errors
    )
