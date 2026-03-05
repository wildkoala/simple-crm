from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# Contact schemas
class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(max_length=50)
    organization: str = Field(max_length=200)
    contact_type: Literal["individual", "commercial", "government"]
    status: Literal["cold", "warm", "hot"]
    needs_follow_up: bool = False
    follow_up_date: Optional[datetime] = None
    notes: str = Field(default="", max_length=10000)


class ContactCreate(ContactBase):
    assigned_user_id: Optional[str] = None


class ContactUpdate(ContactBase):
    last_contacted_at: Optional[datetime] = None
    assigned_user_id: str


class ContactPatch(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    organization: Optional[str] = Field(default=None, max_length=200)
    contact_type: Optional[Literal["individual", "commercial", "government"]] = None
    status: Optional[Literal["cold", "warm", "hot"]] = None
    needs_follow_up: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=10000)
    last_contacted_at: Optional[datetime] = None
    assigned_user_id: Optional[str] = None


class ContactBrief(BaseModel):
    id: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


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
    type: Literal["email", "phone", "meeting", "other"]
    notes: str = Field(default="", max_length=10000)


class CommunicationCreate(CommunicationBase):
    pass


class Communication(CommunicationBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Contract schemas
class ContractBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(default="", max_length=50000)
    source: str = Field(max_length=200)
    deadline: datetime
    status: Literal["prospective", "in progress", "submitted", "not a good fit"]
    submission_link: Optional[str] = Field(default=None, max_length=2048)
    notes: str = Field(default="", max_length=10000)


class ContractCreate(ContractBase):
    assigned_contact_ids: List[str] = []


class ContractUpdate(ContractBase):
    assigned_contact_ids: List[str] = []


class ContractPatch(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = Field(default=None, max_length=50000)
    source: Optional[str] = Field(default=None, max_length=200)
    deadline: Optional[datetime] = None
    status: Optional[Literal["prospective", "in progress", "submitted", "not a good fit"]] = None
    submission_link: Optional[str] = Field(default=None, max_length=2048)
    notes: Optional[str] = Field(default=None, max_length=10000)
    assigned_contact_ids: Optional[List[str]] = None


class Contract(ContractBase):
    id: str
    created_at: datetime
    created_by_user_id: Optional[str] = None
    assigned_contact_ids: List[str] = []
    assigned_contacts: List[ContactBrief] = []

    class Config:
        from_attributes = True


# SAM.gov Import schemas
class SAMGovPointOfContact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    fullName: Optional[str] = None
    type: Optional[str] = None


class SAMGovOpportunity(BaseModel):
    noticeId: str = Field(max_length=255)
    title: str = Field(max_length=300)
    solicitationNumber: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=50000)
    responseDeadLine: Optional[str] = None
    postedDate: Optional[str] = None
    naicsCode: Optional[str] = Field(default=None, max_length=20)
    uiLink: Optional[str] = Field(default=None, max_length=2048)
    pointOfContact: Optional[List[SAMGovPointOfContact]] = None
    source: str = "SAM.gov"
    notes: Optional[str] = Field(default="", max_length=10000)


class SAMGovImportRequest(BaseModel):
    opportunities: List[SAMGovOpportunity]
    auto_create_contacts: bool = True


class SAMGovImportResponse(BaseModel):
    contracts_created: int
    contracts_skipped: int
    contacts_created: int
    errors: List[str] = []


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=150)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserCreateByAdmin(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: Literal["admin", "user"] = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "user"]] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
