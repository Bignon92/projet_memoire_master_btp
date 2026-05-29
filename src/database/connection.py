import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import DATABASE_URL, get_db_connection_string, logger

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db_connection():
    """
    Contexte pour connexion psycopg2 (requêtes raw)
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM dim_temps")
    """
    conn = None
    try:
        conn = psycopg2.connect(get_db_connection_string())
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erreur base de données: {e}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(dictionary=False):
    """
    Contexte pour curseur
    """
    with get_db_connection() as conn:
        cursor_class = RealDictCursor if dictionary else None
        with conn.cursor(cursor_factory=cursor_class) as cursor:
            yield cursor

def get_session():
    """
    Retourne une session SQLAlchemy
    """
    return SessionLocal()

def init_db():
    """
    Initialise la base de données (création des tables)
    """
    from src.database.dwh_schema import (
        DimTemps, DimVehicule, DimConducteur, DimChantier,
        DimGeographie, DimAssureur, DimSinistreType, FaitSinistre
    )
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Base de données initialisée")

def execute_sql_file(sql_file_path):
    """
    Exécute un fichier SQL
    """
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)
    logger.info(f"✅ Fichier SQL exécuté: {sql_file_path}")