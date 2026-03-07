from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import (
    create_access_token,
    generate_api_key,
    get_password_hash,
    hash_api_key,
)
from app.database import Base, get_db
from app.main import app
from app.models.models import Communication, Contact, Contract, User
from app.utils import generate_id

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Provide a test HTTP client."""
    return TestClient(app)


@pytest.fixture
def admin_user(db) -> User:
    """Create and return an admin user."""
    user = User(
        id=generate_id(),
        email="admin@test.com",
        name="Admin User",
        hashed_password=get_password_hash("adminpass123"),
        role="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db) -> User:
    """Create and return a regular user."""
    user = User(
        id=generate_id(),
        email="user@test.com",
        name="Regular User",
        hashed_password=get_password_hash("userpass123"),
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def inactive_user(db) -> User:
    """Create and return an inactive user."""
    user = User(
        id=generate_id(),
        email="inactive@test.com",
        name="Inactive User",
        hashed_password=get_password_hash("inactivepass123"),
        role="user",
        is_active=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user) -> str:
    """Return a JWT token for the admin user."""
    return create_access_token(
        data={"sub": admin_user.email},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def user_token(regular_user) -> str:
    """Return a JWT token for the regular user."""
    return create_access_token(
        data={"sub": regular_user.email},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Return auth headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token) -> dict:
    """Return auth headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def sample_contact(db, admin_user) -> Contact:
    """Create and return a sample contact."""
    contact = Contact(
        id=generate_id(),
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="555-1234",
        organization="Test Corp",
        contact_type="individual",
        status="warm",
        needs_follow_up=False,
        notes="Test contact",
        assigned_user_id=admin_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@pytest.fixture
def sample_contact_for_regular(db, regular_user) -> Contact:
    """Create a contact assigned to the regular user."""
    contact = Contact(
        id=generate_id(),
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="555-5678",
        organization="Other Corp",
        contact_type="government",
        status="hot",
        needs_follow_up=True,
        follow_up_date=datetime.now(timezone.utc) + timedelta(days=3),
        notes="Regular user contact",
        assigned_user_id=regular_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@pytest.fixture
def sample_communication(db, sample_contact) -> Communication:
    """Create and return a sample communication."""
    comm = Communication(
        id=generate_id(),
        contact_id=sample_contact.id,
        date=datetime.now(timezone.utc),
        type="email",
        notes="Test communication",
        created_at=datetime.now(timezone.utc),
    )
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return comm


@pytest.fixture
def sample_contract(db) -> Contract:
    """Create and return a sample contract."""
    contract = Contract(
        id=generate_id(),
        title="Test Contract",
        description="Test description",
        source="SAM.gov",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        status="prospective",
        notes="Test notes",
        created_at=datetime.now(timezone.utc),
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@pytest.fixture
def sample_contract_owned_by_admin(db, admin_user) -> Contract:
    """Create a contract owned by admin user."""
    contract = Contract(
        id=generate_id(),
        title="Admin Contract",
        description="Owned by admin",
        source="SAM.gov",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        status="prospective",
        notes="Admin notes",
        created_by_user_id=admin_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@pytest.fixture
def user_with_api_key(db) -> tuple:
    """Create a user with a hashed API key. Returns (user, raw_api_key)."""
    raw_key = generate_api_key()
    user = User(
        id=generate_id(),
        email="apiuser@test.com",
        name="API User",
        hashed_password=get_password_hash("apiuserpass123"),
        role="user",
        is_active=True,
        api_key_hash=hash_api_key(raw_key),
        api_key_prefix=raw_key[:12] + "...",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, raw_key
