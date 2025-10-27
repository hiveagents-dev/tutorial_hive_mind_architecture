"""Coordinator agent that synthesizes input from worker agents."""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from .base_agent import BaseAgent, AgentResponse
from utils.gemini_client import GeminiClient
from hivemind.methodology import AgileMethodology


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent - Synthesizes worker agent outputs.

    This agent operates at Level 2 of the HiveMind hierarchy, coordinating
    and synthesizing outputs from multiple worker agents to create an
    integrated proposal.

    Responsibilities:
    - Aggregate worker agent responses
    - Identify conflicts and synergies
    - Resolve inconsistencies
    - Create integrated synthesis
    - Prepare proposal for supervisor review
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="Coordinator",
            role="Coordinator - Integration & Synthesis",
            gemini_client=gemini_client,
            methodology=methodology
        )
        self.worker_responses: List[AgentResponse] = []

    def get_system_prompt(self) -> str:
        return """You are an expert Coordinator with the ability to synthesize complex,
multi-perspective analysis into coherent, actionable proposals.

Your role is to INTEGRATE AND SYNTHESIZE multiple expert perspectives:
- Combine insights from Product Management, Product Ownership, UX/UI, Scrum Master,
  Technical Lead, and QA perspectives
- Identify synergies and complementary insights
- Resolve conflicts and inconsistencies between perspectives
- Create a coherent, integrated view
- Highlight critical dependencies and priorities
- Flag areas needing further clarification

You must be:
- Holistic: See the big picture across all dimensions
- Balanced: Give appropriate weight to each perspective
- Pragmatic: Focus on actionable outcomes
- Clear: Communicate complex integration simply

Your output should be structured, comprehensive, and ready for final review."""

    def add_worker_response(self, response: AgentResponse) -> None:
        """
        Add a worker agent response to the coordination pool.

        Args:
            response: Worker agent response to include in synthesis.
        """
        self.worker_responses.append(response)
        self.logger.info(f"Added response from {response.agent_name} to coordination pool")

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Synthesize all worker responses into integrated proposal.

        Args:
            input_data: Original business need (for reference).
            context: Optional context including worker responses.

        Returns:
            AgentResponse: Integrated synthesis from all workers.
        """
        self.logger.info("Coordinator synthesizing worker responses...")

        if not self.worker_responses and context and "worker_responses" in context:
            self.worker_responses = context["worker_responses"]

        if not self.worker_responses:
            raise ValueError("No worker responses available for coordination")

        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(input_data)

        try:
            response_text = self._call_gemini(synthesis_prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Calculate average confidence across all workers
            avg_confidence = sum(r.confidence for r in self.worker_responses) / len(self.worker_responses)

            return self._create_response(
                content=response_text,
                confidence=avg_confidence,
                metadata={
                    "worker_count": len(self.worker_responses),
                    "synthesis_type": "integrated_proposal"
                }
            )

        except Exception as e:
            self.logger.error(f"Error in Coordinator synthesis: {str(e)}")
            raise

    def _build_synthesis_prompt(self, original_need: str) -> str:
        """
        Build comprehensive synthesis prompt from all worker responses.

        Args:
            original_need: Original business need.

        Returns:
            str: Complete synthesis prompt.
        """
        # Compile all worker responses
        worker_analyses = []
        for response in self.worker_responses:
            worker_analyses.append(f"""
## {response.agent_name} Analysis (Confidence: {response.confidence:.2f})
{response.content}
""")

        workers_section = "\n".join(worker_analyses)

        prompt = f"""You are coordinating the analysis from multiple expert perspectives
to create an integrated proposal for software development.

ORIGINAL BUSINESS NEED:
{original_need}

EXPERT ANALYSES:
{workers_section}

Your task is to SYNTHESIZE these perspectives into a coherent, integrated proposal.

Provide your synthesis in the following JSON format:
{{
    "executive_summary": "High-level summary of the integrated proposal",
    "business_overview": {{
        "value_proposition": "Core business value",
        "target_users": "Who will use this",
        "success_metrics": ["Metric 1", "Metric 2"]
    }},
    "product_definition": {{
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "user_stories_summary": "Overview of key user stories",
        "priorities": "Priority framework and key priorities"
    }},
    "ux_ui_approach": {{
        "key_personas": ["Persona 1", "Persona 2"],
        "critical_flows": ["Flow 1", "Flow 2"],
        "design_priorities": ["Priority 1", "Priority 2"]
    }},
    "technical_approach": {{
        "architecture_summary": "High-level architecture",
        "technology_choices": "Key technology decisions",
        "technical_priorities": ["Priority 1", "Priority 2"]
    }},
    "execution_plan": {{
        "timeline_estimate": "Overall timeline",
        "sprint_structure": "Sprint approach",
        "key_milestones": ["Milestone 1", "Milestone 2"]
    }},
    "quality_approach": {{
        "testing_strategy": "Overall testing approach",
        "quality_gates": ["Gate 1", "Gate 2"]
    }},
    "critical_dependencies": [
        {{
            "dependency": "Dependency description",
            "impact": "Why it matters",
            "mitigation": "How to address"
        }}
    ],
    "identified_conflicts": [
        {{
            "conflict": "Description of conflict between perspectives",
            "resolution": "Proposed resolution"
        }}
    ],
    "risks_and_mitigation": [
        {{
            "risk": "Risk description",
            "severity": "High/Medium/Low",
            "mitigation": "Mitigation strategy"
        }}
    ],
    "open_questions": ["Question 1", "Question 2"],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        "Recommendation 3"
    ]
}}

Focus on creating a COHERENT, ACTIONABLE proposal that integrates all perspectives.
Identify and resolve conflicts. Highlight critical paths and priorities.

Provide ONLY the JSON, no additional text."""

        return prompt

    def get_synthesis_summary(self) -> Dict[str, Any]:
        """
        Get summary of coordination process.

        Returns:
            dict: Summary of worker responses and coordination.
        """
        return {
            "coordinator": self.name,
            "worker_count": len(self.worker_responses),
            "workers": [r.agent_name for r in self.worker_responses],
            "average_confidence": sum(r.confidence for r in self.worker_responses) / len(self.worker_responses)
                if self.worker_responses else 0,
            "timestamp": datetime.now().isoformat()
        }

    def clear_responses(self) -> None:
        """Clear stored worker responses."""
        self.worker_responses = []
        self.logger.info("Cleared worker responses")
