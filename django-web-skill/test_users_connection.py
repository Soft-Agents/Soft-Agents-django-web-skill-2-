"""
Script para probar la conexión y obtener usuarios
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def test_users():
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://diegocaso1988_db_user:BFFIoljgd3cAfqs2@webskill.hv6k6mh.mongodb.net/?retryWrites=true&w=majority&appName=webSkill')
        db_name = os.getenv('MONGO_DB_NAME', 'webSkill')
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        users_collection = db['users']
        
        print("🔍 Probando conexión a usuarios...")
        
        # Contar usuarios
        count = users_collection.count_documents({})
        print(f"✅ Total usuarios: {count}")
        
        # Obtener algunos usuarios
        users = list(users_collection.find({}, {
            '_id': 1,
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'created_at': 1
        }).limit(5))
        
        print("\n📋 Primeros 5 usuarios:")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')} - {user.get('email', 'N/A')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_users()