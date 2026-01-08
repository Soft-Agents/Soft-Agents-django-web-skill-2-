// Marco simple estilo Google Meet
class GoogleMeetFrame {
  constructor() {
    this.isListening = false;
    this.audioContext = null;
    this.analyser = null;
    this.microphone = null;
    this.stream = null;
    this.animationFrame = null;
    
    this.setupStyles();
    this.init();
  }

  // Agregar estilos CSS para el marco
  setupStyles() {
    const style = document.createElement('style');
    style.id = 'google-meet-styles';
    style.textContent = `
      /* Marco para Agente Cricker (azul) */
      .speaking-frame-agent {
        border: 3px solid #1a73e8 !important;
        box-shadow: 0 0 0 1px rgba(26, 115, 232, 0.4) !important;
        transition: all 0.2s ease !important;
      }
      
      /* Marco para Coach (verde/amarillo) */
      .speaking-frame-coach {
        border: 3px solid #eab308 !important;
        box-shadow: 0 0 0 1px rgba(234, 179, 8, 0.4) !important;
        transition: all 0.2s ease !important;
      }
      
      /* Marco para Usuario (púrpura) */
      .speaking-frame-user {
        border: 3px solid #a855f7 !important;
        box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.4) !important;
        transition: all 0.2s ease !important;
      }
    `;
    
    // Remover estilo anterior si existe
    const existingStyle = document.getElementById('google-meet-styles');
    if (existingStyle) existingStyle.remove();
    
    document.head.appendChild(style);
  }

  async init() {
    try {
      console.log('🎤 Iniciando detección de micrófono...');
      
      // Solicitar acceso al micrófono
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      });

      // Configurar análisis de audio
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.microphone = this.audioContext.createMediaStreamSource(this.stream);
      
      this.microphone.connect(this.analyser);
      this.analyser.fftSize = 256;
      this.analyser.smoothingTimeConstant = 0.8;

      console.log('✅ Micrófono conectado. Habla para ver el marco.');
      
      this.startDetection();
      
    } catch (error) {
      console.error('❌ Error al acceder al micrófono:', error);
      if (error.name === 'NotAllowedError') {
        alert('Por favor, permite el acceso al micrófono para usar esta función.');
      }
    }
  }

  startDetection() {
    if (!this.analyser) return;
    
    this.isListening = true;
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    let isSpeaking = false;
    
    const detect = () => {
      if (!this.isListening) return;
      
      this.analyser.getByteFrequencyData(dataArray);
      
      // Calcular nivel de audio
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const level = sum / dataArray.length;
      
      // Umbral para detectar habla (ajustable)
      const threshold = 15;
      
      if (level > threshold) {
        if (!isSpeaking) {
          console.log('🎤 Hablando - Activando marco');
          this.activateFrame();
          isSpeaking = true;
        }
      } else {
        if (isSpeaking) {
          console.log('🔇 Silencio - Desactivando marco');
          this.deactivateFrame();
          isSpeaking = false;
        }
      }
      
      this.animationFrame = requestAnimationFrame(detect);
    };
    
    detect();
  }

  activateFrame() {
    // Buscar el card del usuario (participante de la llamada)
    const userCard = document.getElementById('usuario-participante-card');
    if (userCard) {
      userCard.classList.add('speaking-frame-user');
    }
  }

  deactivateFrame() {
    const userCard = document.getElementById('usuario-participante-card');
    if (userCard) {
      userCard.classList.remove('speaking-frame-user');
    }
  }

  // Activar marco del Agente Cricker
  activateAgentFrame() {
    const agentCard = document.getElementById('agente-cricker-card');
    if (agentCard) {
      agentCard.classList.add('speaking-frame-agent');
    }
  }

  deactivateAgentFrame() {
    const agentCard = document.getElementById('agente-cricker-card');
    if (agentCard) {
      agentCard.classList.remove('speaking-frame-agent');
    }
  }

  // Activar marco del Coach
  activateCoachFrame() {
    const coachCard = document.getElementById('coach-card');
    if (coachCard) {
      coachCard.classList.add('speaking-frame-coach');
    }
  }

  deactivateCoachFrame() {
    const coachCard = document.getElementById('coach-card');
    if (coachCard) {
      coachCard.classList.remove('speaking-frame-coach');
    }
  }

  stop() {
    this.isListening = false;
    
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
    
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    
    this.deactivateFrame();
    console.log('🔇 Detección detenida');
  }

  // Ajustar sensibilidad
  setThreshold(newThreshold) {
    this.threshold = newThreshold;
    console.log('🔧 Nueva sensibilidad:', newThreshold);
  }
}

// Funciones globales simples
let googleMeetFrame = null;

