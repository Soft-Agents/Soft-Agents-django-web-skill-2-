# web_skill_app/urls.py

from django.urls import path, re_path
from . import core_views
from . import auth_views
from . import test_views
from . import sofia_views
from . import preguntas_views
from . import streamlit_proxy
from . import dashboard_views
from . import feedback_views
from . import admin_views

urlpatterns = [
    # --- Vistas Estáticas y Principales ---
    path('', core_views.home, name='home'),
    path('pensamiento-critico/', core_views.pensamiento_critico, name='pensamiento-critico'),
    path('comunicacion/', core_views.comunicacion, name='comunicacion'),
    path('creatividad/', core_views.creatividad, name='creatividad'),
    path('colaboracion/', core_views.colaboracion, name='colaboracion'),
    path('skill/', core_views.skill, name='skill'),
    path('presentacion/', core_views.presentacion, name='presentacion'),
    
    # --- Vistas de la App (Dashboard y Agentes) ---
    path('dashboard/', core_views.dashboard_view, name='dashboard'),
    path('chat/knowledge/', core_views.knowledge_view, name='chat_knowledge'),
    path('api/skill_chat/', core_views.skill_chat_api, name='skill_chat_api'), # NUEVA RUTA para el POST AJAX

    # --- Vistas de Autenticación ---
    path('login/', auth_views.login_page, name='login_page'), 
    path('register/', auth_views.register_view, name='register_view'),
    path('logout/', auth_views.logout_view, name='logout_view'),
    
    path('test/', test_views.test_views, name='test_views'),  # Ruta para la vista de prueba
    
    path('ask-sofia/', sofia_views.ask_sofia, name='ask_sofia'), # <-- Añade esta línea

    # --- Vistas de Lecciones (NUEVO) ---
    path("lecciones/<str:leccion_id>/", core_views.leccion_view, name="leccion_view"),
    
    # --- Vistas de la Encuesta Interactiva ---
    path('chat/', core_views.preguntas, name='chat_preguntas'),
    path('encuesta/iniciar/', preguntas_views.iniciar_encuesta, name='iniciar_encuesta'),
    path('encuesta/mensaje/', preguntas_views.procesar_mensaje, name='procesar_mensaje'),
    path('encuesta/dashboard/', dashboard_views.dashboard_view, name='dashboard_encuesta'),
    path('api/resultados/<str:session_id>/', preguntas_views.obtener_resultados, name='obtener_resultados'),
    path('api/graficos/<str:session_id>/<str:tipo_grafico>/', dashboard_views.generar_grafico_api, name='generar_grafico'),
    path('encuesta/inyectar-datos/', preguntas_views.inyectar_datos_prueba, name='inyectar_datos_prueba'),
    path('encuesta/limpiar/', preguntas_views.limpiar_cache, name='limpiar_cache'),
    path('encuesta/eliminar-dashboard/', preguntas_views.eliminar_dashboard, name='eliminar_dashboard'),

    # # --- Proxy para Streamlit ---
    # re_path(r'^streamlit/.*', streamlit_proxy.streamlit_proxy, name='streamlit_proxy'),
    
    # --- feedback ---
    path('feedback/', feedback_views.feedback_page, name='feedback_page'),
    path('feedback/guardar/', feedback_views.guardar_feedback, name='guardar_feedback'),
    
    # --- Vistas de Administrador ---
    path('administrador/', admin_views.admin_dashboard_view, name='admin_dashboard'),
    path('administrador/usuarios/', admin_views.admin_users_list_view, name='admin_users_list'),
    path('administrador/usuarios/<str:user_id>/evaluaciones/', admin_views.admin_user_evaluations_view, name='admin_user_evaluations'),
]