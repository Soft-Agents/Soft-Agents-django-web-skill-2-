// Video Call Controls - Funcionalidades de los botones de llamada
if (typeof VideoCallControls === 'undefined') {
class VideoCallControls {
  constructor() {
    this.isMuted = false;
    this.isVideoOn = true;
    this.isScreenSharing = false;
    this.isMoreOptionsOpen = false;
    this.mediaStream = null;
    this.screenStream = null;
    this.audioContext = null;
    this.analyser = null;
    this.microphone = null;
    this.dataArray = null;
    this.animationId = null;
    
    this.initializeControls();
  }

  initializeControls() {
    // Referencias a los botones
    this.micButton = document.getElementById('mic-button');
    this.cameraButton = document.getElementById('camera-button');
    this.screenShareButton = document.getElementById('screen-share-button');
    this.moreOptionsButton = document.getElementById('more-options-button');
    this.endCallButton = document.getElementById('end-call-button');
    this.moreOptionsMenu = document.getElementById('more-options-menu');

    // Agregar event listeners
    this.setupEventListeners();
    
    console.log('Controles de videollamada inicializados correctamente');
  }

  setupEventListeners() {
    // Botón de micrófono
    this.micButton?.addEventListener('click', () => this.toggleMicrophone());
    
    // Botón de cámara
    this.cameraButton?.addEventListener('click', () => this.toggleCamera());
    
    // Botón de compartir pantalla
    this.screenShareButton?.addEventListener('click', () => this.toggleScreenShare());
    
    // Botón de más opciones
    this.moreOptionsButton?.addEventListener('click', () => this.toggleMoreOptions());
    
    // Botón de salir de llamada
    this.endCallButton?.addEventListener('click', () => this.endCall());

    // Event listeners para las opciones del menú
    this.setupMoreOptionsListeners();

    // Cerrar menú de más opciones al hacer clic fuera
    document.addEventListener('click', (e) => {
      if (!this.moreOptionsMenu?.contains(e.target) && !this.moreOptionsButton?.contains(e.target)) {
        this.closeMoreOptions();
      }
    });
  }

  setupMoreOptionsListeners() {
    // Botón "Ver participantes"
    const viewParticipantsBtn = this.moreOptionsMenu?.querySelector('button:nth-child(1)');
    viewParticipantsBtn?.addEventListener('click', () => this.viewParticipants());

    // Botón "Configuración"
    const settingsBtn = this.moreOptionsMenu?.querySelector('button:nth-child(2)');
    settingsBtn?.addEventListener('click', () => this.openSettings());

    // Botón "Invitar personas"
    const inviteBtn = this.moreOptionsMenu?.querySelector('button:nth-child(3)');
    inviteBtn?.addEventListener('click', () => this.invitePeople());

    // Botón "Reportar problema"
    const reportBtn = this.moreOptionsMenu?.querySelector('button:nth-child(5)');
    reportBtn?.addEventListener('click', () => this.reportProblem());
  }

  async toggleMicrophone() {
    try {
      if (!this.isMuted) {
        // Silenciar micrófono
        await this.muteMicrophone();
      } else {
        // Activar micrófono
        await this.unmuteMicrophone();
      }
    } catch (error) {
      console.error('Error al controlar el micrófono:', error);
      this.showMicrophoneError();
    }
  }

  async muteMicrophone() {
    this.isMuted = true;
    
    // Detener el análisis de audio
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    // Silenciar el stream de audio
    if (this.mediaStream) {
      this.mediaStream.getAudioTracks().forEach(track => {
        track.enabled = false;
      });
    }
    
    this.updateMicrophoneUI();
    console.log('Micrófono silenciado');
  }

  async unmuteMicrophone() {
    try {
      // Solicitar acceso al micrófono
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      this.isMuted = false;
      
      // Configurar análisis de audio para indicador visual
      this.setupAudioAnalysis();
      
      this.updateMicrophoneUI();
      console.log('Micrófono activado');
    } catch (error) {
      console.error('Error al acceder al micrófono:', error);
      this.showMicrophoneError();
    }
  }

  setupAudioAnalysis() {
    if (!this.mediaStream) return;
    
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.analyser = this.audioContext.createAnalyser();
    this.microphone = this.audioContext.createMediaStreamSource(this.mediaStream);
    
    this.microphone.connect(this.analyser);
    this.analyser.fftSize = 256;
    
    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
    
    this.animateMicrophoneLevel();
  }

  animateMicrophoneLevel() {
    if (this.isMuted || !this.analyser) return;
    
    this.analyser.getByteFrequencyData(this.dataArray);
    
    // Calcular el nivel promedio de audio
    let sum = 0;
    for (let i = 0; i < this.dataArray.length; i++) {
      sum += this.dataArray[i];
    }
    const average = sum / this.dataArray.length;
    
    // Actualizar indicador visual del micrófono
    this.updateMicrophoneLevelIndicator(average);
    
    this.animationId = requestAnimationFrame(() => this.animateMicrophoneLevel());
  }

  updateMicrophoneLevelIndicator(level) {
    const micButton = this.micButton;
    if (!micButton) return;
    
    // Remover clases de nivel anterior
    micButton.classList.remove('ring-2', 'ring-green-400', 'ring-yellow-400', 'ring-red-400');
    
    if (level > 50) {
      micButton.classList.add('ring-2', 'ring-red-400');
    } else if (level > 20) {
      micButton.classList.add('ring-2', 'ring-yellow-400');
    } else if (level > 5) {
      micButton.classList.add('ring-2', 'ring-green-400');
    }
  }

  updateMicrophoneUI() {
    const micIcon = this.micButton.querySelector('svg');
    const micPath = micIcon.querySelector('path');
    
    if (this.isMuted) {
      // Icono de micrófono tachado
      micPath.setAttribute('d', 'M13.477 14.89A5 5 0 015 10V6a1 1 0 012 0v4a3 3 0 006 0V6a1 1 0 112 0v4a5 5 0 01-4.477 4.89M9 18v-2a1 1 0 00-2 0v2a1 1 0 102 0z');
      this.micButton.classList.add('bg-red-600');
      this.micButton.classList.remove('bg-gray-700');
      this.micButton.classList.remove('ring-2', 'ring-green-400', 'ring-yellow-400', 'ring-red-400');
    } else {
      // Icono de micrófono normal
      micPath.setAttribute('d', 'M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z');
      this.micButton.classList.remove('bg-red-600');
      this.micButton.classList.add('bg-gray-700');
    }
  }

  showMicrophoneError() {
    // Mostrar notificación de error
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    notification.textContent = 'Error: No se pudo acceder al micrófono';
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  async toggleCamera() {
    try {
      if (this.isVideoOn) {
        // Desactivar cámara
        await this.disableCamera();
      } else {
        // Activar cámara
        await this.enableCamera();
      }
    } catch (error) {
      console.error('Error al controlar la cámara:', error);
      this.showCameraError();
    }
  }

  async disableCamera() {
    this.isVideoOn = false;
    
    // Detener el stream de video
    if (this.mediaStream) {
      this.mediaStream.getVideoTracks().forEach(track => {
        track.enabled = false;
      });
    }
    
    this.updateCameraUI();
    console.log('Cámara desactivada');
  }

  async enableCamera() {
    try {
      // Solicitar acceso a la cámara
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 }
        },
        audio: false
      });
      
      this.isVideoOn = true;
      this.updateCameraUI();
      console.log('Cámara activada');
    } catch (error) {
      console.error('Error al acceder a la cámara:', error);
      this.showCameraError();
    }
  }

  updateCameraUI() {
    const cameraIcon = this.cameraButton.querySelector('svg');
    const cameraPath = cameraIcon.querySelector('path');
    
    if (!this.isVideoOn) {
      // Icono de cámara tachada
      cameraPath.setAttribute('d', 'M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z');
      this.cameraButton.classList.add('bg-red-600');
      this.cameraButton.classList.remove('bg-gray-700');
    } else {
      // Icono de cámara normal
      cameraPath.setAttribute('d', 'M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z');
      this.cameraButton.classList.remove('bg-red-600');
      this.cameraButton.classList.add('bg-gray-700');
    }
  }

  showCameraError() {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    notification.textContent = 'Error: No se pudo acceder a la cámara';
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  async toggleScreenShare() {
    try {
      if (this.isScreenSharing) {
        await this.stopScreenShare();
      } else {
        await this.startScreenShare();
      }
    } catch (error) {
      console.error('Error al compartir pantalla:', error);
      this.showScreenShareError();
    }
  }

  async startScreenShare() {
    try {
      // Solicitar acceso para compartir pantalla
      this.screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          cursor: 'always',
          displaySurface: 'monitor'
        },
        audio: true
      });

      this.isScreenSharing = true;
      this.updateScreenShareUI();
      
      // Manejar cuando el usuario detiene el compartir pantalla
      this.screenStream.getVideoTracks()[0].addEventListener('ended', () => {
        this.stopScreenShare();
      });

      console.log('Compartir pantalla activado');
    } catch (error) {
      if (error.name !== 'NotAllowedError') {
        console.error('Error al compartir pantalla:', error);
        this.showScreenShareError();
      }
    }
  }

  async stopScreenShare() {
    if (this.screenStream) {
      this.screenStream.getTracks().forEach(track => track.stop());
      this.screenStream = null;
    }
    
    this.isScreenSharing = false;
    this.updateScreenShareUI();
    console.log('Compartir pantalla desactivado');
  }

  updateScreenShareUI() {
    if (this.isScreenSharing) {
      this.screenShareButton.classList.add('bg-blue-600');
      this.screenShareButton.classList.remove('bg-gray-700');
    } else {
      this.screenShareButton.classList.remove('bg-blue-600');
      this.screenShareButton.classList.add('bg-gray-700');
    }
  }

  showScreenShareError() {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    notification.textContent = 'Error: No se pudo compartir la pantalla';
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  toggleMoreOptions() {
    this.isMoreOptionsOpen = !this.isMoreOptionsOpen;
    
    if (this.isMoreOptionsOpen) {
      this.moreOptionsMenu.classList.remove('hidden');
    } else {
      this.moreOptionsMenu.classList.add('hidden');
    }
  }

  closeMoreOptions() {
    this.isMoreOptionsOpen = false;
    this.moreOptionsMenu.classList.add('hidden');
  }

  endCall() {
    // Confirmar antes de salir
    if (confirm('¿Estás seguro de que quieres salir de la llamada?')) {
      // Limpiar recursos de audio
      this.cleanupAudioResources();
      
      // Aquí iría la lógica real para terminar la llamada
      console.log('Terminando llamada...');
      
      // Redirigir o cerrar la ventana
      window.location.href = '/'; // O la URL que corresponda
    }
  }

  cleanupAudioResources() {
    // Detener animación
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    // Cerrar contexto de audio
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    
    // Detener tracks de media
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    
    // Limpiar referencias
    this.analyser = null;
    this.microphone = null;
    this.dataArray = null;
  }

  // Métodos para opciones adicionales
  viewParticipants() {
    this.closeMoreOptions();
    
    // Crear modal de participantes
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-gray-800 rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">Participantes</h3>
          <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-3">
          <div class="flex items-center gap-3 p-3 bg-gray-700 rounded-lg">
            <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span class="text-white font-bold">AC</span>
            </div>
            <div>
              <div class="text-white font-medium">Agente Cricker</div>
              <div class="text-green-400 text-sm">En línea</div>
            </div>
          </div>
          <div class="flex items-center gap-3 p-3 bg-gray-700 rounded-lg">
            <div class="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
              <span class="text-white font-bold">U</span>
            </div>
            <div>
              <div class="text-white font-medium">Participante de la llamada</div>
              <div class="text-green-400 text-sm">En línea</div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  openSettings() {
    this.closeMoreOptions();
    
    // Crear modal de configuración
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-gray-800 rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">Configuración</h3>
          <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-white">Calidad de video</span>
            <select class="bg-gray-700 text-white px-3 py-1 rounded">
              <option>HD (720p)</option>
              <option>Full HD (1080p)</option>
              <option>4K</option>
            </select>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-white">Calidad de audio</span>
            <select class="bg-gray-700 text-white px-3 py-1 rounded">
              <option>Estándar</option>
              <option>Alta calidad</option>
            </select>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-white">Notificaciones</span>
            <input type="checkbox" class="rounded" checked>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  invitePeople() {
    this.closeMoreOptions();
    
    // Crear modal para invitar personas
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-gray-800 rounded-lg p-6 w-96">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">Invitar personas</h3>
          <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-white text-sm mb-2">Enlace de invitación</label>
            <div class="flex gap-2">
              <input type="text" value="https://videollamada.com/join/abc123" readonly class="flex-1 bg-gray-700 text-white px-3 py-2 rounded">
              <button class="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded text-white" onclick="navigator.clipboard.writeText(this.previousElementSibling.value); this.textContent='¡Copiado!'; setTimeout(() => this.textContent='Copiar', 2000)">Copiar</button>
            </div>
          </div>
          <div>
            <label class="block text-white text-sm mb-2">Email</label>
            <div class="flex gap-2">
              <input type="email" placeholder="usuario@ejemplo.com" class="flex-1 bg-gray-700 text-white px-3 py-2 rounded">
              <button class="bg-green-600 hover:bg-green-500 px-3 py-2 rounded text-white">Enviar</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  reportProblem() {
    this.closeMoreOptions();
    
    // Crear modal para reportar problema
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-gray-800 rounded-lg p-6 w-96">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">Reportar problema</h3>
          <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-white text-sm mb-2">Tipo de problema</label>
            <select class="w-full bg-gray-700 text-white px-3 py-2 rounded">
              <option>Problema de audio</option>
              <option>Problema de video</option>
              <option>Problema de conexión</option>
              <option>Otro</option>
            </select>
          </div>
          <div>
            <label class="block text-white text-sm mb-2">Descripción</label>
            <textarea placeholder="Describe el problema..." class="w-full bg-gray-700 text-white px-3 py-2 rounded h-24 resize-none"></textarea>
          </div>
          <button class="w-full bg-red-600 hover:bg-red-500 px-4 py-2 rounded text-white">Enviar reporte</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }
}
}

// Inicializar controles cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  if (!window.videoCallControls) {
    window.videoCallControls = new VideoCallControls();
  }
});

