# Script para probar la construcción del Docker localmente
Write-Host "🔨 Probando construcción de Docker..." -ForegroundColor Yellow

# Construir la imagen localmente
docker build -t web-skill-test .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Construcción exitosa!" -ForegroundColor Green
    
    # Opcional: Probar que la imagen funciona
    Write-Host "🧪 Probando que la imagen funciona..." -ForegroundColor Yellow
    docker run --rm -p 8080:8080 -e DEBUG=True web-skill-test
} else {
    Write-Host "❌ Error en la construcción" -ForegroundColor Red
    Write-Host "Revisa los logs arriba para más detalles" -ForegroundColor Yellow
}