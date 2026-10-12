import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.models.base import Base
import backend.app.models
from backend.app.db.session import get_db
from backend.app.db.seed import seed_database
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.memory_cache import InMemoryCache
from backend.app.main import app

from sqlalchemy.pool import StaticPool

# In-memory SQLite for testing with StaticPool so all connections share the memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    seed_database(session, force=True)
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def test_cache():
    return InMemoryCache()

@pytest.fixture(scope="function")
def client(db_session, test_cache):
    def override_get_db():
        yield db_session

    async def override_get_cache():
        return test_cache

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache_dependency] = override_get_cache

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
