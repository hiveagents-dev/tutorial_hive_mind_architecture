"""Modelos Pydantic para la API REST de HiveMind"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from hivemind.methodology import AgileMethodology
from hivemind.consensus import ConsensusStrategy


class MethodologyEnum(str, Enum):
    """Enum para metodologías ágiles en la API"""
    SCRUM = "scrum"
    SAFE = "safe"
    KANBAN = "kanban"


class ConsensusStrategyEnum(str, Enum):
    """Enum para estrategias de consenso en la API"""
    WEIGHTED_VOTING = "weighted_voting"
    MAJORITY = "majority"
    UNANIMOUS = "unanimous"
    CONFIDENCE_THRESHOLD = "confidence_threshold"


# Request Models
class BusinessNeedRequest(BaseModel):
    """Request model para análisis de necesidad de negocio"""
    business_need: str = Field(
        ..., 
        description="Descripción de la necesidad de negocio a analizar",
        min_length=10,
        max_length=5000
    )
    methodology: MethodologyEnum = Field(
        default=MethodologyEnum.SCRUM,
        description="Metodología ágil a utilizar"
    )
    consensus_strategy: ConsensusStrategyEnum = Field(
        default=ConsensusStrategyEnum.WEIGHTED_VOTING,
        description="Estrategia de consenso a utilizar"
    )
    verbose: bool = Field(
        default=True,
        description="Si incluir información detallada en la respuesta"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "business_need": "Necesitamos crear una aplicación móvil para reservar citas médicas. La app debe permitir a los pacientes buscar doctores por especialidad, ver disponibilidad y reservar citas.",
                "methodology": "scrum",
                "consensus_strategy": "weighted_voting",
                "verbose": True
            }
        }


class AgentResponseModel(BaseModel):
    """Modelo para respuesta de un agente individual"""
    agent_name: str = Field(..., description="Nombre del agente")
    confidence: float = Field(..., description="Nivel de confianza (0.0-1.0)")
    timestamp: datetime = Field(..., description="Timestamp de la respuesta")
    methodology: Optional[str] = Field(None, description="Metodología utilizada")
    content: str = Field(..., description="Contenido de la respuesta")
    content_length: int = Field(..., description="Longitud del contenido")


class ConsensusResultModel(BaseModel):
    """Modelo para resultado del consenso"""
    consensus_level: float = Field(..., description="Nivel de consenso alcanzado")
    achieved: bool = Field(..., description="Si se alcanzó consenso")
    strategy_used: str = Field(..., description="Estrategia utilizada")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles del consenso")


class HiveMindResponseModel(BaseModel):
    """Modelo completo de respuesta del HiveMind"""
    success: bool = Field(..., description="Si la ejecución fue exitosa")
    execution_time: float = Field(..., description="Tiempo de ejecución en segundos")
    methodology: str = Field(..., description="Metodología utilizada")
    consensus_result: ConsensusResultModel = Field(..., description="Resultado del consenso")
    
    # Respuestas de agentes
    worker_responses: List[AgentResponseModel] = Field(..., description="Respuestas de workers")
    coordinator_response: AgentResponseModel = Field(..., description="Respuesta del coordinador")
    supervisor_response: AgentResponseModel = Field(..., description="Respuesta del supervisor")
    
    # Metadatos
    metadata: Dict[str, Any] = Field(..., description="Metadatos adicionales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")


class ErrorResponseModel(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")


class HealthCheckModel(BaseModel):
    """Modelo para health check"""
    status: str = Field(..., description="Estado del servicio")
    version: str = Field(..., description="Versión de la API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    dependencies: Dict[str, str] = Field(..., description="Estado de dependencias")


class MethodologyInfoModel(BaseModel):
    """Modelo para información de metodologías"""
    name: str = Field(..., description="Nombre de la metodología")
    description: str = Field(..., description="Descripción")
    roles: List[str] = Field(..., description="Roles principales")
    artifacts: List[str] = Field(..., description="Artefactos principales")
    ceremonies: List[str] = Field(..., description="Ceremonias principales")
    metrics: List[str] = Field(..., description="Métricas clave")


class SystemInfoModel(BaseModel):
    """Modelo para información del sistema"""
    name: str = Field(..., description="Nombre del sistema")
    version: str = Field(..., description="Versión")
    description: str = Field(..., description="Descripción")
    methodologies: List[MethodologyInfoModel] = Field(..., description="Metodologías soportadas")
    consensus_strategies: List[str] = Field(..., description="Estrategias de consenso soportadas")
    features: List[str] = Field(..., description="Características principales")


# Utility functions
def convert_methodology_enum(methodology: MethodologyEnum) -> AgileMethodology:
    """Convierte MethodologyEnum a AgileMethodology"""
    mapping = {
        MethodologyEnum.SCRUM: AgileMethodology.SCRUM,
        MethodologyEnum.SAFE: AgileMethodology.SAFE,
        MethodologyEnum.KANBAN: AgileMethodology.KANBAN,
    }
    return mapping[methodology]


def convert_consensus_strategy_enum(strategy: ConsensusStrategyEnum) -> ConsensusStrategy:
    """Convierte ConsensusStrategyEnum a ConsensusStrategy"""
    mapping = {
        ConsensusStrategyEnum.WEIGHTED_VOTING: ConsensusStrategy.WEIGHTED_VOTING,
        ConsensusStrategyEnum.MAJORITY: ConsensusStrategy.MAJORITY,
        ConsensusStrategyEnum.UNANIMOUS: ConsensusStrategy.UNANIMOUS,
        ConsensusStrategyEnum.CONFIDENCE_THRESHOLD: ConsensusStrategy.CONFIDENCE_THRESHOLD,
    }
    return mapping[strategy]
