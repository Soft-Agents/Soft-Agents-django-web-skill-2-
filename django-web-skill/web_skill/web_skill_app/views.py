# # web_skill_app/views.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.conf import settings
# # Asegúrate de que tus services.py contiene estas funciones
# from .services import get_agent_response_criker, get_conversation_history_criker, get_agent_response_knowledge, get_conversation_history_knowledge
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import bcrypt
# from functools import wraps
# import datetime 
# from django.urls import reverse

# # --- Decorador de autenticación personalizado ---
# def login_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         # Verificar si hay un ID de usuario en la sesión
#         if 'user_id' not in request.session:
#             messages.info(request, "Debes iniciar sesión para acceder a esta página.")
#             return redirect('login_page')
        
#         # Recuperar datos del usuario de la sesión para el contexto
#         request.user = get_current_user(request)
        
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view

# # --- Funciones auxiliares para manejo de sesiones ---
# def login_user_session(request, user_data):
#     """Inicia sesión manual guardando datos del usuario en la sesión"""
#     # CRÍTICO: user_data['_id'] es un ObjectId de MongoDB, debe ser convertido a string
#     user_id_str = str(user_data['_id']) if isinstance(user_data['_id'], ObjectId) else user_data['_id']
    
#     request.session['user_id'] = user_id_str
#     request.session['user_email'] = user_data['email']
#     request.session['user_first_name'] = user_data['first_name']
#     request.session.modified = True

# def logout_user_session(request):
#     """Cierra sesión eliminando datos de la sesión"""
#     if 'user_id' in request.session:
#         del request.session['user_id']
#     if 'user_email' in request.session:
#         del request.session['user_email']
#     if 'user_first_name' in request.session:
#         del request.session['user_first_name']
#     request.session.modified = True
    
# # Función auxiliar para obtener el usuario (compatible con el decorador)
# def get_current_user(request):
#     """Retorna el objeto de usuario de la sesión o None si no está logueado."""
#     if 'user_id' in request.session:
#         return {
#             'user_id': request.session.get('user_id'),
#             'email': request.session.get('user_email'),
#             'first_name': request.session.get('user_first_name'),
#             'is_authenticated': True
#         }
#     return {'is_authenticated': False}


# # --- Conexión a MongoDB ---
# def get_db_collection():
#     """Establece la conexión a MongoDB Atlas y retorna el cliente y la colección de usuarios."""
#     client = None
#     users_collection = None
#     try:
#         mongo_uri = getattr(settings, 'MONGO_URI')
        
#         client = MongoClient(mongo_uri)
#         # Asegúrate que la base de datos sea 'webSkill' o el nombre correcto
#         db = client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')] 
#         users_collection = db['users']
        
#         # Opcional: Probar la conexión
#         # db.command('ping') 
        
#         return client, users_collection
#     except AttributeError:
#         # Se cierra el cliente si llegó a inicializarse pero falló después
#         if client: client.close() 
#         print("Error de Configuración: MONGO_URI no está definido en settings.py.")
#         return None, None
#     except Exception as e:
#         if client: client.close() 
#         print(f"Error de conexión a MongoDB: {e}")
#         return None, None

# # --- Vistas de páginas estáticas ---
# def home(request):
#     return render(request, 'web_skill_app/index.html')

# def pensamiento_critico(request):
#     return render(request, 'web_skill_app/pensamiento-critico.html')

# def comunicacion(request):
#     return render(request, 'web_skill_app/comunicacion.html')

# def creatividad(request):
#     return render(request, 'web_skill_app/creatividad.html')

# def colaboracion(request):
#     return render(request, 'web_skill_app/colaboracion.html')

# def skill(request):
#     import time
#     context = {
#         'timestamp': int(time.time())  # Timestamp para evitar caché
#     }
#     return render(request, "web_skill_app/skill.html", context)

# # --- Vistas de Autenticación (REPARADAS) ---

# def login_page(request):
#     # Debug info para CSRF
#     if request.method == 'POST':
#         print(f"DEBUG - CSRF Token en POST: {request.POST.get('csrfmiddlewaretoken', 'NO ENCONTRADO')}")
#         print(f"DEBUG - Headers: {dict(request.headers)}")
#         print(f"DEBUG - Host: {request.get_host()}")
#         print(f"DEBUG - Is Secure: {request.is_secure()}")
        
#     client, users_collection = get_db_collection()
    
#     # 1. Si ya está logueado, redirigir
#     if 'user_id' in request.session:
#         if client: client.close()
#         return redirect('dashboard')
        
#     # 2. Verificar si users_collection es None
#     if users_collection is None:
#         messages.error(request, "Error de conexión a la base de datos. Por favor, revisa tu conexión MongoDB.")
#         if client: client.close()
#         return render(request, 'web_skill_app/login.html')

#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         if not all([email, password]):
#             messages.error(request, "Por favor, ingresa tu correo y contraseña.")
#             if client: client.close()
#             return render(request, 'web_skill_app/login.html')

#         try:
#             # 3. Buscar usuario en MongoDB
#             user_data = users_collection.find_one({'email': email.lower()})
            
