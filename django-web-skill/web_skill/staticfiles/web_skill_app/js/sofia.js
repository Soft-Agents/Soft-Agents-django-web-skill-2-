// En: web_skill_app/static/web_skill_app/sofia.js

document.addEventListener('DOMContentLoaded', () => {

    // --- SELECCIÓN DE ELEMENTOS ---
    const avatar = document.getElementById('avatar-flotante');
    const bocadillo = document.getElementById('bocadillo-texto');
    const chatHistory = document.getElementById('sofia-chat-history');
    const textInput = document.getElementById('sofia-text-input');
    const sendButton = document.getElementById('sofia-send-btn');

    // URL de nuestra API interna de Django
    const chatApiUrl = '/ask-sofia/';


    // ==========================================================
    // --- LÓGICA DE ARRASTRAR Y ABRIR/CERRAR EL BOCADILLO ---
    // ==========================================================

    let isDragging = false;
    let hasDragged = false;
    let offsetX = 0;
    let offsetY = 0;

    // Unifica 'mousedown' y 'touchstart'
    function dragStart(e) {
        // ✅ CORRECCIÓN: No prevenir default si el clic es dentro del bocadillo
        // Esto permite que el input funcione correctamente
        if (bocadillo.contains(e.target)) {
            return; // No iniciar drag si se clickea el bocadillo
        }

        isDragging = true;
        hasDragged = false;

        const clientX = e.clientX || e.touches[0].clientX;
        const clientY = e.clientY || e.touches[0].clientY;

        offsetX = clientX - avatar.getBoundingClientRect().left;
        offsetY = clientY - avatar.getBoundingClientRect().top;

        avatar.style.cursor = 'grabbing';
        if (e.type === 'mousedown') e.preventDefault();
    }

    // Unifica 'mousemove' y 'touchmove'
    function dragMove(e) {
        if (!isDragging) return;

        hasDragged = true;

        if (e.type === 'touchmove') e.preventDefault();

        const clientX = e.clientX || e.touches[0].clientX;
        const clientY = e.clientY || e.touches[0].clientY;

        let newX = clientX - offsetX;
        let newY = clientY - offsetY;

        // Limitar al viewport
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        const avatarWidth = avatar.offsetWidth;
        const avatarHeight = avatar.offsetHeight;

        if (newX < 0) newX = 0;
        if (newY < 0) newY = 0;
        if (newX + avatarWidth > screenWidth) newX = screenWidth - avatarWidth;
        if (newY + avatarHeight > screenHeight) newY = screenHeight - avatarHeight;

        avatar.style.left = `${newX}px`;
        avatar.style.top = `${newY}px`;
    }

    // Unifica 'mouseup' y 'touchend'
    function dragEnd() {
        isDragging = false;
        avatar.style.cursor = 'grab';

        setTimeout(() => {
            hasDragged = false;
        }, 0);
    }

    // Eventos de Mouse para arrastrar
    avatar.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', dragMove);
    document.addEventListener('mouseup', dragEnd);

    // Eventos Táctiles (Touch) para arrastrar
    avatar.addEventListener('touchstart', dragStart, { passive: true });
    document.addEventListener('touchmove', dragMove, { passive: false });
    document.addEventListener('touchend', dragEnd);

    // --- Lógica de Clic para Abrir/Cerrar ---

    function toggleBocadillo() {
        const wasVisible = bocadillo.classList.contains('visible');
        bocadillo.classList.toggle('visible');

        // ✅ MEJORA: Auto-focus en el input cuando se abre
        if (!wasVisible) {
            setTimeout(() => {
                textInput.focus();
            }, 300); // Esperar a que termine la animación
        }
    }

    // Clic EN EL AVATAR: Abre/cierra el chat SI NO FUE UN DRAG
    avatar.addEventListener('click', (e) => {
        // Si el clic vino del bocadillo, ignorarlo
        if (bocadillo.contains(e.target)) {
            return;
        }

        if (!hasDragged) {
            toggleBocadillo();
        }
    });

    // Clic EN CUALQUIER PARTE DEL DOCUMENTO
    document.addEventListener('click', (e) => {
        const clickedInsideAvatar = avatar.contains(e.target);
        const clickedInsideBocadillo = bocadillo.contains(e.target);
        const isBocadilloVisible = bocadillo.classList.contains('visible');

        // Solo cerrar si está visible y el clic fue completamente fuera
        if (isBocadilloVisible && !clickedInsideAvatar && !clickedInsideBocadillo) {
            bocadillo.classList.remove('visible');
        }
    });

    // ✅ MEJORA: Prevenir que clics en el bocadillo se propaguen al avatar
    bocadillo.addEventListener('click', (e) => {
        e.stopPropagation();
    });


    // ==========================================
    // --- LÓGICA DEL CHAT INTERNO ---
    // ==========================================

    // Helper function para obtener la cookie CSRF de Django
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

    // Añadir listeners para enviar el mensaje
    sendButton.addEventListener('click', sendMessage);
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // ✅ MEJORA: Placeholder dinámico
    const placeholders = [
        'Escribe tu pregunta...',
        '¿En qué puedo ayudarte?',
        'Pregúntame lo que quieras...',
        'Cuéntame, ¿qué necesitas?'
    ];

    let placeholderIndex = 0;
    textInput.addEventListener('focus', () => {
        if (textInput.value === '') {
            placeholderIndex = (placeholderIndex + 1) % placeholders.length;
            textInput.placeholder = placeholders[placeholderIndex];
        }
    });

    /**
     * Función principal para enviar el mensaje
     */
    function sendMessage() {
        const messageText = textInput.value.trim();
        if (messageText === '') return;

        addMessageToHistory(messageText, 'user');
        textInput.value = '';
        textInput.placeholder = 'Escribe tu pregunta...';
        showTypingIndicator(true);
        fetchSofiaResponse(messageText);
    }

    /**
     * Añade un mensaje (usuario o agente) a la ventana de chat
     */
    function addMessageToHistory(message, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('sofia-message', type);

        // ✅ MEJORA: Soporte para HTML en respuestas (negrita, listas, etc)
        if (type === 'agent') {
            messageElement.innerHTML = formatAgentMessage(message);
        } else {
            messageElement.textContent = message;
        }

        chatHistory.appendChild(messageElement);

        // ✅ MEJORA: Animación suave al aparecer
        setTimeout(() => {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translateY(10px)';
            messageElement.style.transition = 'opacity 0.3s, transform 0.3s';

            requestAnimationFrame(() => {
                messageElement.style.opacity = '1';
                messageElement.style.transform = 'translateY(0)';
            });
        }, 10);

        chatHistory.scrollTop = chatHistory.scrollHeight;
        return messageElement;
    }

    /**
     * ✅ MEJORA: Formatea el mensaje del agente para soportar markdown básico
     */
    function formatAgentMessage(message) {
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **negrita**
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // *cursiva*
            .replace(/\n/g, '<br>'); // saltos de línea
    }

    /**
     * Muestra u oculta el indicador "Sofía está escribiendo..."
     */
    function showTypingIndicator(show) {
        const existingTyping = chatHistory.querySelector('.agent-typing');
        if (existingTyping) {
            existingTyping.remove();
        }
        if (show) {
            const typingElement = addMessageToHistory('Sofía está escribiendo...', 'agent-typing');

            // ✅ MEJORA: Animación de puntos suspensivos
            let dots = 0;
            const typingInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                typingElement.textContent = 'Sofía está escribiendo' + '.'.repeat(dots);
            }, 500);

            // Guardar el intervalo para poder limpiarlo después
            typingElement.dataset.interval = typingInterval;
        }
    }

    /**
     * Llama a la API de Django para obtener la respuesta del agente
     */
    async function fetchSofiaResponse(userMessage) {
        try {
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });

            // Limpiar el indicador de escritura
            const typingElement = chatHistory.querySelector('.agent-typing');
            if (typingElement && typingElement.dataset.interval) {
                clearInterval(parseInt(typingElement.dataset.interval));
            }
            showTypingIndicator(false);

            if (!response.ok) {
                const errorData = await response.json();
                addMessageToHistory(errorData.error || `❌ Error: ${response.status}`, 'agent');
                return;
            }

            const data = await response.json();

            if (data.response) {
                addMessageToHistory(data.response, 'agent');
            } else if (data.error) {
                addMessageToHistory('❌ ' + data.error, 'agent');
            }

        } catch (error) {
            const typingElement = chatHistory.querySelector('.agent-typing');
            if (typingElement && typingElement.dataset.interval) {
                clearInterval(parseInt(typingElement.dataset.interval));
            }
            showTypingIndicator(false);

            console.error('Error en fetch:', error);
            addMessageToHistory('❌ Error de conexión. Por favor, intenta de nuevo.', 'agent');
        }
    }

    // ✅ MEJORA: Atajos de teclado
    document.addEventListener('keydown', (e) => {
        // ESC para cerrar el chat
        if (e.key === 'Escape' && bocadillo.classList.contains('visible')) {
            bocadillo.classList.remove('visible');
        }

        // Ctrl/Cmd + K para abrir el chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (!bocadillo.classList.contains('visible')) {
                toggleBocadillo();
            }
        }
    });

    // ✅ MEJORA: Mensaje de bienvenida personalizado según la hora
    function updateWelcomeMessage() {
        const hour = new Date().getHours();
        let greeting = '¡Hola!';

        if (hour >= 5 && hour < 12) {
            greeting = '¡Buenos días!';
        } else if (hour >= 12 && hour < 19) {
            greeting = '¡Buenas tardes!';
        } else {
            greeting = '¡Buenas noches!';
        }

        const firstMessage = chatHistory.querySelector('.sofia-message.agent');
        if (firstMessage && firstMessage.textContent.includes('¡Hola!')) {
            firstMessage.textContent = `${greeting} Soy Sofía. ¿En qué puedo ayudarte hoy?`;
        }
    }

    updateWelcomeMessage();

    const btnOcultar = document.getElementById("btn-activar-sofia")
    const contenido = document.getElementById("avatar-flotante")

    btnOcultar.addEventListener("click", () => {
        contenido.classList.toggle("contenido-oculto")
    })
}); // Fin de DOMContentLoaded

