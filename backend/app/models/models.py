from sqlalchemy import Boolean, Column, Index, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

# Association table for many-to-many relationship between contracts and contacts
contract_contacts = Table(
    'contract_contacts',
    Base.metadata,
    Column('contract_id', String, ForeignKey('contracts.id', ondelete='CASCADE')),
    Column('contact_id', String, ForeignKey('contacts.id', ondelete='CASCADE'))
)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    contact_type = Column(String, nullable=False)  # individual, commercial, government
    status = Column(String, nullable=False, index=True)  # cold, warm, hot
    needs_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_contacted_at = Column(DateTime, nullable=True)
    assigned_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    communications = relationship("Communication", back_populates="contact", cascade="all, delete-orphan")
    contracts = relationship("Contract", secondary=contract_contacts, back_populates="assigned_contacts")
    assigned_user = relationship("User", back_populates="assigned_contacts")


class Communication(Base):
    __tablename__ = "communications"

    id = Column(String, primary_key=True, index=True)
    contact_id = Column(String, ForeignKey("contacts.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    type = Column(String, nullable=False, index=True)  # email, phone, meeting, other
    notes = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    contact = relationship("Contact", back_populates="communications")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    source = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, index=True)  # prospective, in progress, submitted, not a good fit
    sam_gov_notice_id = Column(String, nullable=True, unique=True, index=True)
    submission_link = Column(String, nullable=True)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    assigned_contacts = relationship("Contact", secondary=contract_contacts, back_populates="contracts")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])

    @property
    def assigned_contact_ids(self):
        return [c.id for c in self.assigned_contacts]


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # "admin" or "user"
    is_active = Column(Boolean, nullable=False, default=True)
    api_key_hash = Column(String, unique=True, nullable=True, index=True)
    api_key_prefix = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    password_reset_token = Column(String, nullable=True, index=True)
    password_reset_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    assigned_contacts = relationship("Contact", back_populates="assigned_user")
