-- Script complet de création du schéma étoile

-- 1. DIMENSION TEMPS
CREATE TABLE IF NOT EXISTS dim_temps (
    id_temps INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    mois_nom VARCHAR(20),
    jour INTEGER,
    trimestre INTEGER,
    semaine INTEGER,
    jour_semaine VARCHAR(20),
    est_weekend BOOLEAN,
    saison VARCHAR(20)
);

-- 2. DIMENSION VEHICULE
CREATE TABLE IF NOT EXISTS dim_vehicule (
    id_vehicule SERIAL PRIMARY KEY,
    immatriculation VARCHAR(50) UNIQUE NOT NULL,
    type_engin VARCHAR(100),
    marque VARCHAR(100),
    age_ans FLOAT,
    km_parcourus FLOAT,
    categorie_km VARCHAR(50),
    date_dernier_sinistre DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. DIMENSION CONDUCTEUR
CREATE TABLE IF NOT EXISTS dim_conducteur (
    id_conducteur SERIAL PRIMARY KEY,
    anciennete_ans FLOAT,
    classe_age VARCHAR(20),
    niveau_experience VARCHAR(20),
    score_risque_conducteur FLOAT DEFAULT 0.5,
    nb_sinistres_historique INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. DIMENSION CHANTIER
CREATE TABLE IF NOT EXISTS dim_chantier (
    id_chantier SERIAL PRIMARY KEY,
    code_chantier VARCHAR(50) UNIQUE,
    nom_chantier VARCHAR(200),
    type_travaux VARCHAR(100),
    phase_chantier VARCHAR(50),
    departement VARCHAR(10),
    date_debut DATE,
    date_fin DATE,
    cout_projet FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. DIMENSION GEOGRAPHIE
CREATE TABLE IF NOT EXISTS dim_geographie (
    id_geo SERIAL PRIMARY KEY,
    departement VARCHAR(10),
    region VARCHAR(50),
    axe_routier VARCHAR(100),
    type_zone VARCHAR(50),
    taux_accidentalite FLOAT,
    code_postal VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT
);

-- 6. DIMENSION ASSUREUR
CREATE TABLE IF NOT EXISTS dim_assureur (
    id_assureur SERIAL PRIMARY KEY,
    nom_assureur VARCHAR(100) NOT NULL,
    type_contrat VARCHAR(50),
    taux_franchise_moyen FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. DIMENSION TYPE SINISTRE
CREATE TABLE IF NOT EXISTS dim_sinistre_type (
    id_type SERIAL PRIMARY KEY,
    type_sinistre VARCHAR(50),
    nature_sinistre VARCHAR(100),
    gravite VARCHAR(20),
    responsabilite VARCHAR(30),
    categorie_risque VARCHAR(20)
);

-- 8. TABLE DE FAITS
CREATE TABLE IF NOT EXISTS fait_sinistres (
    id_sinistre INTEGER PRIMARY KEY,
    id_temps INTEGER,
    id_vehicule INTEGER,
    id_conducteur INTEGER,
    id_chantier INTEGER,
    id_geo INTEGER,
    id_assureur INTEGER,
    id_type INTEGER,
    montant_declare FLOAT,
    franchise FLOAT,
    montant_indemnise FLOAT,
    delai_declaration INTEGER,
    delai_reglement INTEGER,
    cout_total FLOAT,
    est_sinistre_grave BOOLEAN,
    score_risque_predicted FLOAT,
    niveau_risque_reel VARCHAR(20),
    date_integration TIMESTAMP,
    source_systeme VARCHAR(20),
    FOREIGN KEY (id_temps) REFERENCES dim_temps(id_temps),
    FOREIGN KEY (id_vehicule) REFERENCES dim_vehicule(id_vehicule),
    FOREIGN KEY (id_conducteur) REFERENCES dim_conducteur(id_conducteur),
    FOREIGN KEY (id_chantier) REFERENCES dim_chantier(id_chantier),
    FOREIGN KEY (id_geo) REFERENCES dim_geographie(id_geo),
    FOREIGN KEY (id_assureur) REFERENCES dim_assureur(id_assureur),
    FOREIGN KEY (id_type) REFERENCES dim_sinistre_type(id_type)
);

-- Commentaires sur les colonnes
COMMENT ON TABLE fait_sinistres IS 'Table de faits des sinistres automobile et chantier BTP';
COMMENT ON COLUMN fait_sinistres.score_risque_predicted IS 'Score prédit par le modèle ML (0-1)';
COMMENT ON COLUMN fait_sinistres.niveau_risque_reel IS 'Niveau réel: FAIBLE, MODERE, ELEVE, CRITIQUE';

-- Messages de confirmation
SELECT '✅ Schéma créé avec succès !' AS status;