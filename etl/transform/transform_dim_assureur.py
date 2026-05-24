import pandas as pd
def transform_dim_assureur(dataset, trc):

    auto = dataset[["assureur_parc"]].rename(
        columns={"assureur_parc": "assureur"}
    )

    sin = dataset[["assureur_sinistre"]].rename(
        columns={"assureur_sinistre": "assureur"}
    )

    trc_df = trc[["assureur"]]

    df = pd.concat([auto, sin, trc_df])

    df["assureur"] = df["assureur"].str.upper().str.strip()

    df = df.drop_duplicates(subset=["assureur"])

    df["code_assureur"] = range(1, len(df) + 1)

    df["type_contrat"] = "STANDARD"

    return df