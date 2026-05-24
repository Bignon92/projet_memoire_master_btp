import pandas as pd

def transform_dim_vehicule(dataset):

    dim_vehicule = dataset[
        [
            "immatriculation",
            "type_engin_parc",
            "marque_parc",
            "annee_mise_en_service",
            "age_vehicule_ans_parc",
            "km_parcourus_estimes",
            "etat_general",
            "departement_affectation",
            "classe_age",
            "categorie_km"
        ]
    ].copy()

    # Renommer colonnes
    dim_vehicule = dim_vehicule.rename(
        columns={
            "type_engin_parc": "type_engin",
            "marque_parc": "marque",
            "age_vehicule_ans_parc": "age_vehicule_ans"
        }
    )

    # Suppression doublons
    dim_vehicule = dim_vehicule.drop_duplicates(
        subset=["immatriculation"]
    )

    # Suppression immatriculations nulles
    dim_vehicule = dim_vehicule.dropna(
        subset=["immatriculation"]
    )

    return dim_vehicule