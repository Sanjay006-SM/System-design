# NexusPulse — High-Concurrency Personalized News & Information Platform

A production-grade, end-to-end full-stack Personalized News Platform designed to scale to millions of concurrent users during breaking news events.

---

## 🌟 Key Features

1. **Full-Text News Search**: Keyword search across titles, summaries, and topics with pagination and validation.
2. **Article Details & View Tracking**: Non-blocking background view counter tracking.
3. **Topic Following & Unfollowing**: Strict uniqueness constraints, immediate feed invalidation.
4. **Personalized News Feed**: Recency, topic relevance, and user engagement scoring engine.
5. **Trending News**: Recency and engagement weighted algorithm with cache-aside pattern.
6. **Real-time Event-Driven Notifications**: Async event bus broadcasting `NewArticlePublished` events to topic subscribers.
7. **Resilient Architecture**: Automatic fallback from Redis to In-Memory cache, and from PostgreSQL to SQLite.
8. **Interactive React + Vite Dashboard**: Dark/Light mode, user switching, live health status, breaking news publishing simulator.

---

## 🏗️ Architecture & Low-Level Design

### Core Services
- **API Gateway / Router**: FastAPI 3.13 REST API with JSON structured logging and centralized exception handling.
- **Cache Layer**: Redis cache backend with automatic in-memory fallback.
- **Event / Messaging Layer**: Asyncio event bus with Kafka adapter abstraction.
- **Database Layer**: SQLAlchemy ORM with foreign keys, indexes, and cascades.

---

## 🚀 Quick Start Instructions

### 1. Backend Setup

#### Windows PowerShell:
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend development server (automatically seeds 32 articles & topics)
uvicorn backend.app.main:app --reload --port 8000
```

#### Ubuntu / Linux:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

---

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- **Frontend App**: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the backend test suite:

```powershell
.\backend\venv\Scripts\pytest backend/tests/test_api.py -v
```

---

## 🐳 Docker Deployment (Optional)

```bash
docker compose up -d
```
Starts PostgreSQL, Redis, and the FastAPI application in isolated containers.
