def load_dim_chantier(df, engine):

    df.to_sql(
        "dim_chantier",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_chantier alimentée")