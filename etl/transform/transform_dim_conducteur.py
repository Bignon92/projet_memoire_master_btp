import pandas as pd

def transform_dim_conducteur(dataset):

    df = dataset[[
        "conducteur_anciennete_ans",
        "niveau_experience",
        "classe_age"
    ]].copy()

    df = df.rename(columns={
        "classe_age": "tranche_age_conducteur"
    })

    # SUPPRESSION DOUBLONS
    df = df.drop_duplicates()

    # ID métier artificiel
    df["conducteur_id"] = (
        "COND_" + (df.index + 1).astype(str)
    )

    # Réorganisation colonnes
    df = df[[
        "conducteur_id",
        "conducteur_anciennete_ans",
        "niveau_experience",
        "tranche_age_conducteur"
    ]]

    return df