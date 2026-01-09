# web_skill_app/core_views.py

# --- 1. IMPORTS (Mantenemos los que ya tenías) ---
import speech_recognition as sr
from pydub import AudioSegment
import io
import traceback 
# --- IMPORTS NECESARIOS AL INICIO DEL ARCHIVO ---
from .db import get_db_collection
from bson.objectid import ObjectId

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import get_template
import re 
from django.http import HttpResponse
import time
import uuid
import logging  # Importante para el logger
import requests
import json
import os       # Necesario para verificar rutas
import shutil   # Necesario para buscar ffmpeg en el sistema



# Importar el decorador de autenticación
from .auth_helpers import login_required

from .services import (
    get_conversation_history_knowledge, 
    get_agent_response_knowledge,
    get_conversation_history_coach,
    get_agent_response_coach,
    get_conversation_history_criker,
    get_agent_response_criker
)
from .db import get_db_collection
from bson.objectid import ObjectId

# --- 2. DEFINIR LOGGER (ESTO DEBE IR ANTES DE USARLO) ---
logger = logging.getLogger(__name__)

# --- 3. CONFIGURACIÓN DE FFMPEG (Ahora sí podemos usar logger) ---
ffmpeg_path_system = shutil.which("ffmpeg")
ffprobe_path_system = shutil.which("ffprobe")

if ffmpeg_path_system:
    # Si el sistema lo encuentra automáticamente (Linux/Cloud o PC bien configurada)
    AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
    AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
else:
    # FALLBACK: Ruta manual para tu PC local si no está en el PATH
    # Asegúrate de que esta ruta sea real en TU computadora
    local_ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
    local_ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
    
    if os.path.exists(local_ffmpeg):
        AudioSegment.converter = local_ffmpeg
        AudioSegment.ffprobe = local_ffprobe
    else:
        # Ahora sí funcionará este warning porque logger ya existe
        logger.warning("⚠️ FFMPEG no encontrado ni en el sistema ni en C:\\ffmpeg\\bin. La transcripción de audio fallará.")


# --- VISTAS DE PÁGINAS ESTÁTICAS ---

