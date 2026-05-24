from sqlalchemy import text
from config.db_connection import engine
from extract.extract_data import extract_data

from transform.transform_dim_date import transform_dim_date
from transform.transform_dim_vehicule import transform_dim_vehicule
from transform.transform_dim_assureur import transform_dim_assureur
from transform.transform_dim_localisation import transform_dim_localisation
from transform.transform_dim_conducteur import transform_dim_conducteur
from transform.transform_dim_chantier import transform_dim_chantier
from transform.transform_dim_type_sinistre import transform_dim_type_sinistre
from transform.transform_fact_sinistres import transform_fact_sinistres

from load.load_dim_date import load_dim_date
from load.load_dim_vehicule import load_dim_vehicule
from load.load_dim_assureur import load_dim_assureur
from load.load_dim_localisation import load_dim_localisation
from load.load_dim_conducteur import load_dim_conducteur
from load.load_dim_chantier import load_dim_chantier
from load.load_dim_type_sinistres import load_dim_type_sinistre
from load.load_fact_sinistres import load_fact_sinistres



# RESET DWH

def reset_dwh(engine):
    queries = [
        "TRUNCATE TABLE fact_sinistres CASCADE;",
        "TRUNCATE TABLE dim_date CASCADE;",
        "TRUNCATE TABLE dim_vehicule CASCADE;",
        "TRUNCATE TABLE dim_conducteur CASCADE;",
        "TRUNCATE TABLE dim_assureur CASCADE;",
        "TRUNCATE TABLE dim_localisation CASCADE;",
        "TRUNCATE TABLE dim_type_sinistre CASCADE;",
    ]

    with engine.begin() as conn:
        for q in queries:
            conn.execute(text(q))


# PIPELINE

if __name__ == "__main__":

    reset_dwh(engine)
    print("DWH reset OK")

    # EXTRACTION
    dataset, trc = extract_data()

    # DIMENSIONS
    dim_date = transform_dim_date(dataset)
    load_dim_date(dim_date, engine)

    dim_vehicule = transform_dim_vehicule(dataset)
    load_dim_vehicule(dim_vehicule, engine)

    dim_assureur = transform_dim_assureur(dataset, trc)
    load_dim_assureur(dim_assureur, engine)

    dim_localisation = transform_dim_localisation(dataset)
    load_dim_localisation(dim_localisation, engine)

    dim_conducteur = transform_dim_conducteur(dataset)
    load_dim_conducteur(dim_conducteur, engine)

    dim_chantier = transform_dim_chantier(dataset)
    load_dim_chantier(dim_chantier, engine)

    dim_type = transform_dim_type_sinistre(dataset)
    load_dim_type_sinistre(dim_type, engine)

    # FACT TABLE
    # LECTURE DES DIMENSIONS SQL

    import pandas as pd

    dim_date_sql = pd.read_sql(
        "SELECT * FROM dim_date",
        engine
    )

    dim_vehicule_sql = pd.read_sql(
        "SELECT * FROM dim_vehicule",
        engine
    )

    dim_assureur_sql = pd.read_sql(
        "SELECT * FROM dim_assureur",
        engine
    )

    dim_localisation_sql = pd.read_sql(
        "SELECT * FROM dim_localisation",
        engine
    )

    dim_conducteur_sql = pd.read_sql(
        "SELECT * FROM dim_conducteur",
        engine
    )

    dim_chantier_sql = pd.read_sql(
        "SELECT * FROM dim_chantier",
        engine
    )

    dim_type_sinistre_sql = pd.read_sql(
        "SELECT * FROM dim_type_sinistre",
        engine
    )

    
    # FACT TABLE
    

    fact = transform_fact_sinistres(
        dataset,
        dim_date_sql,
        dim_vehicule_sql,
        dim_assureur_sql,
        dim_localisation_sql,
        dim_conducteur_sql,
        dim_chantier_sql,
        dim_type_sinistre_sql
    )

    load_fact_sinistres(fact, engine)

    print("Pipeline terminé avec succès")