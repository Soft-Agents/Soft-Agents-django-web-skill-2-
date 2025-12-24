// Integración específica para skill.html
if (typeof SkillPageIntegration === 'undefined') {
class SkillPageIntegration {
  constructor() {
    this.videoCallControls = null;
    this.videoCallChat = null;
    this.isChatOpen = false;
    
    this.initializeIntegration();
  }

  initializeIntegration() {
    // Esperar a que el DOM esté completamente cargado
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    // Inicializar controles de videollamada
    this.videoCallControls = new VideoCallControls();
    
    // Inicializar chat
    this.videoCallChat = new VideoCallChat();
    
    // Configurar funcionalidad del chat toggle
    this.setupChatToggle();
    
    // Configurar fecha y hora
    this.setupDateTime();
    
    // Configurar animaciones de participantes
    this.setupParticipantAnimations();
    
    // Mensaje de bienvenida del agente
    setTimeout(() => {
      if (this.videoCallChat) {
        this.videoCallChat.addMessage('Agente Cricker', '¡Hola! Bienvenido a la sesión de mejora de habilidades blandas. Hoy trabajaremos en el pensamiento crítico. ¿Estás listo para comenzar?', 'blue', new Date());
        
        // Activar efecto aurora brevemente para el mensaje de bienvenida
        this.showAgentActivityBurst();
      }
    }, 2000);
    
    console.log('Integración de skill.html completada');
  }

  setupChatToggle() {
    const chatToggleButton = document.getElementById('chat-toggle-button');
    const chatModal = document.getElementById('chat-modal');
    const closeChatButton = document.getElementById('close-chat');
    
    if (!chatToggleButton || !chatModal || !closeChatButton) {
      console.error('Elementos del chat no encontrados');
      return;
    }

    // Abrir chat
    chatToggleButton.addEventListener('click', () => {
      this.openChat();
    });
    
    // Cerrar chat
    closeChatButton.addEventListener('click', () => {
      this.closeChat();
    });
    
    // Cerrar chat con Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isChatOpen) {
        this.closeChat();
      }
    });
  }

  openChat() {
    const chatModal = document.getElementById('chat-modal');
    const chatToggleButton = document.getElementById('chat-toggle-button');
    
    chatModal.classList.remove('translate-x-full');
    chatModal.classList.add('translate-x-0');
    
    // Cambiar el color del botón para indicar que está activo
    chatToggleButton.classList.add('bg-blue-600');
    chatToggleButton.classList.remove('bg-gray-700');
    
    this.isChatOpen = true;
    
    // Focus en el input del chat
    setTimeout(() => {
      const messageInput = document.getElementById('message-input');
      if (messageInput) {
        messageInput.focus();
      }
    }, 300);
  }

  closeChat() {
    const chatModal = document.getElementById('chat-modal');
    const chatToggleButton = document.getElementById('chat-toggle-button');
    
    chatModal.classList.add('translate-x-full');
    chatModal.classList.remove('translate-x-0');
    
    // Restaurar el color original del botón
    chatToggleButton.classList.remove('bg-blue-600');
    chatToggleButton.classList.add('bg-gray-700');
    
    this.isChatOpen = false;
  }

  setupDateTime() {
    function updateDateTime() {
      const now = new Date();
      const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      const dateTimeString = now.toLocaleDateString('es-ES', options);
      const dateTimeDisplay = document.getElementById('datetime-display');
      if (dateTimeDisplay) {
        dateTimeDisplay.textContent = dateTimeString;
      }
    }
    
    // Actualizar inmediatamente y luego cada minuto
    updateDateTime();
    setInterval(updateDateTime, 60000);
  }

  setupParticipantAnimations() {
    const participantCards = document.querySelectorAll('.personality-card');
    
    participantCards.forEach((card, index) => {
      // Agregar efecto de hover mejorado
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'scale(1.02) translateY(-5px)';
        card.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.4)';
      });
      
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'scale(1) translateY(0)';
        card.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
      });
      
      // Animación de entrada escalonada
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, index * 200);
    });
  }

  // Método para agregar notificaciones del sistema
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
    
    // Colores según el tipo
    const colors = {
      info: 'bg-blue-600 text-white',
      success: 'bg-green-600 text-white',
      warning: 'bg-yellow-600 text-black',
      error: 'bg-red-600 text-white'
    };
    
    notification.className += ` ${colors[type] || colors.info}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
      notification.classList.add('translate-x-0');
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
      notification.classList.add('translate-x-full');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }

  // Método para mostrar un burst de actividad del agente
  showAgentActivityBurst() {
    const agentCard = document.getElementById('agente-cricker-card');
    const speakingIndicator = document.getElementById('speaking-indicator');
    const personalityIndicator = agentCard?.querySelector('.personality-indicator');

    if (agentCard) {
      // Activar efecto brevemente
      agentCard.classList.add('agent-speaking');
      if (speakingIndicator) {
        speakingIndicator.classList.add('speaking-active');
      }
      if (personalityIndicator) {
        personalityIndicator.classList.add('speaking-indicator-pulse');
      }

      // Desactivar después de 2 segundos
      setTimeout(() => {
        agentCard.classList.remove('agent-speaking');
        if (speakingIndicator) {
          speakingIndicator.classList.remove('speaking-active');
        }
        if (personalityIndicator) {
          personalityIndicator.classList.remove('speaking-indicator-pulse');
        }
      }, 2000);
    }
  }

  // Método para simular actividad de participantes
  simulateParticipantActivity() {
    const indicators = document.querySelectorAll('.personality-indicator');
    
    setInterval(() => {
      indicators.forEach(indicator => {
        // Cambiar color aleatoriamente para simular actividad
        const colors = ['bg-green-500', 'bg-yellow-500', 'bg-blue-500'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        
        indicator.className = indicator.className.replace(/bg-\w+-\d+/, randomColor);
      });
    }, 5000);
  }
}

}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  if (!window.skillPageIntegration) {
    window.skillPageIntegration = new SkillPageIntegration();
  }
});