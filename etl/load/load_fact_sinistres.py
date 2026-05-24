def load_fact_sinistres(fact, engine):

    fact.to_sql(
        "fact_sinistres",
        engine,
        if_exists="append",
        index=False
    )

    print("fact_sinistres alimentée")