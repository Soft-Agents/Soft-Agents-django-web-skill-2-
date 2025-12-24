"""
Script para verificar que el sistema de administrador está configurado correctamente
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def verify_setup():
    """Verifica la configuración del sistema de administrador"""
    
    print("=" * 70)
    print("  VERIFICACIÓN DEL SISTEMA DE ADMINISTRADOR")
    print("=" * 70)
    
    # 1. Verificar conexión a MongoDB
    print("\n1️⃣  Verificando conexión a MongoDB...")
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://diegocaso1988_db_user:BFFIoljgd3cAfqs2@webskill.hv6k6mh.mongodb.net/?retryWrites=true&w=majority&appName=webSkill')
        db_name = os.getenv('MONGO_DB_NAME', 'webSkill')
        
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("   ✅ Conexión exitosa a MongoDB")
        
        db = client[db_name]
        
        # 2. Verificar colección admin
        print("\n2️⃣  Verificando colección 'admin'...")
        admin_collection = db['admin']
        admin_count = admin_collection.count_documents({})
        
        if admin_count > 0:
            print(f"   ✅ Colección 'admin' existe con {admin_count} documento(s)")
            
            # Mostrar admins
            admins = list(admin_collection.find({}, {'email': 1, 'first_name': 1, 'last_name': 1}))
            for admin in admins:
                print(f"      - {admin['first_name']} {admin['last_name']} ({admin['email']})")
        else:
            print("   ⚠️  Colección 'admin' está vacía")
            print("      Ejecuta: python inject_admin.py")
        
        # 3. Verificar colección users
        print("\n3️⃣  Verificando colección 'users'...")
        users_collection = db['users']
        users_count = users_collection.count_documents({})
        print(f"   ✅ Colección 'users' tiene {users_count} usuario(s) registrado(s)")
        
        # 4. Verificar colección survey_results
        print("\n4️⃣  Verificando colección 'survey_results'...")
        survey_collection = db['survey_results']
        survey_count = survey_collection.count_documents({})
        print(f"   ✅ Colección 'survey_results' tiene {survey_count} evaluación(es)")
        
        # 5. Verificar archivos del sistema
        print("\n5️⃣  Verificando archivos del sistema...")
        files_to_check = [
            'web_skill/web_skill_app/admin_views.py',
            'web_skill/web_skill_app/templates/web_skill_app/admin/admin_dashboard.html',
            'web_skill/web_skill_app/templates/web_skill_app/admin/admin_users_list.html',
            'web_skill/web_skill_app/templates/web_skill_app/admin/admin_user_evaluations.html',
        ]
        
        all_files_exist = True
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} NO ENCONTRADO")
                all_files_exist = False
        
        # 6. Resumen final
        print("\n" + "=" * 70)
        print("  RESUMEN")
        print("=" * 70)
        
        if admin_count > 0 and all_files_exist:
            print("✅ Sistema de administrador configurado correctamente")
            print("\n📝 Credenciales de acceso:")
            print("   Email: Administrador1@gmail.com")
            print("   Password: 123456")
            print("\n🌐 URLs de acceso:")
            print("   Login: http://127.0.0.1:8000/login/")
            print("   Admin Dashboard: http://127.0.0.1:8000/administrador/")
            print("   Lista de Usuarios: http://127.0.0.1:8000/administrador/usuarios/")
        else:
            print("⚠️  Hay problemas con la configuración")
            if admin_count == 0:
                print("   - Ejecuta: python inject_admin.py")
            if not all_files_exist:
                print("   - Faltan archivos del sistema")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    verify_setup()
