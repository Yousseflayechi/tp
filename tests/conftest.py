import pytest
import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://etl_user:etl_secret@localhost:5432/warehouse"
)

# ── Fixtures pandas (SANS base de donnees) ────────────────────────────────────

@pytest.fixture
def df_brut():
    """DataFrame brut avec lignes invalides intentionnelles."""
    return pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "client_email": ["Alice@Mail.com", "", "bob@mail.com", "carol@mail.com"],
        "date_vente": ["2024-01-05", "2024-01-06", "2024-01-07", "2024-02-01"],
        "montant": ["120.5", "50", "-10", "200"],
        "categorie": ["electronique", "vetements", "maison", "electronique"],
    })


@pytest.fixture
def df_clean(df_brut):
    """DataFrame apres clean() -- reutilisable dans tous les tests."""
    from src.transform import clean
    return clean(df_brut)


# ── Fixtures PostgreSQL (tests d'integration uniquement) ──────────────────────

@pytest.fixture(scope="session")
def db():
    conn = psycopg2.connect(DATABASE_URL)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def engine():
    return create_engine(DATABASE_URL)
