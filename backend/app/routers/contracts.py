from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Contract, Contact, User
from app.schemas.schemas import Contract as ContractSchema, ContractCreate, ContractUpdate
from app.auth import get_current_user
from app.seed_data import generate_id

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=List[ContractSchema])
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contracts - contracts are shared across all users"""
    contracts = db.query(Contract).all()
    return [
        {
            **contract.__dict__,
            "submission_link": contract.submission_link,
            "created_at": contract.created_at,
            "assigned_contact_ids": [contact.id for contact in contract.assigned_contacts]
        }
        for contract in contracts
    ]


@router.get("/{contract_id}", response_model=ContractSchema)
def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contract - contracts are shared across all users"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return {
        **contract.__dict__,
        "submission_link": contract.submission_link,
        "created_at": contract.created_at,
        "assigned_contact_ids": [contact.id for contact in contract.assigned_contacts]
    }


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
        notes=contract.notes
    )

    # Add assigned contacts - can assign any contacts
    if contract.assigned_contact_ids:
        contacts = db.query(Contact).filter(
            Contact.id.in_(contract.assigned_contact_ids)
        ).all()
        new_contract.assigned_contacts = contacts

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return {
        **new_contract.__dict__,
        "submission_link": new_contract.submission_link,
        "created_at": new_contract.created_at,
        "assigned_contact_ids": [contact.id for contact in new_contract.assigned_contacts]
    }


@router.put("/{contract_id}", response_model=ContractSchema)
def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contract - contracts are shared across all users"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Update fields
    contract.title = contract_update.title
    contract.description = contract_update.description
    contract.source = contract_update.source
    contract.deadline = contract_update.deadline
    contract.status = contract_update.status
    contract.submission_link = contract_update.submission_link
    contract.notes = contract_update.notes

    # Update assigned contacts - can assign any contacts
    if contract_update.assigned_contact_ids is not None:
        contacts = db.query(Contact).filter(
            Contact.id.in_(contract_update.assigned_contact_ids)
        ).all()
        contract.assigned_contacts = contacts

    db.commit()
    db.refresh(contract)

    return {
        **contract.__dict__,
        "submission_link": contract.submission_link,
        "created_at": contract.created_at,
        "assigned_contact_ids": [contact.id for contact in contract.assigned_contacts]
    }


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contract - contracts are shared across all users"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    db.delete(contract)
    db.commit()
    return None
