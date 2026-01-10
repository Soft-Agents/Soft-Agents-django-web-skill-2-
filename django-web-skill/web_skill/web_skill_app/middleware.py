from django.conf import settings
from .db import set_active_db_name

class MultiTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Verificar si el usuario es Admin y tiene una DB seleccionada en su sesión
        if request.user.is_authenticated and request.user.is_superuser:
            # Recuperar la DB activa de la sesión (o usar la default)
            active_db = request.session.get('active_mongo_db', getattr(settings, 'MONGO_DB_NAME', 'webSkill'))
            
            # 2. Configurar la DB para este hilo de ejecución
            set_active_db_name(active_db)
        else:
            # Si no es admin, siempre usa la DB por defecto
            default_db = getattr(settings, 'MONGO_DB_NAME', 'webSkill')
            set_active_db_name(default_db)

        # 3. Continuar con la petición
        response = self.get_response(request)
        return response