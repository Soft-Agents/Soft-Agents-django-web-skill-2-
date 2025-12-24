# web_skill_app/admin_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
import logging

# Importar decorador de admin
from .auth_helpers import admin_required

# Importar colecciones de MongoDB
from .db import get_db_collection, get_survey_results_collection

# Importar funciones de dashboard
from .dashboard_views import generar_grafico_radar, generar_grafico_barras

logger = logging.getLogger(__name__)


@admin_required
def admin_dashboard_view(request):
    """
    Dashboard principal del administrador.
    Muestra un botón para ver las evaluaciones de los usuarios.
    """
    context = {
        'user': request.user
    }
    return render(request, 'web_skill_app/admin/admin_dashboard.html', context)


@admin_required
def admin_users_list_view(request):
    """
    Lista todos los usuarios registrados en la colección 'users'.
    Cada usuario es un botón clickeable.
    """
    try:
        users_collection = get_db_collection()
        
        # Obtener todos los usuarios
        users = list(users_collection.find({}, {
            '_id': 1,
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'created_at': 1
        }).sort('created_at', -1))
        
        print(f"DEBUG: Encontrados {len(users)} usuarios")  # DEBUG
        
        # Convertir ObjectId a string y cambiar _id por id (Django no permite _id en templates)
        for user in users:
            user['id'] = str(user['_id'])  # Cambiar _id por id
            # Asegurar que first_name y last_name no sean None
            if not user.get('first_name'):
                user['first_name'] = 'Sin nombre'
            if not user.get('last_name'):
                user['last_name'] = ''
        
        context = {
            'user': request.user,
            'users': users,
            'total_users': len(users)
        }
        
        print(f"DEBUG: Context users count: {len(context['users'])}")  # DEBUG
        
        return render(request, 'web_skill_app/admin/admin_users_list.html', context)
        
    except Exception as e:
        logger.error(f"Error al obtener lista de usuarios: {e}")
        messages.error(request, f"Error al cargar la lista de usuarios: {str(e)}")
        print(f"DEBUG ERROR: {e}")  # DEBUG
        return redirect('admin_dashboard')


@admin_required
def admin_user_evaluations_view(request, user_id):
    """
    Muestra el dashboard completo de evaluaciones de un usuario específico.
    Idéntico a dashboard_matplotlib.html pero para administradores.
    """
    try:
        users_collection = get_db_collection()
        survey_results_collection = get_survey_results_collection()
        
        # Obtener información del usuario
        from bson.objectid import ObjectId
        try:
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            # Si falla con ObjectId, intentar como string
            user_data = users_collection.find_one({'_id': user_id})
        
        if not user_data:
            messages.error(request, "Usuario no encontrado.")
            return redirect('admin_users_list')
        
        # Obtener el dashboard_id específico si se proporciona
        dashboard_id = request.GET.get('dashboard_id')
        
        # Obtener todas las evaluaciones del usuario para el historial
        evaluations = list(survey_results_collection.find({'user_id': user_id}).sort('timestamp', -1))
        
        # Preparar historial para el sidebar
        historial = []
        for eval in evaluations:
            historial.append({
                'dashboard_id': str(eval['_id']),
                'timestamp': eval.get('timestamp', ''),
                'nivel_evaluado': eval.get('nivel_evaluado', 'Básico'),
                'promedio_global': eval.get('promedio_global', 0),
                'contexto_usuario': eval.get('contexto_usuario', 'Usuario evaluado')
            })
        
        # Determinar qué evaluación mostrar
        if dashboard_id:
            # Mostrar evaluación específica
            try:
                current_evaluation = survey_results_collection.find_one({'_id': ObjectId(dashboard_id)})
            except:
                current_evaluation = survey_results_collection.find_one({'_id': dashboard_id})
        else:
            # Mostrar la más reciente
            current_evaluation = evaluations[0] if evaluations else None
        
        if not current_evaluation:
            messages.error(request, "No se encontraron evaluaciones para este usuario.")
            return redirect('admin_users_list')
        
        # Preparar datos de resultados (igual que dashboard_matplotlib.html)
        resultados = {
            'timestamp': current_evaluation.get('timestamp', ''),
            'promedio_global': current_evaluation.get('promedio_global', 0),
            'nivel_evaluado': current_evaluation.get('nivel_evaluado', ''),
            'fortaleza': current_evaluation.get('fortaleza', ''),
            'oportunidad': current_evaluation.get('oportunidad', ''),
            'contexto_usuario': current_evaluation.get('contexto_usuario', ''),
            'logros': current_evaluation.get('logros', [])
        }
        
        # Preparar perfil individual
        perfil_nbx = current_evaluation.get('perfil_nbx', {})
        perfil = {
            'nb1': int(perfil_nbx.get('NB-1', 0)),
            'nb2': int(perfil_nbx.get('NB-2', 0)),
            'nb3': int(perfil_nbx.get('NB-3', 0)),
            'nb4': int(perfil_nbx.get('NB-4', 0)),
            'nb5': int(perfil_nbx.get('NB-5', 0)),
        }
        
        # Generar gráficos
        graficos = {}
        if perfil_nbx:
            try:
                graficos['radar'] = generar_grafico_radar(perfil_nbx)
                graficos['barras'] = generar_grafico_barras(perfil_nbx)
                # Aquí podrías agregar más gráficos si los tienes
            except Exception as e:
                logger.error(f"Error al generar gráficos: {e}")
                graficos = {}
        
        context = {
            'user': request.user,
            'selected_user': user_data,
            'resultados': resultados,
            'perfil': perfil,
            'graficos': graficos,
            'historial': historial,
            'current_dashboard_id': str(current_evaluation['_id']),
            'dashboard_id': str(current_evaluation['_id']),
            'total_evaluations': len(evaluations),
            'is_admin_view': True  # Flag para identificar que es vista de admin
        }
        
        return render(request, 'web_skill_app/admin/admin_user_evaluations.html', context)
        
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones del usuario {user_id}: {e}")
        messages.error(request, f"Error al cargar las evaluaciones: {str(e)}")
        return redirect('admin_users_list')
