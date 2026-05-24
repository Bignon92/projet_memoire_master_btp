def transform_dim_type_sinistre(dataset):

    df = dataset[[
        "type_sinistre",
        "type_accident",
        "responsabilite",
        "tiers_implique",
        "gravite",
        "statut_dossier"
    ]].copy()

    # NORMALISATION BOOLEAN
    df["tiers_implique"] = df["tiers_implique"].replace({
        "OUI": True,
        "NON": False
    })

    df = df.drop_duplicates(subset=[
        "type_sinistre",
        "type_accident",
        "responsabilite",
        "gravite"
    ])

    return df