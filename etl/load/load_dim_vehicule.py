def load_dim_vehicule(dim_vehicule, engine):

    dim_vehicule.to_sql(
        "dim_vehicule",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_vehicule alimentée")