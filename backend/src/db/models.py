"""SQLAlchemy models for HiveMind database"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Analysis(Base):
    """Model for storing HiveMind analysis executions"""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Input data
    business_need = Column(Text, nullable=False, index=True)
    methodology = Column(String(50), nullable=False, index=True)
    consensus_strategy = Column(String(50), nullable=False)
    
    # Execution metadata
    execution_time = Column(Float, nullable=False)
    success = Column(String(10), nullable=False, default="true")
    
    # Final results
    final_confidence = Column(Float, nullable=True)
    supervisor_response_content = Column(JSON, nullable=True)  # Full JSON content
    
    # Metadata as JSON (renombrado de 'metadata' porque es palabra reservada en SQLAlchemy)
    metadata_json = Column("metadata", JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    agent_responses = relationship(
        "AgentResponse",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_analyses_created_at', 'created_at'),
        Index('idx_analyses_methodology', 'methodology'),
        Index('idx_analyses_success', 'success'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "business_need": self.business_need,
            "methodology": self.methodology,
            "consensus_strategy": self.consensus_strategy,
            "execution_time": self.execution_time,
            "success": self.success,  # Mantener como string "true"/"false" para compatibilidad
            "final_confidence": self.final_confidence,
            "supervisor_response_content": self.supervisor_response_content,
            "metadata": self.metadata_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "agent_responses": [ar.to_dict() for ar in self.agent_responses] if self.agent_responses else []
        }


class AgentResponse(Base):
    """Model for storing individual agent responses"""
    
    __tablename__ = "agent_responses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent identification
    agent_name = Column(String(100), nullable=False, index=True)
    agent_role = Column(String(200), nullable=True)
    agent_level = Column(String(50), nullable=True)  # "worker", "coordinator", "supervisor"
    
    # Input data
    input_content = Column(Text, nullable=True)  # What was sent to the agent
    input_metadata = Column(JSON, nullable=True)  # Additional input context
    
    # Output data
    output_content = Column(Text, nullable=False)  # Agent's response content
    output_json = Column(JSON, nullable=True)  # Parsed JSON if available
    
    # Confidence and metadata
    confidence = Column(Float, nullable=False)
    response_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="agent_responses")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_responses_analysis_id', 'analysis_id'),
        Index('idx_agent_responses_agent_name', 'agent_name'),
        Index('idx_agent_responses_level', 'agent_level'),
        Index('idx_agent_responses_created_at', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "agent_level": self.agent_level,
            "input_content": self.input_content,
            "input_metadata": self.input_metadata or {},
            "output_content": self.output_content,
            "output_json": self.output_json,
            "confidence": self.confidence,
            "response_metadata": self.response_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

