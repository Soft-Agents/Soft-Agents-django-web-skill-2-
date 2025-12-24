# SCRIPT PARA DEPLOY EN GOOGLE CLOUD RUN (PowerShell)
# Version final y corregida para maxima compatibilidad y estabilidad.
# ----------------------------------------------------

# 1. Definir la version y configuracion (IMPORTANTE: Cambia esto en cada despliegue)
$VERSION = "v20" 
$PROJECT_ID = "softagents"
$REGION = "us-central1"

# NOTA: Usamos gcr.io (Container Registry) ya que no necesitas un repositorio en Artifact Registry.
$IMAGE_TAG = "gcr.io/${PROJECT_ID}/web-skill-service:${VERSION}"
$SERVICE_NAME = "web-skill-service"

# --- INICIO DEL DESPLIEGUE ---
Write-Host "Iniciando despliegue de $SERVICE_NAME con la version $VERSION..." -ForegroundColor Green
Write-Host "URL de la imagen: $IMAGE_TAG" -ForegroundColor Green

# 1. Autenticacion con Google Cloud
Write-Host "Verificando autenticacion de Google Cloud..." -ForegroundColor Yellow
gcloud auth print-access-token > $null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Advertencia: Autenticacion necesaria. Ejecutando gcloud auth login..." -ForegroundColor DarkYellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: La autenticacion fallo." -ForegroundColor Red
        exit 1
    }
}

# 2. Configurar proyecto y habilitar servicios
Write-Host "Configurando proyecto: $PROJECT_ID..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host "Habilitando servicio de Cloud Run..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --project=$PROJECT_ID

# 3. Configurar autenticacion de Docker para gcr.io (necesario para el paso 'docker push')
Write-Host "Configurando autenticacion de Docker para gcr.io..." -ForegroundColor Yellow
gcloud auth configure-docker gcr.io

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: La configuracion de Docker fallo." -ForegroundColor Red
    exit 1
}

# 4. Construir la Imagen (Usando --no-cache para corregir dependencias localmente)
Write-Host "Construyendo y etiquetando imagen Docker como $IMAGE_TAG (sin cache)..." -ForegroundColor Cyan
docker build -t $IMAGE_TAG . --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: El 'docker build' fallo. Abortando despliegue." -ForegroundColor Red
    exit 1
}

# 5. Subir la Imagen
Write-Host "Subiendo imagen a Container Registry..." -ForegroundColor Yellow
docker push $IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: El 'docker push' fallo. Abortando despliegue." -ForegroundColor Red
    exit 1
}

# 6. Desplegar a Cloud Run
Write-Host "Desplegando $SERVICE_NAME a Cloud Run..." -ForegroundColor Cyan

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --timeout 300 `
    --memory 1Gi `
    --env-vars-file env.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: El 'gcloud run deploy' fallo." -ForegroundColor Red
    exit 1
}

Write-Host "Despliegue completado!" -ForegroundColor Green

# 7. Obtener URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
Write-Host "--- URL del servicio: $SERVICE_URL" -ForegroundColor White