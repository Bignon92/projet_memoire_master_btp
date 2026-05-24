def load_dim_type_sinistre(df, engine):

    df.to_sql(
        "dim_type_sinistre",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_type_sinistre alimentée")