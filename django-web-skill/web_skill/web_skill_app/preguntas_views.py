# web_skill_app/views/preguntas_views.py
import logging
import uuid
import re
import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random

logger = logging.getLogger(__name__)

# ============================================ 
# CONFIGURACIÓN
# ============================================ 


# Keywords para detectar finalización de encuesta
KEYWORDS_FINALIZACION = [
    "diagnóstico ha concluido",
    "evaluación ha concluido", 
    "perfil nb-x",
    "tu perfil de nivel base",
    "resultados de tu evaluación",
    "evaluación finalizada",
    "perfil de nivel base (nb-x)",
    "hemos llegado al final",
    "completado las 5 preguntas",
    "revelar tu **perfil",
    "felicidades por completar",
    "nb-1:",
    "nb-2:",
    "nb-3:",
    "nb-4:",
    "nb-5:"
]


# ============================================ 
# FUNCIONES AUXILIARES DE CÁLCULO
# ============================================ 

def calcular_pensamiento_estructurado(perfil_nbx):
    """Calcula métricas detalladas de Pensamiento Estructurado desde NB-1, NB-2, NB-3"""
    # CORREGIDO: Normalizar de 0-100 a 0-10 para cálculos internos
    nb1 = perfil_nbx.get('NB-1', 50) / 10.0
    nb2 = perfil_nbx.get('NB-2', 50) / 10.0
    nb3 = perfil_nbx.get('NB-3', 50) / 10.0
    
    return {
        'logica_formal': round(nb1 * 1.11, 1),
        'logica_informal': round(nb1 * 1.03, 1),
        'razonamiento_deductivo': round(nb3 * 1.0, 1),
        'razonamiento_inductivo': round(nb3 * 0.94, 1),
        'argumentos_validos': round(nb2 * 1.09, 1),
        'argumentos_solidos': round(nb2 * 1.0, 1),
        'falacias_detectadas': int(nb2 * 10),
        'falacias_corregidas': int(nb2 * 10 * 0.83)
    }

def calcular_language_skills(perfil_nbx):
    """Calcula métricas de Language Skills desde NB-4"""
    # CORREGIDO: Normalizar de 0-100 a 0-10 para cálculos internos
    nb4 = perfil_nbx.get('NB-4', 50) / 10.0
    
    return {
        'vocabulario': round(nb4 * 1.07, 1),
        'gramatica': round(nb4 * 1.14, 1),
        'coherencia': round(nb4 * 1.0, 1),
        'claridad': round(nb4 * 1.21, 1),
        'precision': round(nb4 * 1.11, 1)
    }

def calcular_argumentation(perfil_nbx):
    """Calcula métricas de Argumentación desde varios NB"""
    # CORREGIDO: Normalizar de 0-100 a 0-10 para cálculos internos
    nb1 = perfil_nbx.get('NB-1', 50) / 10.0
    nb2 = perfil_nbx.get('NB-2', 50) / 10.0
    nb3 = perfil_nbx.get('NB-3', 50) / 10.0
    nb4 = perfil_nbx.get('NB-4', 50) / 10.0
    nb5 = perfil_nbx.get('NB-5', 50) / 10.0
    
    return {
        'estructura': round((nb1 + nb3) / 2, 1),
        'evidencia': round(nb2 * 0.97, 1),
        'contra_argumentos': round((nb2 + nb5) / 2 * 0.93, 1),
        'conclusiones': round(nb3 * 1.07, 1),
        'persuasion': round((nb4 + nb5) / 2, 1)
    }

