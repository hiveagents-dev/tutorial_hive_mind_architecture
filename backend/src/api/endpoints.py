"""Endpoints REST para la API de HiveMind"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from hivemind.architecture import HiveMindArchitecture
from hivemind.methodology import MethodologyFactory
from hivemind.consensus import ConsensusStrategy
from utils.config import Config
from utils.gemini_client import GeminiClient
from db.database import get_db
from db.persistence import PersistenceService

from .models import (
    BusinessNeedRequest,
    HiveMindResponseModel,
    ErrorResponseModel,
    HealthCheckModel,
    SystemInfoModel,
    MethodologyInfoModel,
    convert_methodology_enum,
    convert_consensus_strategy_enum,
    MethodologyEnum,
    ConsensusStrategyEnum
)

logger = logging.getLogger(__name__)

# Router principal
router = APIRouter()

# Dependencias globales
_config = None
_gemini_client = None


def get_config() -> Config:
    """Dependency para obtener configuración"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_gemini_client(config: Config = Depends(get_config)) -> GeminiClient:
    """Dependency para obtener cliente Gemini"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient(
            api_key=config.get_api_key(),
            model_name=config.gemini_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    return _gemini_client


@router.get("/health", response_model=HealthCheckModel)
async def health_check():
    """
    Health check endpoint para verificar el estado del servicio
    """
    try:
        config = get_config()
        gemini_client = get_gemini_client(config)
        
        # Verificar dependencias
        dependencies = {
            "config": "ok",
            "gemini_client": "ok",
            "api_key": "configured" if config.get_api_key() else "missing"
        }
        
        return HealthCheckModel(
            status="healthy",
            version="1.0.0",
            dependencies=dependencies
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckModel(
            status="unhealthy",
            version="1.0.0",
            dependencies={"error": str(e)}
        )


@router.get("/info", response_model=SystemInfoModel)
async def system_info():
    """
    Información del sistema y capacidades
    """
    try:
        # Obtener información de metodologías
        methodologies = []
        for methodology in MethodologyEnum:
            context = MethodologyFactory.get_context(convert_methodology_enum(methodology))
            methodologies.append(MethodologyInfoModel(
                name=context.name,
                description=context.description,
                roles=list(context.roles_mapping.values()),
                artifacts=context.artifacts,
                ceremonies=context.ceremonies,
                metrics=context.metrics
            ))
        
        # Estrategias de consenso soportadas
        consensus_strategies = [strategy.value for strategy in ConsensusStrategyEnum]
        
        # Características principales
        features = [
            "HiveMind Multi-Agent Architecture",
            "Hierarchical Execution Flow",
            "Agile Methodology Support (Scrum, SAFe, Kanban)",
            "A2A Communication Protocol",
            "Consensus Mechanisms",
            "Real-time Gemini API Integration",
            "Quality Assurance & Validation",
            "Comprehensive Documentation Generation"
        ]
        
        return SystemInfoModel(
            name="HiveMind Architecture",
            version="1.0.0",
            description="Sistema multi-agente para transformar necesidades de negocio en requisitos técnicos completos",
            methodologies=methodologies,
            consensus_strategies=consensus_strategies,
            features=features
        )
    except Exception as e:
        logger.error(f"System info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")


@router.post("/analyze", response_model=HiveMindResponseModel)
async def analyze_business_need(
    request: BusinessNeedRequest,
    config: Config = Depends(get_config),
    gemini_client: GeminiClient = Depends(get_gemini_client),
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para analizar necesidades de negocio usando HiveMind
    """
    try:
        logger.info(f"Starting HiveMind analysis for methodology: {request.methodology}")
        
        # Convertir enums
        methodology = convert_methodology_enum(request.methodology)
        consensus_strategy = convert_consensus_strategy_enum(request.consensus_strategy)
        
        # Inicializar arquitectura HiveMind
        architecture = HiveMindArchitecture(
            gemini_client=gemini_client,
            methodology=methodology,
            consensus_strategy=consensus_strategy
        )
        
        # Ejecutar análisis
        result = architecture.execute(
            business_need=request.business_need,
            verbose=request.verbose
        )
        
        # Guardar análisis en base de datos
        persistence = PersistenceService(db)
        saved_analysis = persistence.save_analysis(
            business_need=request.business_need,
            methodology=request.methodology.value,
            consensus_strategy=request.consensus_strategy.value,
            result=result,
            success=True
        )
        
        if saved_analysis:
            logger.info(f"Analysis saved with ID: {saved_analysis.id}")
        else:
            logger.warning("Failed to save analysis to database")
        
        # Convertir resultado a modelo de respuesta
        response = HiveMindResponseModel(
            success=True,
            execution_time=result.execution_time,
            methodology=request.methodology,
            consensus_result={
                "consensus_level": result.consensus_result.consensus_level,
                "achieved": result.consensus_result.achieved,
                "strategy_used": result.consensus_result.strategy_used.value,
                "justification": result.consensus_result.justification,
                "metadata": result.consensus_result.metadata
            },
            worker_responses=[
                {
                    "agent_name": resp.agent_name,
                    "confidence": resp.confidence,
                    "timestamp": resp.timestamp,
                    "methodology": resp.methodology,
                    "content": resp.content,
                    "content_length": len(resp.content)
                }
                for resp in result.worker_responses
            ],
            coordinator_response={
                "agent_name": result.coordinator_response.agent_name,
                "confidence": result.coordinator_response.confidence,
                "timestamp": result.coordinator_response.timestamp,
                "methodology": result.coordinator_response.methodology,
                "content": result.coordinator_response.content,
                "content_length": len(result.coordinator_response.content)
            },
            supervisor_response={
                "agent_name": result.supervisor_response.agent_name,
                "confidence": result.supervisor_response.confidence,
                "timestamp": result.supervisor_response.timestamp,
                "methodology": result.supervisor_response.methodology,
                "content": result.supervisor_response.content,
                "content_length": len(result.supervisor_response.content)
            },
            metadata={
                **result.metadata,
                "analysis_id": saved_analysis.id if saved_analysis else None
            }
        )
        
        logger.info(f"HiveMind analysis completed successfully in {result.execution_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"HiveMind analysis failed: {str(e)}")
        logger.error(traceback.format_exc())
        
        error_response = ErrorResponseModel(
            error="AnalysisError",
            message=f"Error during HiveMind analysis: {str(e)}",
            details={
                "methodology": request.methodology.value,
                "consensus_strategy": request.consensus_strategy.value,
                "business_need_length": len(request.business_need)
            }
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/methodologies/{methodology}", response_model=MethodologyInfoModel)
async def get_methodology_info(methodology: MethodologyEnum):
    """
    Obtener información detallada de una metodología específica
    """
    try:
        context = MethodologyFactory.get_context(convert_methodology_enum(methodology))
        
        return MethodologyInfoModel(
            name=context.name,
            description=context.description,
            roles=list(context.roles_mapping.values()),
            artifacts=context.artifacts,
            ceremonies=context.ceremonies,
            metrics=context.metrics
        )
    except Exception as e:
        logger.error(f"Error getting methodology info: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Methodology {methodology.value} not found")


@router.get("/methodologies", response_model=Dict[str, MethodologyInfoModel])
async def get_all_methodologies():
    """
    Obtener información de todas las metodologías soportadas
    """
    try:
        methodologies = {}
        for methodology in MethodologyEnum:
            context = MethodologyFactory.get_context(convert_methodology_enum(methodology))
            methodologies[methodology.value] = MethodologyInfoModel(
                name=context.name,
                description=context.description,
                roles=list(context.roles_mapping.values()),
                artifacts=context.artifacts,
                ceremonies=context.ceremonies,
                metrics=context.metrics
            )
        
        return methodologies
    except Exception as e:
        logger.error(f"Error getting all methodologies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting methodologies: {str(e)}")


@router.get("/consensus-strategies")
async def get_consensus_strategies():
    """
    Obtener todas las estrategias de consenso soportadas
    """
    try:
        strategies = {}
        for strategy in ConsensusStrategyEnum:
            strategies[strategy.value] = {
                "name": strategy.value.replace("_", " ").title(),
                "description": f"Consensus strategy using {strategy.value.replace('_', ' ')}"
            }
        
        return {
            "strategies": strategies,
            "default": ConsensusStrategyEnum.WEIGHTED_VOTING.value
        }
    except Exception as e:
        logger.error(f"Error getting consensus strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting consensus strategies: {str(e)}")


# -----------------------------
# History Endpoints
# -----------------------------

logger.info("📝 Registering history endpoints...")

@router.get("/history")
async def get_analysis_history(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de análisis a retornar"),
    offset: int = Query(0, ge=0, description="Número de análisis a saltar"),
    methodology: Optional[str] = Query(None, description="Filtrar por metodología"),
    success_only: bool = Query(False, description="Solo análisis exitosos"),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de análisis ejecutados
    """
    logger.info("🔍 History endpoint called")
    try:
        persistence = PersistenceService(db)
        analyses = persistence.list_analyses(
            limit=limit,
            offset=offset,
            methodology=methodology,
            success_only=success_only
        )
        
        return {
            "success": True,
            "count": len(analyses),
            "limit": limit,
            "offset": offset,
            "analyses": [analysis.to_dict() for analysis in analyses]
        }
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/history/{analysis_id}")
async def get_analysis_by_id(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un análisis específico por ID
    """
    try:
        persistence = PersistenceService(db)
        analysis = persistence.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
        
        return {
            "success": True,
            "analysis": analysis.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")


# Endpoint de ejemplo
@router.post("/example")
async def example_analysis():
    """
    Endpoint de ejemplo con un caso de uso predefinido
    """
    try:
        example_request = BusinessNeedRequest(
            business_need="Necesitamos crear una aplicación móvil para reservar citas médicas. La app debe permitir a los pacientes buscar doctores por especialidad, ver disponibilidad y reservar citas. También debe enviar recordatorios.",
            methodology=MethodologyEnum.SCRUM,
            consensus_strategy=ConsensusStrategyEnum.WEIGHTED_VOTING,
            verbose=True
        )
        # Resolver dependencias explícitamente (evitar pasar objetos Depends)
        config = get_config()
        gemini_client = get_gemini_client(config)
        # Reutilizar la lógica del endpoint principal inyectando deps resueltas
        return await analyze_business_need(example_request, config=config, gemini_client=gemini_client)
        
    except Exception as e:
        logger.error(f"Example analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in example analysis: {str(e)}")


# -----------------------------
# WebSocket: análisis en tiempo real
# -----------------------------

@router.websocket("/ws/analyze")
async def analyze_business_need_ws(websocket: WebSocket):
    """
    WebSocket para ejecutar el análisis y emitir progreso incremental.
    """
    logger.info(f"🔌 WebSocket connection attempt from {websocket.client.host}")
    db = None
    db_gen = None
    
    try:
        await websocket.accept()
        logger.info(f"✅ WebSocket accepted from {websocket.client.host}")
        await websocket.send_json({"type": "connected"})
        
        # Get database session for this WebSocket connection
        db_gen = get_db()
        db = next(db_gen)
    except Exception as e:
        logger.error(f"❌ WebSocket accept failed: {str(e)}")
        return
    
    try:
        payload = await websocket.receive_json()
        logger.info(f"📨 Received payload: {payload.get('action', 'unknown')}")
        
        if not isinstance(payload, dict) or payload.get("action") != "start":
            await websocket.send_json({"type": "error", "message": "Invalid start payload"})
            await websocket.close()
            return

        # Resolver dependencias
        config = get_config()
        gemini_client = get_gemini_client(config)

        # Parseo de parámetros
        try:
            meth = payload.get("methodology", MethodologyEnum.SCRUM)
            cons = payload.get("consensus_strategy", ConsensusStrategyEnum.WEIGHTED_VOTING)
            methodology = convert_methodology_enum(meth)
            consensus_strategy = convert_consensus_strategy_enum(cons)
        except Exception:
            await websocket.send_json({"type": "error", "message": "Invalid methodology or consensus_strategy"})
            await websocket.close()
            return

        business_need = (payload.get("business_need") or "").strip()
        verbose = bool(payload.get("verbose", True))
        if not business_need:
            await websocket.send_json({"type": "error", "message": "business_need is required"})
            await websocket.close()
            return

        # Inicializar arquitectura
        architecture = HiveMindArchitecture(
            gemini_client=gemini_client,
            methodology=methodology,
            consensus_strategy=consensus_strategy
        )

        # Ejecutar en executor y streamear mensajes del CommunicationBus
        last_index = 0
        loop = asyncio.get_running_loop()

        def run_execute():
            return architecture.execute(business_need=business_need, verbose=verbose)

        exec_task = loop.run_in_executor(None, run_execute)

        # Polling del bus mientras corre la ejecución
        try:
            while True:
                done = exec_task.done()
                try:
                    history = architecture.communication_bus.get_message_history()
                except Exception:
                    history = []

                for msg in history[last_index:]:
                    # msg puede ser objeto con to_dict
                    try:
                        data = msg.to_dict() if hasattr(msg, "to_dict") else (msg if isinstance(msg, dict) else getattr(msg, "__dict__", {}))
                    except Exception:
                        data = {}
                    await websocket.send_json({"type": "agent_update", "data": data})
                last_index = len(history)

                if done:
                    break
                await asyncio.sleep(0.5)

            # Obtener resultado final
            result = await exec_task
            final_payload = {
                "success": True,
                "execution_time": result.execution_time,
                "methodology": payload.get("methodology", MethodologyEnum.SCRUM.value),
                "consensus_result": {
                    "consensus_level": result.consensus_result.consensus_level,
                    "achieved": result.consensus_result.achieved,
                    "strategy_used": result.consensus_result.strategy_used.value,
                    "justification": result.consensus_result.justification,
                    "metadata": result.consensus_result.metadata,
                },
                "worker_responses": [
                    {
                        "agent_name": r.agent_name,
                        "confidence": r.confidence,
                        "timestamp": r.timestamp,
                        "methodology": r.methodology,
                        "content": r.content,
                        "content_length": len(r.content),
                    }
                    for r in result.worker_responses
                ],
                "coordinator_response": {
                    "agent_name": result.coordinator_response.agent_name,
                    "confidence": result.coordinator_response.confidence,
                    "timestamp": result.coordinator_response.timestamp,
                    "methodology": result.coordinator_response.methodology,
                    "content": result.coordinator_response.content,
                    "content_length": len(result.coordinator_response.content),
                },
                "supervisor_response": {
                    "agent_name": result.supervisor_response.agent_name,
                    "confidence": result.supervisor_response.confidence,
                    "timestamp": result.supervisor_response.timestamp,
                    "methodology": result.supervisor_response.methodology,
                    "content": result.supervisor_response.content,
                    "content_length": len(result.supervisor_response.content),
                },
                "metadata": result.metadata,
            }
            await websocket.send_json({"type": "final", "data": final_payload})
            
            # Guardar análisis en base de datos si fue exitoso
            if result.success and db:
                try:
                    persistence = PersistenceService(db)
                    saved_analysis = persistence.save_analysis(
                        business_need=business_need,
                        methodology=methodology.value,
                        consensus_strategy=consensus_strategy.value,
                        result=result,
                        success=True
                    )
                    if saved_analysis:
                        logger.info(f"Analysis saved with ID: {saved_analysis.id}")
                        # Update final payload with analysis_id
                        final_payload["metadata"] = final_payload.get("metadata", {})
                        final_payload["metadata"]["analysis_id"] = saved_analysis.id
                        await websocket.send_json({"type": "final", "data": final_payload})
                except Exception as e:
                    logger.warning(f"Failed to save analysis to database: {str(e)}")
            
            await websocket.close()
            
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WS analyze error: {e}")
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close()
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
            await websocket.close()
        except:
            pass
    finally:
        if db_gen:
            try:
                db_gen.close()
            except:
                pass
