import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.seed_data import SEED_PLANTS
from app.models import Plant

TEST_DATABASE_URL = "sqlite:///./test_cropshield.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    for item in SEED_PLANTS:
        db.add(Plant(**item))
    db.commit()
    db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_auth_registration_and_login(client):
    reg_data = {
        "full_name": "Ramesh Patil",
        "email": "ramesh@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r = client.post("/api/auth/register", json=reg_data)
    assert r.status_code == 201
    res = r.json()
    assert "access_token" in res
    assert res["user"]["email"] == "ramesh@example.com"
    token = res["access_token"]

    # Duplicate registration should be rejected
    r_dup = client.post("/api/auth/register", json=reg_data)
    assert r_dup.status_code == 400
    assert "already exists" in r_dup.json()["detail"]

    # Login
    login_data = {
        "email": "ramesh@example.com",
        "password": "Password123!"
    }
    r_log = client.post("/api/auth/login", json=login_data)
    assert r_log.status_code == 200
    assert "access_token" in r_log.json()

    # Get /me
    r_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    assert r_me.json()["full_name"] == "Ramesh Patil"

def test_user_data_isolation_and_bookmarks(client):
    # Register User A
    user_a_res = client.post("/api/auth/register", json={
        "full_name": "User A",
        "email": "user_a@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_a = user_a_res["access_token"]

    # Register User B
    user_b_res = client.post("/api/auth/register", json={
        "full_name": "User B",
        "email": "user_b@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_b = user_b_res["access_token"]

    # User A bookmarks Plant 1
    r_bm = client.post("/api/plants/1/bookmark", headers={"Authorization": f"Bearer {token_a}"})
    assert r_bm.status_code == 201

    # Verify User A has 1 bookmark
    r_a_bms = client.get("/api/plants/bookmarks", headers={"Authorization": f"Bearer {token_a}"})
    assert r_a_bms.status_code == 200
    assert len(r_a_bms.json()) == 1
    assert r_a_bms.json()[0]["id"] == 1

    # Verify User B has 0 bookmarks (Data Isolation)
    r_b_bms = client.get("/api/plants/bookmarks", headers={"Authorization": f"Bearer {token_b}"})
    assert r_b_bms.status_code == 200
    assert len(r_b_bms.json()) == 0

    # User A removes bookmark
    r_del = client.delete("/api/plants/1/bookmark", headers={"Authorization": f"Bearer {token_a}"})
    assert r_del.status_code == 200

    r_a_bms_after = client.get("/api/plants/bookmarks", headers={"Authorization": f"Bearer {token_a}"})
    assert len(r_a_bms_after.json()) == 0

def test_plantopedia_search_and_detail(client):
    user_res = client.post("/api/auth/register", json={
        "full_name": "Test Searcher",
        "email": "searcher@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token = user_res["access_token"]

    # Search for Tomato
    r = client.get("/api/plants?q=Tomato", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any("Tomato" in p["common_name"] for p in data["items"])

    # Detail
    plant_id = data["items"][0]["id"]
    r_detail = client.get(f"/api/plants/{plant_id}", headers={"Authorization": f"Bearer {token}"})
    assert r_detail.status_code == 200
    assert r_detail.json()["common_name"] == data["items"][0]["common_name"]

def test_demo_stores(client):
    r = client.get("/api/stores/demo")
    assert r.status_code == 200
    stores = r.json()
    assert len(stores) >= 5
    assert all(s["is_demo"] is True for s in stores)
    assert all("[DEMO" in s["address"] for s in stores)
