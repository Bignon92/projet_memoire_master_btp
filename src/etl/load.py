"""
Module de chargement dans PostgreSQL DWH
"""
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
from src.database.connection import get_db_connection, get_db_cursor
from src.config import logger, DATA_PROCESSED

class DataLoader:
    """Chargement des données dans le DWH PostgreSQL"""
    
    def __init__(self):
        self.logger = logger
        self.processed_path = DATA_PROCESSED
    
    def generate_surrogate_key(self, value):
        """Génération de clé de substitution compatible PostgreSQL INT (max 2 147 483 647)"""
        raw = int(hashlib.md5(str(value).encode()).hexdigest()[:8], 16)
        return raw % 2_147_483_647  # on reste dans les limites de INT4
    
    def load_dim_temps(self, df_auto, df_chantier):
        """Chargement de la dimension temps"""
        self.logger.info("Chargement dim_temps...")
        
        dates_auto = pd.to_datetime(df_auto['date_accident'])
        dates_chantier = pd.to_datetime(df_chantier['date_declaration'])
        all_dates = pd.Series(pd.concat([dates_auto, dates_chantier]).unique())
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for date in all_dates:
                    date_obj = pd.to_datetime(date)
                    id_temps = int(date_obj.strftime('%Y%m%d'))
                    
                    cur.execute("""
                        INSERT INTO dim_temps (id_temps, date, annee, mois, mois_nom, jour, trimestre, semaine, jour_semaine, est_weekend, saison)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id_temps) DO NOTHING
                    """, (
                        id_temps, date_obj, date_obj.year, date_obj.month,
                        date_obj.strftime('%B'), date_obj.day, date_obj.quarter,
                        date_obj.isocalendar()[1], date_obj.strftime('%A'),
                        date_obj.weekday() >= 5,
                        'Printemps' if date_obj.month in [3,4,5] else 'Ete' if date_obj.month in [6,7,8] else 'Automne' if date_obj.month in [9,10,11] else 'Hiver'
                    ))
        
        self.logger.info(f"✅ {len(all_dates)} dates chargées")
    
    def load_dim_vehicule(self, df):
        """Chargement dimension véhicule"""
        self.logger.info("Chargement dim_vehicule...")
        
        vehicules = df[['immatriculation', 'type_engin_sinistre', 'marque_sinistre', 
                        'age_vehicule_ans_sinistre', 'km_parcourus_estimes', 'categorie_km']].drop_duplicates()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in vehicules.iterrows():
                    cur.execute("""
                        INSERT INTO dim_vehicule (immatriculation, type_engin, marque, age_ans, km_parcourus, categorie_km)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (immatriculation) DO UPDATE SET
                            type_engin = EXCLUDED.type_engin,
                            marque = EXCLUDED.marque,
                            age_ans = EXCLUDED.age_ans,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        str(row['immatriculation']),
                        str(row['type_engin_sinistre']) if pd.notna(row['type_engin_sinistre']) else 'Inconnu',
                        str(row['marque_sinistre']) if pd.notna(row['marque_sinistre']) else 'Inconnue',
                        int(row['age_vehicule_ans_sinistre']) if pd.notna(row['age_vehicule_ans_sinistre']) else 0,
                        int(row['km_parcourus_estimes']) if pd.notna(row['km_parcourus_estimes']) else 0,
                        str(row['categorie_km']) if pd.notna(row['categorie_km']) else 'Inconnue'
                    ))
        
        self.logger.info(f"✅ {len(vehicules)} véhicules chargés")
    
    def load_dim_assureur(self, df):
        """Chargement dimension assureur"""
        
        self.logger.info("Chargement dim_assureur...")
        
        assureurs = df['assureur_sinistre'].dropna().unique()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                for assureur in assureurs:
                    
                    subset = df[df['assureur_sinistre'] == assureur]
                    
                    # Gestion sécurisée des colonnes optionnelles
                    type_contrat = (
                        str(subset['type_contrat'].iloc[0])
                        if 'type_contrat' in df.columns and not subset.empty
                        else 'Inconnu'
                    )
                    
                    taux_franchise_moyen = (
                        float(subset['taux_franchise_moyen'].iloc[0])
                        if 'taux_franchise_moyen' in df.columns and not subset.empty
                        else 0.0
                    )
                    
                    cur.execute("""
                        INSERT INTO dim_assureur (
                            nom_assureur,
                            type_contrat,
                            taux_franchise_moyen,
                            created_at
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (nom_assureur) DO UPDATE SET
                            type_contrat = EXCLUDED.type_contrat,
                            taux_franchise_moyen = EXCLUDED.taux_franchise_moyen
                    """, (
                        str(assureur),
                        type_contrat,
                        taux_franchise_moyen,
                        datetime.now()
                    ))
        
        self.logger.info(f"✅ {len(assureurs)} assureurs chargés")
    
    def load_dim_geographie(self, df_auto, df_chantier):
        """Chargement dimension géographique"""
        self.logger.info("Chargement dim_geographie...")
        
        depts_auto = df_auto['departement_accident'].unique() if 'departement_accident' in df_auto.columns else []
        depts_chantier = df_chantier['departement'].unique() if 'departement' in df_chantier.columns else []
        all_depts = set(list(depts_auto) + list(depts_chantier))
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for dept in all_depts:
                    if pd.notna(dept):
                        cur.execute("""
                             INSERT INTO dim_geographie (departement, region)
                            VALUES (%s, %s)
                            ON CONFLICT (departement) DO NOTHING
                        """, (str(dept), f"Region_{dept}"))
        
        self.logger.info(f"✅ {len(all_depts)} départements chargés")
    
    # ⬇️⬇️⬇️ NOUVELLE FONCTION ⬇️⬇️⬇️
    def load_dim_conducteur(self, df):
        """Chargement dimension conducteur"""
        self.logger.info("Chargement dim_conducteur...")
        
        conducteurs = df[['conducteur_anciennete_ans', 'classe_age', 'niveau_experience']].drop_duplicates()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in conducteurs.iterrows():
                    id_conducteur = self.generate_surrogate_key(f"{row['conducteur_anciennete_ans']}_{row['classe_age']}")
                    
                    cur.execute("""
                        INSERT INTO dim_conducteur (id_conducteur, anciennete_ans, classe_age, niveau_experience, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id_conducteur) DO UPDATE SET
                            anciennete_ans = EXCLUDED.anciennete_ans,
                            niveau_experience = EXCLUDED.niveau_experience
                    """, (
                        id_conducteur,
                        int(row['conducteur_anciennete_ans']) if pd.notna(row['conducteur_anciennete_ans']) else 0,
                        str(row['classe_age']) if pd.notna(row['classe_age']) else 'Inconnue',
                        str(row['niveau_experience']) if pd.notna(row['niveau_experience']) else 'Inconnu',
                        datetime.now()
                    ))
        
        self.logger.info(f"✅ {len(conducteurs)} conducteurs chargés")
    
    # ⬇️⬇️⬇️ NOUVELLE FONCTION ⬇️⬇️⬇️
    def load_dim_chantier(self, df_chantier):
        """Chargement dimension chantier"""
        self.logger.info("Chargement dim_chantier...")
        
        if df_chantier is None or len(df_chantier) == 0:
            self.logger.warning("Aucune donnée chantier à charger")
            return
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in df_chantier.iterrows():
                    if pd.notna(row.get('code_chantier')):
                        cur.execute("""
                            INSERT INTO dim_chantier (code_chantier, nom_chantier, type_travaux, phase_chantier, departement, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (code_chantier) DO UPDATE SET
                                nom_chantier = EXCLUDED.nom_chantier,
                                type_travaux = EXCLUDED.type_travaux,
                                phase_chantier = EXCLUDED.phase_chantier
                        """, (
                            row['code_chantier'],
                            row.get('nom_chantier', 'Inconnu'),
                            row.get('type_travaux', 'Non spécifié'),
                            row.get('phase_chantier', 'Inconnue'),
                            row.get('departement', '00'),
                            datetime.now()
                        ))
        
        self.logger.info(f"✅ Données chantier chargées")
    
    # ⬇️⬇️⬇️ NOUVELLE FONCTION ⬇️⬇️⬇️
    def load_dim_sinistre_type(self, df):
        """Chargement dimension type de sinistre"""
        self.logger.info("Chargement dim_sinistre_type...")
        
        sinistres_types = df[['type_sinistre', 'gravite', 'responsabilite']].drop_duplicates()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in sinistres_types.iterrows():
                    cur.execute("""
                        INSERT INTO dim_sinistre_type (type_sinistre, gravite, responsabilite)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (type_sinistre, gravite, responsabilite) DO NOTHING
                    """, (
                        row['type_sinistre'],
                        row['gravite'],
                        row['responsabilite']
                    ))
        
        self.logger.info(f"✅ {len(sinistres_types)} types de sinistres chargés")
    
    def load_fact_sinistres_auto(self, df):
        """Chargement des sinistres auto dans table de faits"""
        self.logger.info("Chargement fait_sinistres (auto)...")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    date_accident = pd.to_datetime(row['date_accident'])
                    id_temps = int(date_accident.strftime('%Y%m%d'))
                    
                    # Récupération des IDs
                    cur.execute("SELECT id_vehicule FROM dim_vehicule WHERE immatriculation = %s", (row['immatriculation'],))
                    vehicule_result = cur.fetchone()
                    id_vehicule = vehicule_result[0] if vehicule_result else None
                    
                    cur.execute("SELECT id_geo FROM dim_geographie WHERE departement = %s", (row['departement_accident'],))
                    geo_result = cur.fetchone()
                    id_geo = geo_result[0] if geo_result else None
                    
                    # Conducteur
                    id_conducteur = self.generate_surrogate_key(f"{row['conducteur_anciennete_ans']}_{row['classe_age']}")
                    
                    # Assureur
                    cur.execute("SELECT id_assureur FROM dim_assureur WHERE nom_assureur = %s", (row['assureur_sinistre'],))
                    assureur_result = cur.fetchone()
                    id_assureur = assureur_result[0] if assureur_result else 1
                    
                    # Type sinistre
                    cur.execute("""
                        SELECT id_type FROM dim_sinistre_type 
                        WHERE type_sinistre = %s AND gravite = %s AND responsabilite = %s
                    """, (row['type_sinistre'], row['gravite'], row['responsabilite']))
                    type_result = cur.fetchone()
                    id_type = type_result[0] if type_result else None
                    
                    cur.execute("""
                        INSERT INTO fait_sinistres (
                            id_sinistre, id_temps, id_vehicule, id_conducteur, id_geo, id_assureur, id_type,
                            montant_declare, franchise, montant_indemnise,
                            delai_declaration, delai_reglement, cout_total,
                            est_sinistre_grave, date_integration, source_systeme
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id_sinistre) DO UPDATE SET
                            cout_total = EXCLUDED.cout_total,
                            date_integration = EXCLUDED.date_integration
                    """, (
                        str(row['id_sinistre']),
                        id_temps,
                        id_vehicule,
                        id_conducteur,
                        id_geo,
                        id_assureur,
                        id_type,
                        row['montant_declare_fcfa'],
                        row['franchise_fcfa'],
                        row['montant_indemnise_fcfa'],
                        row['delai_declaration_jours'],
                        row['delai_reglement_jours'],
                        row['cout_total_fcfa'],
                        bool(row.get('sinistre_grave', False)),
                        datetime.now(),
                        'PARC_AUTO'
                    ))
        
        self.logger.info(f"✅ {len(df)} sinistres auto chargés")
    
    def run_full_load(self, auto_df, chantier_df):
        """Exécution complète du chargement"""
        self.logger.info("=== DÉBUT CHARGEMENT DWH ===")
        
        # Chargement dimensions
        self.load_dim_temps(auto_df, chantier_df)
        self.load_dim_vehicule(auto_df)
        self.load_dim_assureur(auto_df)
        self.load_dim_geographie(auto_df, chantier_df)
        self.load_dim_conducteur(auto_df)      # ← AJOUTÉ
        self.load_dim_chantier(chantier_df)    # ← AJOUTÉ
        self.load_dim_sinistre_type(auto_df)   # ← AJOUTÉ
        
        # Chargement des faits
        self.load_fact_sinistres_auto(auto_df)
        
        self.logger.info("=== CHARGEMENT DWH TERMINÉ ===")

if __name__ == "__main__":
    loader = DataLoader()
    print("Module DataLoader prêt")