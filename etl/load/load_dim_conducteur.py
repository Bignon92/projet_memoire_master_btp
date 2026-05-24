def load_dim_conducteur(df, engine):

    df.to_sql(
        "dim_conducteur",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_conducteur alimentée")