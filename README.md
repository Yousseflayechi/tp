# DataOps ETL Pipeline — pandas + PostgreSQL + pytest + GitHub Actions

![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)

Pipeline ETL complet : **Extract → Transform (pandas) → Load (PostgreSQL)**

> **Principe fondamental** : transformer AVANT de stocker.  
> Les fonctions pandas sont testables sans base de données (avantage ETL vs ELT).

---

## Structure du projet

```
dataops_etl/
├── src/
│   ├── extract.py          # E : lit le CSV → DataFrame brut
│   ├── transform.py        # T : clean() + aggregate_by_month() + aggregate_by_category()
│   ├── load.py             # L : écrit les DataFrames dans PostgreSQL
│   └── run.py              # Orchestrateur E→T→L + logging
├── data/
│   └── ventes.csv          # Fichier source (10 lignes, 2 invalides intentionnelles)
├── tests/
│   ├── conftest.py         # Fixtures DataFrames + connexion DB
│   ├── test_transforms.py  # Tests unitaires pandas (SANS base de données)
│   └── test_load.py        # Tests intégration load dans PostgreSQL
├── .github/
│   └── workflows/
│       └── ci.yml          # Workflow GitHub Actions
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Prérequis

- Python 3.10+
- Docker Desktop
- Git

---

## Démarrage rapide

### 1. Lancer PostgreSQL (entrepôt)

```bash
docker-compose up -d
docker ps
# Vérifier la base :
docker exec -it etl_warehouse psql -U etl_user -d warehouse -c "\l"
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer le pipeline ETL

```bash
python src/run.py
```

**Résultat attendu :**
```
=== Pipeline ETL DataOps ===

[1/3] Extract...
[Extract] 10 lignes lues depuis data/ventes.csv

[2/3] Transform (pandas)...
  2 lignes invalides ecartees
  8 lignes valides
  CA total : 1290.40 EUR

[3/3] Load (PostgreSQL)...
  ventes_propres  : 8 lignes
  ca_par_mois     : 3 lignes
  ca_par_categorie: 3 lignes

[DONE] Pipeline ETL termine avec succes.
```

---

## Tests

### Tests unitaires pandas (rapides, sans DB)

```bash
pytest tests/test_transforms.py -v
```

### Tests d'intégration (nécessite PostgreSQL)

```bash
pytest tests/test_load.py -v
```

### Tous les tests avec couverture (bonus)

```bash
pytest --cov=src --cov-report=term-missing tests/
```

---

## Données

Le fichier `data/ventes.csv` contient **10 lignes** dont **2 intentionnellement invalides** :

| Ligne | Problème | Action |
|-------|----------|--------|
| 7     | email vide | supprimée par `clean()` |
| 10    | montant négatif (-10.00) | supprimée par `clean()` |

**Valeurs attendues après `clean()` :**
- Lignes valides : **8**
- CA total : **1 290,40 EUR**
- CA janvier : 485,50 € | CA février : 315,40 € | CA mars : 505,00 €

---

## ETL vs ELT

| | ETL (ce TP) | ELT |
|---|---|---|
| Transformation | En Python/pandas **avant** le chargement | En SQL **après** le chargement |
| Tests | Unitaires sans DB ✅ | Nécessite la DB |
| PostgreSQL | Entrepôt uniquement | Fait aussi les transformations |

---

## Bonus implémentés

- ✅ `aggregate_by_category(df)` avec ses tests (`TestAggregateByCategory`)
- ✅ Couverture de tests avec `pytest-cov`
- ✅ Badge GitHub Actions CI dans le README

---

*Dr. Abdelhak Touiti — Université — Cours DevOps & DataOps — Jour 2*
# tp
