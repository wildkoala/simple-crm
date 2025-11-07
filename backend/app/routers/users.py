from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import User as UserSchema
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserSchema])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users"""
    users = db.query(User).all()
    return users