def generar_historial_simulado(perfil_nbx, nivel, timestamp):
    """Genera historial simulado de 3 evaluaciones para mostrar evolución"""
    historial = []
    
    # Evaluación hace 60 días (más baja)
    fecha_1 = timestamp - timedelta(days=60)
    perfil_1 = {
        # CORREGIDO: Ajustar valores a escala 0-100
        f'NB-{i}': max(10, perfil_nbx.get(f'NB-{i}', 50) - random.randint(10, 20))
        for i in range(1, 6)
    }
    historial.append({
        'fecha': fecha_1.strftime('%Y-%m-%d'),
        'perfil': list(perfil_1.values()),
        'nivel': 'Básico' if nivel != 'Básico' else 'Básico',
        'promedio': round(sum(perfil_1.values()) / 5, 1),
        'duracion': random.randint(18, 25)
    })
    
    # Evaluación hace 30 días (intermedia)
    fecha_2 = timestamp - timedelta(days=30)
    perfil_2 = {
        # CORREGIDO: Ajustar valores a escala 0-100
        f'NB-{i}': max(perfil_1[f'NB-{i}'], perfil_nbx.get(f'NB-{i}', 50) - random.randint(0, 10))
        for i in range(1, 6)
    }
    historial.append({
        'fecha': fecha_2.strftime('%Y-%m-%d'),
        'perfil': list(perfil_2.values()),
        'nivel': 'Intermedio' if nivel == 'Experto' else nivel,
        'promedio': round(sum(perfil_2.values()) / 5, 1),
        'duracion': random.randint(35, 42)
    })
    
    # Evaluación actual
    historial.append({
        'fecha': timestamp.strftime('%Y-%m-%d'),
        'perfil': list(perfil_nbx.values()),
        'nivel': nivel,
        'promedio': round(sum(perfil_nbx.values()) / 5, 1),
        'duracion': random.randint(38, 45)
    })
    
    return historial

def calcular_logros(perfil_nbx, promedio_global):
    """Calcula logros desbloqueados basados en el perfil"""
    logros = [
        {'nombre': '🎯 Diagnóstico Inicial', 'descripcion': 'Completar tu primer test de Scouter', 'desbloqueado': True},
        {'nombre': '📊 Perfil Completo', 'descripcion': 'Obtener tu perfil NB-X completo', 'desbloqueado': True},
        {'nombre': '🔄 Evaluación Recurrente', 'descripcion': 'Realizar 3 diagnósticos', 'desbloqueado': True},
        {'nombre': '⚡ Diagnóstico Rápido', 'descripcion': 'Completar un test en menos de 20 minutos', 'desbloqueado': True},
        # CORREGIDO: Ajustar descripciones a la lógica 0-100
        {'nombre': '🧠 Pensador Analítico', 'descripcion': 'Obtener 80+ en NB-1 (Análisis)', 'desbloqueado': perfil_nbx.get('NB-1', 0) >= 80},
        {'nombre': '🎓 Evaluador Experto', 'descripcion': 'Obtener 80+ en NB-2 (Evaluación)', 'desbloqueado': perfil_nbx.get('NB-2', 0) >= 80},
        {'nombre': '💡 Maestro de Inferencia', 'descripcion': 'Obtener 80+ en NB-3 (Inferencia)', 'desbloqueado': perfil_nbx.get('NB-3', 0) >= 80},
        {'nombre': '🗣️ Comunicador Excepcional', 'descripcion': 'Obtener 80+ en NB-4 (Explicación)', 'desbloqueado': perfil_nbx.get('NB-4', 0) >= 80},
        {'nombre': '🔀 Mente Flexible', 'descripcion': 'Obtener 80+ en NB-5 (Flexibilidad)', 'desbloqueado': perfil_nbx.get('NB-5', 0) >= 80},
        {'nombre': '💯 Maestro del PC', 'descripcion': 'Promedio global de 85+', 'desbloqueado': promedio_global >= 85}
    ]
    return logros

