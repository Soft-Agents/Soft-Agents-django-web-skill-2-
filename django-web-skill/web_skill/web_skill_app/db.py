from django.conf import settings
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

# --- Variables globales para conexión lazy ---
mongo_client = None
db = None
users_collection_instance = None
feedbacks_collection_instance = None
admin_collection_instance = None
survey_results_collection_instance = None

def _get_mongo_connection():
    """Establece la conexión a MongoDB de forma lazy (solo cuando se necesita)."""
    global mongo_client, db, users_collection_instance, feedbacks_collection_instance, admin_collection_instance, survey_results_collection_instance
    
    if mongo_client is None:
        try:
            mongo_uri = getattr(settings, 'MONGO_URI')
            mongo_client = MongoClient(mongo_uri)
            
            # Probar la conexión solo cuando se necesita
            mongo_client.admin.command('ping')
            logger.info("Conexión a MongoDB establecida exitosamente.")
            
            db_name = getattr(settings, 'MONGO_DB_NAME', 'webSkill')
            db = mongo_client[db_name]
            
            # --- COLECCIONES ---
            users_collection_instance = db['users']
            feedbacks_collection_instance = db['feedbacks']
            admin_collection_instance = db['admin']
            survey_results_collection_instance = db['survey_results']
            
        except AttributeError:
            logger.error("Error Crítico: MONGO_URI no está definido en settings.py.")
            raise ConnectionError("MONGO_URI no está definido en settings.py.")
        except Exception as e:
            logger.error(f"Error Crítico al conectar con MongoDB: {e}")
            raise ConnectionError(f"Error al conectar con MongoDB: {e}")
    
    return mongo_client, db

def get_db_collection():
    """Retorna la colección de usuarios (users)."""
    _get_mongo_connection()  # Asegurar conexión
    if users_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de usuarios.")
    return users_collection_instance

def get_feedback_collection():
    """Retorna la nueva colección de feedback (feedbacks)."""
    _get_mongo_connection()  # Asegurar conexión
    if feedbacks_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de feedbacks.")
    return feedbacks_collection_instance

def get_admin_collection():
    """Retorna la colección de administradores (admin)."""
    _get_mongo_connection()  # Asegurar conexión
    if admin_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de administradores.")
    return admin_collection_instance

def get_survey_results_collection():
    """Retorna la colección de resultados de encuestas (survey_results)."""
    _get_mongo_connection()  # Asegurar conexión
    if survey_results_collection_instance is None:
        raise ConnectionError("No hay conexión con la colección de survey_results.")
    return survey_results_collection_instance

def close_mongo_connection():
    if mongo_client:
        mongo_client.close()
        logger.info("Conexión a MongoDB cerrada.")