def load_dim_date(dim_date, engine):

    dim_date.to_sql(
        "dim_date",
        engine,
        if_exists="append",
        index=False
    )

    print("dim_date alimentée")