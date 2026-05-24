def load_dim_localisation(dim_localisation, engine):

    dim_localisation.to_sql(
        "dim_localisation",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_localisation alimentée")