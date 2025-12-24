"""
Script para probar la conexión del admin y ver exactamente qué datos tenemos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('web_skill')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_skill.settings')
django.setup()

from web_skill_app.db import get_db_collection, get_survey_results_collection

def test_admin_data():
    print("=" * 60)
    print("  PRUEBA DE DATOS PARA EL ADMIN")
    print("=" * 60)
    
    try:
        # 1. Probar usuarios
        print("\n1️⃣  Probando colección 'users'...")
        users_collection = get_db_collection()
        
        users = list(users_collection.find({}, {
            '_id': 1,
            'first_name': 1,
            'last_name': 1,
            'email': 1,
            'created_at': 1
        }).limit(3))
        
        print(f"✅ Encontrados {len(users)} usuarios (mostrando 3):")
        for i, user in enumerate(users, 1):
            user_id = str(user['_id'])
            first_name = user.get('first_name', 'Sin nombre')
            last_name = user.get('last_name', '')
            email = user.get('email', 'Sin email')
            print(f"  {i}. ID: {user_id[:8]}... | {first_name} {last_name} | {email}")
        
        # 2. Probar evaluaciones
        print("\n2️⃣  Probando colección 'survey_results'...")
        survey_collection = get_survey_results_collection()
        
        evaluations = list(survey_collection.find({}).limit(3))
        print(f"✅ Encontradas {len(evaluations)} evaluaciones (mostrando 3):")
        
        for i, eval in enumerate(evaluations, 1):
            eval_id = str(eval['_id'])
            user_id = eval.get('user_id', 'Sin user_id')
            session_id = eval.get('session_id', 'Sin session_id')
            timestamp = eval.get('timestamp', 'Sin timestamp')
            print(f"  {i}. Eval ID: {eval_id[:8]}... | User ID: {user_id[:8]}... | Session: {session_id[:8]}... | {timestamp}")
        
        # 3. Verificar relación user_id
        if users and evaluations:
            print("\n3️⃣  Verificando relación user_id...")
            first_user_id = str(users[0]['_id'])
            user_evaluations = list(survey_collection.find({'user_id': first_user_id}))
            print(f"✅ Usuario {first_user_id[:8]}... tiene {len(user_evaluations)} evaluación(es)")
        
        print("\n" + "=" * 60)
        print("✅ CONEXIÓN EXITOSA - Los datos están disponibles")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_data()