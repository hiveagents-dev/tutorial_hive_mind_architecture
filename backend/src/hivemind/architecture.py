"""HiveMind architecture orchestration for Discovery to Technical Requirements."""

from typing import List, Dict, Any, Optional
import time
import logging
from datetime import datetime

from agents.base_agent import AgentResponse
from agents.worker_agents import (
    ProductManagerAgent,
    ProductOwnerAgent,
    UXUIAgent,
    ScrumMasterAgent,
    TechnicalLeadAgent,
    QASpecialistAgent
)
from agents.coordinator_agent import CoordinatorAgent
from agents.supervisor_agent import SupervisorAgent
from utils.gemini_client import GeminiClient
from .communication import CommunicationBus, MessageType
from .consensus import ConsensusManager, ConsensusStrategy
from .methodology import AgileMethodology, MethodologyFactory
from .hierarchical_flow import HierarchicalExecutionFlow

# AgentDB cognitive memory integration
from agentdb import AgentDB, AgentDBConfig, HiveMindMemoryManager

logger = logging.getLogger(__name__)


class HiveMindResult:
    """
    Result of HiveMind execution.

    Contains all outputs from each level of the hierarchy plus metadata.
    """

    def __init__(self):
        self.worker_responses: List[AgentResponse] = []
        self.coordinator_response: Optional[AgentResponse] = None
        self.supervisor_response: Optional[AgentResponse] = None
        self.consensus_result: Optional[Any] = None
        self.communication_log: str = ""
        self.execution_time: float = 0.0
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "worker_responses": [
                {
                    "agent": r.agent_name,
                    "confidence": r.confidence,
                    "timestamp": r.timestamp
                }
                for r in self.worker_responses
            ],
            "coordinator_response": {
                "agent": self.coordinator_response.agent_name,
                "confidence": self.coordinator_response.confidence,
                "timestamp": self.coordinator_response.timestamp
            } if self.coordinator_response else None,
            "supervisor_response": {
                "agent": self.supervisor_response.agent_name,
                "confidence": self.supervisor_response.confidence,
                "timestamp": self.supervisor_response.timestamp
            } if self.supervisor_response else None,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


