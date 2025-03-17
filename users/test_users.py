import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from config import settings
from main import app
from users.schemas import UserCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from users.models import *
from passlib.context import CryptContext

engine = create_engine(settings.SYNC_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="module")
def db():
    """Set up a session for database interaction during tests."""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_users(db: Session):
    db.query(User).filter(User.email == "testuser@example.com").delete()
    db.commit()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@pytest.fixture
def create_test_user(db: Session):
    hashed_password = hash_password("password123")
    user_data = UserCreate(
        email="testuser@example.com", first_name="Test", last_name="User", password=hashed_password
    )
    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def test_register(client: TestClient):
    data = {"email": "newuser@example.com", "password": "newpassword123"}
    response = client.post("/users/register", json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"


def test_register_existing_email(client: TestClient, create_test_user: User):
    data = {"email": create_test_user.email, "password": "newpassword123"}
    response = client.post("/users/register", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login(create_test_user, db: Session):
    user = db.query(User).filter_by(email="testuser@example.com").first()
    assert verify_password("password123", user.password)


def test_get_profile(client: TestClient, create_test_user: User):
    login_data = {"email": create_test_user.email, "password": "password123"}
    login_response = client.post("/users/token", data=login_data)
    access_token = login_response.json()["access_token"]

    response = client.get("/users/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == create_test_user.email


def test_update_user(client: TestClient, create_test_user: User):
    login_data = {"email": create_test_user.email, "password": "password123"}
    login_response = client.post("/users/token", data=login_data)
    access_token = login_response.json()["access_token"]

    updated_data = {"email": "updateduser@example.com", "first_name": "Updated", "last_name": "User"}
    response = client.put("/users/update", json=updated_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "updateduser@example.com"


def test_delete_user(client: TestClient, create_test_user: User):
    login_data = {"email": create_test_user.email, "password": "password123"}
    login_response = client.post("/users/token", data=login_data)
    access_token = login_response.json()["access_token"]

    response = client.delete("/users/delete", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == f"User {create_test_user.id} deleted"
