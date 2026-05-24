import pandas as pd

def transform_dim_chantier(dataset):

    types_travaux = [
        "TERRASSEMENT",
        "ROUTIER",
        "BÂTIMENT",
        "PONT",
        "ASSAINISSEMENT"
    ]

    phases = [
        "PREPARATION",
        "EXECUTION",
        "FINITION"
    ]

    engins = dataset["type_engin_parc"].dropna().unique()

    rows = []

    i = 1

    for engin in engins:

        rows.append({
            "code_chantier": f"CH_{i}",
            "nom_chantier": f"CHANTIER_{i}",
            "type_travaux": types_travaux[i % len(types_travaux)],
            "phase_chantier": phases[i % len(phases)],
            "engin_implique": engin
        })

        i += 1

    df = pd.DataFrame(rows)

    return df