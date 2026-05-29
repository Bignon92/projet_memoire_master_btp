import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Chargement des variables d'environnement
load_dotenv()

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_MODELS = PROJECT_ROOT / "data" / "models"
SQL_DIR = PROJECT_ROOT / "sql"
LOGS_DIR = PROJECT_ROOT / "logs"

# Création des dossiers
for dir_path in [DATA_RAW, DATA_PROCESSED, DATA_MODELS, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configuration PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'btp_sinistres_dwh'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Js81pr0teg2D')
}

# URL de connexion SQLAlchemy
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Configuration des logs
logger.add(
    LOGS_DIR / "btp_etl.log",
    rotation="500 MB",
    retention="10 days",
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

def get_db_connection_string():
    """Retourne la chaîne de connexion pour psycopg2"""
    return f"dbname={DB_CONFIG['database']} user={DB_CONFIG['user']} password={DB_CONFIG['password']} host={DB_CONFIG['host']} port={DB_CONFIG['port']}"

def test_connection():
    """Teste la connexion à PostgreSQL"""
    import psycopg2
    try:
        conn = psycopg2.connect(get_db_connection_string())
        conn.close()
        logger.info("✅ Connexion PostgreSQL établie avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Database URL: {DATABASE_URL}")
    test_connection()