function startGoogleMeetFrame() {
  if (googleMeetFrame) {
    googleMeetFrame.stop();
  }
  googleMeetFrame = new GoogleMeetFrame();
}

function stopGoogleMeetFrame() {
  if (googleMeetFrame) {
    googleMeetFrame.stop();
    googleMeetFrame = null;
  }
}

// Funciones para activar marcos individuales
function activateAgentSpeaking() {
  const agentCard = document.getElementById('agente-cricker-card');
  if (agentCard) {
    agentCard.classList.add('speaking-frame-agent');
    console.log('🎤 Marco del Agente Cricker activado');
  }
}

function deactivateAgentSpeaking() {
  const agentCard = document.getElementById('agente-cricker-card');
  if (agentCard) {
    agentCard.classList.remove('speaking-frame-agent');
    console.log('🔇 Marco del Agente Cricker desactivado');
  }
}

function activateCoachSpeaking() {
  const coachCard = document.getElementById('coach-card');
  if (coachCard) {
    coachCard.classList.add('speaking-frame-coach');
    console.log('🎤 Marco del Coach activado');
  }
}

function deactivateCoachSpeaking() {
  const coachCard = document.getElementById('coach-card');
  if (coachCard) {
    coachCard.classList.remove('speaking-frame-coach');
    console.log('🔇 Marco del Coach desactivado');
  }
}

function activateUserSpeaking() {
  const userCard = document.getElementById('usuario-participante-card');
  if (userCard) {
    userCard.classList.add('speaking-frame-user');
    console.log('🎤 Marco del Usuario activado');
  }
}

function deactivateUserSpeaking() {
  const userCard = document.getElementById('usuario-participante-card');
  if (userCard) {
    userCard.classList.remove('speaking-frame-user');
    console.log('🔇 Marco del Usuario desactivado');
  }
}

// Funciones de prueba
function testAllFrames() {
  console.log('🧪 Probando todos los marcos...');
  
  // Agente Cricker (azul)
  activateAgentSpeaking();
  setTimeout(() => {
    deactivateAgentSpeaking();
    
    // Coach (amarillo)
    activateCoachSpeaking();
    setTimeout(() => {
      deactivateCoachSpeaking();
      
      // Usuario (púrpura)
      activateUserSpeaking();
      setTimeout(() => {
        deactivateUserSpeaking();
        console.log('✅ Prueba de marcos completada');
      }, 1000);
    }, 1000);
  }, 1000);
}

// Hacer funciones disponibles globalmente
window.startGoogleMeetFrame = startGoogleMeetFrame;
window.stopGoogleMeetFrame = stopGoogleMeetFrame;
window.activateAgentSpeaking = activateAgentSpeaking;
window.deactivateAgentSpeaking = deactivateAgentSpeaking;
window.activateCoachSpeaking = activateCoachSpeaking;
window.deactivateCoachSpeaking = deactivateCoachSpeaking;
window.activateUserSpeaking = activateUserSpeaking;
window.deactivateUserSpeaking = deactivateUserSpeaking;
window.testAllFrames = testAllFrames;

// Inicializar automáticamente cuando la página cargue
document.addEventListener('DOMContentLoaded', () => {
  console.log('🎯 Marco de Google Meet listo.');
  console.log('📝 Ejecuta startGoogleMeetFrame() para activar');
  console.log('📝 Ejecuta stopGoogleMeetFrame() para desactivar');
});
// Int
egrar con TTS del agente
function setupTTSIntegration() {
  if (window.speechSynthesis) {
    const originalSpeak = window.speechSynthesis.speak;
    
    window.speechSynthesis.speak = function(utterance) {
      console.log('🎤 TTS iniciado - Activando marco del agente');
      activateAgentSpeaking();
      
      const originalOnEnd = utterance.onend;
      const originalOnError = utterance.onerror;
      
      utterance.onend = function(event) {
        console.log('🔇 TTS terminado - Desactivando marco del agente');
        deactivateAgentSpeaking();
        if (originalOnEnd) originalOnEnd.call(this, event);
      };
      
      utterance.onerror = function(event) {
        console.log('❌ Error en TTS - Desactivando marco del agente');
        deactivateAgentSpeaking();
        if (originalOnError) originalOnError.call(this, event);
      };
      
      return originalSpeak.call(this, utterance);
    };
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  console.log('🎯 Marco de Google Meet listo para TODAS las tarjetas.');
  console.log('📝 Ejecuta startGoogleMeetFrame() para activar detección de micrófono');
  console.log('📝 Ejecuta testAllFrames() para probar todos los marcos');
  
  // Configurar integración con TTS
  setTimeout(setupTTSIntegration, 1000);
});