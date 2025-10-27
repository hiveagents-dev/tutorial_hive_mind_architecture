"""Aplicación principal FastAPI para HiveMind"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .endpoints import router
from .models import ErrorResponseModel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Starting HiveMind API Server")
    logger.info("📊 Initializing dependencies...")
    
    try:
        # Agregar path para imports
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        # Verificar configuración
        from utils.config import Config
        config = Config()
        logger.info(f"✅ Configuration loaded: {config.gemini_model}")
        
        # Verificar cliente Gemini
        from utils.gemini_client import GeminiClient
        gemini_client = GeminiClient(
            api_key=config.get_api_key(),
            model_name=config.gemini_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        logger.info("✅ Gemini client initialized")
        
        logger.info("🎉 HiveMind API Server ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HiveMind API Server")


# Crear aplicación FastAPI
app = FastAPI(
    title="HiveMind Architecture API",
    description="""
    🐝 **HiveMind Architecture API** - Sistema multi-agente para transformar necesidades de negocio en requisitos técnicos completos
    
    ## Características Principales
    
    - **Arquitectura Multi-Agente**: Sistema jerárquico con workers, coordinador y supervisor
    - **Flujo Jerárquico**: Ejecución secuencial siguiendo mejores prácticas de Product Management
    - **Metodologías Ágiles**: Soporte para Scrum, SAFe y Kanban
    - **Protocolo A2A**: Comunicación entre agentes con traceabilidad completa
    - **Mecanismos de Consenso**: Múltiples estrategias para alcanzar consenso
    - **Integración Gemini**: API real de Google Gemini para generación de contenido
    - **Control de Calidad**: Validación y aseguramiento de calidad en cada fase
    
    ## Flujo de Trabajo
    
    1. **Business Foundation** (ProductManager) - Análisis de viabilidad empresarial
    2. **Product Definition** (ProductOwner) - User Stories y Product Backlog
    3. **User Experience** (UXUI_Designer) - Diseño de experiencia de usuario
    4. **Technical Foundation** (TechnicalLead) - Arquitectura técnica
    5. **Process Optimization** (ScrumMaster) - Optimización de procesos
    6. **Quality Assurance** (QA_Specialist) - Estrategia de calidad
    7. **Coordination** (Coordinator) - Síntesis e integración
    8. **Supervision** (Supervisor) - Decisión final y documentación
    
    ## Metodologías Soportadas
    
    - **Scrum**: Desarrollo iterativo con sprints
    - **SAFe**: Escalado ágil para organizaciones grandes
    - **Kanban**: Gestión de flujo continuo
    
    ## Estrategias de Consenso
    
    - **Weighted Voting**: Votación ponderada por confianza
    - **Majority**: Consenso por mayoría
    - **Unanimous**: Consenso unánime
    - **Confidence Threshold**: Consenso por umbral de confianza
    """,
    version="1.0.0",
    contact={
        "name": "HiveMind Architecture Team",
        "email": "support@hivemind-arch.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests"""
    start_time = time.time()
    
    # Log del request
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    # Procesar request
    response = await call_next(request)
    
    # Log del response
    process_time = time.time() - start_time
    logger.info(f"📤 {response.status_code} - {process_time:.3f}s")
    
    return response


# Exception handlers globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para excepciones no manejadas"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    logger.error(f"Request: {request.method} {request.url.path}")
    
    error_response = ErrorResponseModel(
        error="InternalServerError",
        message="An unexpected error occurred",
        details={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


# Incluir routers
app.include_router(router, prefix="/api/v1", tags=["HiveMind"])


# Endpoints raíz
@app.get("/")
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": "🐝 Welcome to HiveMind Architecture API",
        "version": "1.0.0",
        "description": "Sistema multi-agente para transformar necesidades de negocio en requisitos técnicos",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "info": "/api/v1/info"
    }


@app.get("/status")
async def status():
    """Endpoint de estado simple"""
    return {"status": "healthy", "service": "HiveMind API"}


# Función para ejecutar el servidor
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Ejecutar el servidor FastAPI"""
    logger.info(f"🚀 Starting HiveMind API Server on {host}:{port}")
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import time
    run_server(reload=True)
