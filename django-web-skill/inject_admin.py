"""
Script para inyectar el usuario administrador en MongoDB
Ejecutar una sola vez: python inject_admin.py
"""

import bcrypt
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Credenciales del administrador
ADMIN_EMAIL = "Administrador1@gmail.com"
ADMIN_PASSWORD = "123456"
ADMIN_FIRST_NAME = "Administrador"
ADMIN_LAST_NAME = "Principal"

def inject_admin():
    """Inyecta el usuario administrador en la colección 'admin'"""
    
    # Obtener URI de MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://diegocaso1988_db_user:BFFIoljgd3cAfqs2@webskill.hv6k6mh.mongodb.net/?retryWrites=true&w=majority&appName=webSkill')
    db_name = os.getenv('MONGO_DB_NAME', 'webSkill')
    
    try:
        # Conectar a MongoDB
        print("🔄 Conectando a MongoDB...")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        admin_collection = db['admin']
        
        # Verificar si ya existe el admin
        existing_admin = admin_collection.find_one({'email': ADMIN_EMAIL.lower()})
        
        if existing_admin:
            print(f"⚠️  El administrador '{ADMIN_EMAIL}' ya existe en la base de datos.")
            print(f"   ID: {existing_admin['_id']}")
            return
        
        # Hashear la contraseña
        print("🔐 Hasheando contraseña...")
        hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        
        # Crear documento del admin
        admin_doc = {
            'first_name': ADMIN_FIRST_NAME,
            'last_name': ADMIN_LAST_NAME,
            'email': ADMIN_EMAIL.lower(),
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow(),
            'is_admin': True
        }
        
        # Insertar en la colección
        print("💾 Insertando administrador en la base de datos...")
        result = admin_collection.insert_one(admin_doc)
        
        print("✅ ¡Administrador creado exitosamente!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   ID: {result.inserted_id}")
        print(f"   Colección: admin")
        
        # Cerrar conexión
        client.close()
        
    except Exception as e:
        print(f"❌ Error al crear el administrador: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  SCRIPT DE INYECCIÓN DE ADMINISTRADOR")
    print("=" * 60)
    inject_admin()
    print("=" * 60)
