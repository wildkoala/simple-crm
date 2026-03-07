from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models.models import Proposal, User
from app.schemas.schemas import (
    Proposal as ProposalSchema,
)
from app.schemas.schemas import (
    ProposalCreate,
    ProposalPatch,
    ProposalUpdate,
)
from app.utils import generate_id

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.get("", response_model=List[ProposalSchema])
def get_proposals(
    opportunity_id: Optional[str] = Query(default=None),
    proposal_status: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Proposal)
    if opportunity_id:
        query = query.filter(Proposal.opportunity_id == opportunity_id)
    if proposal_status:
        query = query.filter(Proposal.status == proposal_status)
    return query.offset(skip).limit(limit).all()


@router.get("/{proposal_id}", response_model=ProposalSchema)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
        )
    return proposal


@router.post("", response_model=ProposalSchema, status_code=status.HTTP_201_CREATED)
def create_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if proposal already exists for this opportunity
    existing = (
        db.query(Proposal)
        .filter(Proposal.opportunity_id == proposal.opportunity_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A proposal already exists for this opportunity",
        )

    new_proposal = Proposal(
        id=generate_id(),
        opportunity_id=proposal.opportunity_id,
        proposal_manager_id=proposal.proposal_manager_id or current_user.id,
        submission_type=proposal.submission_type,
        submission_deadline=proposal.submission_deadline,
        status=proposal.status,
        notes=proposal.notes,
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    return new_proposal


@router.put("/{proposal_id}", response_model=ProposalSchema)
def update_proposal(
    proposal_id: str,
    proposal_update: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
        )

    proposal.proposal_manager_id = proposal_update.proposal_manager_id
    proposal.submission_type = proposal_update.submission_type
    proposal.submission_deadline = proposal_update.submission_deadline
    proposal.status = proposal_update.status
    proposal.notes = proposal_update.notes

    db.commit()
    db.refresh(proposal)
    return proposal


@router.patch("/{proposal_id}", response_model=ProposalSchema)
def patch_proposal(
    proposal_id: str,
    updates: ProposalPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
        )

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proposal, field, value)

    db.commit()
    db.refresh(proposal)
    return proposal


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
        )

    db.delete(proposal)
    db.commit()
    return None
