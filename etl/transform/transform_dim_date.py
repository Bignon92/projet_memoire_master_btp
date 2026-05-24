import pandas as pd

def transform_dim_date(dataset):

    dataset["date_accident"] = pd.to_datetime(
        dataset["date_accident"]
    )

    dim_date = pd.DataFrame()

    dim_date["date_complete"] = (
        dataset["date_accident"].drop_duplicates()
    )

    dim_date["jour"] = dim_date["date_complete"].dt.day

    dim_date["mois"] = dim_date["date_complete"].dt.month

    dim_date["trimestre"] = (
        (dim_date["mois"] - 1) // 3 + 1
    )

    dim_date["semestre"] = dim_date["mois"].apply(
        lambda x: 1 if x <= 6 else 2
    )

    dim_date["annee"] = dim_date["date_complete"].dt.year

    dim_date["nom_mois"] = (
        dim_date["date_complete"].dt.month_name()
    )

    dim_date["nom_jour"] = (
        dim_date["date_complete"].dt.day_name()
    )

    dim_date["jour_semaine_num"] = (
        dim_date["date_complete"].dt.weekday + 1
    )

    dim_date["est_weekend"] = (
        dim_date["jour_semaine_num"] >= 6
    )

    dim_date["semaine_annee"] = (
        dim_date["date_complete"].dt.isocalendar().week
    )

    dim_date["est_jour_ferie"] = False

    dim_date["est_fin_mois"] = (
        dim_date["date_complete"].dt.is_month_end
    )

    return dim_date