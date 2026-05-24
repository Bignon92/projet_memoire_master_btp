import pandas as pd 

def transform_dim_localisation(dataset):

    df = dataset[[
        "departement_accident",
        "departement_affectation",
        "axe_routier"
    ]].copy()

    df1 = df.rename(columns={
        "departement_accident": "departement"
    })[["departement", "axe_routier"]]

    df2 = df.rename(columns={
        "departement_affectation": "departement"
    })[["departement", "axe_routier"]]

    df = pd.concat([df1, df2])

    df = df.drop_duplicates(subset=["departement", "axe_routier"])

    df["nom_departement"] = df["departement"]

    df["region"] = None
    df["type_zone"] = None

    return df