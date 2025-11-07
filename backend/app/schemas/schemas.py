from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Contact schemas
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    organization: str
    contact_type: str
    status: str
    needs_follow_up: bool = False
    follow_up_date: Optional[datetime] = None
    notes: str = ""


class ContactCreate(ContactBase):
    assigned_user_id: Optional[str] = None  # Optional - will default to current user if not provided


class ContactUpdate(ContactBase):
    last_contacted_at: Optional[datetime] = None
    assigned_user_id: str


class Contact(ContactBase):
    id: str
    created_at: datetime
    last_contacted_at: Optional[datetime] = None
    assigned_user_id: str
    assigned_user: Optional["User"] = None

    class Config:
        from_attributes = True


# Communication schemas
class CommunicationBase(BaseModel):
    contact_id: str
    date: datetime
    type: str
    notes: str = ""


class CommunicationCreate(CommunicationBase):
    pass


class Communication(CommunicationBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Contract schemas
class ContractBase(BaseModel):
    title: str
    description: str = ""
    source: str
    deadline: datetime
    status: str
    submission_link: Optional[str] = None
    notes: str = ""


class ContractCreate(ContractBase):
    assigned_contact_ids: List[str] = []


class ContractUpdate(ContractBase):
    assigned_contact_ids: List[str] = []


class Contract(ContractBase):
    id: str
    created_at: datetime
    assigned_contact_ids: List[str] = []

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
