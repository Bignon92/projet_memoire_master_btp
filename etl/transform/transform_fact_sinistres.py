import pandas as pd


def transform_fact_sinistres(
    dataset,
    dim_date_sql,
    dim_vehicule_sql,
    dim_assureur_sql,
    dim_localisation_sql,
    dim_conducteur_sql,
    dim_chantier_sql,
    dim_type_sinistre_sql
):

    fact = dataset.copy()

    # =====================================================
    # DATE
    # =====================================================

    fact["date_complete"] = pd.to_datetime(
        fact["date_accident"]
    )

    dim_date_sql["date_complete"] = pd.to_datetime(
        dim_date_sql["date_complete"]
    )

    fact = fact.merge(
        dim_date_sql[
            [
                "date_key",
                "date_complete"
            ]
        ],
        on="date_complete",
        how="left"
    )

    # =====================================================
    # VEHICULE
    # =====================================================

    fact = fact.merge(
        dim_vehicule_sql[
            [
                "vehicule_key",
                "immatriculation"
            ]
        ],
        on="immatriculation",
        how="left"
    )

    # =====================================================
    # ASSUREUR
    # =====================================================

    fact = fact.merge(
        dim_assureur_sql[
            [
                "assureur_key",
                "assureur"
            ]
        ],
        left_on="assureur_parc",
        right_on="assureur",
        how="left"
    )

    fact.drop(
        columns=["assureur"],
        inplace=True
    )

    # =====================================================
    # LOCALISATION
    # =====================================================

    fact = fact.merge(
        dim_localisation_sql[
            [
                "localisation_key",
                "departement"
            ]
        ],
        left_on="departement_accident",
        right_on="departement",
        how="left"
    )

    fact.drop(
        columns=["departement"],
        inplace=True
    )

    # =====================================================
    # CONDUCTEUR
    # =====================================================

    fact = fact.merge(
        dim_conducteur_sql[
            [
                "conducteur_key",
                "conducteur_id"
            ]
        ],
        left_on="immatriculation",
        right_on="conducteur_id",
        how="left"
    )

    fact.drop(
        columns=["conducteur_id"],
        inplace=True
    )

    # =====================================================
    # CHANTIER
    # =====================================================

    fact = fact.merge(
        dim_chantier_sql[
            [
                "chantier_key",
                "code_chantier"
            ]
        ],
        left_on="immatriculation",
        right_on="code_chantier",
        how="left"
    )

    fact.drop(
        columns=["code_chantier"],
        inplace=True
    )

    # =====================================================
    # TYPE SINISTRE
    # =====================================================

    fact = fact.merge(
        dim_type_sinistre_sql[
            [
                "type_sinistre_key",
                "type_sinistre"
            ]
        ],
        on="type_sinistre",
        how="left"
    )

    # =====================================================
    # TABLE DE FAIT FINALE
    # =====================================================

    fact_final = fact[
        [
            "date_key",
            "vehicule_key",
            "conducteur_key",
            "chantier_key",
            "assureur_key",
            "localisation_key",
            "type_sinistre_key",

            "montant_declare_fcfa",
            "franchise_fcfa",
            "montant_indemnise_fcfa",
            "cout_total_fcfa",

            "delai_declaration_jours",
            "delai_reglement_jours",

            "score_risque"
        ]
    ]

    return fact_final