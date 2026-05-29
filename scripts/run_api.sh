#!/bin/bash
echo "🚀 Démarrage de l'API FastAPI..."
cd /path/to/project
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000