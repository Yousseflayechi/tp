import pytest
from src.load import create_tables, load_ventes, load_mart, load_mart_category
from src.transform import aggregate_by_month, aggregate_by_category


@pytest.fixture(scope="module", autouse=True)
def setup_db(db, engine, df_clean):
    """Prepare la base : cree les tables et charge les donnees de test."""
    create_tables(db)
    load_ventes(df_clean, engine)
    load_mart(aggregate_by_month(df_clean), engine)
    load_mart_category(aggregate_by_category(df_clean), engine)


def query(db, sql):
    with db.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]


class TestLoadVentes:

    def test_ventes_propres_count(self, db, df_clean):
        """La table doit contenir le meme nombre de lignes que le DataFrame."""
        n = query(db, "SELECT COUNT(*) FROM ventes_propres")
        assert n == len(df_clean)

    def test_ventes_pas_de_montant_negatif(self, db):
        """Aucun montant negatif dans la table."""
        n = query(db, "SELECT COUNT(*) FROM ventes_propres WHERE montant <= 0")
        assert n == 0

    def test_ventes_pas_email_vide(self, db):
        """Aucun email vide dans la table."""
        n = query(db, """
            SELECT COUNT(*) FROM ventes_propres
            WHERE client_email IS NULL OR client_email = ''
        """)
        assert n == 0

    def test_ventes_montant_total(self, db):
        """Le CA total en base doit etre correct."""
        total = query(db, "SELECT SUM(montant) FROM ventes_propres")
        assert float(total) == pytest.approx(320.5)


class TestLoadMart:

    def test_ca_par_mois_count(self, db):
        """La table ca_par_mois doit contenir 2 mois."""
        n = query(db, "SELECT COUNT(*) FROM ca_par_mois")
        assert n == 2

    def test_ca_par_mois_ca_positif(self, db):
        """Tous les CA mensuels doivent etre positifs."""
        mini = query(db, "SELECT MIN(chiffre_affaires) FROM ca_par_mois")
        assert mini > 0


class TestLoadMartCategory:
    """Tests bonus pour load_mart_category()."""

    def test_ca_par_categorie_count(self, db, df_clean):
        """La table ca_par_categorie doit contenir le bon nombre de categories."""
        n = query(db, "SELECT COUNT(*) FROM ca_par_categorie")
        expected = df_clean["categorie"].nunique()
        assert n == expected

    def test_ca_par_categorie_ca_positif(self, db):
        """Tous les CA par categorie doivent etre positifs."""
        mini = query(db, "SELECT MIN(chiffre_affaires) FROM ca_par_categorie")
        assert mini > 0
