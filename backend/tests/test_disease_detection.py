import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Plant, DiseaseDetection, User
from app.seed_data import SEED_PLANTS
from app.services.disease_model import disease_model_service

TEST_DATABASE_URL = "sqlite:///./test_cropshield_disease.db"
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

def create_test_image(format="JPEG", size=(256, 256), color=(40, 150, 40)):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()

def test_unauthenticated_detection_request(client):
    img_bytes = create_test_image()
    files = {"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    data = {"crop": "Tomato"}
    response = client.post("/api/disease/detect", data=data, files=files)
    assert response.status_code == 401

def test_successful_inference_and_database_persistence(client):
    # Register and login user
    user_data = {
        "full_name": "Kavita Rao",
        "email": "kavita@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    reg_res = client.post("/api/auth/register", json=user_data)
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload valid plant image
    img_bytes = create_test_image(format="JPEG")
    files = {"file": ("test_tomato_leaf.jpg", img_bytes, "image/jpeg")}
    data = {"crop": "Tomato"}

    detect_res = client.post("/api/disease/detect", data=data, files=files, headers=headers)
    assert detect_res.status_code == 201
    result = detect_res.json()

    # Validate output structure
    assert "id" in result
    assert "predicted_label" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], int)
    assert 0 <= result["confidence"] <= 100
    assert "is_healthy" in result
    assert "model_version" in result
    assert result["model_version"] == "mobilenet_v2_plantvillage_v1"
    assert "top_classes" in result
    assert len(result["top_classes"]) > 0
    assert "disease_info" in result
    assert "precautions" in result["disease_info"]
    assert len(result["disease_info"]["precautions"]) > 0

    record_id = result["id"]

    # Verify history list contains the record
    hist_res = client.get("/api/disease/history", headers=headers)
    assert hist_res.status_code == 200
    history_items = hist_res.json()
    assert len(history_items) >= 1
    assert any(h["id"] == record_id for h in history_items)

    # Fetch record detail by ID
    detail_res = client.get(f"/api/disease/history/{record_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["predicted_label"] == result["predicted_label"]

def test_user_history_isolation(client):
    # Register Farmer A
    user_a = client.post("/api/auth/register", json={
        "full_name": "Farmer A",
        "email": "farmer_a@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_a = user_a["access_token"]

    # Register Farmer B
    user_b = client.post("/api/auth/register", json={
        "full_name": "Farmer B",
        "email": "farmer_b@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_b = user_b["access_token"]

    # Farmer A submits detection
    img_bytes = create_test_image()
    res_a = client.post(
        "/api/disease/detect",
        data={"crop": "Potato"},
        files={"file": ("potato_leaf.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res_a.status_code == 201
    record_a_id = res_a.json()["id"]

    # Farmer B should NOT see Farmer A's detection in history list
    hist_b = client.get("/api/disease/history", headers={"Authorization": f"Bearer {token_b}"})
    assert hist_b.status_code == 200
    b_records = [r["id"] for r in hist_b.json()]
    assert record_a_id not in b_records

    # Farmer B attempting to access Farmer A's record ID directly should get 403 Forbidden
    detail_forbidden = client.get(
        f"/api/disease/history/{record_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert detail_forbidden.status_code == 403

def test_invalid_file_format_rejected(client):
    # Login
    user_res = client.post("/api/auth/register", json={
        "full_name": "Tester",
        "email": "tester_upload@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    headers = {"Authorization": f"Bearer {user_res['access_token']}"}

    # Upload plain text disguised as image
    fake_img = b"This is not a real image file content."
    files = {"file": ("malicious.jpg", fake_img, "image/jpeg")}
    r = client.post("/api/disease/detect", data={"crop": "Tomato"}, files=files, headers=headers)
    assert r.status_code == 400
    assert "Corrupted or invalid image data" in r.json()["detail"] or "Unsupported" in r.json()["detail"]

def test_corrupted_image_rejected(client):
    user_res = client.post("/api/auth/login", json={
        "email": "tester_upload@example.com",
        "password": "Password123!"
    }).json()
    headers = {"Authorization": f"Bearer {user_res['access_token']}"}

    # Incomplete byte header
    corrupt_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00deadbeefcorruptedpayload"
    files = {"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    r = client.post("/api/disease/detect", data={"crop": "Tomato"}, files=files, headers=headers)
    assert r.status_code == 400

def test_model_status_endpoint(client):
    r = client.get("/api/disease/status")
    assert r.status_code == 200
    data = r.json()
    assert data["is_configured"] is True
    assert data["total_classes"] == 38
    assert "Tomato" in data["supported_crops"]
