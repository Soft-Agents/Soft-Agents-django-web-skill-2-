#!/bin/bash

# Script de despliegue para Cloud Run
# Asegúrate de tener configurado gcloud CLI y Docker

set -e

# Variables de configuración
PROJECT_ID="tu-project-id"  # Cambia esto por tu Project ID
SERVICE_NAME="web-skill-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Iniciando despliegue de $SERVICE_NAME..."

# Verificar que gcloud esté configurado
echo "📋 Verificando configuración de gcloud..."
gcloud config get-value project

# Construir la imagen Docker
echo "🔨 Construyendo imagen Docker..."
docker build -t $IMAGE_NAME .

# Subir la imagen a Google Container Registry
echo "📤 Subiendo imagen a Container Registry..."
docker push $IMAGE_NAME

# Desplegar a Cloud Run
echo "🌐 Desplegando a Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --env-vars-file env.yaml \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

echo "✅ Despliegue completado!"
echo "🔗 URL del servicio:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'