-- Création de la base de données (exécuté automatiquement par Docker)
-- Script manuel: sudo -u postgres psql < 01_create_database.sql

-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS btp_sinistres_dwh
    WITH 
    OWNER = btp_admin
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- Connexion à la base
\c btp_sinistres_dwh;

-- Extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension pour les statistiques avancées
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";