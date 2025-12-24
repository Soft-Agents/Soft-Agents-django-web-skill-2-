#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_skill.settings')
django.setup()

from django.core.cache import cache
from web_skill_app.db import mongo_client
from django.conf import settings
from bson.objectid import ObjectId

def inyectar_datos_prueba():
    """Inyecta datos de prueba en el cache y MongoDB para testing del dashboard"""
    # Generar ObjectId para MongoDB
    mongo_id = ObjectId()
    session_id = str(mongo_id)
    
    # Datos de prueba del perfil NB-X
    perfil_nbx = {
        'NB-1': 7,  # Análisis
        'NB-2': 5,  # Evaluación  
        'NB-3': 8,  # Inferencia
        'NB-4': 6,  # Explicación
        'NB-5': 9,  # Flexibilidad
    }
    
    nivel = 'Intermedio'
    timestamp = datetime.now()
    promedio_global = round(sum(perfil_nbx.values()) / len(perfil_nbx), 1)
    
    # Calcular fortaleza y oportunidad
    nombres_pilares = {
        'NB-1': 'NB-1: Análisis',
        'NB-2': 'NB-2: Evaluación',
        'NB-3': 'NB-3: Inferencia',
        'NB-4': 'NB-4: Explicación',
        'NB-5': 'NB-5: Flexibilidad Cognitiva'
    }
    
    max_key = max(perfil_nbx, key=perfil_nbx.get)
    min_key = min(perfil_nbx, key=perfil_nbx.get)
    fortaleza = nombres_pilares[max_key]
    oportunidad = nombres_pilares[min_key]
    
    # Datos completos para el dashboard
    resultados_completos = {
        'perfil_nbx': perfil_nbx,
        'nivel_evaluado': nivel,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'promedio_global': promedio_global,
        'fortaleza': fortaleza,
        'oportunidad': oportunidad,
        'contexto_usuario': 'Estudiante universitario de ingeniería'
    }
    
    # Guardar en cache (temporal)
    cache.set(f'resultados_{session_id}', resultados_completos, timeout=3600)
    
    # Guardar en MongoDB Atlas (permanente)
    try:
        db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
        survey_collection = db['survey_results']
        
        # Crear documento para MongoDB
        survey_doc = {
            '_id': mongo_id,
            'user_id': '68d85d3be0b203c98b17894a',  # ID del usuario de prueba de la imagen
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'perfil_nbx': perfil_nbx,
            'nivel_evaluado': nivel,
            'promedio_global': promedio_global,
            'fortaleza': fortaleza,
            'oportunidad': oportunidad,
            'contexto_usuario': 'Estudiante universitario de ingeniería - Datos de prueba',
            'pensamiento_estructurado': {
                'logica_formal': round(perfil_nbx['NB-1'] * 1.11, 1),
                'logica_informal': round(perfil_nbx['NB-1'] * 1.03, 1),
                'razonamiento_deductivo': round(perfil_nbx['NB-3'] * 1.0, 1),
                'razonamiento_inductivo': round(perfil_nbx['NB-3'] * 0.94, 1),
            },
            'language_skills': {
                'vocabulario': round(perfil_nbx['NB-4'] * 1.07, 1),
                'gramatica': round(perfil_nbx['NB-4'] * 1.14, 1),
                'coherencia': round(perfil_nbx['NB-4'] * 1.0, 1),
            },
            'argumentation': {
                'estructura': round((perfil_nbx['NB-1'] + perfil_nbx['NB-3']) / 2, 1),
                'evidencia': round(perfil_nbx['NB-2'] * 0.97, 1),
                'conclusiones': round(perfil_nbx['NB-3'] * 1.07, 1),
            },
            'logros': [
                {'nombre': '🎯 Diagnóstico Inicial', 'descripcion': 'Completar tu primer test de Scouter', 'desbloqueado': True},
                {'nombre': '📊 Perfil Completo', 'descripcion': 'Obtener tu perfil NB-X completo', 'desbloqueado': True},
                {'nombre': '🧠 Pensador Analítico', 'descripcion': 'Obtener 8+ en NB-1 (Análisis)', 'desbloqueado': perfil_nbx['NB-1'] >= 8},
                {'nombre': '🔀 Mente Flexible', 'descripcion': 'Obtener 8+ en NB-5 (Flexibilidad)', 'desbloqueado': perfil_nbx['NB-5'] >= 8},
            ]
        }
        
        # Insertar en MongoDB
        result = survey_collection.insert_one(survey_doc)
        print(f"✅ Datos guardados en MongoDB con ID: {result.inserted_id}")
        
        # Actualizar historial del usuario
        users_collection = db['users']
        users_collection.update_one(
            {'_id': ObjectId('68d85d3be0b203c98b17894a')},
            {'$push': {'survey_history': str(result.inserted_id)}}
        )
        print(f"✅ Historial de usuario actualizado")
        
    except Exception as e:
        print(f"❌ Error guardando en MongoDB: {e}")
    
    print(f"✅ Datos de prueba inyectados correctamente!")
    print(f"📊 Session ID: {session_id}")
    print(f"🎯 Promedio global: {promedio_global}")
    print(f"💪 Fortaleza: {fortaleza}")
    print(f"🎯 Oportunidad: {oportunidad}")
    print(f"🔗 URL del dashboard: http://localhost:8001/encuesta/dashboard/?session_id={session_id}")
    print(f"🔗 URL sin session_id: http://localhost:8001/encuesta/dashboard/ (carga automáticamente el más reciente)")
    
    return session_id

if __name__ == "__main__":
    inyectar_datos_prueba()