from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_user
from app.database import get_db
from app.models.models import Teaming, User
from app.schemas.schemas import (
    Teaming as TeamingSchema,
)
from app.schemas.schemas import (
    TeamingCreate,
    TeamingPatch,
    TeamingUpdate,
)
from app.utils import generate_id

router = APIRouter(prefix="/teaming", tags=["teaming"])


@router.get("", response_model=List[TeamingSchema])
def get_teaming_records(
    opportunity_id: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Teaming).options(joinedload(Teaming.partner_account))
    if opportunity_id:
        query = query.filter(Teaming.opportunity_id == opportunity_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{teaming_id}", response_model=TeamingSchema)
def get_teaming(
    teaming_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    teaming = (
        db.query(Teaming)
        .options(joinedload(Teaming.partner_account))
        .filter(Teaming.id == teaming_id)
        .first()
    )
    if not teaming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teaming record not found"
        )
    return teaming


@router.post("", response_model=TeamingSchema, status_code=status.HTTP_201_CREATED)
def create_teaming(
    teaming: TeamingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    new_teaming = Teaming(
        id=generate_id(),
        opportunity_id=teaming.opportunity_id,
        partner_account_id=teaming.partner_account_id,
        role=teaming.role,
        status=teaming.status,
        notes=teaming.notes,
    )
    db.add(new_teaming)
    db.commit()
    db.refresh(new_teaming)
    return new_teaming


@router.put("/{teaming_id}", response_model=TeamingSchema)
def update_teaming(
    teaming_id: str,
    teaming_update: TeamingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    teaming = db.query(Teaming).filter(Teaming.id == teaming_id).first()
    if not teaming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teaming record not found"
        )

    teaming.opportunity_id = teaming_update.opportunity_id
    teaming.partner_account_id = teaming_update.partner_account_id
    teaming.role = teaming_update.role
    teaming.status = teaming_update.status
    teaming.notes = teaming_update.notes

    db.commit()
    db.refresh(teaming)
    return teaming


@router.patch("/{teaming_id}", response_model=TeamingSchema)
def patch_teaming(
    teaming_id: str,
    updates: TeamingPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    teaming = db.query(Teaming).filter(Teaming.id == teaming_id).first()
    if not teaming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teaming record not found"
        )

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teaming, field, value)

    db.commit()
    db.refresh(teaming)
    return teaming


@router.delete("/{teaming_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teaming(
    teaming_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    teaming = db.query(Teaming).filter(Teaming.id == teaming_id).first()
    if not teaming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teaming record not found"
        )

    db.delete(teaming)
    db.commit()
    return None
