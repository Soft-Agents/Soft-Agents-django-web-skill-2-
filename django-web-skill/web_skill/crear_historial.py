#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_skill.settings')
django.setup()

from django.core.cache import cache
from web_skill_app.db import mongo_client
from django.conf import settings
from bson.objectid import ObjectId

def crear_historial_evaluaciones():
    """Crea múltiples evaluaciones de prueba para mostrar el historial"""
    
    user_id = '68d85d3be0b203c98b17894a'  # ID del usuario de la imagen
    
    # Datos de 3 evaluaciones diferentes
    evaluaciones = [
        {
            'perfil': {'NB-1': 6, 'NB-2': 4, 'NB-3': 7, 'NB-4': 5, 'NB-5': 8},
            'nivel': 'Básico',
            'contexto': 'Primera evaluación - Estudiante de primer año',
            'dias_atras': 30
        },
        {
            'perfil': {'NB-1': 7, 'NB-2': 6, 'NB-3': 8, 'NB-4': 6, 'NB-5': 8},
            'nivel': 'Intermedio', 
            'contexto': 'Segunda evaluación - Después de curso de lógica',
            'dias_atras': 15
        },
        {
            'perfil': {'NB-1': 8, 'NB-2': 7, 'NB-3': 9, 'NB-4': 8, 'NB-5': 9},
            'nivel': 'Experto',
            'contexto': 'Evaluación más reciente - Estudiante avanzado',
            'dias_atras': 2
        }
    ]
    
    try:
        db = mongo_client[getattr(settings, 'MONGO_DB_NAME', 'webSkill')]
        survey_collection = db['survey_results']
        users_collection = db['users']
        
        survey_ids = []
        
        for i, eval_data in enumerate(evaluaciones):
            # Crear timestamp
            timestamp = datetime.now() - timedelta(days=eval_data['dias_atras'])
            
            # Calcular métricas
            perfil_nbx = eval_data['perfil']
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
            
            # Crear documento
            mongo_id = ObjectId()
            survey_doc = {
                '_id': mongo_id,
                'user_id': user_id,
                'session_id': str(mongo_id),
                'timestamp': timestamp.isoformat(),
                'perfil_nbx': perfil_nbx,
                'nivel_evaluado': eval_data['nivel'],
                'promedio_global': promedio_global,
                'fortaleza': fortaleza,
                'oportunidad': oportunidad,
                'contexto_usuario': eval_data['contexto'],
                'pensamiento_estructurado': {
                    'logica_formal': round(perfil_nbx['NB-1'] * 1.11, 1),
                    'razonamiento_deductivo': round(perfil_nbx['NB-3'] * 1.0, 1),
                },
                'language_skills': {
                    'vocabulario': round(perfil_nbx['NB-4'] * 1.07, 1),
                    'coherencia': round(perfil_nbx['NB-4'] * 1.0, 1),
                },
                'argumentation': {
                    'estructura': round((perfil_nbx['NB-1'] + perfil_nbx['NB-3']) / 2, 1),
                    'evidencia': round(perfil_nbx['NB-2'] * 0.97, 1),
                },
                'logros': [
                    {'nombre': '🎯 Diagnóstico Inicial', 'descripcion': 'Completar tu primer test', 'desbloqueado': True},
                    {'nombre': '📊 Perfil Completo', 'descripcion': 'Obtener perfil NB-X', 'desbloqueado': True},
                ]
            }
            
            # Insertar en MongoDB
            result = survey_collection.insert_one(survey_doc)
            survey_ids.append(str(result.inserted_id))
            
            print(f"✅ Evaluación {i+1} guardada: {eval_data['nivel']} - Promedio: {promedio_global}")
        
        # Actualizar historial del usuario
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'survey_history': {'$each': survey_ids}}}
        )
        
        print(f"✅ Historial completo creado para usuario: {user_id}")
        print(f"📊 Total de evaluaciones: {len(survey_ids)}")
        print(f"🔗 Dashboard (último): http://localhost:8001/encuesta/dashboard/?session_id={survey_ids[-1]}")
        print(f"🔗 Dashboard (automático): http://localhost:8001/encuesta/dashboard/")
        
        return survey_ids
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    crear_historial_evaluaciones()