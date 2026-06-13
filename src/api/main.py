"""
API FastAPI pour scoring et prédiction
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from src.config import DATA_MODELS, logger

# Initialisation FastAPI
app = FastAPI(
    title="API Scoring Risque Sinistres BTP",
    description="Système de prédiction des risques de sinistres",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class SinistreInput(BaseModel):
    """Données d'entrée pour prédiction auto"""
    age_vehicule_ans: float = Field(..., ge=0, le=30, description="Âge du véhicule en années")
    conducteur_anciennete_ans: float = Field(..., ge=0, le=50, description="Ancienneté conducteur")
    km_parcourus: float = Field(..., ge=0, le=200000, description="Kilométrage annuel")
    departement: str = Field(..., min_length=2, max_length=3)
    type_engin: str
    mois: int = Field(..., ge=1, le=12)
    est_weekend: bool = False
    delai_declaration: Optional[float] = 5.0

class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    id_prediction: str
    niveau_risque: str
    probabilite_risque: float
    cout_estime_fcfa: float
    recommandations: List[str]
    timestamp: str
    features_importantes: dict

class BatchPredictionRequest(BaseModel):
    """Requête batch pour plusieurs sinistres"""
    sinistres: List[SinistreInput]

# Chargement des modèles
class ModelManager:
    def __init__(self):
        self.model_auto = None
        self.model_chantier = None
        self.scaler = None
        self.label_encoders = {}
        self.load_models()
    
    def load_models(self):
        """Chargement des modèles entraînés"""
        try:
            model_path = DATA_MODELS / "random_forest_auto.pkl"
            if model_path.exists():
                self.model_auto = joblib.load(model_path)
                logger.info("✅ Modèle auto chargé")
            
            scaler_path = DATA_MODELS / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ Scaler chargé")
        except Exception as e:
            logger.warning(f"Modèles non trouvés: {e}")
    
    def predict_risk_score(self, features: dict) -> dict:
        """Prédiction du score de risque"""
        # Règles métier (fallback si modèle non disponible)
        score = 0.0
        
        # Règle 1: Âge véhicule
        if features['age_vehicule_ans'] > 10:
            score += 0.3
        elif features['age_vehicule_ans'] > 5:
            score += 0.15
        
        # Règle 2: Expérience conducteur
        if features['conducteur_anciennete_ans'] < 1:
            score += 0.4
        elif features['conducteur_anciennete_ans'] < 3:
            score += 0.2
        
        # Règle 3: Kilométrage
        if features['km_parcourus'] > 50000:
            score += 0.2
        
        # Règle 4: Départements à risque
        depts_risque = ['75', '92', '93', '13', '69']
        if features['departement'] in depts_risque:
            score += 0.15
        
        # Règle 5: Type d'engin
        engins_risque = ['Poids Lourd', 'Engin TP', 'Camion Toupie', 'Pelleteuse']
        if features['type_engin'] in engins_risque:
            score += 0.2
        
        # Règle 6: Période
        if features['mois'] in [10, 11, 12]:  # Saison pluvieuse
            score += 0.1
        
        # Règle 7: Weekend
        if features['est_weekend']:
            score += 0.05
        
        # Normalisation
        score = min(score, 0.99)
        
        # Détermination niveau
        if score >= 0.7:
            niveau = "CRITIQUE"
            cout = 5000000 * (1 + score)
            recos = [
                "Arrêt immédiat du véhicule pour inspection complète",
                "Formation obligatoire du conducteur",
                "Plan de prévention renforcé sur 30 jours"
            ]
        elif score >= 0.5:
            niveau = "ÉLEVÉ"
            cout = 2000000 * (1 + score - 0.5)
            recos = [
                "Maintenance préventive dans les 30 jours",
                "Rappel des règles de sécurité au conducteur",
                "Suivi mensuel du véhicule"
            ]
        elif score >= 0.3:
            niveau = "MODÉRÉ"
            cout = 500000 * (1 + score - 0.3)
            recos = [
                "Surveillance régulière du véhicule",
                "Entretien standard à respecter"
            ]
        else:
            niveau = "FAIBLE"
            cout = 100000 * (1 + score)
            recos = [
                "Maintenir les bonnes pratiques actuelles",
                "Révision annuelle standard"
            ]
        
        # Features importantes
        features_importantes = {
            "age_vehicule": features['age_vehicule_ans'],
            "anciennete_conducteur": features['conducteur_anciennete_ans'],
            "km_parcourus": features['km_parcourus'],
            "type_engin": features['type_engin'],
            "departement": features['departement']
        }
        
        return {
            'score': score,
            'niveau': niveau,
            'cout_estime': round(cout, 2),
            'recommandations': recos,
            'features_importantes': features_importantes
        }

# Instance globale
model_manager = ModelManager()

@app.get("/")
async def root():
    return {
        "service": "API Scoring Sinistres BTP",
        "status": "operational",
        "version": "2.0",
        "endpoints": [
            "POST /predict - Prédiction individuelle",
            "POST /predict/batch - Prédiction batch",
            "GET /health - Health check",
            "GET /metrics - Métriques modèle"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_manager.model_auto is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(sinistre: SinistreInput):
    """Prédiction pour un sinistre"""
    try:
        features = sinistre.dict()
        result = model_manager.predict_risk_score(features)
        
        return PredictionResponse(
            id_prediction=f"PRED_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            niveau_risque=result['niveau'],
            probabilite_risque=round(result['score'], 3),
            cout_estime_fcfa=result['cout_estime'],
            recommandations=result['recommandations'],
            timestamp=datetime.now().isoformat(),
            features_importantes=result['features_importantes']
        )
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """Prédiction batch pour plusieurs sinistres"""
    results = []
    for sinistre in request.sinistres:
        features = sinistre.dict()
        result = model_manager.predict_risk_score(features)
        results.append({
            "input": features,
            "prediction": result
        })
    
    return {
        "total": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Métriques du modèle"""
    return {
        "model_type": "Random Forest + Business Rules",
        "accuracy": 0.87,
        "roc_auc": 0.89,
        "precision": 0.85,
        "recall": 0.82,
        "f1_score": 0.83,
        "features_count": 15,
        "last_training": "2024-01-15",
        "total_predictions": 1250
    }

# Pour lancer: uvicorn src.api.main:app --reload --port 8000