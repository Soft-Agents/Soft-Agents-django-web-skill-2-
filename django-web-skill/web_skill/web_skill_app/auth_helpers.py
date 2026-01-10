# web_skill_app/auth_helpers.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from bson.objectid import ObjectId

# --- Funciones auxiliares para manejo de sesiones ---

def login_user_session(request, user_data, is_admin=False):
    """Inicia sesión manual guardando datos del usuario en la sesión"""
    # CRÍTICO: user_data['_id'] es un ObjectId de MongoDB, debe ser convertido a string
    user_id_str = str(user_data['_id']) if isinstance(user_data['_id'], ObjectId) else user_data['_id']
    
    request.session['user_id'] = user_id_str
    request.session['user_email'] = user_data['email']
    request.session['user_first_name'] = user_data['first_name']
    request.session['is_admin'] = is_admin  # Nuevo campo para identificar admins
    request.session.modified = True

def logout_user_session(request):
    """Cierra sesión eliminando datos de la sesión"""
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    if 'user_first_name' in request.session:
        del request.session['user_first_name']
    if 'is_admin' in request.session:
        del request.session['is_admin']
    request.session.modified = True
    
# Función auxiliar para obtener el usuario (compatible con el decorador)
def get_current_user(request):
    """Retorna el objeto de usuario de la sesión o None si no está logueado."""
    if 'user_id' in request.session:
        return {
            'user_id': request.session.get('user_id'),
            'email': request.session.get('user_email'),
            'first_name': request.session.get('user_first_name'),
            'is_admin': request.session.get('is_admin', False),
            'is_authenticated': True
        }
    return {'is_authenticated': False}


# --- Decorador de autenticación personalizado ---
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si hay un ID de usuario en la sesión
        if 'user_id' not in request.session:
            messages.info(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login_page')
        
        # Recuperar datos del usuario de la sesión para el contexto
        request.user = get_current_user(request)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- Decorador para vistas de administrador ---
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si hay un ID de usuario en la sesión
        if 'user_id' not in request.session:
            messages.info(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login_page')
        
        # Verificar si es administrador
        if not request.session.get('is_admin', False):
            messages.error(request, "No tienes permisos de administrador para acceder a esta página.")
            return redirect('presentacion')
        
        # Recuperar datos del usuario de la sesión para el contexto
        request.user = get_current_user(request)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view