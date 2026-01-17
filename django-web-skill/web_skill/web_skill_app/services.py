# web_skill_app/services.py

import requests
from django.conf import settings
from bson.objectid import ObjectId
import datetime
import re
import logging
import json
import hashlib
from django.core.cache import cache

# --- NUEVA IMPORTACIÓN ---
from .db import get_db_collection

# Configurar un logger
logger = logging.getLogger(__name__)

# --- Helper Functions (Keep as is) ---
def format_timestamp_for_display(timestamp):
    if not timestamp:
        return ""
    try:
        if isinstance(timestamp, datetime.datetime):
            return timestamp.strftime("%H:%M")
        if isinstance(timestamp, str):
            clean_timestamp = re.sub(r'\.\d+', '', timestamp)
            clean_timestamp = clean_timestamp.replace('Z', '').replace('+00:00', '')
            dt = datetime.datetime.fromisoformat(clean_timestamp)
            return dt.strftime("%H:%M")
    except Exception as e:
        logger.warning(f"No se pudo formatear timestamp {timestamp}: {e}")
        return str(timestamp)
    return str(timestamp)

def _get_user_doc(collection, user_id):
    """Helper to get user document safely."""
    if isinstance(user_id, str):
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            logger.error(f"Invalid user_id format: {user_id}")
            raise ValueError("Invalid user ID format.")
    else:
        user_object_id = user_id
        
    user_doc = collection.find_one({'_id': user_object_id})
    if not user_doc:
        logger.error(f"User with ID {user_object_id} not found.")
        raise ValueError("User profile not found.")
    return user_doc, user_object_id

# ===== FUNCIONES PARA KNOWLEDGE (Teoría - Página 'knowledge.html') =====
def get_conversation_history_knowledge(user_id):
    try:
        users_collection = get_db_collection()
        user_doc, _ = _get_user_doc(users_collection, user_id)
        conversation_history = user_doc.get('conversation_history_knowledge', [])
        for message in conversation_history:
            if 'timestamp' in message:
                message['formatted_timestamp'] = format_timestamp_for_display(message['timestamp'])
        return conversation_history
    except (ConnectionError, ValueError) as e:
         logger.error(f"Error getting Knowledge history for {user_id}: {e}")
         return []
    except Exception as e:
        logger.error(f"Unexpected error getting Knowledge history: {e}")
        return []

