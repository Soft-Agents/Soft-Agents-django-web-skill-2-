# web_skill_app/views/dashboard_views.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from bson.objectid import ObjectId
from .services import get_user_survey_history
from .db import get_db_collection
from django.views.decorators.clickjacking import xframe_options_exempt # <-- AÑADE ESTA LÍNEA

# Configurar matplotlib
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Colores del tema
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2', 
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
}

def generar_grafico_radar(perfil_nbx):
    """Genera gráfico radar del perfil NB-X"""
    categorias = ['Análisis\n(NB-1)', 'Evaluación\n(NB-2)', 'Inferencia\n(NB-3)', 
                  'Explicación\n(NB-4)', 'Flexibilidad\n(NB-5)']
    
    # NO dividir - usar escala 0-100 directa
    valores = [perfil_nbx.get(f'NB-{i}', 0) for i in range(1, 6)]
    
    # Cerrar el polígono
    valores += valores[:1]
    categorias += categorias[:1]
    
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=True)
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    ax.plot(angulos, valores, 'o-', linewidth=2, color=COLORS['primary'], label='Tu Perfil')
    ax.fill(angulos, valores, alpha=0.25, color=COLORS['primary'])
    
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias[:-1])
    ax.set_ylim(0, 100)  # ✅ Escala 0-100
    ax.set_yticks(range(0, 101, 5))  # ✅ 0, 10, 20, 30...100
    ax.grid(True)
    
    plt.title('Perfil de Pensamiento Crítico NB-X', size=16, fontweight='bold', pad=20)
    
    # ... resto igual
    
    # Convertir a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

