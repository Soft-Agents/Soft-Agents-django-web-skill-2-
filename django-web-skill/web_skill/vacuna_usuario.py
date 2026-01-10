import os
import django
import datetime
from bson.objectid import ObjectId

# 1. Configurar entorno Django (necesario para usar la DB)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_skill.settings')
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass
django.setup()

# 2. Importar tu conexión a BD
from web_skill_app.db import get_db_collection

def vacunar_usuario():
    # ESTE ES EL ID QUE TE DIO ERROR EN LA TERMINAL
    user_id_str = "6962571af9a545334a95b378" 
    
    print(f"💉 Iniciando vacuna para el usuario: {user_id_str}")
    
    try:
        users_collection = get_db_collection()
        user_oid = ObjectId(user_id_str)
        
        # 3. Crear un historial "semilla"
        # Esto engaña al Agente: al ver que ya hay un mensaje, no intenta inicializar variables vacías
        fake_history = [
            {
                'role': 'agent', 
                'message': '¡Hola! Soy Yashay. He reiniciado mis sistemas y estoy listo para explicarte cualquier tema teórico. ¿En qué te ayudo hoy?', 
                'timestamp': datetime.datetime.now().isoformat()
            }
        ]
        
        # 4. Inyectarlo en la base de datos a la fuerza
        result = users_collection.update_one(
            {'_id': user_oid},
            {'$set': {'conversation_history_knowledge': fake_history}}
        )
        
        if result.modified_count > 0:
            print("✅ ¡ÉXITO! Usuario vacunado.")
            print("El historial ha sido reiniciado con un mensaje de bienvenida.")
            print("Ahora puedes ir al chat y hablar con Yashay sin errores.")
        else:
            print("⚠️ No se pudo actualizar. Tal vez el ID no existe o ya estaba vacunado.")
        
    except Exception as e:
        print(f"❌ Error durante la vacuna: {e}")

if __name__ == '__main__':
    vacunar_usuario()