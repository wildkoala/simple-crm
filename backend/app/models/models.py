from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for many-to-many relationship between contracts and contacts
contract_contacts = Table(
    "contract_contacts",
    Base.metadata,
    Column("contract_id", String(36), ForeignKey("contracts.id", ondelete="CASCADE")),
    Column("contact_id", String(36), ForeignKey("contacts.id", ondelete="CASCADE")),
)

# Association table for many-to-many relationship between opportunities and contract vehicles
opportunity_vehicles = Table(
    "opportunity_vehicles",
    Base.metadata,
    Column(
        "opportunity_id", String(36), ForeignKey("opportunities.id", ondelete="CASCADE")
    ),
    Column("vehicle_id", String(36), ForeignKey("contract_vehicles.id", ondelete="CASCADE")),
)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    account_type = Column(
        String(30), nullable=False
    )  # government_agency, prime_contractor, subcontractor, partner, vendor
    parent_agency = Column(String(300), nullable=True)
    office = Column(String(300), nullable=True)
    location = Column(String(300), nullable=True)
    website = Column(String(2048), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    contacts = relationship("Contact", back_populates="account")
    teaming_records = relationship("Teaming", back_populates="partner_account")


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
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True, index=True)
    title = Column(String(200), nullable=True)
    relationship_strength = Column(String(30), nullable=True)  # contracting_officer, etc.

    # Relationships
    communications = relationship(
        "Communication", back_populates="contact", cascade="all, delete-orphan"
    )
    contracts = relationship(
        "Contract", secondary=contract_contacts, back_populates="assigned_contacts"
    )
    assigned_user = relationship("User", back_populates="assigned_contacts")
    account = relationship("Account", back_populates="contacts")


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
    managed_opportunities = relationship(
        "Opportunity",
        back_populates="capture_manager",
        foreign_keys="Opportunity.capture_manager_id",
    )
    managed_proposals = relationship(
        "Proposal",
        back_populates="proposal_manager",
        foreign_keys="Proposal.proposal_manager_id",
    )


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    is_government_contract = Column(Boolean, nullable=False, default=False)
    description = Column(Text, default="")
    agency = Column(String(300), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True, index=True)
    naics_code = Column(String(20), nullable=True)
    set_aside_type = Column(
        String(30), nullable=True
    )  # small_business, 8a, hubzone, wosb, sdvosb, full_and_open, none
    estimated_value = Column(Float, nullable=True)
    solicitation_number = Column(String(255), nullable=True)
    sam_gov_notice_id = Column(String(255), nullable=True, index=True)
    submission_link = Column(String(2048), nullable=True)
    deadline = Column(DateTime, nullable=True)
    source = Column(
        String(30), nullable=True
    )  # sam_gov, agency_forecast, incumbent_recompete, partner_referral, internal
    stage = Column(
        String(20), nullable=False, index=True, default="identified"
    )  # identified, qualified, capture, teaming, proposal, submitted, awarded, lost
    capture_manager_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    expected_release_date = Column(DateTime, nullable=True)
    proposal_due_date = Column(DateTime, nullable=True)
    award_date_estimate = Column(DateTime, nullable=True)
    win_probability = Column(Integer, nullable=True)  # 0-100
    notes = Column(Text, default="")
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    account = relationship("Account", foreign_keys=[account_id])
    capture_manager = relationship(
        "User", back_populates="managed_opportunities", foreign_keys=[capture_manager_id]
    )
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    vehicles = relationship(
        "ContractVehicle", secondary=opportunity_vehicles, back_populates="opportunities"
    )
    teaming_records = relationship(
        "Teaming", back_populates="opportunity", cascade="all, delete-orphan"
    )
    proposal = relationship(
        "Proposal", back_populates="opportunity", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def vehicle_ids(self):
        return [v.id for v in self.vehicles]


class ContractVehicle(Base):
    __tablename__ = "contract_vehicles"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    agency = Column(String(300), nullable=True)
    contract_number = Column(String(255), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    ceiling_value = Column(Float, nullable=True)
    prime_or_sub = Column(String(10), nullable=True)  # prime, sub
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    opportunities = relationship(
        "Opportunity", secondary=opportunity_vehicles, back_populates="vehicles"
    )


class Teaming(Base):
    __tablename__ = "teaming"

    id = Column(String(36), primary_key=True, index=True)
    opportunity_id = Column(
        String(36), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    partner_account_id = Column(
        String(36), ForeignKey("accounts.id"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False)  # prime, subcontractor, jv_partner
    status = Column(
        String(20), nullable=False, default="potential"
    )  # potential, nda_signed, teaming_agreed, active, inactive
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    opportunity = relationship("Opportunity", back_populates="teaming_records")
    partner_account = relationship("Account", back_populates="teaming_records")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, index=True)
    opportunity_id = Column(
        String(36), ForeignKey("opportunities.id"), nullable=False, unique=True, index=True
    )
    proposal_manager_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    submission_type = Column(String(20), nullable=True)  # full, partial, draft
    submission_deadline = Column(DateTime, nullable=True)
    status = Column(
        String(20), nullable=False, default="not_started"
    )  # not_started, in_progress, review, final, submitted
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    opportunity = relationship("Opportunity", back_populates="proposal")
    proposal_manager = relationship(
        "User", back_populates="managed_proposals", foreign_keys=[proposal_manager_id]
    )


class Compliance(Base):
    __tablename__ = "compliance"

    id = Column(String(36), primary_key=True, index=True)
    certification_type = Column(
        String(30), nullable=False
    )  # small_business, 8a, hubzone, wosb, sdvosb, edwosb
    issued_by = Column(String(300), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    status = Column(
        String(20), nullable=False, default="active"
    )  # active, expiring_soon, expired, pending
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
