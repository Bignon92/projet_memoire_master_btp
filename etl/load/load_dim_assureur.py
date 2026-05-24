def load_dim_assureur(dim_assureur, engine):

    dim_assureur.to_sql(
        "dim_assureur",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_assureur alimentée")