def extraer_resultados_nbx(response_text):
    """Extrae las puntuaciones NB-X del texto de respuesta del agente"""
    
    perfil = {}
    
    # Buscar en formato tabla markdown: | NB-1: Análisis | 45.0 |
    lines = response_text.split('\n')
    for line in lines:
        # Buscar líneas que contengan NB-X y números
        if 'nb-' in line.lower() and '|' in line:
            # Limpiar la línea
            parts = [p.strip() for p in line.split('|')]
            
            for i, part in enumerate(parts):
                # Buscar NB-X en esta parte
                nb_match = re.search(r'nb-?(\d+)', part, re.IGNORECASE)
                if nb_match:
                    num = nb_match.group(1)
                    # Buscar número en las siguientes partes
                    for next_part in parts[i+1:]:
                        score_match = re.search(r'(\d+(?:\.\d+)?)', next_part)
                        if score_match:
                            score_val = float(score_match.group(1))
                            # CORREGIDO: Se elimina la división. Se guarda el valor 0-100
                            perfil[f'NB-{num}'] = round(score_val, 1)
                            break
    
    # Fallback: buscar patrón simple NB-X: 45
    if not perfil or len(perfil) < 5:
        simple_matches = re.findall(r'nb-?(\d+)[:\s]+(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
        for num, score in simple_matches:
            if f'NB-{num}' not in perfil:
                score_val = float(score)
                # CORREGIDO: Se elimina la división por 10
                perfil[f'NB-{num}'] = round(score_val, 1)
    
    # Detectar nivel
    nivel = 'Intermedio'
    texto_lower = response_text.lower()
    if 'nivel básico' in texto_lower or 'básico' in texto_lower:
        nivel = 'Básico'
    elif 'nivel experto' in texto_lower or 'experto' in texto_lower:
        nivel = 'Experto'
    
    return perfil, nivel

def calcular_fortaleza_oportunidad(perfil_nbx):
    """Identifica la fortaleza y área de oportunidad"""
    nombres_pilares = {
        'NB-1': 'NB-1: Análisis',
        'NB-2': 'NB-2: Evaluación',
        'NB-3': 'NB-3: Inferencia',
        'NB-4': 'NB-4: Explicación',
        'NB-5': 'NB-5: Flexibilidad Cognitiva'
    }
    
    # Esto funciona igual con 0-10 o 0-100
    max_key = max(perfil_nbx, key=perfil_nbx.get)
    min_key = min(perfil_nbx, key=perfil_nbx.get)
    
    return nombres_pilares[max_key], nombres_pilares[min_key]


# ============================================ 
# VISTAS
# ============================================ 

@require_http_methods(["GET"])
def inyectar_datos_prueba(request):
    """Injects sample survey data into the cache for testing."""
    session_id = "test-session-123"
    # CORREGIDO: Valores de prueba en escala 0-100
    perfil_nbx = {
        'NB-1': 70,
        'NB-2': 50,
        'NB-3': 80,
        'NB-4': 60,
        'NB-5': 90,
    }
    nivel = 'Intermedio'
    timestamp = datetime.now()
    # El promedio ahora será 0-100 (ej. 70.0)
    promedio_global = round(sum(perfil_nbx.values()) / len(perfil_nbx), 1)
    fortaleza, oportunidad = calcular_fortaleza_oportunidad(perfil_nbx)

    resultados_completos = {
        'perfil_nbx': perfil_nbx,
        'nivel_evaluado': nivel,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'promedio_global': promedio_global,
        'fortaleza': fortaleza,
        'oportunidad': oportunidad,
        # Estas funciones ahora reciben 0-100 y lo manejan
        'pensamiento_estructurado': calcular_pensamiento_estructurado(perfil_nbx),
        'language_skills': calcular_language_skills(perfil_nbx),
        'argumentation': calcular_argumentation(perfil_nbx),
        'historial': generar_historial_simulado(perfil_nbx, nivel, timestamp),
        'logros': calcular_logros(perfil_nbx, promedio_global)
    }

    cache.set(f'resultados_{session_id}', resultados_completos, timeout=3600)

    dashboard_url = f'/encuesta/dashboard/?session_id={session_id}'
    return JsonResponse({
        'message': 'Datos de prueba inyectados correctamente.',
        'session_id': session_id,
        'dashboard_url': dashboard_url
    })

@require_http_methods(["GET"])
def iniciar_encuesta(request):
    """Renderiza la interfaz de chat y genera session_id único"""
    # Generar session_id único
    session_id = str(uuid.uuid4())
    
    # Inicializar historial vacío en cache
    cache.set(f'historial_{session_id}', [], timeout=3600)
    
    context = {
        'session_id': session_id
    }
    
    return render(request, 'encuesta/chat.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def procesar_mensaje(request):
    """Endpoint AJAX que procesa mensajes del usuario y los envía al agente"""
    try:
        import json
        data = json.loads(request.body)
        
        session_id = data.get('session_id')
        mensaje_usuario = data.get('message', '').strip()
        
        if not session_id or not mensaje_usuario:
            return JsonResponse({
                'error': 'session_id y message son requeridos'
            }, status=400)
        
        # Verificar URL del agente
        if not settings.AGENT_ENCUESTA_URL:
            return JsonResponse({
                'error': 'AGENT_ENCUESTA_URL no configurada',
                'info': 'Por favor configura la URL del agente en settings.py'
            }, status=500)
        
        # Recuperar historial del cache
        historial = cache.get(f'historial_{session_id}', [])
        
        # Hacer POST al agente en Cloud Run
        try:
            agent_response = requests.post(
                settings.AGENT_ENCUESTA_URL,
                json={
                    'user_id': session_id,
                    'message': mensaje_usuario
                },
                timeout=30
            )
            agent_response.raise_for_status()
            respuesta_agente = agent_response.json().get('response', '')
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'error': f'Error al comunicarse con el agente: {str(e)}'
            }, status=500)
        
        # Agregar al historial
        historial.append({'role': 'user', 'message': mensaje_usuario})
        historial.append({'role': 'agent', 'message': respuesta_agente})
        cache.set(f'historial_{session_id}', historial, timeout=3600)
        
        # Detectar si la encuesta finalizó
        finalizado = any(keyword in respuesta_agente.lower() 
                        for keyword in KEYWORDS_FINALIZACION)
        
        response_data = {
            'response': respuesta_agente,
            'finalizado': finalizado
        }
        
        # Si finalizó, extraer y guardar resultados
        if finalizado:
            logger.info(f"Respuesta del agente: {respuesta_agente}")
            # perfil_nbx ahora estará en escala 0-100
            perfil_nbx, nivel = extraer_resultados_nbx(respuesta_agente)
            logger.info(f"Perfil NBX extraído: {perfil_nbx}")
            
            # Si se detectaron resultados, procesarlos
            if perfil_nbx and len(perfil_nbx) == 5: # Asegurarse que el perfil está completo
                timestamp = datetime.now()
                # promedio_global ahora será 0-100
                promedio_global = round(sum(perfil_nbx.values()) / len(perfil_nbx), 1)
                fortaleza, oportunidad = calcular_fortaleza_oportunidad(perfil_nbx)
                
                resultados_completos = {
                    # Datos reales (0-100)
                    'perfil_nbx': perfil_nbx,
                    'nivel_evaluado': nivel,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'promedio_global': promedio_global,
                    'fortaleza': fortaleza,
                    'oportunidad': oportunidad,
                    
                    # Datos calculados (funciones internas manejan 0-100)
                    'pensamiento_estructurado': calcular_pensamiento_estructurado(perfil_nbx),
                    'language_skills': calcular_language_skills(perfil_nbx),
                    'argumentation': calcular_argumentation(perfil_nbx),
                    'historial': generar_historial_simulado(perfil_nbx, nivel, timestamp),
                    'logros': calcular_logros(perfil_nbx, promedio_global)
                }
                
                # Guardar en cache (temporal)
                cache.set(f'resultados_{session_id}', resultados_completos, timeout=3600)
                logger.info(f"Resultados guardados en cache para session_id: {session_id}")
                
                # Guardar en MongoDB Atlas (permanente)
                try:
                    from .db import mongo_client
                    from bson.objectid import ObjectId
                    
                    db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
                    survey_collection = db['survey_results']
                    
                    # Crear documento para MongoDB (todo en 0-100)
                    survey_doc = {
                        '_id': ObjectId(session_id) if len(session_id) == 24 else ObjectId(),
                        'user_id': request.session.get('user_id'),  # Asociar al usuario
                        'session_id': session_id,
                        'timestamp': timestamp.isoformat(),
                        'perfil_nbx': perfil_nbx,
                        'nivel_evaluado': nivel,
                        'promedio_global': promedio_global,
                        'fortaleza': fortaleza,
                        'oportunidad': oportunidad,
                        'contexto_usuario': 'Usuario evaluado',  # Puedes personalizar esto
                        'pensamiento_estructurado': resultados_completos['pensamiento_estructurado'],
                        'language_skills': resultados_completos['language_skills'],
                        'argumentation': resultados_completos['argumentation'],
                        'logros': resultados_completos['logros']
                    }
                    
                    # Insertar en MongoDB
                    result = survey_collection.insert_one(survey_doc)
                    mongo_id = str(result.inserted_id)
                    logger.info(f"Resultados guardados en MongoDB con ID: {mongo_id}")
                    
                    # Actualizar historial del usuario
                    if request.session.get('user_id'):
                        users_collection = db['users']
                        users_collection.update_one(
                            {'_id': ObjectId(request.session.get('user_id'))},
                            {'$push': {'survey_history': mongo_id}}
                        )
                        logger.info(f"Historial actualizado para usuario: {request.session.get('user_id')}")
                    
                    # Usar el MongoDB ID para el redirect
                    response_data['redirect_url'] = f'/encuesta/dashboard/?session_id={mongo_id}'
                    
                except Exception as e:
                    logger.error(f"Error guardando en MongoDB: {e}")
                    # Fallback al session_id original si falla MongoDB
                    response_data['redirect_url'] = f'/encuesta/dashboard/?session_id={session_id}'
            else:
                logger.warning(f"La encuesta finalizó pero no se pudo extraer un perfil NBX completo para session_id: {session_id}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error en procesar_mensaje: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error interno: {str(e)}'
        }, status=500)

