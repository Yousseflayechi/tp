"""
Orchestrateur ETL DataOps.
Ordre strict : Extract -> Transform -> Load
Usage : python src/run.py
"""
import os
import sys
import psycopg2

# Allow running from project root or src/
sys.path.insert(0, os.path.dirname(__file__))

from extract import extract
from transform import clean, aggregate_by_month, aggregate_by_category
from load import get_engine, create_tables, load_ventes, load_mart, load_mart_category, log_etape

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://etl_user:etl_secret@localhost:5432/warehouse"
)
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ventes.csv")


def main():
    print("=== Pipeline ETL DataOps ===")
    conn = psycopg2.connect(DATABASE_URL)
    engine = get_engine(DATABASE_URL)

    try:
        create_tables(conn)

        # EXTRACT
        print("\n[1/3] Extract...")
        df_brut = extract(CSV_PATH)
        log_etape(conn, "extract", "success", nb_lignes=len(df_brut))

        # TRANSFORM
        print("\n[2/3] Transform (pandas)...")
        df_clean = clean(df_brut)
        df_mart = aggregate_by_month(df_clean)
        df_mart_cat = aggregate_by_category(df_clean)
        ecartees = len(df_brut) - len(df_clean)
        print(f"  {ecartees} lignes invalides ecartees")
        print(f"  {len(df_clean)} lignes valides")
        print(f"  CA total : {df_clean['montant'].sum():.2f} EUR")
        log_etape(conn, "transform", "success", nb_lignes=len(df_clean))

        # LOAD
        print("\n[3/3] Load (PostgreSQL)...")
        n1 = load_ventes(df_clean, engine)
        n2 = load_mart(df_mart, engine)
        n3 = load_mart_category(df_mart_cat, engine)
        log_etape(conn, "load", "success", nb_lignes=n1 + n2 + n3)

        print(f"\n  ventes_propres  : {n1} lignes")
        print(f"  ca_par_mois     : {n2} lignes")
        print(f"  ca_par_categorie: {n3} lignes")
        print("\n[DONE] Pipeline ETL termine avec succes.")

    except Exception as e:
        log_etape(conn, "pipeline", "failure", message=str(e))
        print(f"\n[ERROR] {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
