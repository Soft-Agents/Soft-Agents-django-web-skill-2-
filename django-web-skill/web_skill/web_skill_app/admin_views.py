# web_skill_app/admin_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .auth_helpers import login_required, admin_required
from .db import get_db_collection
from bson.objectid import ObjectId
import logging

# Importamos las funciones de gráficos y servicios desde tus otros archivos
# Asegúrate de que dashboard_views.py tenga estas funciones disponibles
from .dashboard_views import generar_grafico_radar, generar_grafico_barras
from .services import get_user_survey_history

logger = logging.getLogger(__name__)

@login_required
@admin_required
def admin_dashboard(request):
    """Panel principal del administrador."""
    return render(request, 'web_skill_app/admin/admin_dashboard.html')

@login_required
@admin_required
def admin_users_list(request):
    """Lista todos los usuarios registrados (excluyendo administradores si se desea)."""
    try:
        users_collection = get_db_collection()
        # Buscamos usuarios que NO sean admin (o todos si prefieres)
        # Aquí traemos todos para que puedas ver a cualquiera
        users_cursor = users_collection.find().sort('created_at', -1)
        
        users = []
        for user in users_cursor:
            users.append({
                'id': str(user['_id']),
                'first_name': user.get('first_name', 'N/A'),
                'last_name': user.get('last_name', ''),
                'email': user.get('email', 'N/A'),
                'created_at': user.get('created_at'),
                'is_admin': user.get('is_admin', False)
            })

        context = {
            'users': users,
            'total_users': len(users)
        }
        return render(request, 'web_skill_app/admin/admin_users_list.html', context)

    except Exception as e:
        logger.error(f"Error listando usuarios en admin: {e}")
        messages.error(request, "Error al cargar la lista de usuarios.")
        return redirect('admin_dashboard')

@login_required
@admin_required
def admin_user_evaluations(request, user_id):
    try:
        db = get_db_collection().database
        users_collection = db['users']
        survey_collection = db['survey_results']

        # 1. Obtener usuario (Esto ya funcionaba bien)
        try:
            user_doc = users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            user_doc = users_collection.find_one({'_id': user_id})
            
        if not user_doc:
            messages.error(request, "Usuario no encontrado.")
            return redirect('admin_users_list')

        selected_user = {
            'id': str(user_doc['_id']),
            'first_name': user_doc.get('first_name', ''),
            'last_name': user_doc.get('last_name', ''),
            'email': user_doc.get('email', '')
        }

        # 2. Obtener Historial (Usando la función mejorada del Paso 1)
        historial = get_user_survey_history(user_id)

        # 3. Determinar qué evaluación mostrar
        dashboard_id = request.GET.get('dashboard_id')
        survey_doc = None

        if dashboard_id:
            # Si seleccionaron una específica del historial
            try:
                survey_doc = survey_collection.find_one({'_id': ObjectId(dashboard_id)})
            except:
                survey_doc = survey_collection.find_one({'session_id': dashboard_id})
        elif historial:
            # Si no seleccionaron nada, pero HAY historial, tomar la primera (la más reciente)
            first_id = historial[0]['dashboard_id']
            survey_doc = survey_collection.find_one({'_id': ObjectId(first_id)})
            dashboard_id = first_id

        # 4. Si después de todo NO hay survey_doc, es que el usuario está virgen (sin datos)
        if not survey_doc:
            # --- MODO FALLBACK VISUAL ---
            # Si quieres que se vea algo aunque no haya datos, descomenta esto para probar:
            # context = { 'selected_user': selected_user, 'error': 'Sin datos reales.' } 
            # return render(request, 'web_skill_app/admin/admin_user_evaluations.html', context)
            
            # Lo dejamos limpio indicando el error:
            context = {
                'selected_user': selected_user,
                'historial': [],
                'resultados': None,
                'graficos': {},
                'error': "Este usuario aún no ha realizado ninguna evaluación."
            }
            return render(request, 'web_skill_app/admin/admin_user_evaluations.html', context)

        # 5. Si SÍ hay datos, procesar gráficos (Igual que antes) ...
        resultados = {
            'perfil_nbx': survey_doc.get('perfil_nbx', {}),
            'nivel_evaluado': survey_doc.get('nivel_evaluado', 'N/A'),
            'timestamp': survey_doc.get('timestamp', ''),
            'promedio_global': survey_doc.get('promedio_global', 0),
            'fortaleza': survey_doc.get('fortaleza', 'N/A'),
            'oportunidad': survey_doc.get('oportunidad', 'N/A'),
            'contexto_usuario': survey_doc.get('contexto_usuario', ''),
            'pensamiento_estructurado': survey_doc.get('pensamiento_estructurado', {}),
            'language_skills': survey_doc.get('language_skills', {}),
            'argumentation': survey_doc.get('argumentation', {}),
            'logros': survey_doc.get('logros', [])
        }

        perfil_individual = {
            'nb1': int(resultados['perfil_nbx'].get('NB-1', 0)),
            'nb2': int(resultados['perfil_nbx'].get('NB-2', 0)),
            'nb3': int(resultados['perfil_nbx'].get('NB-3', 0)),
            'nb4': int(resultados['perfil_nbx'].get('NB-4', 0)),
            'nb5': int(resultados['perfil_nbx'].get('NB-5', 0)),
        }

        graficos = {}
        try:
            graficos['radar'] = generar_grafico_radar(resultados['perfil_nbx'])
            graficos['barras'] = generar_grafico_barras(resultados['perfil_nbx'])
        except Exception as e:
            logger.error(f"Error generando gráficos admin: {e}")

        context = {
            'selected_user': selected_user,
            'resultados': resultados,
            'perfil': perfil_individual,
            'graficos': graficos,
            'historial': historial,
            'current_dashboard_id': dashboard_id,
            'dashboard_id': dashboard_id
        }

        return render(request, 'web_skill_app/admin/admin_user_evaluations.html', context)

    except Exception as e:
        logger.error(f"Error fatal en admin view: {e}")
        messages.error(request, "Error interno del servidor")
        return redirect('admin_users_list')