def generar_grafico_barras(perfil_nbx):
    """Genera gráfico de barras comparativo"""
    categorias = ['Análisis', 'Evaluación', 'Inferencia', 'Explicación', 'Flexibilidad']
    
    # NO dividir - usar escala 0-100
    valores = [perfil_nbx.get(f'NB-{i}', 0) for i in range(1, 6)]
    
    # Colores según el nivel
    colores = []
    for valor in valores:
        if valor >= 80:  # Era >= 8
            colores.append(COLORS['success'])
        elif valor >= 60:  # Era >= 6
            colores.append(COLORS['warning'])
        else:
            colores.append(COLORS['danger'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categorias, valores, color=colores, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Agregar valores en las barras
    for bar, valor in zip(bars, valores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{valor:.0f}/100', ha='center', va='bottom', fontweight='bold')  # ✅
    
    ax.set_ylim(0, 100)  # ✅
    ax.set_yticks(range(0, 101, 10))  # ✅ 0, 10, 20...100
    ax.set_ylabel('Puntuación (0-100)', fontweight='bold')  # ✅
    
    # Líneas de referencia
    ax.axhline(y=60, color='gray', linestyle='--', alpha=0.5, label='Nivel Intermedio')
    ax.axhline(y=80, color='gray', linestyle='--', alpha=0.7, label='Nivel Experto')
    
    # ... resto igual
    
    ax.grid(axis='y', alpha=0.3)
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Convertir a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

@xframe_options_exempt  # <-- AÑADE ESTA LÍNEA
@require_http_methods(["GET"])
def dashboard_view(request):
    """Vista principal del dashboard con gráficos"""
    session_id = request.GET.get('session_id')
    dashboard_id = request.GET.get('dashboard_id')  # Para flujo normal de encuesta
    # --- MODIFICACIÓN AQUÍ ---
    # 1. Intenta obtener el user_id desde el parámetro GET (para el iframe)
    user_id_from_get = request.GET.get('user_id')

    # 2. Si no existe, intenta obtenerlo de la sesión (para navegación normal)
    user_id_from_session = request.session.get('user_id')

    # 3. El user_id final es cualquiera de los dos que exista
    user_id = user_id_from_get or user_id_from_session
    # --- FIN MODIFICACIÓN ---

    # 1. Creamos la variable. Si user_id_from_get existe, es verdad.
    is_in_iframe = bool(user_id_from_get)
    # --- FIN DE LA MODIFICACIÓN ---
    
    try:
        from .db import mongo_client
        from django.conf import settings
        
        db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
        survey_collection = db['survey_results']
        
        # Determinar qué ID usar para buscar los datos
        search_id = dashboard_id or session_id
        
        # Si no hay ningún ID pero hay usuario logueado, obtener la evaluación más reciente
        if not search_id and user_id:
            latest_survey = survey_collection.find_one(
                {'user_id': user_id},
                sort=[('timestamp', -1)]  # Ordenar por fecha descendente
            )
            if latest_survey:
                search_id = str(latest_survey['_id'])
            else:
                return render(request, 'web_skill_app/dashboard_vacio.html', {
                    'error': 'No se encontraron evaluaciones para este usuario.'
                }, status=404)
        elif not search_id:
            # Si no hay ID y no hay usuario, usar datos demo
            search_id = 'demo-dashboard'
        
        # Obtener datos del dashboard desde MongoDB
        survey_doc = None
        
        # Si es demo-dashboard, usar datos de demostración
        # Si es demo-dashboard, usar datos de demostración
        if search_id == 'demo-dashboard':
            resultados = {
                'perfil_nbx': {
                    # CORREGIDO: Valores en escala 0-100
                    'NB-1': 75.0,
                    'NB-2': 82.0,
                    'NB-3': 68.0,
                    'NB-4': 79.0,
                    'NB-5': 71.0
                },
                'nivel_evaluado': 'Intermedio-Avanzado',
                'timestamp': '2024-10-28 14:30:00',
                # CORREGIDO: Promedio en escala 0-100
                'promedio_global': 75.0, # (O el promedio real, ej: (75+82+68+79+71)/5 = 75.0)
                'fortaleza': 'Evaluación crítica',
                'oportunidad': 'Inferencia lógica',
                'contexto_usuario': 'Perfil de demostración para testing',
                'pensamiento_estructurado': {}, # (Estos se deben recalcular si importan)
                'language_skills': {},
                'argumentation': {},
                'logros': ['Completó evaluación demo', 'Accedió al dashboard'] # (La lógica de logros también debe actualizarse)
            }
        else:
            # Buscar en MongoDB
            try:
                survey_doc = survey_collection.find_one({'_id': ObjectId(search_id)})
            except:
                # Si falla ObjectId, buscar por session_id string
                survey_doc = survey_collection.find_one({'session_id': search_id})
            
            if not survey_doc:
                # Fallback: intentar obtener desde cache
                resultados = cache.get(f'resultados_{search_id}')
                if not resultados:
                    return JsonResponse({'error': 'Resultados no encontrados para la sesión'}, status=404)
            else:
                # Convertir documento de MongoDB al formato esperado
                resultados = {
                    'perfil_nbx': survey_doc.get('perfil_nbx', {}),
                    'nivel_evaluado': survey_doc.get('nivel_evaluado', ''),
                    'timestamp': survey_doc.get('timestamp', ''),
                    'promedio_global': survey_doc.get('promedio_global', 0),
                    'fortaleza': survey_doc.get('fortaleza', ''),
                    'oportunidad': survey_doc.get('oportunidad', ''),
                    'contexto_usuario': survey_doc.get('contexto_usuario', ''),
                    'pensamiento_estructurado': survey_doc.get('pensamiento_estructurado', {}),
                    'language_skills': survey_doc.get('language_skills', {}),
                    'argumentation': survey_doc.get('argumentation', {}),
                    'logros': survey_doc.get('logros', [])
                }
        
        # Obtener historial de evaluaciones para el sidebar
        historial = []
        if user_id:
            historial = get_user_survey_history(user_id)
        
        # Generar gráficos
        graficos = {}
        try:
            # Gráfico radar
            graficos['radar'] = generar_grafico_radar(resultados['perfil_nbx'])
            
            # Gráfico de barras
            graficos['barras'] = generar_grafico_barras(resultados['perfil_nbx'])
        except Exception as e:
            print(f"Error generando gráficos: {e}")
            graficos = {}
        
        # Preparar datos para el template
        perfil_individual = {
            'nb1': int(resultados['perfil_nbx'].get('NB-1', 0)),
            'nb2': int(resultados['perfil_nbx'].get('NB-2', 0)),
            'nb3': int(resultados['perfil_nbx'].get('NB-3', 0)),
            'nb4': int(resultados['perfil_nbx'].get('NB-4', 0)),
            'nb5': int(resultados['perfil_nbx'].get('NB-5', 0)),
        }
        
        # Preparar datos de resultados
        resultados_display = {
            'timestamp': resultados.get('timestamp', ''),
            'promedio_global': resultados.get('promedio_global', 0),
            'nivel_evaluado': resultados.get('nivel_evaluado', ''),
            'fortaleza': resultados.get('fortaleza', ''),
            'oportunidad': resultados.get('oportunidad', ''),
            'contexto_usuario': resultados.get('contexto_usuario', '')
        }
        
        context = {
            'resultados': resultados_display,
            'perfil': perfil_individual,
            'graficos': graficos,
            'dashboard_id': search_id, # Usamos search_id como identificador
            'historial': historial,  # Para el sidebar
            'current_dashboard_id': search_id,  # Para marcar activo en sidebar
            'is_demo': search_id == 'demo-dashboard',  # Indicar si es demo
            'is_in_iframe': is_in_iframe, # <-- 2. La añadimos al contexto
            'user_id': user_id  # <--- AÑADE ESTA LÍNEA
        }
        return render(request, 'web_skill_app/dashboard_matplotlib.html', context)
        
    except Exception as e:
        return JsonResponse({'error': f'Error cargando dashboard: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def generar_grafico_api(request, session_id, tipo_grafico):
    """API endpoint para generar gráficos dinámicamente."""
    resultados = cache.get(f'resultados_{session_id}')
    
    if not resultados:
        return JsonResponse({'error': 'No se encontraron resultados para este session_id'}, status=404)
    
    perfil_nbx = resultados.get('perfil_nbx')
    
    if not perfil_nbx:
        return JsonResponse({'error': 'No se encontró un perfil NB-X en los resultados'}, status=404)

    if tipo_grafico == 'radar':
        grafico_b64 = generar_grafico_radar(perfil_nbx)
    elif tipo_grafico == 'barras':
        grafico_b64 = generar_grafico_barras(perfil_nbx)
    else:
        return JsonResponse({'error': 'Tipo de gráfico no válido'}, status=400)
    
    return JsonResponse({'grafico': grafico_b64})
