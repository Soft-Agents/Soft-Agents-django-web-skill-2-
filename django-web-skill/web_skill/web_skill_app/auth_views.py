# web_skill_app/auth_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
import datetime 

# --- Importaciones de nuestros módulos ---
from .db import get_db_collection, get_admin_collection
from .auth_helpers import login_user_session, logout_user_session

# --- Vistas de Autenticación (REPARADAS) ---

def login_page(request):
    # 1. Si ya está logueado, redirigir según tipo de usuario
    if 'user_id' in request.session:
        if request.session.get('is_admin', False):
            return redirect('admin_dashboard')
        return redirect('presentacion')
        
    try:
        users_collection = get_db_collection()
        admin_collection = get_admin_collection()
    except ConnectionError as e:
        messages.error(request, str(e))
        return render(request, 'web_skill_app/login.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not all([email, password]):
            messages.error(request, "Por favor, ingresa tu correo y contraseña.")
            return render(request, 'web_skill_app/login.html')

        try:
            # 3. Primero buscar en la colección de administradores
            admin_data = admin_collection.find_one({'email': email.lower()})
            
            if admin_data:
                # Verificar contraseña del admin
                hashed_password_from_db = admin_data['password']
                if isinstance(hashed_password_from_db, str):
                    hashed_password_from_db = hashed_password_from_db.encode('utf-8')

                if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db):
                    # Iniciar sesión como administrador
                    login_user_session(request, admin_data, is_admin=True)
                    messages.success(request, f"¡Bienvenido Administrador, {admin_data['first_name']}!")
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Contraseña incorrecta. Inténtalo de nuevo.")
                    return render(request, 'web_skill_app/login.html')
            
            # 4. Si no es admin, buscar en usuarios normales
            user_data = users_collection.find_one({'email': email.lower()})
            
            if user_data:
                # Verificar la contraseña hasheada
                hashed_password_from_db = user_data['password']
                if isinstance(hashed_password_from_db, str):
                    hashed_password_from_db = hashed_password_from_db.encode('utf-8')

                if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db):
                    # Iniciar sesión como usuario normal
                    login_user_session(request, user_data, is_admin=False)
                    messages.success(request, f"¡Bienvenido, {user_data['first_name']}!")
                    return redirect('presentacion') 
                else:
                    messages.error(request, "Contraseña incorrecta. Inténtalo de nuevo.")
            else:
                messages.error(request, "Usuario no encontrado. Verifica el correo.")
                
        except Exception as e:
            messages.error(request, f"Ocurrió un error en el servidor: {e}")
            
    # Si es GET o POST fallido, renderiza la página de login
    return render(request, 'web_skill_app/login.html')

def register_view(request):
    # 1. Si ya está logueado, redirigir
    if 'user_id' in request.session:
        return redirect('presentacion')

    if request.method != 'POST':
        return redirect('login_page')

    try:
        users_collection = get_db_collection()
    except ConnectionError as e:
        messages.error(request, str(e))
        return render(request, 'web_skill_app/login.html')
    
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not all([first_name, last_name, email, password]):
        messages.error(request, "Todos los campos son obligatorios.")
        return render(request, 'web_skill_app/login.html')

    try:
        # 3. Verificar si el correo ya existe
        if users_collection.find_one({'email': email.lower()}):
            messages.error(request, "Este correo ya está registrado.")
        else:
            # 4. Hashear y guardar
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user_doc = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email.lower(),
                'password': hashed_password, 
                'created_at': datetime.datetime.utcnow(),
                'conversation_history_criker': [],
                'conversation_history_knowledge': [],
            }
            
            result = users_collection.insert_one(user_doc)
            
            # 5. Iniciar sesión automáticamente
            user_data = users_collection.find_one({'_id': result.inserted_id})
            login_user_session(request, user_data)
            
            messages.success(request, "Registro exitoso. ¡Bienvenido!")
            return redirect('presentacion') 
    except Exception as e:
        messages.error(request, f"Ocurrió un error al registrar el usuario: {e}")

    # Si hay errores de registro, renderizar la página de login de nuevo
    return render(request, 'web_skill_app/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout_user_session(request)
        messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login_page')