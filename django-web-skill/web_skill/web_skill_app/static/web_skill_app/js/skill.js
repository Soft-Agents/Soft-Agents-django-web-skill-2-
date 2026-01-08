/*
  skill.js
  Lógica de la UI para la página de Pizarra de Práctica (skill.html)
  Maneja 2 chats independientes: Coach (teoría) y Criker (práctica)
*/

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Pizarra de Casos de Uso con 2 chats lista.");

  // Verificar que la variable CURRENT_USER_ID esté disponible
  if (typeof CURRENT_USER_ID === 'undefined') {
    console.error("❌ ERROR: CURRENT_USER_ID no está definido. Verifica skill.html");
    return;
  }

  console.log(`👤 Usuario actual: ${CURRENT_USER_ID}`);

  // --- Referencias a elementos del DOM ---
  const sendButtonCoach = document.getElementById("send-button-coach");
  const messageInputCoach = document.getElementById("message-input-coach");
  const chatMessagesCoach = document.getElementById("chat-messages-coach");

  const sendButtonCriker = document.getElementById("send-button-criker");
  const messageInputCriker = document.getElementById("message-input-criker");
  const chatMessagesCriker = document.getElementById("chat-messages-criker");

  const micButtonCoach = document.getElementById("mic-button-coach");
  const micButtonCriker = document.getElementById("mic-button-criker");

  // --- Configuración de Voz (Web Speech API) ---
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;
  const synthesis = window.speechSynthesis;
  let activeMicAgent = null; // 'coach' o 'criker'

  if (recognition) {
    recognition.lang = 'es-MX';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      console.log(`🎙️ Grabación iniciada para: ${activeMicAgent}`);
      if (activeMicAgent === 'coach') {
        micButtonCoach.classList.add('text-red-500', 'animate-pulse');
      } else if (activeMicAgent === 'criker') {
        micButtonCriker.classList.add('text-red-500', 'animate-pulse');
      }
    };

    recognition.onend = () => {
      console.log("🎙️ Grabación finalizada.");
      micButtonCoach.classList.remove('text-red-500', 'animate-pulse');
      micButtonCriker.classList.remove('text-red-500', 'animate-pulse');
      activeMicAgent = null;
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log(`🗣️ Texto reconocido: "${transcript}"`);

      if (activeMicAgent === 'coach') {
        messageInputCoach.value = transcript;
        sendButtonCoach.click();
      } else if (activeMicAgent === 'criker') {
        messageInputCriker.value = transcript;
        sendButtonCriker.click();
      }
    };

    recognition.onerror = (event) => {
      console.error("❌ Error en reconocimiento de voz:", event.error);
      activeMicAgent = null;
    };
  }

  function toggleMic(agent) {
    if (!recognition) {
      alert("Tu navegador no soporta reconocimiento de voz.");
      return;
    }

    if (activeMicAgent === agent) {
      recognition.stop();
    } else {
      if (activeMicAgent) recognition.stop();
      activeMicAgent = agent;
      recognition.start();
    }
  }

  function speakText(text) {
    if (!synthesis) return;
    // Cancelar cualquier habla previa
    synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-MX';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    synthesis.speak(utterance);
  }

  // --- Función para agregar mensajes al chat ---
  function addMessageToChat(chatContainer, role, message) {
    // Remover placeholder si existe
    const placeholder = chatContainer.querySelector('.chat-placeholder');
    if (placeholder) {
      placeholder.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'agent-message');

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');
    messageBubble.textContent = message;

    // Agregar botón de copiar para mensajes del agente
    if (role !== 'user') {
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-button';
      copyBtn.innerHTML = `
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
        </svg>
        <span>Copiar</span>
      `;
      copyBtn.onclick = (e) => {
        e.stopPropagation();
        copyToClipboard(message, copyBtn);
      };
      messageBubble.appendChild(copyBtn);
    }

    messageDiv.appendChild(messageBubble);
    chatContainer.appendChild(messageDiv);

    // Auto-scroll al último mensaje
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // --- Función para copiar al portapapeles ---
  function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
      console.log("📋 Copiado al portapapeles");

      // Feedback visual
      const originalContent = buttonElement.innerHTML;
      buttonElement.innerHTML = `
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <span>¡Copiado!</span>
      `;
      buttonElement.classList.add('copied');

      setTimeout(() => {
        buttonElement.innerHTML = originalContent;
        buttonElement.classList.remove('copied');
      }, 2000);
    }).catch(err => {
      console.error("❌ Error al copiar:", err);
    });
  }

  // --- Función para mostrar indicador de "escribiendo..." ---
  function showTypingIndicator(chatContainer) {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('chat-message', 'agent-message', 'typing-indicator');
    typingDiv.innerHTML = '<div class="message-bubble">●●●</div>';
    typingDiv.id = 'typing-indicator';
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  // --- Función principal para enviar mensajes ---
  async function sendMessage(agentTarget, message, chatContainer) {
    if (!message.trim()) {
      console.warn("⚠️ Mensaje vacío, no se enviará.");
      return;
    }

    console.log(`📤 Enviando mensaje a ${agentTarget}: "${message}"`);

    // Agregar mensaje del usuario al chat
    addMessageToChat(chatContainer, 'user', message);

    // Mostrar indicador de "escribiendo..."
    showTypingIndicator(chatContainer);

    try {
      // Hacer la petición POST al endpoint de Django
      const response = await fetch('/api/skill_chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // Django CSRF protection
        },
        body: JSON.stringify({
          user_id: CURRENT_USER_ID,
          message: message,
          agent_target: agentTarget // 'coach' o 'criker'
        })
      });

      // Remover indicador de "escribiendo..."
      removeTypingIndicator();

      // Verificar si la respuesta es exitosa
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log(`📥 Respuesta recibida de ${agentTarget}:`, data);

      // --- Procesar respuesta según el tipo ---
      if (data.type === "chat") {
        // Respuesta de texto normal
        addMessageToChat(chatContainer, 'agent', data.content);
        // speakText(data.content); // Desactivado por solicitud del usuario
        console.log(`💬 Mensaje de chat agregado para ${agentTarget}`);

      } else if (data.type === "CASO_USO") {
        // Respuesta JSON (Caso de Uso)
        console.log("🎯 Caso de Uso detectado. Mostrando en pantalla...");

        // Informar al usuario en el chat
        addMessageToChat(chatContainer, 'agent', '✅ Caso de uso generado. Revisa el área central.');

        // Mostrar el caso de uso en el área central
        window.mostrarCasoDeUso(data.data_caso);

      } else {
        console.warn("⚠️ Tipo de respuesta desconocido:", data);
        addMessageToChat(chatContainer, 'agent', 'Lo siento, recibí una respuesta inesperada.');
      }

    } catch (error) {
      console.error(`❌ Error al comunicarse con ${agentTarget}:`, error);
      removeTypingIndicator();

      let errorMessage = 'Lo siento, hubo un error al procesar tu mensaje.';
      if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Error de conexión. Verifica tu internet.';
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }

      addMessageToChat(chatContainer, 'agent', errorMessage);
    }
  }

  // --- Función auxiliar para obtener el CSRF token ---
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

  // --- Función para mostrar Caso de Uso en el área central ---
  window.mostrarCasoDeUso = function (data) {
    console.log("🎨 Mostrando caso de uso en área central:", data);

    // Ocultar pantalla de bienvenida
    const pantallaBienvenida = document.getElementById("pantalla-bienvenida");
    if (pantallaBienvenida) {
      pantallaBienvenida.classList.add("hidden");
    }

    // Mostrar área de caso de uso
    const areaCasoUso = document.getElementById("area-caso-uso");
    if (areaCasoUso) {
      areaCasoUso.classList.remove("hidden");
    }

    // Rellenar título y prólogo
    const tituloCaso = document.getElementById("titulo-caso");
    if (tituloCaso) {
      tituloCaso.textContent = data.titulo_caso || "Caso de Uso";
    }

    const prologoTexto = document.getElementById("prologo-texto");
    if (prologoTexto) {
      prologoTexto.textContent = data.prologo_escenario || "";
    }

    // Rellenar personaje 1
    if (data.personajes && data.personajes[0]) {
      const name1 = document.getElementById("name-1");
      const logo1 = document.getElementById("logo-1");

      if (name1) name1.textContent = data.personajes[0].nombre;
      if (logo1) logo1.textContent = data.personajes[0].nombre.charAt(0).toUpperCase();
    }

    // Rellenar personaje 2
    if (data.personajes && data.personajes[1]) {
      const name2 = document.getElementById("name-2");
      const logo2 = document.getElementById("logo-2");

      if (name2) name2.textContent = data.personajes[1].nombre;
      if (logo2) logo2.textContent = data.personajes[1].nombre.charAt(0).toUpperCase();
    }

    // Rellenar diálogos con números de secuencia
    const bubble1 = document.getElementById("bubble-1");
    const bubble2 = document.getElementById("bubble-2");
    const sequence1 = document.getElementById("sequence-1");
    const sequence2 = document.getElementById("sequence-2");

    if (bubble1 && data.dialogo && data.personajes && data.personajes[0]) {
      // Crear array con índice global para mostrar orden cronológico
      const mensajesConOrden = data.dialogo
        .map((d, index) => ({ ...d, orden: index + 1 })) // Agregar número de orden global
        .filter(d => d.id_personaje === data.personajes[0].id); // Filtrar por personaje 1

      // Generar HTML con badges de secuencia
      const lineasHTML1 = mensajesConOrden
        .map(d => `
          <div class="mb-3">
            <span class="inline-block px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded-full mb-1">#${d.orden}</span>
            <p class="text-slate-200">${d.linea}</p>
          </div>
        `)
        .join('');

      bubble1.innerHTML = lineasHTML1 || "";

      // Actualizar badge principal con el primer número
      if (sequence1 && mensajesConOrden.length > 0) {
        sequence1.textContent = mensajesConOrden[0].orden;
      }
    }

    if (bubble2 && data.dialogo && data.personajes && data.personajes[1]) {
      // Crear array con índice global para mostrar orden cronológico
      const mensajesConOrden = data.dialogo
        .map((d, index) => ({ ...d, orden: index + 1 })) // Agregar número de orden global
        .filter(d => d.id_personaje === data.personajes[1].id); // Filtrar por personaje 2

      // Generar HTML con badges de secuencia (color rosa para personaje 2)
      const lineasHTML2 = mensajesConOrden
        .map(d => `
          <div class="mb-3">
            <span class="inline-block px-2 py-1 bg-pink-600 text-white text-xs font-bold rounded-full mb-1">#${d.orden}</span>
            <p class="text-slate-200">${d.linea}</p>
          </div>
        `)
        .join('');

      bubble2.innerHTML = lineasHTML2 || "";

      // Actualizar badge principal con el primer número
      if (sequence2 && mensajesConOrden.length > 0) {
        sequence2.textContent = mensajesConOrden[0].orden;
      }
    }

    // Rellenar preguntas
    const listaPreguntas = document.getElementById("lista-preguntas");
    if (listaPreguntas) {
      listaPreguntas.innerHTML = "";

      if (data.preguntas_para_usuario && Array.isArray(data.preguntas_para_usuario)) {
        data.preguntas_para_usuario.forEach((pregunta) => {
          const li = document.createElement("li");
          li.textContent = pregunta;
          listaPreguntas.appendChild(li);
        });
      }
    }

    console.log("✅ Caso de uso renderizado correctamente.");
  };

  // --- Event Listeners para COACH ---
  if (sendButtonCoach && messageInputCoach && chatMessagesCoach) {
    sendButtonCoach.addEventListener("click", () => {
      const message = messageInputCoach.value;
      sendMessage('coach', message, chatMessagesCoach);
      messageInputCoach.value = "";
    });

    messageInputCoach.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendButtonCoach.click();
      }
    });

    micButtonCoach?.addEventListener("click", () => toggleMic('coach'));

    // Auto-resize para textarea
    messageInputCoach.addEventListener("input", function () {
      this.style.height = '40px'; // Reset to min-height
      let newHeight = Math.min(this.scrollHeight, 100);
      this.style.height = newHeight + 'px';

      if (this.scrollHeight > 100) {
        this.style.overflowY = 'auto';
      } else {
        this.style.overflowY = 'hidden';
      }
    });

    console.log("✅ Event listeners de Coach configurados.");
  } else {
    console.error("❌ No se encontraron elementos del chat de Coach.");
  }

  // --- Event Listeners para CRIKER ---
  if (sendButtonCriker && messageInputCriker && chatMessagesCriker) {
    sendButtonCriker.addEventListener("click", () => {
      const message = messageInputCriker.value;
      sendMessage('criker', message, chatMessagesCriker);
      messageInputCriker.value = "";
    });

    messageInputCriker.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendButtonCriker.click();
      }
    });

    micButtonCriker?.addEventListener("click", () => toggleMic('criker'));

    // Auto-resize para textarea
    messageInputCriker.addEventListener("input", function () {
      this.style.height = '40px'; // Reset to min-height
      let newHeight = Math.min(this.scrollHeight, 100);
      this.style.height = newHeight + 'px';

      if (this.scrollHeight > 100) {
        this.style.overflowY = 'auto';
      } else {
        this.style.overflowY = 'hidden';
      }
    });

    console.log("✅ Event listeners de Criker configurados.");
  } else {
    console.error("❌ No se encontraron elementos del chat de Criker.");
  }

  console.log("🚀 skill.js cargado completamente.");
});