"""
Module de transformation des données
"""
import pandas as pd
import numpy as np
from datetime import datetime
from src.config import logger, DATA_PROCESSED

class DataTransformer:
    """Transformation et nettoyage des données"""
    
    def __init__(self):
        self.processed_path = DATA_PROCESSED
        self.logger = logger
    
    def clean_auto_data(self, df):
        """Nettoyage des données sinistres auto"""
        self.logger.info("Nettoyage des données auto...")
        
        df_clean = df.copy()
        
        # Suppression des doublons
        df_clean = df_clean.drop_duplicates(subset=['id_sinistre'])
        
        # Gestion des valeurs manquantes
        numeric_cols = ['montant_declare_fcfa', 'franchise_fcfa', 'montant_indemnise_fcfa',
                       'delai_declaration_jours', 'delai_reglement_jours', 'cout_total_fcfa']
        
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        # Catégorisation des coûts
        if 'cout_total_fcfa' in df_clean.columns:
            df_clean['categorie_cout'] = pd.cut(
                df_clean['cout_total_fcfa'],
                bins=[0, 100000, 500000, 1000000, 5000000, float('inf')],
                labels=['Très faible', 'Faible', 'Moyen', 'Élevé', 'Très élevé']
            )
        
        # Feature engineering temporel
        if 'date_accident' in df_clean.columns:
            df_clean['date_accident'] = pd.to_datetime(df_clean['date_accident'])
            df_clean['jour_semaine'] = df_clean['date_accident'].dt.day_name()
            df_clean['heure_accident'] = df_clean['date_accident'].dt.hour
            df_clean['est_weekend'] = df_clean['date_accident'].dt.weekday >= 5
        
        # Calcul du ratio d'indemnisation
        if all(col in df_clean.columns for col in ['montant_indemnise_fcfa', 'cout_total_fcfa']):
            df_clean['ratio_indemnisation'] = (
                df_clean['montant_indemnise_fcfa'] /
                (df_clean['cout_total_fcfa'] + 1)
            )

        # Calcul de l'efficacité traitement
        if all(col in df_clean.columns for col in ['delai_reglement_jours', 'delai_declaration_jours']):
            df_clean['efficacite_traitement'] = (
                df_clean['delai_reglement_jours'] /
                (df_clean['delai_declaration_jours'] + 1)
            )
        
        self.logger.info(f"Nettoyage terminé: {len(df_clean)} lignes")
        return df_clean
    
    def clean_chantier_data(self, df):
        """Nettoyage des données sinistres chantier"""
        self.logger.info("Nettoyage des données chantier...")
        
        df_clean = df.copy()
        
        # Suppression des doublons
        df_clean = df_clean.drop_duplicates(subset=['id_sinistre'])
        
        # Gestion des valeurs manquantes
        numeric_cols = ['montant_declare_fcfa', 'franchise_fcfa', 'montant_indemnise_fcfa',
                       'delai_declaration_jours', 'delai_reglement_jours', 'cout_total_fcfa']
        
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        # Catégorisation par type de travaux
        if 'type_travaux' in df_clean.columns:
            df_clean['type_travaux_categorise'] = df_clean['type_travaux'].fillna('Non spécifié')
        
        # Classification par phase de chantier
        if 'phase_chantier' in df_clean.columns:
            phases_risque = ['Démarrage', 'Travaux souterrains', 'Travaux en hauteur']
            df_clean['phase_risquee'] = df_clean['phase_chantier'].isin(phases_risque)
        
        self.logger.info(f"Nettoyage terminé: {len(df_clean)} lignes")
        return df_clean
    
    def save_processed_data(self, df, name):
        """Sauvegarde des données transformées"""
        file_path = self.processed_path / f"{name}_cleaned.parquet"
        df.to_parquet(file_path, index=False)
        self.logger.info(f"✅ Données sauvegardées: {file_path}")
        return file_path

if __name__ == "__main__":
    transformer = DataTransformer()
    # Test avec données mockées
    test_df = pd.DataFrame({'id_sinistre': [1,2], 'cout_total_fcfa': [1000, 2000]})
    cleaned = transformer.clean_auto_data(test_df)
    print(cleaned)