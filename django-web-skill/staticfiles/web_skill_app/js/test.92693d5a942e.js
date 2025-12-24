// web_skill_app/static/js/chat.js

// ============================================
// VARIABLES GLOBALES
// ============================================
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');
const finalizacionModal = document.getElementById('finalizacionModal');
const verDashboardBtn = document.getElementById('verDashboardBtn');

let isProcessing = false;
let redirectUrl = null;

// ============================================
// FUNCIONES AUXILIARES
// ============================================

/**
 * Obtiene el token CSRF de Django
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * Obtiene la hora actual formateada
 */
function getCurrentTime() {
    return new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Scroll automático al último mensaje
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Agrega un mensaje al chat
 */
function addMessage(role, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 message-animate';
    
    const isUser = role === 'user';
    
    if (isUser) {
        // Mensaje del usuario (derecha)
        messageDiv.className += ' flex-row-reverse space-x-reverse';
        messageDiv.innerHTML = `
            <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                </div>
            </div>
            <div class="flex-1 flex justify-end">
                <div class="bg-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl rounded-tr-none px-4 py-3 max-w-2xl">
                    <div class="flex items-center justify-end space-x-2 mb-1">
                        <span class="text-xs text-blue-200">${getCurrentTime()}</span>
                        <span class="text-xs font-semibold text-white">Tú</span>
                    </div>
                    <p class="text-white text-sm leading-relaxed">${escapeHtml(text)}</p>
                </div>
            </div>
        `;
    } else {
        // Mensaje del agente (izquierda)
        messageDiv.innerHTML = `
            <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                </div>
            </div>
            <div class="flex-1">
                <div class="bg-slate-700/50 rounded-2xl rounded-tl-none px-4 py-3 max-w-2xl">
                    <div class="flex items-center space-x-2 mb-1">
                        <span class="text-xs font-semibold text-purple-300">Agente Scouter</span>
                        <span class="text-xs text-slate-400">${getCurrentTime()}</span>
                    </div>
                    <p class="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">${escapeHtml(text)}</p>
                </div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Muestra/oculta el indicador de carga
 */
function toggleLoading(show) {
    if (show) {
        statusIndicator.classList.remove('hidden');
    } else {
        statusIndicator.classList.add('hidden');
    }
}

/**
 * Deshabilita/habilita el input y botón
 */
function toggleInputs(disabled) {
    messageInput.disabled = disabled;
    sendButton.disabled = disabled;
    isProcessing = disabled;
}

/**
 * Muestra el modal de finalización
 */
function showFinalizacionModal(url) {
    redirectUrl = url;
    finalizacionModal.classList.remove('hidden');
}

/**
 * Envía el mensaje al servidor
 */
async function sendMessage(message) {
    try {
        toggleInputs(true);
        toggleLoading(true);
        
        // Agregar mensaje del usuario al chat
        addMessage('user', message);
        
        // Enviar al backend Django
        const response = await fetch('/encuesta/mensaje/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Agregar respuesta del agente
            addMessage('agent', data.response);
            
            // Verificar si finalizó
            if (data.finalizado && data.redirect_url) {
                setTimeout(() => {
                    showFinalizacionModal(data.redirect_url);
                }, 1000);
            }
        } else {
            // Mostrar error
            addMessage('agent', `❌ Error: ${data.error || 'No se pudo procesar el mensaje'}`);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('agent', '❌ Error de conexión. Por favor, intenta de nuevo.');
    } finally {
        toggleLoading(false);
        toggleInputs(false);
        messageInput.focus();
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

/**
 * Manejo del formulario
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }
    
    // Limpiar input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Enviar mensaje
    await sendMessage(message);
});

/**
 * Auto-resize del textarea
 */
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

/**
 * Permitir enviar con Enter (sin Shift)
 */
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

/**
 * Botón del modal para ir al dashboard
 */
verDashboardBtn.addEventListener('click', () => {
    if (redirectUrl) {
        window.location.href = redirectUrl;
    }
});

// ============================================
// INICIALIZACIÓN
// ============================================

// Focus automático en el input
messageInput.focus();

// Prevenir pérdida de datos al cerrar
window.addEventListener('beforeunload', (e) => {
    if (chatMessages.children.length > 1 && !redirectUrl) {
        e.preventDefault();
        e.returnValue = '¿Estás seguro de que quieres salir? Perderás tu progreso.';
    }
});

console.log('💬 Chat inicializado correctamente');
console.log('🔑 Session ID:', SESSION_ID);