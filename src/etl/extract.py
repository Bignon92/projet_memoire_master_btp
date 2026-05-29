"""
Module d'extraction des données
"""
import pandas as pd
from pathlib import Path
from src.config import DATA_PROCESSED, logger 

class DataExtractor:
    """Extraction des données depuis sources"""
    
    def __init__(self):
        self.processed_path = DATA_PROCESSED
        self.logger = logger
        
    def extract_auto_sinistres(self):
        """Extraction des sinistres automobile"""
        try:
            file_path = self.processed_path / "dataset_analytique.csv"
            df = pd.read_csv(file_path)
            self.logger.info(f"✅ {len(df)} sinistres auto extraits")
            return df
        except Exception as e:
            self.logger.error(f"Erreur extraction auto: {e}")
            raise
    
    def extract_trc_sinistres(self):
        """Extraction des sinistres chantier TRC"""
        try:
            file_path = self.processed_path / "sinistre_trc_enrichi.csv"
            df = pd.read_csv(file_path)
            self.logger.info(f"✅ {len(df)} sinistres chantier extraits")
            return df
        except Exception as e:
            self.logger.error(f"Erreur extraction chantier: {e}")
            raise
    
    def extract_all(self):
        """Extraction de toutes les sources"""
        auto_df = self.extract_auto_sinistres()
        chantier_df = self.extract_trc_sinistres()
        
        # Ajout d'une colonne source
        auto_df['source_systeme'] = 'PARC_AUTO'
        chantier_df['source_systeme'] = 'TRC'
        
        return {
            'automobile': auto_df,
            'chantier': chantier_df
        }

if __name__ == "__main__":
    extractor = DataExtractor()
    data = extractor.extract_all()
    print(f"Auto: {data['automobile'].shape}")
    print(f"Chantier: {data['chantier'].shape}")