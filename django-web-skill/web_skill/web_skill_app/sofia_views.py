# En: web_skill_app/sofia_views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import requests # ¡Recuerda instalarlo! pip install requests

# --- Configuración ---
# Coloca aquí la URL real de tu agente Sofía desplegado
SOFIA_AGENT_URL = "httpsIA://URL-DE-TU-AGENTE.com/api/ask" 
# ---------------------


@require_POST  # Nos aseguramos que esta vista solo acepte peticiones POST
def ask_sofia(request):
    """
    API interna para que el chat flotante hable con el agente externo.
    Espera un JSON: {"message": "hola"}
    Devuelve un JSON: {"response": "hola, soy sofía"}
    """
    
    # 1. Obtener el ID de Sesión del usuario (para anónimos)
    # Esto nos permite mantener el historial de la conversación con el agente.
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    # 2. Leer el mensaje del usuario desde el body del request
    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        if not user_message:
            return JsonResponse({'error': 'No se recibió ningún mensaje'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    # 3. Preparar y enviar la petición a tu agente externo
    try:
        payload = {
            'user_id': session_id,  # Usamos session_id en lugar de un user_id de BD
            'message': user_message
        }
        
        # Hacemos la llamada HTTP a tu agente
        response = requests.post(SOFIA_AGENT_URL, json=payload, timeout=10) # 10 seg de timeout

        # 4. Procesar la respuesta del agente
        if response.status_code == 200:
            agent_data = response.json()
            # Asumimos que tu agente devuelve un JSON con una clave "response"
            agent_response = agent_data.get('response', 'Lo siento, no pude procesar eso.')
            
            # 5. Devolver la respuesta al frontend (sofia.js)
            return JsonResponse({'response': agent_response})
        else:
            # El servidor del agente respondió con un error
            return JsonResponse({'error': f'El agente respondió con error {response.status_code}'}, status=502)

    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'El agente tardó mucho en responder.'}, status=504)
    except requests.exceptions.RequestException as e:
        # Error de conexión (ej: no se pudo conectar a la URL del agente)
        return JsonResponse({'error': f'Error de conexión con el agente.'}, status=503)
    except Exception as e:
        # Cualquier otro error inesperado
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)