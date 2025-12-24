Proyecto Django  Web Skill
Este proyecto es una aplicación web construida con Django, Tailwind CSS y MongoDB Atlas. Permite a los usuarios registrarse y guardar sus datos en una base de datos NoSQL.

Características Principales
Autenticación de Usuarios: Los usuarios pueden registrarse y sus datos se guardan directamente en una colección de MongoDB.

Conexión Directa a MongoDB: Utiliza el driver pymongo para una conexión segura y directa, evitando problemas de compatibilidad.

Interfaz Moderna: El diseño está impulsado por Tailwind CSS.

Guía de Instalación y Ejecución
Sigue estos pasos en orden para poner el proyecto en marcha.

Paso 1: Prerrequisitos
Asegúrate de que estos programas estén instalados en tu sistema:

Python 3.11+: Esencial para Django.

Node.js y npm: Necesarios para compilar los estilos de Tailwind CSS.

Paso 2: Clonar el Repositorio
Intento

git clone https:
cd nombre-del-repo
Paso 3: Configurar el Entorno Virtual
Crea y activa un entorno virtual para manejar las dependencias del proyecto de forma segura.

Crear: python -m venv venv

Activar (Windows): venv\Scripts\activate

Activar (macOS/Linux): source venv/bin/activate

Paso 4: Instalar Dependencias
Instala todas las bibliotecas de Python y Node.js que el proyecto necesita.

Dependencias de Python:

Intento

pip install -r requirements.txt
Dependencias de Node.js :

Intento

npm install
Paso 5: Configuración de la Base de Datos
Obtener la URL de Conexión:

Crea un clúster enAtlas de MongoDB.

Crea un usuario de base de datos (diegocaso1988_db_user).

Obtén la cadena de conexión (SRV) desde el panel de Atlas.

Crear el archivo .env:
En la raíz del proyecto, crea un archivo llamado .env y pega tu cadena de conexión, reemplazando <password> por la tuya.

Fragmento de código

DATABASE_URL=mongodb+srv://diegocaso1988_db_user:<password>@weskill.hv6k6mh.mongodb.net/?retryWrites=true&w=majority&appName=weskill
Paso 6: Ejecutar Migraciones
Django usa su base de datos interna de SQLite para el panel de administración y otras funciones. Ejecuta estos comandos para prepararla.

Intento

python manage.py makemigrations
python manage.py migrate

Paso 7: Ejecutar la Aplicación
Abre dos terminales separadas para ejecutar el proyecto.

Terminal 1 (para Tailwind):
Este comando compila tus estilos de forma automática cada vez que haces un cambio.

Intento

python manage.py tailwind start
Terminal 2 (para Django):
Este comando inicia el servidor web de Django.

Intento

python manage.py runserver