# --- VISTAS DE PÁGINAS ESTÁTICAS (sin cambios) ---
def transcribe_audio(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES.get('audio_data')
            if not audio_file:
                return JsonResponse({'status': 'error', 'message': 'No audio file received'}, status=400)

            # Conversión usando pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_file.read()))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            # Reconocimiento
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                # --- AGREGAR ESTO: Calibrar ruido de fondo ---
                # Ayuda a que Google ignore el siseo o ruido del ambiente
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio_data = recognizer.record(source)
                
                try:
                    text = recognizer.recognize_google(audio_data, language="es-ES")
                    return JsonResponse({'status': 'ok', 'text': text})
                
                # Manejo específico si Google no entiende nada (audio vacío o puro ruido)
                except sr.UnknownValueError:
                    print("--- Google Speech no detectó palabras claras ---")
                    return JsonResponse({
                        'status': 'error', 
                        'text': '', 
                        'message': 'No se detectó voz clara. Intenta hablar más fuerte.'
                    }, status=200)

        except Exception as e:
            print(f"--- Fallo en transcripción: {str(e)} ---")
            return JsonResponse({
                'status': 'error', 
                'text': '', 
                'message': f'Error interno: {str(e)}'
            }, status=200)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def home(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/index.html', context)

def pensamiento_critico(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/pensamiento-critico.html', context)

def comunicacion(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/comunicacion.html', context)

def creatividad(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/creatividad.html', context)

def colaboracion(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/colaboracion.html', context)

def presentacion(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'web_skill_app/presentacion.html', context)

def skill(request):
    context = {'timestamp': int(time.time())}
    return render(request, "web_skill_app/skill.html", context)



@login_required # <-- 1. AÑADE EL DECORADOR
def preguntas(request):
    """Vista para el chat de preguntas/encuesta"""
    session_id = str(uuid.uuid4())

# 2. OBTÉN EL USER_ID DESDE EL USUARIO LOGUEADO
    user_id_str = request.user.get('user_id')

    context = {
        'timestamp': int(time.time()),
        'session_id': session_id,
        'user_id_str': user_id_str # <-- 3. PÁSALO AL CONTEXTO
    }
    return render(request, "web_skill_app/chat.html", context)


# --- VISTA DEL DASHBOARD (sin cambios) ---
@login_required
def dashboard_view(request):
    context = {'user': request.user} 
    return render(request, 'web_skill_app/dashboard.html', context)

@login_required # <-- Añadido si la página requiere login
def skill(request):
    """Renders the skill.html template."""
    context = {'timestamp': int(time.time()), 'user': request.user} # Pass user if needed
    return render(request, "web_skill_app/skill.html", context)


# --- VISTA PRINCIPAL DEL CHAT (KNOWLEDGE) ---
@login_required
def knowledge_view(request):
    """
    Maneja tanto la carga inicial de la página (GET)
    como las peticiones de chat asíncronas (POST).
    """
    
    user = request.user
    user_id_str = user['user_id'] 
    user_first_name = user.get('first_name', 'Usuario')

    # --- LÓGICA PARA POST (AJAX) - CORREGIDA ---
    if request.method == 'POST':
        try:
            # Validar que el content-type sea JSON
            if request.content_type != 'application/json':
                logger.error(f"Content-Type incorrecto: {request.content_type}")
                return HttpResponseBadRequest(json.dumps({
                    'error': 'Content-Type debe ser application/json'
                }), content_type='application/json')
            
            # Validar que request.body no esté vacío
            if not request.body:
                logger.error("request.body está vacío")
                return HttpResponseBadRequest(json.dumps({
                    'error': 'Body vacío'
                }), content_type='application/json')
            
            # Intentar parsear el JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as je:
                logger.error(f"Error al parsear JSON: {je}. Body recibido: {request.body}")
                return HttpResponseBadRequest(json.dumps({
                    'error': f'JSON inválido: {str(je)}'
                }), content_type='application/json')
            
            # Extraer el mensaje del usuario
            user_message = data.get('user_message')

            if not user_message or not user_message.strip():
                return HttpResponseBadRequest(json.dumps({
                    'error': 'Mensaje vacío.'
                }), content_type='application/json')

            # Llamar al servicio (que guarda en webSkill.users)
            agent_response = get_agent_response_knowledge(user_id_str, user_message.strip())
            
            # Devolver la respuesta como JSON
            return JsonResponse({'agent_response': agent_response, 'status': 'ok'})

        except Exception as e:
            logger.exception(f"Error en POST de knowledge_view para user {user_id_str}")
            return JsonResponse({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=500)

    # --- LÓGICA DE GET (Carga inicial de la página) ---
    # (Esta parte es la misma que antes)
    
    conversation_history = []
    completed_lessons = [] # Lista vacía por defecto

    try:
        # 1. Recuperar historial
        conversation_history = get_conversation_history_knowledge(user_id_str)
        
        # 2. Si es la primera vez, enviar saludo automático
        if not conversation_history:
            logger.info(f"Historial vacío para {user_id_str}. Enviando saludo.")
            welcome_message = (
                f"Hola {user_first_name}, bienvenido a la fase de inducción y conocimientos. "
                "¿En qué puedo ayudarte hoy?"
            )
            get_agent_response_knowledge(user_id_str, welcome_message)
            
            # Recargar el historial después del saludo
            conversation_history = get_conversation_history_knowledge(user_id_str)
        
        # 3. RECUPERAR LECCIONES COMPLETADAS DE MONGODB (NUEVO)
        users_collection = get_db_collection()
        user_doc = users_collection.find_one({'_id': ObjectId(user_id_str)})
        if user_doc:
            completed_lessons = user_doc.get('lecciones_completadas', [])
            
    except Exception as e:
        logger.error(f"Error en GET de knowledge_view para {user_id_str}: {e}")
        messages.error(request, f"Error al cargar historial: {str(e)}")
        conversation_history = []
    
    # 3. Renderizar la plantilla
    return render(
        request, 
        'web_skill_app/knowledge.html', 
        {
            'user': user,
            'conversation_history': conversation_history,
            # Convertimos a JSON string para que JS lo lea fácil
            'completed_lessons_json': json.dumps(completed_lessons),
        }
    )
    
    # --- ¡NUEVA VISTA PARA EL CHAT DE SKILL (PIZARRA)! ---
@login_required
def skill_chat_api(request):
    """
    API endpoint ONLY for handling POST requests (AJAX) from skill.html.
    It expects a JSON body with 'user_id', 'message', and 'agent_target'.
    """
    if request.method != 'POST':
        logger.warning("Received non-POST request on skill_chat_api")
        return HttpResponseBadRequest(json.dumps({'error': 'Only POST requests allowed.'}))

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id') # Assuming user_id is sent from frontend JS
        user_message = data.get('message')
        agent_target = data.get('agent_target') # Expected: 'coach' or 'criker'

        # Validate input
        if not all([user_id, user_message, agent_target]):
            return HttpResponseBadRequest(json.dumps({'error': 'Missing user_id, message, or agent_target.'}))
        if agent_target not in ['coach', 'criker']:
             return HttpResponseBadRequest(json.dumps({'error': 'Invalid agent_target specified.'}))

        response_content = None
        response_type = "chat" # Default to chat

        # --- Call the appropriate service based on agent_target ---
        if agent_target == 'coach':
            logger.info(f"Routing message from {user_id} to Coach agent.")
            response_content = get_agent_response_coach(user_id, user_message.strip())
            # Coach always returns text

        elif agent_target == 'criker':
            logger.info(f"Routing message from {user_id} to Criker agent.")
            response_content = get_agent_response_criker(user_id, user_message.strip())
            
            # --- Check if Criker returned JSON (dict) or text (str) ---
            if isinstance(response_content, dict):
                response_type = "CASO_USO"
                logger.info(f"Received CASO_USO JSON from Criker for {user_id}")
            elif isinstance(response_content, str):
                response_type = "chat"
                logger.info(f"Received CHAT text from Criker for {user_id}")
            else:
                 # Should not happen if services.py is correct, but handle defensively
                 raise TypeError("Unexpected response type received from Criker service.")

        # --- Format the JSON response for the frontend ---
        if response_type == "chat":
            json_response_data = {
                "type": "chat",
                "agent": agent_target, # 'coach' or 'criker'
                "content": response_content # The text string
            }
        elif response_type == "CASO_USO":
            json_response_data = {
                "type": "CASO_USO",
                "agent": "criker", # Only Criker sends this
                "data_caso": response_content # The dictionary itself
            }
        else:
             # Should not be reachable
             raise ValueError("Invalid response_type determined.")

        return JsonResponse(json_response_data, status=200)

    except json.JSONDecodeError:
        logger.error("Error decoding JSON body in skill_chat_api")
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON format.'}))
    except ValueError as ve: # Catch specific errors like invalid user ID
         logger.error(f"Validation error in skill_chat_api: {ve}")
         return HttpResponseBadRequest(json.dumps({'error': str(ve)}))
    except ConnectionError as ce:
        logger.error(f"Database connection error in skill_chat_api: {ce}")
        return JsonResponse({'error': 'Database connection failed.'}, status=503) # Service Unavailable
    except requests.exceptions.RequestException as re:
         logger.error(f"Agent connection error in skill_chat_api: {re}")
         return JsonResponse({'error': 'Failed to connect to the AI agent.'}, status=502) # Bad Gateway
    except Exception as e:
        logger.exception(f"Unexpected error in skill_chat_api for user {data.get('user_id', 'unknown')}") # Log full traceback
        # Be cautious about sending detailed internal errors to the client
        return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)
    
@login_required
def leccion_view(request, leccion_id):
    """
    Renderiza la página de la lección, incrustando el contenido de la lección específica
    en la plantilla base.
    """
    template_name = f"web_skill_app/lecciones/leccion{leccion_id}.html"
    # Simplemente renderizamos la plantilla. Django se encargará de la herencia.
    return render(request, template_name)

# --- NUEVA VISTA PARA GUARDAR EL PROGRESO ---
@login_required
def marcar_leccion_completada(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        leccion_id = data.get('leccion_id')
        user_id_str = request.user.get('user_id')

        if not leccion_id or not user_id_str:
            return JsonResponse({'error': 'Faltan datos'}, status=400)

        users_collection = get_db_collection()
        
        # Usamos $addToSet para que no se dupliquen si el usuario le da click varias veces
        users_collection.update_one(
            {'_id': ObjectId(user_id_str)},
            {'$addToSet': {'lecciones_completadas': leccion_id}}
        )

        return JsonResponse({'status': 'ok', 'leccion_id': leccion_id})

    except Exception as e:
        logger.error(f"Error marcando lección: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
# --- FIN DEL CÓDIGO ---




    