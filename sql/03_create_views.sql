-- Vues pour l'analyse et le reporting

-- Vue 1: Résumé quotidien des sinistres
CREATE OR REPLACE VIEW vue_resume_quotidien AS
SELECT 
    t.date,
    t.annee,
    t.mois,
    t.jour_semaine,
    COUNT(f.id_sinistre) AS nb_sinistres,
    SUM(f.cout_total) AS cout_total,
    AVG(f.cout_total) AS cout_moyen,
    AVG(f.delai_reglement) AS delai_moyen,
    COUNT(CASE WHEN f.est_sinistre_grave THEN 1 END) AS nb_graves,
    AVG(f.score_risque_predicted) AS score_risque_moyen
FROM fait_sinistres f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.date, t.annee, t.mois, t.jour_semaine
ORDER BY t.date DESC;

-- Vue 2: Analyse par véhicule
CREATE OR REPLACE VIEW vue_analyse_vehicule AS
SELECT 
    v.immatriculation,
    v.type_engin,
    v.marque,
    v.age_ans,
    COUNT(f.id_sinistre) AS nb_sinistres,
    SUM(f.cout_total) AS cout_total,
    AVG(f.cout_total) AS cout_moyen,
    MAX(f.score_risque_predicted) AS risque_max,
    ROW_NUMBER() OVER (ORDER BY SUM(f.cout_total) DESC) AS ranking_cout
FROM fait_sinistres f
JOIN dim_vehicule v ON f.id_vehicule = v.id_vehicule
GROUP BY v.immatriculation, v.type_engin, v.marque, v.age_ans
HAVING COUNT(f.id_sinistre) > 0
ORDER BY cout_total DESC;

-- Vue 3: Analyse géographique des risques
CREATE OR REPLACE VIEW vue_risques_geographiques AS
SELECT 
    g.departement,
    g.region,
    COUNT(f.id_sinistre) AS nb_sinistres,
    SUM(f.cout_total) AS cout_total,
    AVG(f.cout_total) AS cout_moyen,
    AVG(f.score_risque_predicted) AS score_risque_moyen,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY f.cout_total) AS cout_percentile_75,
    -- Classification du risque
    CASE 
        WHEN AVG(f.score_risque_predicted) > 0.7 THEN 'CRITIQUE'
        WHEN AVG(f.score_risque_predicted) > 0.5 THEN 'ÉLEVÉ'
        WHEN AVG(f.score_risque_predicted) > 0.3 THEN 'MODÉRÉ'
        ELSE 'FAIBLE'
    END AS niveau_risque
FROM fait_sinistres f
JOIN dim_geographie g ON f.id_geo = g.id_geo
GROUP BY g.departement, g.region
ORDER BY score_risque_moyen DESC;

-- Vue 4: Suivi mensuel (pour forecasting)
CREATE OR REPLACE VIEW vue_suivi_mensuel AS
SELECT 
    t.annee,
    t.mois,
    t.mois_nom,
    COUNT(f.id_sinistre) AS nb_sinistres,
    SUM(f.cout_total) AS cout_total,
    AVG(f.delai_reglement) AS delai_moyen,
    LAG(COUNT(f.id_sinistre)) OVER (ORDER BY t.annee, t.mois) AS nb_mois_precedent,
    LAG(SUM(f.cout_total)) OVER (ORDER BY t.annee, t.mois) AS cout_mois_precedent,
    -- Taux d'évolution
    CASE 
        WHEN LAG(COUNT(f.id_sinistre)) OVER (ORDER BY t.annee, t.mois) > 0 
        THEN ROUND(((COUNT(f.id_sinistre) - LAG(COUNT(f.id_sinistre)) OVER (ORDER BY t.annee, t.mois)) * 100.0 / LAG(COUNT(f.id_sinistre)) OVER (ORDER BY t.annee, t.mois)), 2)
        ELSE 0
    END AS evolution_pct
FROM fait_sinistres f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee, t.mois, t.mois_nom
ORDER BY t.annee DESC, t.mois DESC;

-- Vue 5: Alertes risques (pour dashboard)
CREATE OR REPLACE VIEW vue_alertes_risques AS
SELECT 
    f.id_sinistre,
    t.date,
    v.immatriculation,
    v.type_engin,
    f.cout_total,
    f.delai_reglement,
    f.score_risque_predicted,
    CASE 
        WHEN f.score_risque_predicted > 0.8 THEN 'URGENT: Risque critique'
        WHEN f.score_risque_predicted > 0.6 AND f.delai_reglement > 30 THEN 'Action requise: Délai excessif'
        WHEN f.cout_total > (SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY cout_total) FROM fait_sinistres) 
             THEN 'Alerte: Coût anormalement élevé'
        ELSE 'Surveillance normale'
    END AS alerte_message,
    CURRENT_DATE AS date_alerte
FROM fait_sinistres f
JOIN dim_temps t ON f.id_temps = t.id_temps
JOIN dim_vehicule v ON f.id_vehicule = v.id_vehicule
WHERE f.score_risque_predicted > 0.5
   OR f.delai_reglement > 45
   OR f.cout_total > (SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cout_total) FROM fait_sinistres)
ORDER BY f.score_risque_predicted DESC;

-- Vue matérialisée pour les performances (actualisation quotidienne)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stats_hebdomadaires AS
SELECT 
    DATE_TRUNC('week', t.date) AS semaine,
    COUNT(f.id_sinistre) AS nb_sinistres,
    SUM(f.cout_total) AS cout_total,
    AVG(f.score_risque_predicted) AS risque_moyen
FROM fait_sinistres f
JOIN dim_temps t ON f.id_temps = t.id_temps
GROUP BY DATE_TRUNC('week', t.date)
WITH DATA;

CREATE UNIQUE INDEX idx_mv_semaine ON mv_stats_hebdomadaires (semaine);

-- Fonction pour rafraîchir la vue matérialisée
CREATE OR REPLACE FUNCTION refresh_mv_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats_hebdomadaires;
END;
$$ LANGUAGE plpgsql;

SELECT '✅ Vues créées avec succès !' AS status;