#AQUIIIIII!!!!
@require_http_methods(["GET"])
def obtener_resultados(request, session_id):
    """API endpoint para que Streamlit obtenga los resultados del cache"""
    resultados = cache.get(f'resultados_{session_id}')
    
    if not resultados:
        return JsonResponse({
            'error': 'No se encontraron resultados para este session_id'
        }, status=404)
    
    return JsonResponse(resultados)


# Vista del dashboard movida a dashboard_views.py


@csrf_exempt
@require_http_methods(["POST"])
def limpiar_cache(request):
    """Limpia el cache de una sesión (opcional)"""
    import json
    data = json.loads(request.body)
    session_id = data.get('session_id')
    
    if session_id:
        cache.delete(f'historial_{session_id}')
        cache.delete(f'resultados_{session_id}')
        return JsonResponse({'status': 'ok', 'message': 'Cache limpiado'})
    
    return JsonResponse({'error': 'session_id requerido'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def eliminar_dashboard(request):
    """Elimina un dashboard de la BD"""
    try:
        import json
        from bson.objectid import ObjectId
        
        data = json.loads(request.body)
        dashboard_id = data.get('dashboard_id')
        
        if not dashboard_id:
            return JsonResponse({'error': 'dashboard_id requerido'}, status=400)
        
        from .db import mongo_client
        from django.conf import settings
        
        db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
        survey_collection = db['survey_results']
        
        # Obtener user_id antes de eliminar
        dashboard_doc = survey_collection.find_one({'_id': ObjectId(dashboard_id)})
        user_id = dashboard_doc.get('user_id') if dashboard_doc else None
        
        # Eliminar documento
        result = survey_collection.delete_one({'_id': ObjectId(dashboard_id)})
        
        if result.deleted_count > 0:
            # Determinar URL de redirección
            if user_id:
                # Buscar si el usuario tiene más dashboards
                next_dashboard = survey_collection.find_one(
                    {'user_id': user_id},
                    sort=[('timestamp', -1)]
                )
                if next_dashboard:
                    redirect_url = f'/encuesta/dashboard/?dashboard_id={str(next_dashboard["_id"])}'
                else:
                    redirect_url = f'/encuesta/dashboard/?user_id={user_id}'
            else:
                redirect_url = '/chat/'
            
            return JsonResponse({
                'success': True,
                'redirect_url': redirect_url
            })
        else:
            return JsonResponse({'error': 'Dashboard no encontrado'}, status=404)
            
    except Exception as e:
        logger.error(f"Error eliminando dashboard: {e}")
        return JsonResponse({'error': str(e)}, status=500)