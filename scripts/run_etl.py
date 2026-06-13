#!/usr/bin/env python3
"""
Script principal ETL - Orchestration complète
Usage: python scripts/run_etl.py
"""
import sys
from pathlib import Path

# Ajout du chemin src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader
from src.config import logger
from src.config import test_connection

def main():
    """Orchestration ETL"""
    logger.info("="*60)
    logger.info("DÉMARRAGE DU PIPELINE ETL - SINISTRES BTP")
    logger.info("="*60)
    
    # 1. Test connexion PostgreSQL
    if not test_connection():
        logger.error("Impossible de se connecter à PostgreSQL")
        sys.exit(1)
    
    # 2. Extraction
    logger.info("🔍 Phase 1: Extraction")
    extractor = DataExtractor()
    data = extractor.extract_all()
    
    # 3. Transformation
    logger.info("🔄 Phase 2: Transformation")
    transformer = DataTransformer()
    
    auto_cleaned = transformer.clean_auto_data(data['automobile'])
    chantier_cleaned = transformer.clean_chantier_data(data['chantier'])
    
    # Sauvegarde intermédiaire
    transformer.save_processed_data(auto_cleaned, 'auto')
    transformer.save_processed_data(chantier_cleaned, 'chantier')
    
    # 4. Chargement
    logger.info("💾 Phase 3: Chargement DWH")
    loader = DataLoader()
    loader.run_full_load(auto_cleaned, chantier_cleaned)
    
    logger.info("="*60)
    logger.info("✅ PIPELINE ETL TERMINÉ AVEC SUCCÈS")
    logger.info("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())