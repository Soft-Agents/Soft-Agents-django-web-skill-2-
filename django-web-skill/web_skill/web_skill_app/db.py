from django.conf import settings
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

# --- Cliente de MongoDB Persistente ---
try:
    mongo_uri = getattr(settings, 'MONGO_URI')
    mongo_client = MongoClient(mongo_uri)
    
    # Probar la conexión al inicio
    mongo_client.admin.command('ping')
    logger.info("Conexión a MongoDB establecida exitosamente.")
    
    db_name = getattr(settings, 'MONGO_DB_NAME', 'webSkill')
    db = mongo_client[db_name]
    
    # --- COLECCIONES ---
    users_collection_instance = db['users']
    # Nueva colección para el feedback
    feedbacks_collection_instance = db['feedbacks']
    # Colección para administradores
    admin_collection_instance = db['admin']
    # Colección para resultados de encuestas
    survey_results_collection_instance = db['survey_results']

except AttributeError:
    logger.error("Error Crítico: MONGO_URI no está definido en settings.py.")
    mongo_client = None
    users_collection_instance = None
    feedbacks_collection_instance = None
    admin_collection_instance = None
    survey_results_collection_instance = None
except Exception as e:
    logger.error(f"Error Crítico al conectar con MongoDB: {e}")
    mongo_client = None
    users_collection_instance = None
    feedbacks_collection_instance = None
    admin_collection_instance = None
    survey_results_collection_instance = None

def get_db_collection():
    """Retorna la colección de usuarios (users)."""
    if users_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de usuarios.")
    return users_collection_instance

def get_feedback_collection():
    """Retorna la nueva colección de feedback (feedbacks)."""
    if feedbacks_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de feedbacks.")
    return feedbacks_collection_instance

def get_admin_collection():
    """Retorna la colección de administradores (admin)."""
    if admin_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de administradores.")
    return admin_collection_instance

def get_survey_results_collection():
    """Retorna la colección de resultados de encuestas (survey_results)."""
    if survey_results_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de survey_results.")
    return survey_results_collection_instance

def close_mongo_connection():
    if mongo_client:
        mongo_client.close()
        logger.info("Conexión a MongoDB cerrada.")