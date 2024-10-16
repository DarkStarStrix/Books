import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from Models import Base, User
import coverage

# Start coverage measurement
cov = coverage.Coverage ()
cov.start ()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine (SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker (autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all (bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal ()
        yield db
    finally:
        # noinspection PyUnboundLocalVariable
        db.close ()


app.dependency_overrides [get_db] = override_get_db

client = TestClient (app)


def create_test_user(db):
    hashed_password = get_password_hash ("testpassword")
    # noinspection PyArgumentList
    db_user = User (username="testuser", email="testuser@example.com", full_name="Test User", disabled=False,
                    password=hashed_password)
    db.add (db_user)
    db.commit ()
    db.refresh (db_user)
    return db_user


@pytest.fixture (scope="module")
def test_db():
    db = TestingSessionLocal ()
    yield db
    db.close ()


def login_user(client, username, password):
    response = client.post ("/token", data={"username": username, "password": password})
    return response


def register_user(client, username, password, email, full_name):
    response = client.post ("/register",
                            json={"username": username, "password": password, "email": email, "full_name": full_name})
    return response


def login_page(client):
    response = client.get ("/login")
    return response


def register_page(client):
    response = client.get ("/register")
    return response


def home_page(client):
    response = client.get ("/")
    return response


def login_for_access_token_success():
    db = next (override_get_db ())
    create_test_user (db)
    response = login_user (client, "testuser", "testpassword")
    assert response.status_code == 200
    assert "access_token" in response.json ()


def login_for_access_token_failure():
    response = login_user (client, "wronguser", "wrongpassword")
    assert response.status_code == 401


def register_user_success():
    response = register_user (client, "newuser", "newpassword", "newuser@example.com", "New User")
    assert response.status_code == 200
    assert response.json () ["username"] == "newuser"


def register_user_failure():
    db = next (override_get_db ())
    create_test_user (db)
    response = register_user (client, "testuser", "testpassword", "testuser@example.com", "Test User")
    assert response.status_code == 400


def read_root_success():
    response = home_page (client)
    assert response.status_code == 200


def login_page_success():
    response = login_page (client)
    assert response.status_code == 200


def register_page_success():
    response = register_page (client)
    assert response.status_code == 200


# Stop coverage measurement and save the report
cov.stop ()
cov.save ()
cov.html_report (directory='coverage_report')
