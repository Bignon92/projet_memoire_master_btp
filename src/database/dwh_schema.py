"""
Modèles SQLAlchemy pour le Data Warehouse
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, 
    ForeignKey, UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from src.database.connection import Base

class DimTemps(Base):
    """Dimension Temps (Calendar)"""
    __tablename__ = 'dim_temps'
    
    id_temps = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    annee = Column(Integer, nullable=False)
    mois = Column(Integer, nullable=False)
    mois_nom = Column(String(20))
    jour = Column(Integer)
    trimestre = Column(Integer)
    semaine = Column(Integer)
    jour_semaine = Column(String(20))
    est_weekend = Column(Boolean)
    saison = Column(String(20))

class DimVehicule(Base):
    """Dimension Véhicule"""
    __tablename__ = 'dim_vehicule'
    
    id_vehicule = Column(Integer, primary_key=True)
    immatriculation = Column(String(50), unique=True, nullable=False)
    type_engin = Column(String(100))
    marque = Column(String(100))
    age_ans = Column(Float)
    km_parcourus = Column(Float)
    categorie_km = Column(String(50))
    date_dernier_sinistre = Column(Date)

class DimConducteur(Base):
    """Dimension Conducteur"""
    __tablename__ = 'dim_conducteur'
    
    id_conducteur = Column(Integer, primary_key=True)
    anciennete_ans = Column(Float)
    classe_age = Column(String(20))
    niveau_experience = Column(String(20))
    score_risque_conducteur = Column(Float)
    nb_sinistres_historique = Column(Integer, default=0)

class DimChantier(Base):
    """Dimension Chantier (pour sinistres TRC)"""
    __tablename__ = 'dim_chantier'
    
    id_chantier = Column(Integer, primary_key=True)
    code_chantier = Column(String(50), unique=True)
    nom_chantier = Column(String(200))
    type_travaux = Column(String(100))
    phase_chantier = Column(String(50))
    departement = Column(String(10))
    date_debut = Column(Date)
    date_fin = Column(Date)
    cout_projet = Column(Float)

class DimGeographie(Base):
    """Dimension Géographique"""
    __tablename__ = 'dim_geographie'
    
    id_geo = Column(Integer, primary_key=True)
    departement = Column(String(10))
    region = Column(String(50))
    axe_routier = Column(String(100))
    type_zone = Column(String(50))
    taux_accidentalite = Column(Float)

class DimAssureur(Base):
    """Dimension Assureur"""
    __tablename__ = 'dim_assureur'
    
    id_assureur = Column(Integer, primary_key=True)
    nom_assureur = Column(String(100))
    type_contrat = Column(String(50))
    taux_franchise_moyen = Column(Float)

class DimSinistreType(Base):
    """Dimension Type de Sinistre"""
    __tablename__ = 'dim_sinistre_type'
    
    id_type = Column(Integer, primary_key=True)
    type_sinistre = Column(String(50))
    nature_sinistre = Column(String(100))
    gravite = Column(String(20))
    responsabilite = Column(String(30))
    categorie_risque = Column(String(20))

class FaitSinistre(Base):
    """Table de Faits Sinistres"""
    __tablename__ = 'fait_sinistres'
    
    id_sinistre = Column(Integer, primary_key=True)
    id_temps = Column(Integer, ForeignKey('dim_temps.id_temps'))
    id_vehicule = Column(Integer, ForeignKey('dim_vehicule.id_vehicule'), nullable=True)
    id_conducteur = Column(Integer, ForeignKey('dim_conducteur.id_conducteur'), nullable=True)
    id_chantier = Column(Integer, ForeignKey('dim_chantier.id_chantier'), nullable=True)
    id_geo = Column(Integer, ForeignKey('dim_geographie.id_geo'))
    id_assureur = Column(Integer, ForeignKey('dim_assureur.id_assureur'))
    id_type = Column(Integer, ForeignKey('dim_sinistre_type.id_type'))
    
    montant_declare = Column(Float)
    franchise = Column(Float)
    montant_indemnise = Column(Float)
    delai_declaration = Column(Integer)
    delai_reglement = Column(Integer)
    cout_total = Column(Float)
    est_sinistre_grave = Column(Boolean)
    score_risque_predicted = Column(Float)
    niveau_risque_reel = Column(String(20))
    date_integration = Column(DateTime)
    
    # Relations
    temps = relationship("DimTemps")
    vehicule = relationship("DimVehicule")
    conducteur = relationship("DimConducteur")
    chantier = relationship("DimChantier")
    geographie = relationship("DimGeographie")
    assureur = relationship("DimAssureur")
    type_sinistre = relationship("DimSinistreType")

# Index pour performances
Index('idx_fait_temps', FaitSinistre.id_temps)
Index('idx_fait_vehicule', FaitSinistre.id_vehicule)
Index('idx_fait_cout', FaitSinistre.cout_total)
Index('idx_fait_date_integration', FaitSinistre.date_integration)
Index('idx_dim_vehicule_immat', DimVehicule.immatriculation)
Index('idx_dim_chantier_code', DimChantier.code_chantier)