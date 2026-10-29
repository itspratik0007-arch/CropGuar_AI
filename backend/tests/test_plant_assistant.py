import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth import hash_password, create_access_token
from app.models import User, Plant, PlantConversation, ConversationMessage
from app.seed_data import SEED_PLANTS

TEST_DATABASE_URL = "sqlite:///./test_cropshield.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    # Create test user 1
    u1 = User(
        full_name="Rajesh Patil",
        email="rajesh.farmer@example.com",
        hashed_password=hash_password("FarmSecurePass123!"),
        farm_location="Pune, Maharashtra"
    )
    # Create test user 2 (for user-isolation checks)
    u2 = User(
        full_name="Sunita Sharma",
        email="sunita.grower@example.com",
        hashed_password=hash_password("GrowerSecret456!"),
        farm_location="Nashik, Maharashtra"
    )
    db.add(u1)
    db.add(u2)
    db.commit()

    # Seed plants
    for p_data in SEED_PLANTS:
        db.add(Plant(**p_data))
    db.commit()
    db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

def get_auth_headers(email="rajesh.farmer@example.com"):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}

def test_plant_search_endpoint(client):
    headers = get_auth_headers()
    # Test search query
    response = client.get("/api/plants/search?q=tomato", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Tomato" in item["common_name"] for item in data["items"])

def test_plant_detail_endpoint(client):
    headers = get_auth_headers()
    db = TestingSessionLocal()
    plant = db.query(Plant).filter(Plant.common_name == "Tomato").first()
    db.close()
    assert plant is not None

    response = client.get(f"/api/plants/{plant.id}", headers=headers)
    assert response.status_code == 200
    detail = response.json()
    assert detail["scientific_name"] == "Solanum lycopersicum"
    assert detail["temperature_range"] is not None
    assert detail["fertilizer"] is not None
    assert detail["common_diseases"] is not None

def test_plant_assistant_chat_and_persistence(client):
    headers = get_auth_headers("rajesh.farmer@example.com")
    db = TestingSessionLocal()
    plant = db.query(Plant).filter(Plant.common_name == "Tomato").first()
    db.close()

    payload = {
        "message": "What is the recommended fertilizer schedule and what if I overwater it?",
        "plant_id": plant.id
    }
    response = client.post("/api/plant-assistant/chat", json=payload, headers=headers)
    assert response.status_code == 200
    res_data = response.json()

    assert "conversation_id" in res_data
    conv_id = res_data["conversation_id"]
    assert res_data["plant_id"] == plant.id
    assert res_data["message"]["role"] == "assistant"
    assert len(res_data["message"]["content"]) > 50

    # Follow-up turn in same conversation
    follow_up_payload = {
        "message": "How can I prevent early fungal blight naturally?",
        "conversation_id": conv_id,
        "plant_id": plant.id
    }
    follow_up_res = client.post("/api/plant-assistant/chat", json=follow_up_payload, headers=headers)
    assert follow_up_res.status_code == 200
    fu_data = follow_up_res.json()
    assert fu_data["conversation_id"] == conv_id

    # Fetch conversation details
    detail_res = client.get(f"/api/plant-assistant/conversations/{conv_id}", headers=headers)
    assert detail_res.status_code == 200
    conv_detail = detail_res.json()
    # Should have 4 messages (2 user, 2 assistant)
    assert len(conv_detail["messages"]) == 4

def test_conversation_user_isolation(client):
    headers_u1 = get_auth_headers("rajesh.farmer@example.com")
    headers_u2 = get_auth_headers("sunita.grower@example.com")

    # User 1 creates conversation
    create_res = client.post("/api/plant-assistant/chat", json={"message": "Wheat rust protection"}, headers=headers_u1)
    conv_id = create_res.json()["conversation_id"]

    # User 2 attempts to read User 1's conversation -> 403 Forbidden
    unauth_get = client.get(f"/api/plant-assistant/conversations/{conv_id}", headers=headers_u2)
    assert unauth_get.status_code == 403

    # User 2 attempts to delete User 1's conversation -> 403 Forbidden
    unauth_delete = client.delete(f"/api/plant-assistant/conversations/{conv_id}", headers=headers_u2)
    assert unauth_delete.status_code == 403

    # User 1 deletes their own conversation -> 200 OK
    auth_delete = client.delete(f"/api/plant-assistant/conversations/{conv_id}", headers=headers_u1)
    assert auth_delete.status_code == 200

def test_disease_history_alias_endpoint(client):
    headers = get_auth_headers()
    res = client.get("/api/disease-history", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_gemini_service_integration():
    from app.services.ai_assistant import ai_assistant_service
    # When GEMINI_API_KEY is not configured in local environment, it safely reports fallback mode
    res = await ai_assistant_service.generate_response(
        messages=[{"role": "user", "content": "How much water does tomato need?"}],
        plant_context={"common_name": "Tomato", "scientific_name": "Solanum lycopersicum", "watering": "Regular"}
    )
    assert "content" in res
    assert len(res["content"]) > 30
    assert "model" in res

@pytest.mark.asyncio
async def test_perenual_service_integration():
    from app.services.plant_api import plant_api_service
    # Verifies service properties and graceful behavior when key is not configured
    if not plant_api_service.is_perenual_configured:
        res = await plant_api_service.search_plants("tomato")
        assert res is None or isinstance(res, list)

