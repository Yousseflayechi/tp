import pytest
import pandas as pd
from src.transform import clean, aggregate_by_month, aggregate_by_category


class TestClean:

    def test_clean_retire_email_vide(self, df_brut):
        """clean() doit supprimer les lignes sans email."""
        df = clean(df_brut)
        assert "" not in df["client_email"].values

    def test_clean_retire_montant_negatif(self, df_brut):
        """clean() doit supprimer les lignes avec montant <= 0."""
        df = clean(df_brut)
        assert (df["montant"] > 0).all()

    def test_clean_nombre_lignes(self, df_brut):
        """Apres clean(), 2 lignes valides restent (email vide + negatif supprimes)."""
        df = clean(df_brut)
        assert len(df) == 2

    def test_clean_email_lowercase(self, df_brut):
        """Les emails doivent etre en minuscules et sans espaces."""
        df = clean(df_brut)
        assert df["client_email"].iloc[0] == "alice@mail.com"

    def test_clean_montant_float(self, df_brut):
        """La colonne montant doit etre de type float64."""
        df = clean(df_brut)
        assert df["montant"].dtype == "float64"

    def test_clean_date_datetime(self, df_brut):
        """La colonne date_vente doit etre de type datetime."""
        df = clean(df_brut)
        assert pd.api.types.is_datetime64_any_dtype(df["date_vente"])

    def test_clean_ne_modifie_pas_original(self, df_brut):
        """clean() ne doit pas modifier le DataFrame original."""
        original_len = len(df_brut)
        clean(df_brut)
        assert len(df_brut) == original_len

    def test_clean_index_reset(self, df_brut):
        """L'index du DataFrame nettoye doit etre reinitialise."""
        df = clean(df_brut)
        assert list(df.index) == list(range(len(df)))

    def test_clean_categorie_title_case(self, df_brut):
        """Les categories doivent etre en Title Case."""
        df = clean(df_brut)
        for cat in df["categorie"]:
            assert cat == cat.title()


class TestAggregateByMonth:

    def test_agg_nombre_mois(self, df_clean):
        """Le DataFrame fixture a 2 mois distincts (janv + fevr)."""
        mart = aggregate_by_month(df_clean)
        assert len(mart) == 2

    def test_agg_ca_total(self, df_clean):
        """Le CA total doit correspondre a la somme des montants valides."""
        mart = aggregate_by_month(df_clean)
        assert mart["chiffre_affaires"].sum() == pytest.approx(320.5)

    def test_agg_colonnes_presentes(self, df_clean):
        """Le mart doit avoir les colonnes mois, chiffre_affaires, nb_transactions."""
        mart = aggregate_by_month(df_clean)
        assert set(mart.columns) >= {"mois", "chiffre_affaires", "nb_transactions"}

    def test_agg_ca_positifs(self, df_clean):
        """Tous les CA mensuels doivent etre positifs."""
        mart = aggregate_by_month(df_clean)
        assert (mart["chiffre_affaires"] > 0).all()

    def test_agg_trie_par_mois(self, df_clean):
        """Le mart doit etre trie par mois croissant."""
        mart = aggregate_by_month(df_clean)
        mois = mart["mois"].tolist()
        assert mois == sorted(mois)

    def test_agg_nb_transactions(self, df_clean):
        """nb_transactions doit etre >= 1 pour chaque mois."""
        mart = aggregate_by_month(df_clean)
        assert (mart["nb_transactions"] >= 1).all()


class TestAggregateByCategory:
    """Tests bonus pour aggregate_by_category()."""

    def test_agg_cat_colonnes_presentes(self, df_clean):
        """Le mart categorie doit avoir les bonnes colonnes."""
        mart = aggregate_by_category(df_clean)
        assert set(mart.columns) >= {"categorie", "chiffre_affaires", "nb_transactions"}

    def test_agg_cat_ca_positifs(self, df_clean):
        """Tous les CA par categorie doivent etre positifs."""
        mart = aggregate_by_category(df_clean)
        assert (mart["chiffre_affaires"] > 0).all()

    def test_agg_cat_categories_uniques(self, df_clean):
        """Chaque categorie ne doit apparaitre qu'une fois."""
        mart = aggregate_by_category(df_clean)
        assert mart["categorie"].nunique() == len(mart)
