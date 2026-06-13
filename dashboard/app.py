import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine
import numpy as np

from src.config import DATABASE_URL, logger

# Configuration page
st.set_page_config(
    page_title="Dashboard Sinistres BTP",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-critical { color: #dc3545; font-weight: bold; }
    .risk-high { color: #fd7e14; font-weight: bold; }
    .risk-moderate { color: #ffc107; font-weight: bold; }
    .risk-low { color: #28a745; font-weight: bold; }
    .dashboard-title {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<p class="dashboard-title">🏗️ Système Décisionnel BTP - Gestion des Risques</p>', unsafe_allow_html=True)
st.caption(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Sidebar
st.sidebar.header("🔍 Filtres")
type_sinistre = st.sidebar.selectbox("Type de sinistre", ["Tous", "Automobile", "Chantier"])
periode = st.sidebar.selectbox("Période", ["6 derniers mois", "12 derniers mois", "Année en cours", "Toutes"])
departements = st.sidebar.multiselect("Département", ["75", "92", "93", "13", "69", "31", "59", "33", "06"])

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=300)
def load_data_from_dwh():
    """Chargement des données depuis PostgreSQL"""
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            f.*,
            t.annee,
            t.mois,
            t.mois_nom,
            t.jour_semaine,
            v.type_engin,
            v.marque,
            v.age_ans,
            g.departement,
            g.region
        FROM fait_sinistres f
        JOIN dim_temps t ON f.id_temps = t.id_temps
        LEFT JOIN dim_vehicule v ON f.id_vehicule = v.id_vehicule
        LEFT JOIN dim_geographie g ON f.id_geo = g.id_geo
        ORDER BY f.date_integration DESC
        LIMIT 10000
        """
        
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return pd.DataFrame()

# Chargement
with st.spinner("Chargement des données..."):
    df = load_data_from_dwh()

if not df.empty:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nb_sinistres = len(df)
        st.metric("📊 Total Sinistres", f"{nb_sinistres:,}", delta="+12% vs N-1")
    
    with col2:
        cout_total = df['cout_total'].sum() / 1e6 if 'cout_total' in df.columns else 0
        st.metric("💰 Coût Total", f"{cout_total:.1f} M FCFA", delta="+8%")
    
    with col3:
        cout_moyen = df['cout_total'].mean() if 'cout_total' in df.columns else 0
        st.metric("📈 Coût Moyen", f"{cout_moyen:,.0f} FCFA", delta="-5%")
    
    with col4:
        delai_moyen = df['delai_reglement'].mean() if 'delai_reglement' in df.columns else 0
        st.metric("⏱️ Délai Règlement", f"{delai_moyen:.1f} jours", delta="-3j")
    
    # Graphiques
    st.subheader("📈 Analyses Graphiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'cout_total' in df.columns:
            fig = px.histogram(df, x='cout_total', nbins=50, 
                              title="Distribution des coûts des sinistres",
                              color_discrete_sequence=['#667eea'])
            fig.update_layout(xaxis_title="Coût (FCFA)", yaxis_title="Fréquence")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'type_engin' in df.columns:
            df_engin = df['type_engin'].value_counts().head(10).reset_index()
            df_engin.columns = ['Type', 'Nombre']
            fig = px.bar(df_engin, x='Nombre', y='Type', orientation='h',
                        title="Top 10 des engins sinistrés",
                        color='Nombre', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    # Carte des risques
    if 'departement' in df.columns:
        st.subheader("🗺️ Cartographie des Risques")
        df_geo = df.groupby('departement').agg({
            'cout_total': 'sum',
            'id_sinistre': 'count'
        }).reset_index()
        df_geo['risque_score'] = (df_geo['cout_total'] / df_geo['cout_total'].max() * 0.6 + 
                                   df_geo['id_sinistre'] / df_geo['id_sinistre'].max() * 0.4) * 100
        
        fig = px.choropleth(df_geo, 
                            locations='departement',
                            color='risque_score',
                            hover_name='departement',
                            color_continuous_scale='RdYlGn_r',
                            title="Score de risque par département",
                            labels={'risque_score': 'Score'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Formulaire prédiction
    st.subheader("🎯 Prédiction en Temps Réel")
    
    with st.expander("📝 Nouveau sinistre - Estimer le risque", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age_vehicule = st.number_input("Âge du véhicule (années)", 0, 30, 5)
            anciennete = st.number_input("Ancienneté conducteur (années)", 0, 40, 3)
        
        with col2:
            km = st.number_input("Kilométrage annuel", 0, 150000, 15000)
            type_engin = st.selectbox("Type d'engin", 
                                     ["Véhicule léger", "Poids Lourd", "Engin TP", "Camion Toupie"])
        
        with col3:
            dept = st.selectbox("Département", ["75", "92", "93", "13", "69", "31"])
            mois = st.selectbox("Mois", range(1, 13), datetime.now().month - 1)
            weekend = st.checkbox("Weekend?")
        
        if st.button("🔮 Prédire le risque", type="primary"):
            payload = {
                "age_vehicule_ans": age_vehicule,
                "conducteur_anciennete_ans": anciennete,
                "km_parcourus": km,
                "departement": dept,
                "type_engin": type_engin,
                "mois": mois,
                "est_weekend": weekend,
                "delai_declaration": 5.0
            }
            
            try:
                response = requests.post("http://localhost:8000/predict", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Prédiction réalisée avec succès!")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        niveau = result['niveau_risque']
                        color_class = {"CRITIQUE": "risk-critical", "ÉLEVÉ": "risk-high",
                                      "MODÉRÉ": "risk-moderate", "FAIBLE": "risk-low"}.get(niveau, "")
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Niveau de Risque</h4>
                            <h2 class="{color_class}">{niveau}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Probabilité</h4>
                            <h2>{result['probabilite_risque']*100:.1f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Coût Estimé</h4>
                            <h2>{result['cout_estime_fcfa']:,.0f} FCFA</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("**Recommandations:**")
                    for rec in result['recommandations']:
                        st.markdown(f"- {rec}")
                else:
                    st.error("Erreur API")
            except Exception as e:
                st.error(f"Erreur connexion: {e}")
                st.info("Lancez l'API: uvicorn src.api.main:app --reload")
    
    # Tableau récent
    st.subheader("📋 Derniers sinistres enregistrés")
    cols_to_show = ['id_sinistre', 'cout_total', 'delai_reglement', 'type_engin', 'departement', 'date_integration']
    cols_exist = [c for c in cols_to_show if c in df.columns]
    st.dataframe(df[cols_exist].head(20), use_container_width=True)
    
    # Export
    st.download_button(
        label="📥 Exporter CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"export_sinistres_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.warning("Aucune donnée trouvée. Exécutez d'abord le pipeline ETL.")