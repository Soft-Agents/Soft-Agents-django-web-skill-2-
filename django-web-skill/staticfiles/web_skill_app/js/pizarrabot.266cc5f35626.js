// Contenido fusionado de api.js
// Configuración de la API
const getApiBaseUrl = () => {
  const storedUrl = localStorage.getItem('agent_api_url');
  return storedUrl || 'https://se-agent-knowledge-v1-178017465262.us-central1.run.app'; // URL actualizada para el cuadro de diálogo grande
};

// Generar un ID de usuario único para la sesión
const generateUserId = () => {
  const storedUserId = localStorage.getItem('agent_user_id');
  if (storedUserId) {
    return storedUserId;
  }

  const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem('agent_user_id', newUserId);
  return newUserId;
};

// Función para enviar mensaje al agente
const sendMessage = async (message) => {
  const userId = generateUserId();
  const API_BASE_URL = getApiBaseUrl();

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message: message,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error HTTP ${response.status}: ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error al enviar el mensaje:', error);
    throw new Error('No se pudo conectar con el servidor.');
  }
};

// Función para verificar la conexión con la API
const checkApiConnection = async () => {
  const API_BASE_URL = getApiBaseUrl();

  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch (error) {
    console.error('Error verificando conexión:', error);
    return false;
  }
};

// Función para obtener el historial de conversación (si está disponible)
const getConversationHistory = async () => {
  const userId = generateUserId();
  const API_BASE_URL = getApiBaseUrl();

  try {
    const response = await fetch(`${API_BASE_URL}/history/${userId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    return data.history || [];
  } catch (error) {
    console.error('Error obteniendo historial:', error);
    return [];
  }
};

// Contenido original de pizarrabot.js
document.addEventListener("DOMContentLoaded", () => {
  const professorAvatar = document.getElementById("professor-avatar");
  const chatModal = document.getElementById("chat-modal");
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");
  const chatHistory = document.getElementById("chat-history");
  const whiteboardInput = document.getElementById("whiteboard-input");
  const whiteboardSend = document.getElementById("whiteboard-send");
  const whiteboardContent = document.getElementById("whiteboard-content");

  // URL para el cuadro de diálogo grande (Whiteboard)
  //const API_URL_WHITEBOARD = "https://se-agent-knowledge-v1-178017465262.us-central1.run.app";
  //  const API_URL_WHITEBOARD = "https://se-agent-knowledge-v1-178017465262.us-central1.run.app";

  // URL para el cuadro de diálogo pequeño (Chat Modal)
  const API_URL_CHAT_MODAL = "https://se-agent-knowledge-v1-178017465262.us-central1.run.app";

  //  const API_URL_CHAT_MODAL = "https://se-agent-criker-178017465262.us-central1.run.app";

  /**
   * Envía un mensaje a la API del agente.
   * @param {string} message - El mensaje del usuario.
   * @param {string} apiUrl - La URL de la API.
   * @returns {Promise<string>} La respuesta del agente.
   */
  async function sendMessageToAPI(message, apiUrl) {
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Error HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.response; // Ajustar a la estructura de la respuesta de tu API
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
      throw new Error('No se pudo conectar con el servidor.');
    }
  }

  // Lógica para el avatar del profesor
  if (professorAvatar) {
    professorAvatar.addEventListener("click", () => {
      chatModal.classList.toggle("hidden");
      // Cargar historial de conversación al abrir el modal
      getConversationHistory().then(history => {
        chatHistory.innerHTML = ""; // Limpiar el historial
        history.forEach(item => {
          appendMessage(`Tú: ${item.user_message}`);
          appendMessage(`Profesor IA: ${item.agent_response}`);
        });
      });
    });
  }

  // Lógica para el botón de enviar en el chat
  if (chatSend) {
    chatSend.addEventListener("click", async () => {
      const userMessage = chatInput.value.trim();
      if (userMessage === "") return;

      chatSend.disabled = true; // Deshabilitar el botón de envío
      appendMessage(`Tú: ${userMessage}`);

      const thinkingDiv = document.createElement("div");
      thinkingDiv.textContent = "...pensando";
      thinkingDiv.className = "text-gray-400 italic mb-2";
      chatHistory.appendChild(thinkingDiv);

      try {
        const agentResponse = await sendMessageToAPI(userMessage, API_URL_CHAT_MODAL);
        chatHistory.removeChild(thinkingDiv); // Eliminar indicador "...pensando"

        const agentMessageDiv = document.createElement("div");
        agentMessageDiv.className = "p-2 bg-green-100 rounded-lg mb-2 text-gray-800";
        chatHistory.appendChild(agentMessageDiv);

        simulateTyping(agentMessageDiv, `Profesor IA: ${agentResponse}`); // Simular tipeo
      } catch (error) {
        chatHistory.removeChild(thinkingDiv); // Eliminar indicador "...pensando"

        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.textContent = `Error: ${error.message}`;
        errorMessageDiv.className = "text-red-500 bg-gray-800 p-2 rounded mb-2";
        chatHistory.appendChild(errorMessageDiv);
      } finally {
        chatSend.disabled = false; // Habilitar el botón de envío
        chatInput.value = ""; // Limpiar el cuadro de entrada
      }
    });
  }

  // Funcionalidad de la pizarra
  if (whiteboardSend) {
    whiteboardSend.addEventListener("click", async () => {
      const userPrompt = whiteboardInput.value.trim();
      if (userPrompt === "") return;

      whiteboardSend.disabled = true;
      whiteboardContent.textContent = "Cargando respuesta...";

      try {
        const agentResponse = await sendMessageToAPI(userPrompt, API_URL_WHITEBOARD);
        whiteboardContent.textContent = agentResponse;
      } catch (error) {
        whiteboardContent.textContent = `Error: ${error.message}`;
        console.error("Error en la pizarra:", error);
      } finally {
        whiteboardSend.disabled = false;
      }
    });
  }

  function appendMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "mb-2 text-gray-800";
    messageDiv.textContent = message;
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function simulateTyping(element, text) {
    let i = 0;
    element.textContent = '';
    const interval = setInterval(() => {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
        chatHistory.scrollTop = chatHistory.scrollHeight;
      } else {
        clearInterval(interval);
      }
    }, 50);
  }
});