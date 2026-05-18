import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le DataFrame brut :
    - Cast des types
    - Nettoyage des emails
    - Suppression des lignes invalides
    Retourne une copie propre (n'altere pas l'original).
    """
    df = df.copy()

    # 1. Cast des types
    df["montant"] = pd.to_numeric(df["montant"], errors="coerce")
    df["date_vente"] = pd.to_datetime(df["date_vente"], errors="coerce")
    df["id"] = pd.to_numeric(df["id"], errors="coerce")

    # 2. Nettoyage email et categorie
    df["client_email"] = df["client_email"].str.strip().str.lower()
    df["categorie"] = df["categorie"].str.strip().str.title()

    # 3. Suppression des lignes invalides
    df = df[df["client_email"].notna() & (df["client_email"] != "")]
    df = df[df["montant"].notna() & (df["montant"] > 0)]
    df = df[df["date_vente"].notna()]

    return df.reset_index(drop=True)


def aggregate_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregation mensuelle du CA.
    Prend en entree le DataFrame nettoye (sortie de clean()).
    """
    df = df.copy()
    df["mois"] = df["date_vente"].dt.to_period("M").astype(str)

    mart = (
        df.groupby("mois")
        .agg(
            chiffre_affaires=("montant", "sum"),
            nb_transactions=("montant", "count")
        )
        .reset_index()
        .sort_values("mois")
    )
    return mart


def aggregate_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregation par categorie du CA. (Bonus)
    Prend en entree le DataFrame nettoye (sortie de clean()).
    """
    df = df.copy()

    mart = (
        df.groupby("categorie")
        .agg(
            chiffre_affaires=("montant", "sum"),
            nb_transactions=("montant", "count")
        )
        .reset_index()
        .sort_values("chiffre_affaires", ascending=False)
    )
    return mart
