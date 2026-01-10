from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .db import get_feedback_collection

def feedback_page(request):
    """Renderiza la página de feedback."""
    return render(request, 'web_skill_app/feedback.html')

def guardar_feedback(request):
    """Recibe los datos del formulario y los guarda en MongoDB con datos del usuario."""
    if request.method == 'POST':
        try:
            # 1. Obtener datos del formulario
            rating = request.POST.get('rating')
            comments = request.POST.get('comments')
            
            # Validar que existan datos básicos
            if not rating:
                messages.error(request, "Por favor selecciona una calificación de estrellas.")
                return redirect('feedback_page')

            # 2. Preparar los datos del Usuario
            # Por defecto, asumimos que es anónimo
            user_info = {
                "user_id": None,
                "username": "Anónimo",
                "full_name": "Visitante",
                "email": None
            }

            # Si el usuario está logueado en Django, sobrescribimos con sus datos reales
            if request.user.is_authenticated:
                user_info["user_id"] = request.user.id
                user_info["username"] = request.user.username
                user_info["email"] = request.user.email
                
                # Construimos el nombre completo si existe, si no usamos el username
                nombre = request.user.first_name
                apellido = request.user.last_name
                if nombre or apellido:
                    user_info["full_name"] = f"{nombre} {apellido}".strip()
                else:
                    user_info["full_name"] = request.user.username

            # 3. Crear el documento final para MongoDB
            feedback_doc = {
                # Datos del Usuario (Desempaquetamos el diccionario user_info)
                "user_id": user_info["user_id"],
                "username": user_info["username"],
                "nombre_completo": user_info["full_name"],
                "correo": user_info["email"],
                
                # Datos del Feedback
                "rating": int(rating),
                "mensaje": comments,
                
                # Metadatos
                "fecha_creacion": datetime.now()
            }

            # 4. Insertar en la colección 'feedbacks'
            collection = get_feedback_collection()
            collection.insert_one(feedback_doc)

            messages.success(request, '¡Gracias! Tu opinión ha sido guardada exitosamente.')
            return redirect('dashboard')

        except Exception as e:
            print(f"Error al guardar feedback: {e}")
            messages.error(request, 'Hubo un error al guardar tu opinión. Inténtalo de nuevo.')
            return redirect('feedback_page')
            
    return redirect('feedback_page')