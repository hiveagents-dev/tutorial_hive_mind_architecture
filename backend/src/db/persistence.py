"""Persistence service for saving HiveMind analysis results"""

import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Analysis, AgentResponse
from agents.base_agent import AgentResponse as HiveMindAgentResponse
from hivemind.architecture import HiveMindResult

logger = logging.getLogger(__name__)


class PersistenceService:
    """Service for persisting HiveMind analysis results to database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_analysis(
        self,
        business_need: str,
        methodology: str,
        consensus_strategy: str,
        result: HiveMindResult,
        success: bool = True
    ) -> Optional[Analysis]:
        """
        Save a complete HiveMind analysis to the database.
        
        Args:
            business_need: The original business need
            methodology: Methodology used (scrum, safe, kanban)
            consensus_strategy: Consensus strategy used
            result: HiveMindResult object with all responses
            success: Whether the execution was successful
            
        Returns:
            Analysis: The saved Analysis object, or None if save failed
        """
        try:
            # Parse supervisor response content if available
            supervisor_content_json = None
            if result.supervisor_response and result.supervisor_response.content:
                try:
                    cleaned_content = result.supervisor_response.content.strip()
                    # Intentar parsear JSON
                    supervisor_content_json = json.loads(cleaned_content)
                    
                    # Validar que tenga campos esenciales
                    essential_fields = ['project_info', 'executive_summary', 'functional_requirements']
                    missing = [f for f in essential_fields if f not in supervisor_content_json]
                    if missing:
                        logger.warning(f"⚠️  Supervisor JSON falta campos: {missing}")
                    
                    logger.info(f"✅ Supervisor JSON parseado: {len(supervisor_content_json)} campos, tamaño: {len(cleaned_content)} chars")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"❌ Error parseando Supervisor JSON: {e}")
                    # Intentar extraer JSON del contenido si tiene markdown
                    import re
                    json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
                    if json_match:
                        try:
                            supervisor_content_json = json.loads(json_match.group())
                            logger.info("✅ JSON extraído de markdown")
                        except:
                            supervisor_content_json = {"raw_content": result.supervisor_response.content[:10000]}
                    else:
                        supervisor_content_json = {"raw_content": result.supervisor_response.content[:10000]}
            
            # Create Analysis record
            analysis = Analysis(
                business_need=business_need,
                methodology=methodology,
                consensus_strategy=consensus_strategy,
                execution_time=result.execution_time,
                success="true" if success else "false",
                final_confidence=result.supervisor_response.confidence if result.supervisor_response else None,
                supervisor_response_content=supervisor_content_json,
                metadata_json=result.metadata
            )
            
            self.db.add(analysis)
            self.db.flush()  # Get the ID
            
            # Save all worker responses
            for worker_response in result.worker_responses:
                self._save_agent_response(
                    analysis_id=analysis.id,
                    agent_response=worker_response,
                    agent_level="worker",
                    input_content=business_need
                )
            
            # Save coordinator response
            if result.coordinator_response:
                # Build context from worker responses for coordinator input
                coordinator_input = self._build_coordinator_input(
                    business_need,
                    result.worker_responses
                )
                self._save_agent_response(
                    analysis_id=analysis.id,
                    agent_response=result.coordinator_response,
                    agent_level="coordinator",
                    input_content=coordinator_input
                )
            
            # Save supervisor response
            if result.supervisor_response:
                # Build context from coordinator for supervisor input
                supervisor_input = self._build_supervisor_input(
                    business_need,
                    result.coordinator_response
                )
                self._save_agent_response(
                    analysis_id=analysis.id,
                    agent_response=result.supervisor_response,
                    agent_level="supervisor",
                    input_content=supervisor_input
                )
            
            self.db.commit()
            logger.info(f"✅ Analysis {analysis.id} saved successfully")
            return analysis
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ Database error saving analysis: {str(e)}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Unexpected error saving analysis: {str(e)}")
            return None
    
    def _save_agent_response(
        self,
        analysis_id: int,
        agent_response: HiveMindAgentResponse,
        agent_level: str,
        input_content: str
    ) -> Optional[AgentResponse]:
        """Save an individual agent response to the database"""
        try:
            # Try to parse JSON from content
            output_json = None
            if agent_response.content:
                try:
                    output_json = json.loads(agent_response.content)
                except (json.JSONDecodeError, TypeError):
                    # Content is not JSON, store as text
                    pass
            
            # Extract role from agent name if possible
            agent_role = getattr(agent_response, 'role', None)
            if not agent_role:
                # Try to infer from agent_name
                name_lower = agent_response.agent_name.lower()
                if 'product manager' in name_lower or 'productmanager' in name_lower:
                    agent_role = "Product Manager"
                elif 'product owner' in name_lower or 'productowner' in name_lower:
                    agent_role = "Product Owner"
                elif 'ux' in name_lower or 'ui' in name_lower or 'designer' in name_lower:
                    agent_role = "UX/UI Designer"
                elif 'scrum' in name_lower or 'master' in name_lower:
                    agent_role = "Scrum Master"
                elif 'technical' in name_lower or 'lead' in name_lower:
                    agent_role = "Technical Lead"
                elif 'qa' in name_lower or 'quality' in name_lower:
                    agent_role = "QA Specialist"
                elif 'coordinator' in name_lower:
                    agent_role = "Coordinator"
                elif 'supervisor' in name_lower:
                    agent_role = "Supervisor"
            
            agent_response_db = AgentResponse(
                analysis_id=analysis_id,
                agent_name=agent_response.agent_name,
                agent_role=agent_role,
                agent_level=agent_level,
                input_content=input_content[:10000] if len(input_content) > 10000 else input_content,  # Limit length
                input_metadata={},
                output_content=agent_response.content[:50000] if len(agent_response.content) > 50000 else agent_response.content,  # Limit length
                output_json=output_json,
                confidence=agent_response.confidence,
                response_metadata={
                    "timestamp": agent_response.timestamp,
                    "model": getattr(agent_response, 'model', None),
                }
            )
            
            self.db.add(agent_response_db)
            return agent_response_db
            
        except Exception as e:
            logger.error(f"❌ Error saving agent response for {agent_response.agent_name}: {str(e)}")
            return None
    
    def _build_coordinator_input(self, business_need: str, worker_responses: List[HiveMindAgentResponse]) -> str:
        """Build input context for coordinator from worker responses"""
        parts = [f"Business Need: {business_need}\n\nWorker Agent Responses:"]
        for response in worker_responses:
            parts.append(f"\n--- {response.agent_name} ---")
            parts.append(response.content[:1000])  # Truncate for input context
        return "\n".join(parts)
    
    def _build_supervisor_input(self, business_need: str, coordinator_response: Optional[HiveMindAgentResponse]) -> str:
        """Build input context for supervisor from coordinator response"""
        parts = [f"Business Need: {business_need}"]
        if coordinator_response:
            parts.append(f"\nCoordinator Synthesis:\n{coordinator_response.content[:2000]}")  # Truncate
        return "\n".join(parts)
    
    def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """Retrieve an analysis by ID"""
        try:
            return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        except Exception as e:
            logger.error(f"❌ Error retrieving analysis {analysis_id}: {str(e)}")
            return None
    
    def list_analyses(
        self,
        limit: int = 50,
        offset: int = 0,
        methodology: Optional[str] = None,
        success_only: bool = False
    ) -> List[Analysis]:
        """List analyses with optional filtering"""
        try:
            query = self.db.query(Analysis)
            
            if methodology:
                query = query.filter(Analysis.methodology == methodology)
            
            if success_only:
                query = query.filter(Analysis.success == "true")
            
            query = query.order_by(Analysis.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
        except Exception as e:
            logger.error(f"❌ Error listing analyses: {str(e)}")
            return []

