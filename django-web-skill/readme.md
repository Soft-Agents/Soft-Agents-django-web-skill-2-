# Soft Agents - Django Web Skill

Aplicación web construida con Django, Tailwind CSS y MongoDB Atlas. Integra Agentes de IA y funcionalidad de transcripción de voz a texto (STT) para interactuar con los usuarios.

---

## 🚀 Características Principales

- **Autenticación de Usuarios:** Registro y login con almacenamiento directo en MongoDB.
- **Conexión Directa a MongoDB:** Uso del driver `pymongo` para alta compatibilidad.
- **Agentes de IA:** Integración con microservicios de IA (Profesor, Coach, Criker, Scouter).
- **Transcripción de Audio:** Funcionalidad para grabar voz en el navegador, convertirla y transcribirla a texto usando FFmpeg y SpeechRecognition.
- **Interfaz Moderna:** Diseño responsivo impulsado por Tailwind CSS.

---

## 📋 Guía de Instalación y Ejecución

Sigue estos pasos estrictamente en orden para evitar errores de dependencias.

### Paso 1: Prerrequisitos del Sistema

Asegúrate de tener instalado:

1.  **Python 3.11+**: Lenguaje base.
2.  **Node.js y npm**: Necesarios para compilar Tailwind CSS.
3.  **FFmpeg (CRÍTICO)**: Necesario para que funcione el audio.

#### ⚠️ Configuración de FFmpeg (Obligatorio)

Sin esto, la grabación de voz lanzará error.

- **En Windows:**
  1.  Descarga FFmpeg (versión essentials o full).
  2.  Extrae y copia los archivos `.exe` (`ffmpeg.exe`, `ffprobe.exe`) en una carpeta, por ejemplo: `C:\ffmpeg\bin`.
  3.  **IMPORTANTE:** Agrega `C:\ffmpeg\bin` a las **Variables de Entorno (PATH)** de tu sistema.
  4.  Reinicia tu terminal/editor para aplicar cambios.
- **En Linux/Mac:**
  - Ejecuta: `sudo apt-get install ffmpeg`

---

### Paso 2: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd soft-agents-django


### Paso 3: Configurar el Entorno Virtual

# Crear entorno
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS/Linux)
source venv/bin/activate

### Paso 4: Instalar Dependencias

#Backend (Python): Incluye Django, PyMongo, Pydub y SpeechRecognition.
pip install -r web_skill/requirements.txt

#Frontend (Tailwind):
npm install

### Paso 5: Configuración de Variables de Entorno (.env)
# Configuración General
DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
ALLOWED_HOSTS_PROD=localhost,127.0.0.1

# Base de Datos (MongoDB Atlas)
MONGO_URI=mongodb+srv://diegocaso1988_db_user:<password>@weskill.hv6k6mh.mongodb.net/?retryWrites=true&w=majority&appName=weskill
MONGO_DB_NAME=webSkill

# URLs de los Agentes de IA (Cloud Run)
# Si no se definen, el sistema usará las URLs por defecto configuradas en settings.py
AGENT_PROFESOR=[https://agente-profesor-redis-178017465262.us-central1.run.app/chat](https://agente-profesor-redis-178017465262.us-central1.run.app/chat)
AGENT_CRIKER_COACH=[https://agente-coach-redis-178017465262.us-central1.run.app/chat](https://agente-coach-redis-178017465262.us-central1.run.app/chat)
AGENT_CRIKER_SKILL=[https://agente-criker-redis2-178017465262.us-central1.run.app/chat](https://agente-criker-redis2-178017465262.us-central1.run.app/chat)
SOFIA_AGENT_URL=[https://agente-sofia-redis-178017465262.us-central1.run.app/chat](https://agente-sofia-redis-178017465262.us-central1.run.app/chat)

### Paso 6: Ejecutar Migraciones

python manage.py makemigrations
python manage.py migrate

### Paso 7: Ejecutar la Aplicación

#Terminal 1 (Compilador de Tailwind):

python manage.py tailwind start

#Terminal 2 (Servidor Django):
python manage.py runserver

#Otra opcion de ejecucion:
python manage.py runserver --noreload


### Despliegue con docker: Comandos para probar Docker localmente
docker build -t web-skill-app .
docker run -p 8080:8080 web-skill-app


```
