# Sistema de Administrador - Web Skill

## 📋 Resumen

Se ha implementado un sistema completo de administrador que permite visualizar las evaluaciones de todos los usuarios registrados.

## 🔐 Credenciales del Administrador

```
Email: Administrador1@gmail.com
Password: 123456
```

## 🗄️ Estructura de Base de Datos

### Colecciones MongoDB:
- **admin**: Almacena los usuarios administradores
- **users**: Usuarios normales del sistema
- **survey_results**: Resultados de las evaluaciones

## 🚀 Flujo de Navegación del Administrador

```
1. Login (Administrador1@gmail.com)
   ↓
2. Admin Dashboard (/admin/dashboard/)
   - Botón: "Ver Evaluaciones de Usuarios"
   ↓
3. Lista de Usuarios (/admin/users/)
   - Muestra todos los usuarios registrados
   - Cada usuario es clickeable
   - Botón: "← Volver"
   ↓
4. Evaluaciones del Usuario (/admin/users/<user_id>/evaluations/)
   - Muestra todas las evaluaciones del usuario seleccionado
   - Gráficos similares a dashboard_matplotlib.html
   - Historial de evaluaciones
   - Botón: "← Volver a Lista de Usuarios"
```

## 📁 Archivos Creados/Modificados

### Nuevos Archivos:
1. **inject_admin.py** - Script para crear el administrador
2. **web_skill/web_skill_app/admin_views.py** - Vistas del panel de admin
3. **web_skill/web_skill_app/templates/web_skill_app/admin/admin_dashboard.html**
4. **web_skill/web_skill_app/templates/web_skill_app/admin/admin_users_list.html**
5. **web_skill/web_skill_app/templates/web_skill_app/admin/admin_user_evaluations.html**

### Archivos Modificados:
1. **web_skill/web_skill_app/db.py** - Agregadas colecciones admin y survey_results
2. **web_skill/web_skill_app/auth_helpers.py** - Agregado decorador @admin_required
3. **web_skill/web_skill_app/auth_views.py** - Login con verificación de admin
4. **web_skill/web_skill_app/urls.py** - Rutas del panel de admin

## 🔧 Funcionalidades Implementadas

### 1. Sistema de Autenticación Dual
- Verifica primero en colección `admin`
- Si no es admin, verifica en colección `users`
- Guarda flag `is_admin` en sesión

### 2. Decorador @admin_required
- Protege las vistas de administrador
- Redirige a login si no está autenticado
- Redirige a presentacion si no es admin

### 3. Panel de Administrador
- Dashboard principal con botón de acceso
- Lista de todos los usuarios registrados
- Vista detallada de evaluaciones por usuario
- Gráficos de evaluación (radar, barras, evolución, métricas)

### 4. Navegación Intuitiva
- Botones de retroceso en cada página
- Breadcrumbs visuales
- Diseño consistente con el resto de la aplicación

## 🎨 Diseño

- Tema oscuro (slate-900, blue-900, purple-900)
- Cards con glassmorphism
- Iconos Material Icons
- Responsive design (Tailwind CSS)
- Animaciones y transiciones suaves

## 🧪 Cómo Probar

1. **Ejecutar el script de inyección** (ya ejecutado):
   ```bash
   python inject_admin.py
   ```

2. **Iniciar el servidor**:
   ```bash
   python manage.py runserver
   ```

3. **Acceder al login**:
   - URL: http://127.0.0.1:8000/login/
   - Email: Administrador1@gmail.com
   - Password: 123456

4. **Navegar por el panel**:
   - Serás redirigido a `/admin/dashboard/`
   - Click en "Ver Evaluaciones de Usuarios"
   - Selecciona un usuario para ver sus evaluaciones

## ⚠️ Notas Importantes

1. El administrador NO tiene acceso a las funcionalidades normales de usuario
2. Los usuarios normales NO pueden acceder al panel de admin
3. El script `inject_admin.py` solo debe ejecutarse UNA VEZ
4. Si intentas ejecutarlo de nuevo, detectará que el admin ya existe

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Sesiones seguras de Django
- Decoradores de protección en todas las vistas
- Validación de permisos en cada request

## 📊 Visualización de Datos

El panel de admin reutiliza la función `generar_graficos_matplotlib()` de `dashboard_views.py` para mostrar:
- Gráfico Radar (Perfil NB-X)
- Gráfico de Barras (Comparación por pilares)
- Evolución Temporal
- Métricas Detalladas

## 🐛 Troubleshooting

### El admin no puede iniciar sesión:
- Verifica que el script se ejecutó correctamente
- Revisa que la colección `admin` existe en MongoDB
- Verifica las credenciales exactas (case-sensitive)

### No se muestran las evaluaciones:
- Verifica que la colección `survey_results` tiene datos
- Revisa que el campo `user_id` coincide con el `_id` del usuario

### Error de conexión a MongoDB:
- Verifica el MONGO_URI en settings.py o .env
- Asegúrate de tener conexión a internet
