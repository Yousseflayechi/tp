import pandas as pd


def extract(csv_path: str) -> pd.DataFrame:
    """
    Lit le fichier CSV source et retourne un DataFrame brut.
    Aucune transformation ici : on garde tout tel quel.
    """
    df = pd.read_csv(csv_path, dtype=str)  # tout en str
    print(f"[Extract] {len(df)} lignes lues depuis {csv_path}")
    return df