#             if user_data:
#                 # 4. Verificar la contraseña hasheada
#                 # CORRECCIÓN: Nos aseguramos de que el hash almacenado también sea un objeto bytes.
#                 # Si el hash almacenado es una cadena, lo convertimos a bytes para checkpw
#                 hashed_password_from_db = user_data['password']
#                 if isinstance(hashed_password_from_db, str):
#                     hashed_password_from_db = hashed_password_from_db.encode('utf-8')

#                 if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db):
#                     # 5. Iniciar sesión y REDIRIGIR
#                     login_user_session(request, user_data)
#                     messages.success(request, f"¡Bienvenido, {user_data['first_name']}!")
#                     return redirect('dashboard') 
#                 else:
#                     messages.error(request, "Contraseña incorrecta. Inténtalo de nuevo.")
#             else:
#                 messages.error(request, "Usuario no encontrado. Verifica el correo.")
                
#         except Exception as e:
#             messages.error(request, f"Ocurrió un error en el servidor: {e}")
            
#         finally:
#             if client:
#                 client.close()
    
#     # Si es GET o POST fallido, renderiza la página de login
#     if client: client.close()
#     return render(request, 'web_skill_app/login.html')

# def register_view(request):
#     client, users_collection = get_db_collection()
    
#     # 1. Si ya está logueado, redirigir
#     if 'user_id' in request.session:
#         if client: client.close()
#         return redirect('dashboard')
        
#     # 2. Verificar si users_collection es None
#     if users_collection is None:
#         messages.error(request, "Error de conexión a la base de datos. Por favor, revisa tu conexión MongoDB.")
#         if client: client.close()
#         return render(request, 'web_skill_app/login.html')
    
#     if request.method == 'POST':
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         if not all([first_name, last_name, email, password]):
#             messages.error(request, "Todos los campos son obligatorios.")
#         else:
#             try:
#                 # 3. Verificar si el correo ya existe
#                 if users_collection.find_one({'email': email.lower()}):
#                     messages.error(request, "Este correo ya está registrado.")
#                 else:
#                     # 4. Hashear y guardar
#                     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    
#                     user_doc = {
#                         'first_name': first_name,
#                         'last_name': last_name,
#                         'email': email.lower(),
#                         'password': hashed_password, 
#                         'created_at': datetime.datetime.utcnow(),
#                         'conversation_history_criker': [],
#                         'conversation_history_knowledge': [],
#                     }
                    
#                     result = users_collection.insert_one(user_doc)
                    
#                     # 5. Iniciar sesión automáticamente
#                     user_data = users_collection.find_one({'_id': result.inserted_id})
#                     login_user_session(request, user_data)
                    
#                     messages.success(request, "Registro exitoso. ¡Bienvenido!")
#                     return redirect('dashboard') 
#             except Exception as e:
#                 messages.error(request, f"Ocurrió un error al registrar el usuario: {e}")
#             finally:
#                 if client:
#                     client.close()
        
#         # Si hay errores, redirigir de vuelta al login
#         if client: client.close()
#         return render(request, 'web_skill_app/login.html')

#     # Si es GET, redirigir al login
#     if client: client.close()
#     return redirect('login_page')


# def logout_view(request):
#     if request.method == 'POST':
#         logout_user_session(request)
#         messages.success(request, "Sesión cerrada correctamente.")
#     return redirect('login_page')

# @login_required
# def dashboard_view(request):
#     context = {'user': request.user} 
#     return render(request, 'web_skill_app/dashboard.html', context)


# # --- Vistas de Agentes (Asegurando compatibilidad con la nueva estructura) ---

# @login_required 
# def pizarrabot_view(request): 
#     user = request.user
#     user_id_str = user['user_id']
    
#     if request.method == 'POST':
#         user_message = request.POST.get('user_message')
#         if user_message:
#             try:
#                 get_agent_response_criker(user_id_str, user_message) 
#                 messages.success(request, "Mensaje enviado correctamente")
#             except Exception as e:
#                 messages.error(request, f"Hubo un problema al procesar tu mensaje: {e}")
            
#         return redirect('pizarrabot') 

#     try:
#         conversation_history = get_conversation_history_criker(user_id_str)
#     except Exception as e:
#         conversation_history = []
#         messages.error(request, f"No se pudo cargar el historial de conversaciones: {e}")

#     return render(
#         request, 
#         'web_skill_app/pizarrabot.html', 
#         {'conversation_history': conversation_history, 'user': user}
#     )

# @login_required
# def knowledge_view(request):
#     user = request.user
#     user_id_str = user['user_id']
    
#     if request.method == 'POST':
#         user_message = request.POST.get('user_message')
#         if not user_message:
#             messages.warning(request, "El mensaje no puede estar vacío.")
#             return redirect('chat_knowledge')
        
#         try:
#             get_agent_response_knowledge(user_id_str, user_message) 
#             messages.success(request, "Consulta enviada correctamente")
            
#         except Exception as e:
#             messages.error(request, f"Hubo un problema al procesar tu mensaje: {e}")
            
#         return redirect('chat_knowledge')

#     try:
#         conversation_history = get_conversation_history_knowledge(user_id_str)
#     except Exception as e:
#         conversation_history = []
#         messages.error(request, "No se pudo cargar el historial de consultas Knowledge.")

#     return render(
#         request, 
#         'web_skill_app/knowledge.html', 
#         {
#             'user': user,
#             'conversation_history': conversation_history,
#         }
#     )

