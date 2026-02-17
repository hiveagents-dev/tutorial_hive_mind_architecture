"""
HiveMind Integration Layer for AgentDB.

Provides the bridge between AgentDB's cognitive memory system and the
HiveMind multi-agent architecture. Key components:

- MemoryEnabledAgent: Mixin/wrapper that adds AgentDB memory to any BaseAgent
- HiveMindMemoryBus: Extends CommunicationBus with memory-backed context
- AgentDBMiddleware: FastAPI middleware for automatic episode tracking
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from .core import AgentDB, AgentDBConfig

logger = logging.getLogger(__name__)


class MemoryEnabledAgent:
    """
    Wrapper that adds cognitive memory capabilities to any HiveMind agent.

    This class wraps an existing BaseAgent instance and augments its
    process() method with:
    - Pre-processing: Retrieves relevant past episodes and skills
    - Post-processing: Stores the episode with critique and reward
    - Causal tracking: Records cause-effect relationships
    - Reasoning patterns: Stores and retrieves reasoning approaches

    Usage:
        from agents.worker_agents import ProductManagerAgent
        from agentdb.integration import MemoryEnabledAgent

        agent = ProductManagerAgent(gemini_client, methodology)
        memory_agent = MemoryEnabledAgent(agent, agentdb)
        response = memory_agent.process(input_data, context)
    """

    def __init__(
        self,
        agent,
        agentdb: AgentDB,
        auto_store: bool = True,
    ):
        """
        Initialize memory-enabled agent wrapper.

        Args:
            agent: The BaseAgent instance to wrap.
            agentdb: Initialized AgentDB instance (or namespaced instance).
            auto_store: Automatically store episodes after processing.
        """
        self._agent = agent
        self._db = agentdb.create_namespaced(agent.name)
        self._auto_store = auto_store
        logger.info(f"MemoryEnabledAgent wrapping '{agent.name}' with namespace '{agent.name}'")

    @property
    def agent(self):
        """Access the wrapped agent."""
        return self._agent

    @property
    def db(self) -> AgentDB:
        """Access the agent's namespaced AgentDB."""
        return self._db

    @property
    def name(self) -> str:
        return self._agent.name

    @property
    def role(self) -> str:
        return self._agent.role

    def process(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Process input with memory augmentation.

        1. Retrieve relevant past episodes and skills
        2. Inject memory context into the agent's context
        3. Call the original agent's process()
        4. Store the episode and track patterns

        Args:
            input_data: Input data for the agent.
            context: Optional context dict.

        Returns:
            AgentResponse from the wrapped agent.
        """
        context = context or {}
        start_time = time.time()

        # ── Phase 1: Memory Retrieval ─────────────────────────────────
        memory_context = self._retrieve_memory_context(input_data)

        # Inject memory into context
        enriched_context = {**context}
        if memory_context["episodes"]:
            enriched_context["past_episodes"] = memory_context["episodes"]
            enriched_context["memory_insights"] = memory_context["insights"]
        if memory_context["skills"]:
            enriched_context["available_skills"] = memory_context["skills"]
        if memory_context["reasoning"]:
            enriched_context["recommended_approach"] = memory_context["reasoning"]

        # Log the retrieval event
        self._db.storage.log_event(
            agent_name=self._agent.name,
            event_type="planning",
            content=f"Retrieved {len(memory_context['episodes'])} episodes, "
                    f"{len(memory_context['skills'])} skills for task",
            phase="memory_retrieval",
            namespace=self._agent.name,
        )

        # ── Phase 2: Agent Execution ──────────────────────────────────
        # Build memory-augmented input
        augmented_input = self._build_augmented_input(input_data, memory_context)

        response = self._agent.process(augmented_input, enriched_context)

        execution_time = time.time() - start_time

        # ── Phase 3: Memory Storage ───────────────────────────────────
        if self._auto_store:
            self._store_episode(
                input_data=input_data,
                response=response,
                execution_time=execution_time,
                memory_context=memory_context,
            )

        return response

    def _retrieve_memory_context(self, input_data: str) -> Dict[str, Any]:
        """Retrieve relevant memory context for the current task."""
        context = {
            "episodes": [],
            "insights": [],
            "skills": [],
            "reasoning": None,
        }

        try:
            # Retrieve relevant episodes
            reflexion_result = self._db.reflexion.retrieve_relevant(
                query=input_data, k=3, threshold=0.2,
            )
            context["episodes"] = [
                {
                    "task": ep.task,
                    "outcome": ep.output[:500],
                    "critique": ep.critique,
                    "success": ep.success,
                    "reward": ep.reward,
                }
                for ep in reflexion_result.episodes
            ]
            context["insights"] = reflexion_result.insights

        except Exception as e:
            logger.warning(f"Error retrieving episodes: {e}")

        try:
            # Search for applicable skills
            skills = self._db.skills.search_skills(
                query=input_data, k=3, min_success_rate=0.3,
            )
            context["skills"] = [
                {
                    "name": sk.name,
                    "description": sk.description,
                    "success_rate": sk.success_rate,
                }
                for sk in skills
            ]

        except Exception as e:
            logger.warning(f"Error retrieving skills: {e}")

        try:
            # Get best reasoning approach
            best = self._db.reasoning.get_best_approach(
                task_type=self._agent.name,
                context=input_data[:200],
            )
            if best:
                context["reasoning"] = {
                    "approach": best.approach,
                    "success_rate": best.success_rate,
                    "reward": best.reward,
                }

        except Exception as e:
            logger.warning(f"Error retrieving reasoning patterns: {e}")

        return context

    def _build_augmented_input(
        self, input_data: str, memory_context: Dict[str, Any]
    ) -> str:
        """Build memory-augmented input for the agent."""
        parts = [input_data]

        if memory_context["insights"]:
            parts.append("\n\n--- MEMORY INSIGHTS (from past similar tasks) ---")
            for insight in memory_context["insights"]:
                parts.append(f"- {insight}")

        if memory_context["skills"]:
            parts.append("\n\n--- AVAILABLE SKILLS (learned from experience) ---")
            for skill in memory_context["skills"]:
                parts.append(
                    f"- {skill['name']}: {skill['description']} "
                    f"(success rate: {skill['success_rate']:.0%})"
                )

        if memory_context["reasoning"]:
            reasoning = memory_context["reasoning"]
            parts.append("\n\n--- RECOMMENDED APPROACH (from reasoning bank) ---")
            parts.append(
                f"Approach: {reasoning['approach']}"
                f" (success rate: {reasoning['success_rate']:.0%})"
            )

        return "\n".join(parts)

    def _store_episode(
        self,
        input_data: str,
        response,
        execution_time: float,
        memory_context: Dict[str, Any],
    ) -> None:
        """Store the processing episode in memory."""
        try:
            # Determine success based on confidence
            success = response.confidence >= 0.6
            reward = response.confidence * 2 - 1  # Map 0-1 to -1..+1

            self._db.reflexion.store_episode(
                task=f"[{self._agent.name}] {input_data[:200]}",
                input_data=input_data[:1000],
                output=response.content[:2000],
                critique="",  # Will be filled by coordinator/supervisor feedback
                reward=reward,
                success=success,
                metadata={
                    "agent_name": self._agent.name,
                    "confidence": response.confidence,
                    "execution_time": execution_time,
                    "memory_used": {
                        "episodes": len(memory_context["episodes"]),
                        "skills": len(memory_context["skills"]),
                        "had_reasoning": memory_context["reasoning"] is not None,
                    },
                },
            )

            # Store reasoning pattern
            self._db.reasoning.store_pattern(
                task_type=self._agent.name,
                approach=f"Processed with {len(memory_context['episodes'])} past episodes, "
                         f"{len(memory_context['skills'])} skills",
                context=input_data[:500],
                outcome=f"confidence={response.confidence:.2f}",
                success=success,
                reward=reward,
            )

            # Log execution event
            self._db.storage.log_event(
                agent_name=self._agent.name,
                event_type="execution",
                content=f"Processed task (confidence={response.confidence:.2f}, time={execution_time:.2f}s)",
                phase="post_execution",
                namespace=self._agent.name,
            )

        except Exception as e:
            logger.warning(f"Error storing episode for {self._agent.name}: {e}")

    def store_feedback(
        self,
        critique: str,
        reward_adjustment: float = 0.0,
    ) -> None:
        """
        Store external feedback (e.g., from coordinator or supervisor).

        This updates the most recent episode's critique and reward.

        Args:
            critique: Feedback text.
            reward_adjustment: Adjustment to reward (-1.0 to 1.0).
        """
        try:
            episodes = self._db.storage.get_episodes(
                namespace=self._agent.name, limit=1,
            )
            if episodes:
                latest = episodes[0]
                new_reward = max(-1.0, min(1.0, latest["reward"] + reward_adjustment))
                self._db.storage.update_episode(
                    latest["id"],
                    critique=critique,
                    reward=new_reward,
                )
                logger.info(
                    f"Stored feedback for {self._agent.name} "
                    f"(critique length={len(critique)}, reward_adj={reward_adjustment:+.2f})"
                )
        except Exception as e:
            logger.warning(f"Error storing feedback: {e}")

    def get_info(self) -> Dict[str, Any]:
        """Get agent info including memory stats."""
        base_info = self._agent.get_info()
        base_info["memory"] = self._db.get_stats()
        return base_info

    def __getattr__(self, name):
        """Proxy attribute access to the wrapped agent."""
        return getattr(self._agent, name)

    def __repr__(self) -> str:
        return f"MemoryEnabledAgent({self._agent.name})"


class HiveMindMemoryManager:
    """
    Manages AgentDB integration across the entire HiveMind architecture.

    Creates and coordinates per-agent memory namespaces, handles
    cross-agent causal tracking, and provides system-wide memory analytics.

    Usage:
        agentdb = AgentDB(AgentDBConfig(path="hivemind_memory.sqlite"))
        agentdb.initialize()

        memory_manager = HiveMindMemoryManager(agentdb)

        # Wrap all agents with memory
        memory_agents = memory_manager.wrap_agents(worker_agents)

        # Track cross-agent causality
        memory_manager.track_flow(worker_responses, coordinator_response)

        # Get system analytics
        stats = memory_manager.get_system_stats()
    """

    def __init__(self, agentdb: AgentDB):
        self._db = agentdb
        self._wrapped_agents: Dict[str, MemoryEnabledAgent] = {}
        logger.info("HiveMindMemoryManager initialized")

    def wrap_agent(self, agent, auto_store: bool = True) -> MemoryEnabledAgent:
        """Wrap a single agent with memory capabilities."""
        wrapped = MemoryEnabledAgent(agent, self._db, auto_store)
        self._wrapped_agents[agent.name] = wrapped
        return wrapped

    def wrap_agents(self, agents: list, auto_store: bool = True) -> List[MemoryEnabledAgent]:
        """Wrap multiple agents with memory capabilities."""
        return [self.wrap_agent(agent, auto_store) for agent in agents]

    def track_worker_to_coordinator_flow(
        self,
        worker_responses: list,
        coordinator_response,
    ) -> None:
        """
        Track causal relationships between worker outputs and coordinator synthesis.

        Args:
            worker_responses: List of AgentResponse from workers.
            coordinator_response: AgentResponse from coordinator.
        """
        global_causal = self._db.causal

        for resp in worker_responses:
            # Track: worker_output → coordinator_confidence
            global_causal.add_causal_edge(
                cause=f"{resp.agent_name}_output",
                effect="coordinator_synthesis",
                uplift=resp.confidence,
                confidence=coordinator_response.confidence,
                metadata={
                    "worker": resp.agent_name,
                    "worker_confidence": resp.confidence,
                    "coordinator_confidence": coordinator_response.confidence,
                },
            )

    def track_coordinator_to_supervisor_flow(
        self,
        coordinator_response,
        supervisor_response,
    ) -> None:
        """Track causal relationships between coordinator and supervisor."""
        self._db.causal.add_causal_edge(
            cause="coordinator_synthesis",
            effect="supervisor_decision",
            uplift=coordinator_response.confidence,
            confidence=supervisor_response.confidence,
            metadata={
                "coordinator_confidence": coordinator_response.confidence,
                "supervisor_confidence": supervisor_response.confidence,
            },
        )

    def provide_feedback_to_workers(
        self,
        supervisor_response,
    ) -> None:
        """
        Propagate supervisor feedback back to worker agents' memory.

        Uses the supervisor's confidence as a reward signal for all
        wrapped worker agents.
        """
        reward_adj = supervisor_response.confidence * 2 - 1  # Map 0-1 to -1..+1

        for name, wrapped in self._wrapped_agents.items():
            if name not in ("Coordinator", "Supervisor"):
                wrapped.store_feedback(
                    critique=f"Supervisor confidence: {supervisor_response.confidence:.2f}",
                    reward_adjustment=reward_adj * 0.3,  # Dampened feedback
                )

    def consolidate_skills(self) -> List[int]:
        """
        Consolidate successful episodes into reusable skills.

        Runs skill consolidation across all agent namespaces.
        """
        all_skill_ids = []
        for name, wrapped in self._wrapped_agents.items():
            episodes = wrapped.db.storage.get_episodes(
                namespace=name, limit=100,
            )
            if episodes:
                skill_ids = wrapped.db.skills.consolidate_from_episodes(episodes)
                all_skill_ids.extend(skill_ids)

        logger.info(f"Consolidated {len(all_skill_ids)} skills across all agents")
        return all_skill_ids

    def get_system_stats(self) -> Dict[str, Any]:
        """Get memory statistics across the entire HiveMind system."""
        stats = {
            "global": self._db.get_stats(),
            "agents": {},
        }
        for name, wrapped in self._wrapped_agents.items():
            stats["agents"][name] = wrapped.db.get_stats()
        return stats

    def get_agent_db(self, agent_name: str) -> Optional[AgentDB]:
        """Get the AgentDB instance for a specific agent."""
        wrapped = self._wrapped_agents.get(agent_name)
        return wrapped.db if wrapped else None
