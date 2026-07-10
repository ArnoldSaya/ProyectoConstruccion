#!/usr/bin/env bash
# =============================================================
# build.sh — Script de build para Render
# Instala el backend (pip), instala el frontend (npm) y genera
# el bundle de Vue dentro de backend/app/static/dist/ para que
# Flask lo sirva directamente.
# =============================================================
set -o errexit  # salir si hay error

echo "===== [1/3] Instalando dependencias Python ====="
pip install -r requirements.txt

echo "===== [2/3] Instalando dependencias Node (frontend) ====="
cd ../frontend
npm install

echo "===== [3/3] Build del frontend (Vite -> backend/app/static/dist) ====="
VITE_API_URL=/api npm run build

echo "===== Build completo ====="
