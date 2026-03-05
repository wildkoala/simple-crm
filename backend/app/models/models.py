from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for many-to-many relationship between contracts and contacts
contract_contacts = Table(
    "contract_contacts",
    Base.metadata,
    Column("contract_id", String(36), ForeignKey("contracts.id", ondelete="CASCADE")),
    Column("contact_id", String(36), ForeignKey("contacts.id", ondelete="CASCADE")),
)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    organization = Column(String(200), nullable=False)
    contact_type = Column(String(20), nullable=False)  # individual, commercial, government
    status = Column(String(20), nullable=False, index=True)  # cold, warm, hot
    needs_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True, index=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_contacted_at = Column(DateTime, nullable=True)
    assigned_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    communications = relationship(
        "Communication", back_populates="contact", cascade="all, delete-orphan"
    )
    contracts = relationship(
        "Contract", secondary=contract_contacts, back_populates="assigned_contacts"
    )
    assigned_user = relationship("User", back_populates="assigned_contacts")


class Communication(Base):
    __tablename__ = "communications"

    id = Column(String(36), primary_key=True, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # email, phone, meeting, other
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    contact = relationship("Contact", back_populates="communications")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    source = Column(String(200), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(
        String(20), nullable=False, index=True
    )  # prospective, in progress, submitted, not a good fit
    sam_gov_notice_id = Column(String(255), nullable=True, unique=True, index=True)
    submission_link = Column(String(2048), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationships
    assigned_contacts = relationship(
        "Contact", secondary=contract_contacts, back_populates="contracts"
    )
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])

    @property
    def assigned_contact_ids(self):
        return [c.id for c in self.assigned_contacts]


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # "admin" or "user"
    is_active = Column(Boolean, nullable=False, default=True)
    api_key_hash = Column(String(255), unique=True, nullable=True, index=True)
    api_key_prefix = Column(String(20), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    assigned_contacts = relationship("Contact", back_populates="assigned_user")
