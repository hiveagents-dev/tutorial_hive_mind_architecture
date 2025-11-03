// Cliente API para HiveMind
// Prioriza variable de entorno Vite, con fallback sensible a entorno (local/docker)
const ENV_API_BASE = import.meta?.env?.VITE_API_BASE_URL;
const API_BASE_URL = ENV_API_BASE && ENV_API_BASE.trim().length > 0
  ? ENV_API_BASE.trim()
  : (typeof window !== 'undefined' && window.location.hostname === 'localhost'
      ? 'http://localhost:8002'
      : 'http://hivemind-api:8000');

function wsBaseUrl() {
  try {
    const http = API_BASE_URL;
    // Para desarrollo local, usar localhost:8002
    if (http.includes('localhost:8002')) {
      return 'ws://localhost:8002';
    }
    // Para Docker, usar el hostname del contenedor
    if (http.includes('hivemind-api:8000')) {
      return 'ws://hivemind-api:8000';
    }
    // Fallback genérico
    return http.replace('http://', 'ws://').replace('https://', 'wss://');
  } catch {
    return 'ws://localhost:8002';
  }
}

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);
    
    try {
      // Crear un AbortController para manejar timeouts
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log(`⏰ Timeout reached for ${endpoint}, aborting request`);
        controller.abort();
      }, 60000); // Reducir a 60 segundos
      
      const startTime = Date.now();
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      const duration = Date.now() - startTime;
      
      console.log(`📡 API Response: ${response.status} ${response.statusText} (${duration}ms)`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`❌ API Error Response:`, errorData);
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log(`✅ API Success: ${endpoint} completed in ${duration}ms`);
      return result;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error(`⏰ API Timeout: ${endpoint} - Request cancelled after 120s`);
        throw new Error('La solicitud tardó demasiado tiempo en responder');
      }
      console.error(`❌ API Request Failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/api/v1/health');
  }

  // Obtener información del sistema
  async getInfo() {
    return this.request('/api/v1/info');
  }

  // Analizar necesidad de negocio
  async analyzeBusinessNeed(data) {
    console.log('🚀 Starting analyzeBusinessNeed with data:', data);
    
    // Intentar hasta 3 veces con backoff
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        console.log(`🔄 Attempt ${attempt}/3 for analyzeBusinessNeed`);
        const result = await this.request('/api/v1/analyze', {
          method: 'POST',
          body: JSON.stringify(data),
        });
        console.log('✅ analyzeBusinessNeed completed successfully:', result);
        return result;
      } catch (error) {
        console.error(`❌ analyzeBusinessNeed attempt ${attempt} failed:`, error);
        
        if (attempt === 3) {
          console.error('❌ All attempts failed for analyzeBusinessNeed');
          throw error;
        }
        
        // Esperar antes del siguiente intento
        const delay = attempt * 2000; // 2s, 4s
        console.log(`⏳ Waiting ${delay}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // Ejecutar análisis de ejemplo
  async runExampleAnalysis() {
    return this.request('/api/v1/example', {
      method: 'POST',
    });
  }

  // Obtener historial de análisis
  async getAnalysisHistory({ limit = 50, offset = 0, methodology = null, success_only = false } = {}) {
    const params = new URLSearchParams();
    params.append('limit', limit);
    params.append('offset', offset);
    if (methodology) params.append('methodology', methodology);
    if (success_only) params.append('success_only', 'true');
    
    return this.request(`/api/v1/history?${params.toString()}`);
  }

  // Obtener un análisis específico por ID
  async getAnalysisById(analysisId) {
    return this.request(`/api/v1/history/${analysisId}`);
  }

  // WebSocket: análisis con streaming
  connectAnalysisWS({ business_need, methodology, consensus_strategy, verbose = true, onAgentUpdate, onFinal, onError, onOpen, onClose }) {
    const url = `${wsBaseUrl()}/api/v1/ws/analyze`;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      onOpen && onOpen();
      ws.send(JSON.stringify({
        action: 'start',
        business_need,
        methodology,
        consensus_strategy,
        verbose
      }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'agent_update') {
          onAgentUpdate && onAgentUpdate(msg.data);
        } else if (msg.type === 'final') {
          onFinal && onFinal(msg.data);
        } else if (msg.type === 'error') {
          onError && onError(msg.message || 'Error en WebSocket');
        }
      } catch (e) {
        onError && onError('Mensaje WS inválido');
      }
    };

    ws.onerror = () => {
      onError && onError('Error de conexión WS');
    };

    ws.onclose = () => {
      onClose && onClose();
    };

    return ws;
  }
}

export const apiClient = new ApiClient();
