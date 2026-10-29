# tests/conftest.py
import pytest
import os
import sys
import shutil

# Ensure src directory is in sys.path for test imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

# Isolar banco de dados de testes para não poluir data/app.db da aplicação
PROD_DB = os.path.join(ROOT_DIR, "data", "app.db")
TEST_DB = os.path.join(ROOT_DIR, "data", "test_app.db")
if os.path.exists(PROD_DB):
    shutil.copyfile(PROD_DB, TEST_DB)
os.environ["SQLITE_DSN"] = "sqlite+aiosqlite:///data/test_app.db"
os.environ["APP_DB_URL"] = "sqlite+aiosqlite:///data/test_app.db"

from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    """
    Fixture de teste que fornece um TestClient configurado para fazer requisições à aplicação FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client
