# web_skill_app/context_processors.py (crear este archivo nuevo)

def user_context(request):
    """
    Context processor para hacer disponible la información del usuario
    en todos los templates automáticamente
    """
    from .auth_helpers import get_current_user
    
    user = get_current_user(request)
    
    return {
        'user': user if user else {'is_authenticated': False}
    }