# CropShield AI — Phase 1 Working Application

CropShield AI is an intelligent crop-health intelligence platform. This repository contains the complete **Phase 1** implementation, featuring secure user authentication, persistent database storage, an interactive authenticated dashboard, a botanical Plantopedia with external API integration & curated fallback data, and a dummy agricultural supplier directory.

---

## 1. Phase 1 Scope & Features

### Active & Fully Functional Features:
- **Authentication**:
  - Secure User Registration with password confirmation and full validation.
  - Argon2id password hashing and JWT bearer token authentication.
  - Session persistence across page reloads.
  - Clean Logout and token invalidation.
- **Database Persistence**:
  - PostgreSQL support (and zero-config SQLite development mode).
  - Alembic database migrations.
  - Automated database seeding script for Plantopedia.
  - Multi-tenant data isolation: users can only view and manage their own bookmarks and dashboard records.
- **Authenticated Dashboard**:
  - Personalized farmer greeting with real user details from the database.
  - Total saved plants counter and recently bookmarked crops list.
  - Quick-search shortcut directly into Plantopedia.
  - Transparent feature cards marking future capabilities as "Coming Soon".
- **Plantopedia**:
  - Search by common name, scientific name, or botanical family.
  - External API integration with graceful curated local fallback.
  - 10 curated starter crops: **Tomato, Wheat, Rice, Mango, Neem, Chilli, Potato, Cotton, Banana, Soybean**.
  - Detailed modal views displaying sunlight, watering, soil requirements, climate, and cultivation facts.
  - Save/Bookmark and Remove Bookmark functionality connected directly to database records.
- **Nearby Stores (Demo)**:
  - Fictional agricultural suppliers (seeds, fertilizers, bio-inputs, implements).
  - Prominent "DEMO DATA ONLY" warning banner.
  - Category filters and product search.
  - No live GPS tracking, fake distance calculations, or unverified contact details.

- **AI Plant Disease Detection**:
  - Pretrained MobileNetV2 vision classification model fine-tuned on the benchmark PlantVillage dataset (38 disease and healthy classes across 14 crop varieties).
  - Drag-and-drop leaf image upload with instant client-side preview, format validation, and dimension checking.
  - CPU-optimized ONNX Runtime inference pipeline (quantized 2.68 MB model loaded once on startup).
  - Softmax multi-class probability ranking with confidence scores and healthy vs. diseased categorization.
  - Verified agronomic precautions, botanical descriptions, and cross-links to Plantopedia crop entries.
  - Per-user isolated detection history with deletion, detail inspection, and ownership enforcement.

### Explicitly Out of Scope (Marked "Coming Soon"):
- Weather-based microclimate disease-risk prediction models
- Direct pesticide prescriptions or chemical dosage calculators (only verified agronomic management precautions are provided)

---

## 2. Technology Stack

- **Frontend**:
  - React 19 + TypeScript + Vite
  - Tailwind CSS + Lucide Icons
  - React Router
- **Backend**:
  - Python 3.12 + FastAPI
  - SQLAlchemy 2.0 ORM
  - Alembic Database Migrations
  - Argon2id (`argon2-cffi`) password hashing + `python-jose` JWT
  - `pydantic[email]` with `email-validator`
- **Database**:
  - PostgreSQL 16 (via Docker Compose)
  - SQLite (default fallback for instant zero-dependency local runs)

---

## 3. Windows Setup & Run Instructions

### Prerequisites
- Python 3.12+ installed
- Node.js (v18+) and npm installed
- *(Optional)* Docker Desktop if running PostgreSQL via Docker

---

### Step 1: Clone & Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Default `.env` settings:
```ini
DATABASE_URL=sqlite:///./cropshield.db
SECRET_KEY=cropshield_phase1_super_secret_jwt_key_local_dev_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PLANT_API_KEY=
PLANT_API_BASE_URL=https://trefle.io/api/v1
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

> **Using PostgreSQL via Docker (Recommended for production/Docker users)**:
> ```powershell
> docker compose up -d
> ```
> Then update `.env`:
> ```ini
> DATABASE_URL=postgresql://cropshield_user:cropshield_password@localhost:5432/cropshield_db
> ```

---

### Step 2: Set Up Backend

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd c:\Users\prati\OneDrive\Desktop\CropShield_AI_Website
   ```

2. Create virtual environment and install dependencies:
   ```powershell
   python -m venv backend/venv
   .\backend\venv\Scripts\python.exe -m pip install -r backend/requirements.txt
   ```

3. Run Alembic migrations:
   ```powershell
   .\backend\venv\Scripts\alembic.exe upgrade head
   ```

4. Seed the Plantopedia starter crops:
   ```powershell
   .\backend\venv\Scripts\python.exe backend/app/seed.py
   ```

5. Start the FastAPI backend server:
   ```powershell
   $env:PYTHONPATH="backend"
   .\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *FastAPI Interactive Docs:* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Step 3: Set Up Frontend

1. In a new PowerShell window, navigate to the `frontend` directory:
   ```powershell
   cd c:\Users\prati\OneDrive\Desktop\CropShield_AI_Website\frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start Vite development server:
   ```powershell
   npm run dev
   ```

4. Open your browser at [http://127.0.0.1:5173](http://127.0.0.1:5173).

---

## 4. Running Automated Tests

Run backend tests for authentication, database persistence, bookmarks, and user isolation:
```powershell
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\pytest.exe backend/tests/test_phase1.py -v
```

---

## 5. External Plant API Configuration (Trefle)

To connect live external botanical searches:
1. Register for a free API token at [https://trefle.io](https://trefle.io).
2. Set your API key in `.env`:
   ```ini
   PLANT_API_KEY=your_trefle_token_here
   PLANT_API_BASE_URL=https://trefle.io/api/v1
   ```
3. Restart the backend server.
4. When `PLANT_API_KEY` is empty or rate-limited, the system automatically uses the curated starter collection.
