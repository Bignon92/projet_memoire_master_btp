from sqlalchemy import create_engine

USER = "postgres"

PASSWORD = "keren"

HOST = "localhost"

PORT = "5432"

DATABASE = "btp_sinistres_dwh"

DATABASE_URL = (
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

engine = create_engine(DATABASE_URL)

print("Connexion PostgreSQL OK")