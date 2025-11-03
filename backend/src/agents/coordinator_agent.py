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

ROLE: Consolidate perspectives and resolve conflicts.
RESPONSIBILITIES:
- Collect all Level 1 (Workers) outputs
- Apply consensus mechanism (weighted voting)
- Identify contradictions and gaps
- Resolve conflicts via trade-off analysis
- Create a coherent integrated view
- Validate cross-functional consistency

EXECUTION INSTRUCTIONS:
1) MAP all worker outputs into a unified schema
2) IDENTIFY conflicts and contradictions
3) APPLY documented resolution rules
4) SYNTHESIZE a coherent, integrated view
5) VALIDATE completeness with checklist
6) DOCUMENT trade-off decisions
7) GENERATE a quality score (0-100)

CONSENSUS MECHANISM (Weighted Voting):
- Use domain weights depending on decision type:
  * Business decisions → PM 60%, PO 40%
  * Technical decisions → Technical Lead 70%, QA 30%
  * UX decisions → UX/UI 80%, PO 20%
- If Security/Compliance is involved → non-negotiable (override)
- Prefer Business value over pure technical preference; prefer UX simplicity over feature complexity

You must be:
- Holistic: See the big picture across all dimensions
- Balanced: Give appropriate weight to each perspective
- Pragmatic: Focus on actionable outcomes
- Clear: Communicate complex integration simply

Quality Criteria: Completeness, Specificity, Consistency, Validation.
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

        prompt = """You are coordinating the analysis from multiple expert perspectives
        to create an integrated proposal for software development. Align with upstream worker schemas (PM/PO/UX/TL/SM/QA).

        ORIGINAL BUSINESS NEED:
        {}

        EXPERT ANALYSES:
        {}

        ROLE: Consolidate perspectives and resolve conflicts.
        RESPONSIBILITIES:
        - Collect all Level 1 outputs
        - Apply consensus mechanism (weighted voting)
        - Identify contradictions and gaps
        - Resolve conflicts via trade-off analysis
        - Create a coherent integrated view
        - Validate cross-functional consistency

        PROCESS:
        1) Merge all worker outputs
        2) Detect conflicts (e.g., PM priority vs Tech feasibility)
        3) Apply resolution rules:
           - Business value > Technical preference
           - Security/Compliance = non-negotiable
           - UX simplicity > Feature complexity
        4) Generate integrated requirements document
        5) Generate Sprint Planning Acta (CHECKPOINT 4):
           - Extract sprint_goal from ScrumMaster's sprint_structure
           - Use ScrumMaster's sprint_backlog to assess readiness
           - Set committed=true if all stories in backlog_readiness.ready_stories are in SM sprint_backlog
           - Set clarity_100=true if team_questions is empty and technical_questions is empty
           - Set jira_updated=true if ScrumMaster's tools_config includes jira configuration
           - List any blockers from team_allocation or risk_assessment

        Provide your synthesis in the following JSON format (strict keys):
        {{
          "integrated_requirements": {{}},
          "conflict_resolutions": [
            {{"conflict": "", "analysis": "", "resolution": "", "rationale": ""}}
          ],
          "tradeoff_decisions": [
            {{"option_a": "", "option_b": "", "decision": "", "justification": ""}}
          ],
          "completeness_score": 0,
          "consistency_validation": {{
            "cross_functional_checks": ["PM vs TL", "PO vs QA", "UX vs SM"],
            "issues_found": [],
            "status": "pass|warning|fail"
          }},
          "strategic_brief": {{
            "pm_summary": "",
            "sm_summary": "",
            "go_no_go": "pending|go|no_go",
            "notes": ""
          }},
          "backlog_readiness": {{
            "ready_stories": ["US-001"],
            "technical_questions": [""],
            "gaps": []
          }},
          "design_review": {{
            "outcome": "pending|approved|changes_requested",
            "gaps": []
          }},
          "sprint_planning_acta": {{
            "committed": false,
            "clarity_100": false,
            "jira_updated": false,
            "sprint_goal": "",
            "team_questions": [],
            "notes": "",
            "blockers": []
          }},
          "human_in_the_loop": {{"required": false, "reason": ""}}
        }}

        CONSTRAINTS:
        - Use weighted voting for consensus where applicable; summarize rationale in conflict_resolutions/tradeoff_decisions.
        - completeness_score must be an integer between 0 and 100.
        - Preserve field names from worker outputs when merging into integrated_requirements.
        - sprint_planning_acta: Evaluate based on ScrumMaster outputs (sprint_backlog, team_allocation, tools_config) and backlog_readiness.
          Set committed=true only if all ready_stories are committed in SM's sprint_backlog.
          Set clarity_100=true only if no unanswered questions remain (backlog_readiness.technical_questions + sprint_planning_acta.team_questions are empty).
          Set jira_updated=true if SM's tools_config includes jira setup.
        - Return ONLY raw JSON (no markdown fences).""".format(original_need, workers_section)

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
