# Guía de Despliegue en Google Cloud Run

## Prerrequisitos

1. **Google Cloud CLI instalado y configurado**

   ```bash
   gcloud auth login
   gcloud config set project TU-PROJECT-ID
   ```

2. **Docker instalado y funcionando**

3. **Habilitar APIs necesarias**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

## Configuración

1. **Actualizar variables en `env.yaml`**

   - Verificar que todas las URLs y credenciales sean correctas
   - Asegurar que `DEBUG` esté en `"False"`

2. **Actualizar PROJECT_ID en los scripts de despliegue**
   - Editar `deploy.sh` o `deploy.ps1`
   - Cambiar `tu-project-id` por tu Project ID real

## Despliegue

### Opción 1: Script automatizado (Windows)

```powershell
.\deploy.ps1
```

### Opción 2: Script automatizado (Linux/Mac)

```bash
./deploy.sh
```

### Opción 3: Comandos manuales

1. **Construir imagen**

   ```bash
   docker build -t gcr.io/TU-PROJECT-ID/web-skill-service .
   ```

2. **Subir imagen**

   ```bash
   docker push gcr.io/TU-PROJECT-ID/web-skill-service
   ```

3. **Desplegar**
   ```bash
   gcloud run deploy web-skill-service \
     --image gcr.io/TU-PROJECT-ID/web-skill-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --env-vars-file env.yaml \
     --memory 1Gi \
     --cpu 1
   ```

## Verificación

1. **Obtener URL del servicio**

   ```bash
   gcloud run services describe web-skill-service \
     --platform managed \
     --region us-central1 \
     --format 'value(status.url)'
   ```

2. **Probar la aplicación**
   - Visitar la URL obtenida
   - Verificar que la página carga correctamente
   - Probar funcionalidades principales

## Monitoreo

- **Logs**: `gcloud logs tail --service=web-skill-service`
- **Métricas**: Google Cloud Console > Cloud Run > web-skill-service

## Solución de Problemas

### Error 500

- Revisar logs: `gcloud logs tail --service=web-skill-service`
- Verificar variables de entorno en `env.yaml`
- Comprobar conectividad con MongoDB

### Error de memoria

- Aumentar memoria en el comando de despliegue: `--memory 2Gi`

### Timeout

- Aumentar timeout: `--timeout 600`

## Actualizaciones

Para actualizar la aplicación:

1. Hacer cambios en el código
2. Ejecutar el script de despliegue nuevamente
3. Cloud Run automáticamente creará una nueva revisión
