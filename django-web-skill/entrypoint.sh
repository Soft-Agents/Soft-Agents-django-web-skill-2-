#!/bin/bash
set -e

echo "🚀 Iniciando aplicación..."
echo "PORT: ${PORT}"

cd /app/web_skill

# Test completo de Django con traceback
echo "🧪 Testeando Django settings..."
python << 'PYEOF'
import sys
import traceback
try:
    import django
    from django.conf import settings
    print(f"✅ Django {django.get_version()} importado")
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ SECRET_KEY: {settings.SECRET_KEY[:10]}...")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ DATABASES: {list(settings.DATABASES.keys())}")
except Exception as e:
    print(f"❌ ERROR AL CARGAR DJANGO:")
    print(traceback.format_exc())
    sys.exit(1)
PYEOF

echo "📋 Aplicando migraciones..."
python manage.py migrate --noinput --traceback 2>&1 || {
    echo "❌ ERROR EN MIGRACIONES"
    exit 1
}

echo "✅ Migraciones OK"

echo "🌐 Iniciando Gunicorn en puerto $PORT..."
exec gunicorn web_skill.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --access-logfile - \
    --error-logfile - 2>&1