class HiveMindArchitecture:
    """
    HiveMind Architecture for Software Development Discovery.

    This class orchestrates the three-level hierarchical consensus architecture:
    - Level 1: Worker Agents (specialist perspectives)
    - Level 2: Coordinator Agent (synthesis and integration)
    - Level 3: Supervisor Agent (final decision and requirements)

    The system transforms a business need into comprehensive technical requirements.
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        methodology: AgileMethodology = AgileMethodology.SCRUM,
        consensus_strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_VOTING,
        agentdb_path: str = "hivemind_memory.sqlite",
        enable_memory: bool = True,
    ):
        """
        Initialize HiveMind architecture.

        Args:
            gemini_client: Initialized Gemini client for all agents.
            methodology: Agile methodology to follow (Scrum, SAFe, Kanban).
            consensus_strategy: Strategy for achieving consensus.
            agentdb_path: Path for AgentDB SQLite database.
            enable_memory: Whether to enable AgentDB cognitive memory.
        """
        self.gemini_client = gemini_client
        self.methodology = methodology
        self.methodology_context = MethodologyFactory.get_context(methodology)
        self.consensus_strategy = consensus_strategy
        self.enable_memory = enable_memory

        # Initialize communication bus
        self.comm_bus = CommunicationBus()

        # Initialize consensus manager
        self.consensus_manager = ConsensusManager()

        # Initialize hierarchical execution flow
        self.hierarchical_flow = HierarchicalExecutionFlow(methodology)

        # Initialize Level 1: Worker Agents
        self.worker_agents = [
            ProductManagerAgent(gemini_client, methodology),
            ProductOwnerAgent(gemini_client, methodology),
            UXUIAgent(gemini_client, methodology),
            ScrumMasterAgent(gemini_client, methodology),
            TechnicalLeadAgent(gemini_client, methodology),
            QASpecialistAgent(gemini_client, methodology)
        ]

        # Initialize Level 2: Coordinator Agent
        self.coordinator = CoordinatorAgent(gemini_client, methodology)

        # Initialize Level 3: Supervisor Agent
        self.supervisor = SupervisorAgent(gemini_client, methodology)

        # Initialize AgentDB cognitive memory system
        self.agentdb: Optional[AgentDB] = None
        self.memory_manager: Optional[HiveMindMemoryManager] = None
        if enable_memory:
            self._init_agentdb(agentdb_path)

        logger.info(f"HiveMind initialized with {methodology.value} methodology (memory={'enabled' if enable_memory else 'disabled'})")

    def _init_agentdb(self, db_path: str) -> None:
        """Initialize AgentDB cognitive memory system."""
        try:
            self.agentdb = AgentDB(AgentDBConfig(
                path=db_path,
                namespace="hivemind_global",
                embedding_provider="auto",
            ))
            self.agentdb.initialize()

            self.memory_manager = HiveMindMemoryManager(self.agentdb)

            # Wrap worker agents with memory capabilities
            self.memory_workers = self.memory_manager.wrap_agents(self.worker_agents)
            self.memory_coordinator = self.memory_manager.wrap_agent(self.coordinator)
            self.memory_supervisor = self.memory_manager.wrap_agent(self.supervisor)

            logger.info(f"AgentDB initialized at {db_path} with {len(self.memory_workers)} memory-enabled agents")
        except Exception as e:
            logger.warning(f"AgentDB initialization failed (running without memory): {e}")
            self.enable_memory = False
            self.agentdb = None
            self.memory_manager = None

    def execute(
        self,
        business_need: str,
        verbose: bool = True
    ) -> HiveMindResult:
        """
        Execute the complete HiveMind process.

        Args:
            business_need: Description of the software development need.
            verbose: Whether to print progress information.

        Returns:
            HiveMindResult: Complete result with all outputs and metadata.
        """
        start_time = time.time()
        result = HiveMindResult()

        logger.info("=" * 80)
        logger.info("STARTING HIVEMIND EXECUTION")
        logger.info("=" * 80)

        if verbose:
            print("\n🐝 HiveMind Architecture - Discovery to Technical Requirements")
            print("=" * 80)

        try:
            # LEVEL 1: Worker Agents Processing
            if verbose:
                print("\n[PHASE 1: Worker Agents Analysis]")

            result.worker_responses = self._execute_workers(business_need, verbose)

            # LEVEL 2: Coordinator Synthesis
            if verbose:
                print("\n[PHASE 2: Coordinator Synthesis]")

            result.coordinator_response = self._execute_coordinator(
                business_need,
                result.worker_responses,
                verbose
            )

            # Apply Consensus
            result.consensus_result = self._apply_consensus(result.worker_responses, verbose)

            # LEVEL 3: Supervisor Final Requirements
            if verbose:
                print("\n[PHASE 3: Supervisor - Final Requirements]")

            result.supervisor_response = self._execute_supervisor(
                business_need,
                result.coordinator_response,
                verbose
            )

            # AgentDB: Track cross-agent causal flow
            if self.enable_memory and self.memory_manager:
                try:
                    if verbose:
                        print("\n[PHASE 4: Memory Consolidation (AgentDB)]")

                    self.memory_manager.track_worker_to_coordinator_flow(
                        result.worker_responses, result.coordinator_response
                    )
                    self.memory_manager.track_coordinator_to_supervisor_flow(
                        result.coordinator_response, result.supervisor_response
                    )
                    self.memory_manager.provide_feedback_to_workers(
                        result.supervisor_response
                    )

                    if verbose:
                        print("  -> Causal flow tracked")
                        print("  -> Supervisor feedback propagated to workers")
                        memory_stats = self.memory_manager.get_system_stats()
                        global_stats = memory_stats.get("global", {}).get("storage", {})
                        print(f"  -> Episodes: {global_stats.get('episodes', 0)} | "
                              f"Skills: {global_stats.get('skills', 0)} | "
                              f"Causal edges: {global_stats.get('causal_edges', 0)} | "
                              f"Patterns: {global_stats.get('reasoning_patterns', 0)}")

                except Exception as e:
                    logger.warning(f"AgentDB memory consolidation error: {e}")

            # Finalize
            end_time = time.time()
            result.execution_time = end_time - start_time
            result.communication_log = self.comm_bus.export_log()
            result.metadata = {
                "methodology": self.methodology.value,
                "methodology_description": self.methodology_context.description,
                "total_agents": len(self.worker_agents) + 2,  # +coordinator +supervisor
                "worker_count": len(self.worker_agents),
                "consensus_strategy": self.consensus_strategy.value,
                "timestamp": datetime.now().isoformat(),
                "memory_enabled": self.enable_memory,
            }

            # Add memory stats to metadata
            if self.enable_memory and self.memory_manager:
                try:
                    result.metadata["agentdb_stats"] = self.memory_manager.get_system_stats()
                except Exception:
                    pass

            if verbose:
                print("\n" + "=" * 80)
                print("HIVEMIND EXECUTION COMPLETED")
                print("=" * 80)
                print(f"Execution Time: {result.execution_time:.2f}s")
                print(f"Consensus Level: {result.consensus_result.consensus_level:.1%}")
                print(f"Final Confidence: {result.supervisor_response.confidence:.1%}")
                if self.enable_memory:
                    print(f"Memory: AgentDB enabled (cognitive memory active)")

            logger.info(f"HiveMind execution completed in {result.execution_time:.2f}s")

        except Exception as e:
            logger.error(f"Error during HiveMind execution: {str(e)}")
            raise

        return result

    def _execute_workers(
        self,
        business_need: str,
        verbose: bool
    ) -> List[AgentResponse]:
        """Execute worker agents using hierarchical flow following Product Management best practices."""
        
        # Create agents dictionary for hierarchical flow
        agents_dict = {
            "ProductManager": self.worker_agents[0],
            "ProductOwner": self.worker_agents[1], 
            "UXUI": self.worker_agents[2],
            "ScrumMaster": self.worker_agents[3],
            "TechnicalLead": self.worker_agents[4],
            "QASpecialist": self.worker_agents[5]
        }
        
        # Execute hierarchical flow
        responses = self.hierarchical_flow.execute_hierarchical_flow(
            business_need=business_need,
            agents=agents_dict,
            verbose=verbose
        )
        
        return responses

    def _execute_coordinator(
        self,
        business_need: str,
        worker_responses: List[AgentResponse],
        verbose: bool
    ) -> AgentResponse:
        """Execute coordinator synthesis."""
        if verbose:
            print(f"  → Coordinator: Synthesizing {len(worker_responses)} worker responses...", end=" ", flush=True)

        # Send coordination request
        self.comm_bus.send_message(
            sender="System",
            recipient=self.coordinator.name,
            content="Synthesize worker responses",
            message_type=MessageType.REQUEST
        )

        # Clear previous responses and add new ones
        self.coordinator.clear_responses()
        for response in worker_responses:
            self.coordinator.add_worker_response(response)

        # Execute coordination
        coordinator_response = self.coordinator.process(
            business_need,
            context={"worker_responses": worker_responses}
        )

        # Log response
        self.comm_bus.send_message(
            sender=self.coordinator.name,
            recipient="System",
            content="Synthesis complete",
            message_type=MessageType.RESPONSE
        )

        if verbose:
            print("✓")

        return coordinator_response

    def _apply_consensus(
        self,
        worker_responses: List[AgentResponse],
        verbose: bool
    ) -> Any:
        """Apply consensus mechanism."""
        if verbose:
            print(f"  → Applying consensus strategy: {self.consensus_strategy.value}...", end=" ", flush=True)

        consensus_result = self.consensus_manager.apply_consensus(
            worker_responses,
            strategy=self.consensus_strategy
        )

        if verbose:
            status = "✓" if consensus_result.achieved else "⚠"
            print(f"{status} (Level: {consensus_result.consensus_level:.1%})")

        return consensus_result

    def _execute_supervisor(
        self,
        business_need: str,
        coordinator_response: AgentResponse,
        verbose: bool
    ) -> AgentResponse:
        """Execute supervisor final requirements generation."""
        if verbose:
            print("  → Supervisor: Generating final technical requirements...", end=" ", flush=True)

        # Send supervisor request
        self.comm_bus.send_message(
            sender="System",
            recipient=self.supervisor.name,
            content="Generate final requirements document",
            message_type=MessageType.REQUEST
        )

        # Execute supervision
        supervisor_response = self.supervisor.process(
            business_need,
            context={"coordinator_synthesis": coordinator_response.content}
        )

        # Log response
        self.comm_bus.send_message(
            sender=self.supervisor.name,
            recipient="System",
            content="Final requirements document generated",
            message_type=MessageType.RESPONSE
        )

        if verbose:
            print("✓")

        return supervisor_response

    def get_communication_statistics(self) -> Dict[str, Any]:
        """Get communication statistics from the bus."""
        return self.comm_bus.get_statistics()

    def export_communication_log(self) -> str:
        """Export complete communication log."""
        return self.comm_bus.export_log()

    def get_agent_info(self) -> Dict[str, List[Dict[str, str]]]:
        """Get information about all agents in the system."""
        return {
            "workers": [agent.get_info() for agent in self.worker_agents],
            "coordinator": self.coordinator.get_info(),
            "supervisor": self.supervisor.get_info()
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"HiveMindArchitecture("
            f"workers={len(self.worker_agents)}, "
            f"consensus={self.consensus_strategy.value})"
        )