def get_agent_response_knowledge(user_id, user_message):
    """
    Gets a response from the Knowledge agent.
    INCLUYE PERSONALIZACIÓN POR CARRERA + PROTECCIÓN ANTI-JSON.
    """
    # 1. Recuperamos el documento del usuario
    try:
        users_collection = get_db_collection()
        user_doc, user_object_id = _get_user_doc(users_collection, user_id)
        
        # --- DATOS DEL USUARIO ---
        completed_lessons = user_doc.get('lecciones_completadas', [])
        lista_lecciones = ", ".join(completed_lessons) if completed_lessons else "Ninguna"
        
        # Intentamos recuperar la carrera o profesión
        # Ajusta las claves ('carrera', 'profesion') según como lo guardes en tu registro
        carrera_usuario = user_doc.get('carrera', user_doc.get('profesion', 'Estudiante General'))
        
        # --- ESTRATEGIA: SYSTEM OVERRIDE CON PERSONALIZACIÓN ---
        system_override = (
            f"[SISTEMA: MODO PROFESOR PERSONALIZADO]\n"
            f"DATOS USUARIO: Carrera/Perfil: {carrera_usuario}. Progreso: {lista_lecciones}.\n"
            f"TU ROL: Profesor Teórico Yashay.\n"
            
            f"🎯 INSTRUCCIÓN DE PERSONALIZACIÓN: Explica los conceptos teóricos usando EJEMPLOS BREVES Y ANALOGÍAS relacionadas con su carrera ({carrera_usuario}). "
            f"Por ejemplo, si es 'Ingeniero', usa analogías de sistemas/construcción. Si es 'Médico', usa analogías de diagnóstico.\n"
            
            f"⛔ PROHIBICIÓN ABSOLUTA: Aunque uses ejemplos de su carrera, NO generes 'Casos Prácticos' completos, ni diálogos simulados, ni JSON.\n"
            f"⛔ PROHIBICIÓN: NO uses formato de guion (Personaje A: ...). Mantén formato de prosa explicativa.\n"
            
            f"Si el usuario pide un ejercicio práctico completo, dile: 'Para aplicar esto en un caso práctico simulado, habla con Criker en la sección Skill'.\n"
            f"MENSAJE DEL USUARIO:\n"
            f"--------------------------------------------------\n"
        )
        # --------------------------------------------

    except Exception as e:
        logger.error(f"Error recuperando usuario en knowledge service: {e}")
        system_override = ""
        user_object_id = user_id

    # CONCATENAMOS
    full_message_for_agent = f"{system_override}{user_message}"
    
    # Hash para caché
    message_hash = hashlib.md5(full_message_for_agent.strip().lower().encode()).hexdigest()
    cache_key = f"agent_knowledge_response:{message_hash}"

    cached_response = cache.get(cache_key)
    
    # --- CACHE HIT ---
    if cached_response:
        logger.info(f"Cache HIT for key {cache_key}")
        try:
            conversation_history = user_doc.get('conversation_history_knowledge', [])
            current_time = datetime.datetime.now()
            conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
            conversation_history.append({'role': 'agent', 'message': cached_response, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
            users_collection.update_one({'_id': user_object_id}, {'$set': {'conversation_history_knowledge': conversation_history}})
        except Exception as e:
            logger.error(f"Error updating history cache: {e}")
        return cached_response

    # --- CACHE MISS ---
    logger.info(f"Cache MISS. Calling agent.")
    try:
        conversation_history = user_doc.get('conversation_history_knowledge', [])
        agent_url = settings.AGENT_PROFESOR
        
        if not agent_url:
            raise ValueError("AGENT_PROFESOR URL not configured.")
            
        payload = {'user_id': str(user_object_id), 'message': full_message_for_agent}
        
        # --- PROTECCIÓN Y FILTRADO ---
        try:
            response = requests.post(agent_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=120)
            response.raise_for_status()
            response_data = response.json()
            
            agent_response = response_data.get('response')
            
            # FILTRO DE SEGURIDAD (Por si el agente es muy terco con el JSON)
            if agent_response and ("{" in agent_response and "titulo_caso" in agent_response):
                logger.warning("Agente intentó enviar JSON. Interceptando...")
                agent_response = (
                    f"Entendido. Como {carrera_usuario}, verás que este concepto es fundamental. "
                    "Te lo explico teóricamente: [El agente tuvo un lapsus técnico, pero aquí estoy para explicarte la teoría pura]."
                )

            if 'error' in response_data:
                 logger.error(f"Agente devolvió error interno: {response_data['error']}")
                 agent_response = "Mis circuitos teóricos se han cruzado un momento. ¿Podrías repetirme tu duda?"

        except Exception as agent_err:
            logger.error(f"Fallo conexión Agente: {agent_err}")
            agent_response = "Estoy experimentando una breve interrupción técnica. Intenta de nuevo en unos segundos."
        # -----------------------------------------------

        cache.set(cache_key, agent_response)
        
        current_time = datetime.datetime.now()
        conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
        conversation_history.append({'role': 'agent', 'message': agent_response, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
        
        users_collection.update_one(
            {'_id': user_object_id},
            {'$set': {'conversation_history_knowledge': conversation_history}}
        )
        
        return agent_response

    except Exception as e:
        logger.error(f"Error CRÍTICO services: {e}")
        return "Error de sistema. Contacta soporte."

# ===== FUNCIONES PARA SKILL (Coach de Teoría - Chat Izquierdo en 'skill.html') =====
def get_conversation_history_coach(user_id):
    """Gets Coach conversation history from 'conversation_history_coach' field."""
    try:
        users_collection = get_db_collection()
        user_doc, _ = _get_user_doc(users_collection, user_id)
        conversation_history = user_doc.get('conversation_history_coach', []) 
        for message in conversation_history:
            if 'timestamp' in message:
                message['formatted_timestamp'] = format_timestamp_for_display(message['timestamp'])
        return conversation_history
    except (ConnectionError, ValueError) as e:
         logger.error(f"Error getting Coach history for {user_id}: {e}")
         return [] 
    except Exception as e:
        logger.error(f"Unexpected error getting Coach history: {e}")
        return []

def get_agent_response_coach(user_id, user_message):
    """Sends message to the Coach agent (AGENT_CRIKER_COACH) and saves history."""
    message_hash = hashlib.md5(user_message.strip().lower().encode()).hexdigest()
    cache_key = f"agent_coach_response:{message_hash}"

    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info(f"Cache HIT for key {cache_key}")
        try:
            users_collection = get_db_collection()
            user_doc, user_object_id = _get_user_doc(users_collection, user_id)
            conversation_history = user_doc.get('conversation_history_coach', [])
            
            current_time = datetime.datetime.now()
            conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
            conversation_history.append({'role': 'agent', 'message': cached_response, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
            
            users_collection.update_one(
                {'_id': user_object_id},
                {'$set': {'conversation_history_coach': conversation_history}}
            )
            logger.debug(f"Coach history updated for {user_object_id} with CACHED response.")
        except (ConnectionError, ValueError) as e:
            logger.error(f"Error updating history with cached response for {user_id}: {e}")
        
        return cached_response

    logger.info(f"Cache MISS for key {cache_key}. Calling agent.")
    try:
        users_collection = get_db_collection()
        user_doc, user_object_id = _get_user_doc(users_collection, user_id)
        conversation_history = user_doc.get('conversation_history_coach', []) 

        agent_url = settings.AGENT_CRIKER_COACH 
        if not agent_url:
            raise ValueError("AGENT_CRIKER_COACH URL not configured.")
        
        #parte para que diga que es yashai

        instruccion_yashay = "SYSTEM: Tu identidad AHORA es 'Yashay' (Agente de Teoría). OLVIDA que eres Coach. Eres académico y sabio."
        
        payload = {
            'user_id': str(user_object_id), 
            'message': f"{instruccion_yashay}\n\nPregunta del usuario: {user_message}"
        }
        
        # ------------------------------------------------------------

        response = requests.post(
            agent_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=120
        )
        response.raise_for_status()
        response_data = response.json()
        
        agent_response = response_data.get('response')
        if 'error' in response_data or not agent_response:
             error_msg = response_data.get('error', 'Unknown agent error.')
             raise Exception(f"Agent Error: {error_msg}")

        cache.set(cache_key, agent_response)
        logger.info(f"Saved new response to cache with key {cache_key}")

        current_time = datetime.datetime.now()
        conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
        conversation_history.append({'role': 'agent', 'message': agent_response, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
        
        users_collection.update_one(
            {'_id': user_object_id},
            {'$set': {'conversation_history_coach': conversation_history}}
        )
        logger.debug(f"Coach history updated for {user_object_id}.")
        
        return agent_response

    except (ConnectionError, ValueError, requests.exceptions.RequestException, Exception) as e:
        logger.error(f"Error in get_agent_response_coach for {user_id}: {e}")
        raise e

# ===== FUNCIONES PARA SKILL (Criker de Práctica - Chat Derecho en 'skill.html') =====
def get_conversation_history_criker(user_id):
    """Gets Criker conversation history from 'conversation_history_criker' field."""
    try:
        users_collection = get_db_collection()
        user_doc, _ = _get_user_doc(users_collection, user_id)
        conversation_history = user_doc.get('conversation_history_criker', []) 
        for message in conversation_history:
            if 'timestamp' in message:
                message['formatted_timestamp'] = format_timestamp_for_display(message['timestamp'])
        return conversation_history
    except (ConnectionError, ValueError) as e:
         logger.error(f"Error getting Criker history for {user_id}: {e}")
         return [] 
    except Exception as e:
        logger.error(f"Unexpected error getting Criker history: {e}")
        return []

def get_agent_response_criker(user_id, user_message):
    """
    Sends message to the Criker Skill agent (AGENT_CRIKER_SKILL).
    Caches TEXT responses but not JSON (Tool Call) responses.
    """
    message_hash = hashlib.md5(user_message.strip().lower().encode()).hexdigest()
    cache_key = f"agent_criker_response:{message_hash}"

    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info(f"Cache HIT for key {cache_key}")
        try:
            users_collection = get_db_collection()
            user_doc, user_object_id = _get_user_doc(users_collection, user_id)
            conversation_history = user_doc.get('conversation_history_criker', [])
            
            current_time = datetime.datetime.now()
            conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
            conversation_history.append({'role': 'agent', 'message': cached_response, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
            
            users_collection.update_one(
                {'_id': user_object_id},
                {'$set': {'conversation_history_criker': conversation_history}}
            )
            logger.debug(f"Criker history updated for {user_object_id} with CACHED response.")
        except (ConnectionError, ValueError) as e:
            logger.error(f"Error updating history with cached response for {user_id}: {e}")
        
        return cached_response

    logger.info(f"Cache MISS for key {cache_key}. Calling agent.")
    try:
        users_collection = get_db_collection()
        user_doc, user_object_id = _get_user_doc(users_collection, user_id)
        conversation_history = user_doc.get('conversation_history_criker', []) 

        agent_url = settings.AGENT_CRIKER_SKILL 
        if not agent_url:
            raise ValueError("AGENT_CRIKER_SKILL URL not configured.")
            
        payload = {'user_id': str(user_object_id), 'message': user_message}
        
        response = requests.post(
            agent_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=180
        )
        response.raise_for_status()
        response_data = response.json()
        
        agent_response_content = None
        is_tool_call = False

        if 'tool_calls' in response_data and response_data['tool_calls'] and isinstance(response_data['tool_calls'], list):
             tool_call_args = response_data['tool_calls'][0].get('args')
             if isinstance(tool_call_args, dict):
                 agent_response_content = tool_call_args
                 is_tool_call = True
        
        if not is_tool_call:
            agent_text_response = response_data.get('response')
            if isinstance(agent_text_response, str) and agent_text_response.strip():
                agent_response_content = agent_text_response
            elif 'error' in response_data:
                 error_msg = response_data.get('error', 'Unknown agent error.')
                 raise Exception(f"Agent Error: {error_msg}")
            else:
                logger.warning(f"Unexpected response structure from Criker for {user_id}: {response_data}")
                agent_response_content = "Sorry, I received an unexpected response."

        if not is_tool_call and isinstance(agent_response_content, str):
            cache.set(cache_key, agent_response_content)
            logger.info(f"Saved new TEXT response to cache with key {cache_key}")
            
            current_time = datetime.datetime.now()
            conversation_history.append({'role': 'user', 'message': user_message, 'timestamp': current_time.isoformat()})
            conversation_history.append({'role': 'agent', 'message': agent_response_content, 'timestamp': (current_time + datetime.timedelta(seconds=1)).isoformat()})
            
            users_collection.update_one(
                {'_id': user_object_id},
                {'$set': {'conversation_history_criker': conversation_history}}
            )
            logger.debug(f"Criker TEXT history updated for {user_object_id}.")
        
        return agent_response_content

    except (ConnectionError, ValueError, requests.exceptions.RequestException, Exception) as e:
        logger.error(f"Error in get_agent_response_criker for {user_id}: {e}")
        raise e


# ===== NUEVAS FUNCIONES PARA AGENTE SCOUTER (Evaluación de Pensamiento Crítico) =====

def get_agent_response_scouter(user_id, user_message):
    """
    Sends message to Scouter agent and handles dashboard creation.
    Returns: {
        'response': str (texto conversacional),
        'dashboard_id': str or None (ID del dashboard si se completó evaluación)
    }
    """
    try:
        agent_url = settings.AGENT_SCOUTER_URL
        if not agent_url:
            raise ValueError("AGENT_SCOUTER_URL not configured in settings.")
        
        # Llamar al agente
        payload = {'user_id': user_id, 'message': user_message}
        response = requests.post(
            agent_url, 
            json=payload, 
            headers={'Content-Type': 'application/json'}, 
            timeout=120
        )
        response.raise_for_status()
        response_data = response.json()
        
        # Extraer respuesta y dashboard_id
        agent_response = response_data.get('response', '')
        dashboard_id = response_data.get('dashboard_id')
        
        if 'error' in response_data:
            error_msg = response_data.get('error', 'Unknown agent error.')
            raise Exception(f"Agent Error: {error_msg}")
        
        # Si se generó un dashboard, guardarlo en el perfil del usuario
        if dashboard_id:
            try:
                users_collection = get_db_collection()
                user_doc, user_object_id = _get_user_doc(users_collection, user_id)
                
                # Agregar dashboard_id al array de historial del usuario
                users_collection.update_one(
                    {'_id': user_object_id},
                    {'$push': {'survey_history': dashboard_id}}
                )
                logger.info(f"Dashboard {dashboard_id} agregado al historial de {user_id}")
            except Exception as e:
                logger.error(f"Error guardando dashboard_id en perfil de usuario: {e}")
        
        return {
            'response': agent_response,
            'dashboard_id': dashboard_id
        }
        
    except (ValueError, requests.exceptions.RequestException, Exception) as e:
        logger.error(f"Error in get_agent_response_scouter for {user_id}: {e}")
        raise e


def get_user_survey_history(user_id):
    """
    Returns list of survey dashboards for sidebar from MongoDB.
    CORREGIDO: Devuelve claves compatibles con ambos templates (Admin y Usuario).
    """
    try:
        from .db import mongo_client
        from django.conf import settings
        import datetime
        
        db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
        survey_collection = db['survey_results']
        
        # Búsqueda híbrida (String y ObjectId) para asegurar que encuentre los datos
        criteria = []
        criteria.append({'user_id': str(user_id)}) 
        try:
            criteria.append({'user_id': ObjectId(str(user_id))})
        except:
            pass
            
        surveys = survey_collection.find(
            {'$or': criteria}
        ).sort('timestamp', -1)
        
        historial = []
        for doc in surveys:
            try:
                # Formatear timestamp
                timestamp_str = doc.get('timestamp', '')
                try:
                    if 'T' in timestamp_str:
                        dt = datetime.datetime.fromisoformat(timestamp_str.replace('Z', ''))
                    else:
                        dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = dt.strftime('%d %b %Y - %H:%M')
                except:
                    formatted_date = timestamp_str
                
                # Extraer valores seguros
                nivel_val = doc.get('nivel_evaluado', 'N/A')
                promedio_val = doc.get('promedio_global', 0)
                if isinstance(promedio_val, float):
                    promedio_val = int(promedio_val) # Convertir a entero para visualización limpia

                historial.append({
                    'id': str(doc['_id']), 
                    'dashboard_id': str(doc['_id']),
                    'timestamp': formatted_date,
                    
                    # --- AQUÍ ESTÁ LA SOLUCIÓN MÁGICA ---
                    # Enviamos con AMBOS nombres para que funcione en todos tus HTMLs
                    'nivel': nivel_val,              # Para sidebar_historial.html
                    'nivel_evaluado': nivel_val,     # Para admin_user_evaluations.html
                    
                    'promedio': promedio_val,        # Para sidebar_historial.html
                    'promedio_global': promedio_val, # Para admin_user_evaluations.html
                    # ------------------------------------
                    
                    'contexto': doc.get('contexto_usuario', ''),         # Para sidebar
                    'contexto_usuario': doc.get('contexto_usuario', '')  # Para admin
                })
            except Exception as e:
                logger.warning(f"Error procesando survey {doc.get('_id')}: {e}")
                continue
        
        return historial
        
    except Exception as e:
        logger.error(f"Error getting survey history for {user_id}: {e}")
        return []