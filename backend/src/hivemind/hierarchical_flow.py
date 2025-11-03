"""Hierarchical execution flow following Product Management best practices."""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass

from agents.base_agent import AgentResponse
from agents.worker_agents import (
    ProductManagerAgent,
    ProductOwnerAgent,
    UXUIAgent,
    ScrumMasterAgent,
    TechnicalLeadAgent,
    QASpecialistAgent
)
from hivemind.communication import CommunicationBus, MessageType
from hivemind.methodology import AgileMethodology

logger = logging.getLogger(__name__)


class ExecutionPhase(Enum):
    """Phases of hierarchical execution."""
    BUSINESS_FOUNDATION = "business_foundation"
    PRODUCT_DEFINITION = "product_definition"
    USER_EXPERIENCE = "user_experience"
    TECHNICAL_FOUNDATION = "technical_foundation"
    PROCESS_OPTIMIZATION = "process_optimization"
    QUALITY_ASSURANCE = "quality_assurance"


@dataclass
class PhaseDependency:
    """Represents a dependency between execution phases."""
    phase: ExecutionPhase
    depends_on: List[ExecutionPhase]
    agent_class: type
    description: str
    methodology_context: str


class HierarchicalExecutionFlow:
    """
    Manages hierarchical execution following Product Management best practices.
    
    This class implements a structured flow where agents execute in a specific
    order based on dependencies and Product Management methodology.
    """
    
    def __init__(self, methodology: AgileMethodology):
        self.methodology = methodology
        self.comm_bus = CommunicationBus()
        self.execution_order = self._define_execution_order()
        self.phase_contexts = {}
        
    def _define_execution_order(self) -> List[PhaseDependency]:
        """Define the execution order based on Product Management best practices."""
        
        if self.methodology == AgileMethodology.SCRUM:
            return [
                PhaseDependency(
                    phase=ExecutionPhase.BUSINESS_FOUNDATION,
                    depends_on=[],
                    agent_class=ProductManagerAgent,
                    description="Business viability and market analysis",
                    methodology_context="Product Owner perspective with business focus"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PRODUCT_DEFINITION,
                    depends_on=[ExecutionPhase.BUSINESS_FOUNDATION],
                    agent_class=ProductOwnerAgent,
                    description="User stories and product backlog definition",
                    methodology_context="Scrum Product Owner creating user stories and backlog"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.USER_EXPERIENCE,
                    depends_on=[ExecutionPhase.PRODUCT_DEFINITION],
                    agent_class=UXUIAgent,
                    description="User experience design based on user stories",
                    methodology_context="UX/UI Designer working with Product Owner stories"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.TECHNICAL_FOUNDATION,
                    depends_on=[ExecutionPhase.USER_EXPERIENCE],
                    agent_class=TechnicalLeadAgent,
                    description="Technical architecture based on UX requirements",
                    methodology_context="Technical Lead designing architecture for UX implementation"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PROCESS_OPTIMIZATION,
                    depends_on=[ExecutionPhase.TECHNICAL_FOUNDATION],
                    agent_class=ScrumMasterAgent,
                    description="Scrum process and sprint planning",
                    methodology_context="Scrum Master planning sprints based on technical requirements"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.QUALITY_ASSURANCE,
                    depends_on=[ExecutionPhase.PROCESS_OPTIMIZATION],
                    agent_class=QASpecialistAgent,
                    description="Quality strategy and testing approach",
                    methodology_context="QA Specialist defining testing strategy for sprint execution"
                )
            ]
            
        elif self.methodology == AgileMethodology.SAFE:
            return [
                PhaseDependency(
                    phase=ExecutionPhase.BUSINESS_FOUNDATION,
                    depends_on=[],
                    agent_class=ProductManagerAgent,
                    description="Portfolio-level business strategy and feature prioritization",
                    methodology_context="SAFe Product Manager (Portfolio) defining strategic features"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PRODUCT_DEFINITION,
                    depends_on=[ExecutionPhase.BUSINESS_FOUNDATION],
                    agent_class=ProductOwnerAgent,
                    description="Program-level feature breakdown and enablers",
                    methodology_context="SAFe Product Owner (Program) breaking down features into capabilities"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.USER_EXPERIENCE,
                    depends_on=[ExecutionPhase.PRODUCT_DEFINITION],
                    agent_class=UXUIAgent,
                    description="Solution-level user experience design",
                    methodology_context="UX/UI Designer creating solution-level user experience"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.TECHNICAL_FOUNDATION,
                    depends_on=[ExecutionPhase.USER_EXPERIENCE],
                    agent_class=TechnicalLeadAgent,
                    description="Solution architecture and technical enablers",
                    methodology_context="Technical Lead designing solution architecture and enablers"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PROCESS_OPTIMIZATION,
                    depends_on=[ExecutionPhase.TECHNICAL_FOUNDATION],
                    agent_class=ScrumMasterAgent,
                    description="Team-level Scrum process and PI planning",
                    methodology_context="Scrum Master (Team) planning for Program Increment"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.QUALITY_ASSURANCE,
                    depends_on=[ExecutionPhase.PROCESS_OPTIMIZATION],
                    agent_class=QASpecialistAgent,
                    description="Solution quality and testing strategy",
                    methodology_context="QA Specialist defining solution-level quality strategy"
                )
            ]
            
        elif self.methodology == AgileMethodology.KANBAN:
            return [
                PhaseDependency(
                    phase=ExecutionPhase.BUSINESS_FOUNDATION,
                    depends_on=[],
                    agent_class=ProductManagerAgent,
                    description="Service request analysis and business value assessment",
                    methodology_context="Kanban Service Request Manager analyzing business value"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PRODUCT_DEFINITION,
                    depends_on=[ExecutionPhase.BUSINESS_FOUNDATION],
                    agent_class=ProductOwnerAgent,
                    description="Work item categorization and flow definition",
                    methodology_context="Kanban Flow Manager categorizing work items and defining flow"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.USER_EXPERIENCE,
                    depends_on=[ExecutionPhase.PRODUCT_DEFINITION],
                    agent_class=UXUIAgent,
                    description="User experience design for continuous delivery",
                    methodology_context="UX/UI Designer creating continuous delivery user experience"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.TECHNICAL_FOUNDATION,
                    depends_on=[ExecutionPhase.USER_EXPERIENCE],
                    agent_class=TechnicalLeadAgent,
                    description="Technical architecture for flow optimization",
                    methodology_context="Technical Lead designing flow-optimized architecture"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PROCESS_OPTIMIZATION,
                    depends_on=[ExecutionPhase.TECHNICAL_FOUNDATION],
                    agent_class=ScrumMasterAgent,
                    description="Flow coordination and WIP limits",
                    methodology_context="Kanban Flow Coordinator setting WIP limits and flow metrics"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.QUALITY_ASSURANCE,
                    depends_on=[ExecutionPhase.PROCESS_OPTIMIZATION],
                    agent_class=QASpecialistAgent,
                    description="Quality gates and flow metrics",
                    methodology_context="QA Specialist defining quality gates and flow metrics"
                )
            ]
    
    def execute_hierarchical_flow(
        self,
        business_need: str,
        agents: Dict[str, Any],
        verbose: bool = True
    ) -> List[AgentResponse]:
        """
        Execute the hierarchical flow following Product Management best practices.
        
        Args:
            business_need: Original business need
            agents: Dictionary of initialized agents
            verbose: Whether to print progress
            
        Returns:
            List of AgentResponse in execution order
        """
        responses = []
        execution_context = {
            "business_need": business_need,
            "methodology": self.methodology.value,
            "previous_responses": []
        }
        
        if verbose:
            print(f"\n🏗️ Executing Hierarchical Flow ({self.methodology.value.upper()})")
            print("=" * 60)
        
        for phase_dep in self.execution_order:
            if verbose:
                print(f"\n📋 Phase: {phase_dep.phase.value.replace('_', ' ').title()}")
                print(f"   Agent: {phase_dep.agent_class.__name__}")
                print(f"   Description: {phase_dep.description}")
                print(f"   Context: {phase_dep.methodology_context}")
                
                # Show dependencies
                if phase_dep.depends_on:
                    dep_names = [dep.value.replace('_', ' ').title() for dep in phase_dep.depends_on]
                    print(f"   Dependencies: {', '.join(dep_names)}")
                else:
                    print(f"   Dependencies: None (Starting phase)")
            
            # Get the agent instance
            agent_name = phase_dep.agent_class.__name__.replace("Agent", "")
            agent = agents.get(agent_name)
            
            if not agent:
                logger.error(f"Agent {agent_name} not found in provided agents")
                continue
            
            # Build context for this phase
            phase_context = self._build_phase_context(phase_dep, execution_context)
            
            try:
                # Send message via communication bus
                self.comm_bus.send_message(
                    sender="System",
                    recipient=agent.name,
                    content=f"Phase: {phase_dep.phase.value} - {phase_dep.description}",
                    message_type=MessageType.REQUEST
                )
                
                # Process with hierarchical context
                response = agent.process(business_need, context=phase_context)
                responses.append(response)
                
                # Update execution context
                execution_context["previous_responses"].append(response)
                self.phase_contexts[phase_dep.phase] = response
                
                # Log response
                self.comm_bus.send_message(
                    sender=agent.name,
                    recipient="System",
                    content=f"Phase {phase_dep.phase.value} complete (confidence: {response.confidence:.2f})",
                    message_type=MessageType.RESPONSE
                )
                
                if verbose:
                    print(f"   ✅ Complete (Confidence: {response.confidence:.2f})")
                
            except Exception as e:
                logger.error(f"Error in phase {phase_dep.phase.value}: {str(e)}")
                if verbose:
                    print(f"   ❌ Error: {str(e)}")
        
        if verbose:
            print(f"\n🎯 Hierarchical Flow Complete - {len(responses)} phases executed")
        
        return responses
    
    def _build_phase_context(
        self,
        phase_dep: PhaseDependency,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context for a specific phase based on dependencies."""
        
        context = {
            "phase": phase_dep.phase.value,
            "methodology": self.methodology.value,
            "methodology_context": phase_dep.methodology_context,
            "dependencies": []
        }
        
        # Add dependency contexts
        for dep_phase in phase_dep.depends_on:
            if dep_phase in self.phase_contexts:
                dep_response = self.phase_contexts[dep_phase]
                context["dependencies"].append({
                    "phase": dep_phase.value,
                    "agent": dep_response.agent_name,
                    "confidence": dep_response.confidence,
                    "content": dep_response.content[:500] + "..." if len(dep_response.content) > 500 else dep_response.content
                })
        
        # Add previous responses for reference
        context["previous_responses"] = execution_context["previous_responses"]
        
        return context
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of the hierarchical execution."""
        return {
            "methodology": self.methodology.value,
            "phases_executed": len(self.execution_order),
            "phase_contexts": {phase.value: {
                "agent": ctx.agent_name,
                "confidence": ctx.confidence
            } for phase, ctx in self.phase_contexts.items()},
            "communication_stats": self.comm_bus.get_statistics()
        }
