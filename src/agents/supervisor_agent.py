"""Supervisor agent that makes final decisions based on coordinator synthesis."""

from typing import Dict, Any, Optional
import json
from datetime import datetime

from .base_agent import BaseAgent, AgentResponse
from utils.gemini_client import GeminiClient
from hivemind.methodology import AgileMethodology


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Final decision maker and requirements generator.

    This agent operates at Level 3 of the HiveMind hierarchy, making final
    decisions and generating the comprehensive technical requirements document.

    Responsibilities:
    - Evaluate coordinator's integrated proposal
    - Validate completeness and feasibility
    - Make final decisions on approach
    - Generate formal technical requirements document
    - Provide executive summary and recommendations
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="Supervisor",
            role="Supervisor - Final Decision & Requirements",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return """You are a senior executive and technical leader with the authority
and expertise to make final decisions on software development initiatives.

Your role is to:
- EVALUATE the integrated proposal from the coordination team
- VALIDATE completeness, feasibility, and alignment
- MAKE FINAL DECISIONS on approach and priorities
- GENERATE comprehensive technical requirements document
- PROVIDE executive guidance and strategic direction

You must be:
- Strategic: See long-term implications
- Decisive: Make clear, justified decisions
- Comprehensive: Ensure nothing critical is missing
- Practical: Balance ambition with feasibility
- Clear: Communicate decisions unambiguously

Your output should be the FINAL, AUTHORITATIVE technical requirements document
ready for development team consumption."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate final technical requirements document.

        Args:
            input_data: Original business need.
            context: Must include coordinator_synthesis.

        Returns:
            AgentResponse: Final technical requirements document.
        """
        self.logger.info("Supervisor generating final requirements document...")

        if not context or "coordinator_synthesis" not in context:
            raise ValueError("Supervisor requires coordinator synthesis in context")

        coordinator_synthesis = context["coordinator_synthesis"]

        # Build final requirements prompt
        requirements_prompt = self._build_requirements_prompt(
            input_data,
            coordinator_synthesis
        )

        try:
            response_text = self._call_gemini(requirements_prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Supervisor confidence is high if reached this stage
            confidence = 0.95

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={
                    "document_type": "technical_requirements",
                    "status": "final"
                }
            )

        except Exception as e:
            self.logger.error(f"Error in Supervisor requirements generation: {str(e)}")
            raise

    def _build_requirements_prompt(
        self,
        original_need: str,
        coordinator_synthesis: str
    ) -> str:
        """
        Build comprehensive requirements generation prompt.

        Args:
            original_need: Original business need.
            coordinator_synthesis: Synthesis from coordinator.

        Returns:
            str: Complete requirements prompt.
        """
        prompt = f"""You are generating the FINAL TECHNICAL REQUIREMENTS DOCUMENT
for a software development initiative.

ORIGINAL BUSINESS NEED:
{original_need}

INTEGRATED PROPOSAL FROM COORDINATION TEAM:
{coordinator_synthesis}

Your task is to generate a comprehensive, authoritative TECHNICAL REQUIREMENTS DOCUMENT.

Provide your requirements document in the following JSON format:

{{
    "document_metadata": {{
        "title": "Technical Requirements Document Title",
        "version": "1.0",
        "date": "{datetime.now().strftime('%Y-%m-%d')}",
        "status": "Approved",
        "approver": "Supervisor Agent"
    }},

    "executive_summary": {{
        "overview": "High-level summary of the initiative",
        "business_objectives": ["Objective 1", "Objective 2"],
        "key_deliverables": ["Deliverable 1", "Deliverable 2"],
        "timeline": "Overall timeline estimate",
        "budget_considerations": "Budget and resource considerations"
    }},

    "business_requirements": {{
        "problem_statement": "Clear problem being solved",
        "target_users": [
            {{
                "persona": "Persona name",
                "needs": ["Need 1", "Need 2"],
                "goals": ["Goal 1", "Goal 2"]
            }}
        ],
        "business_value": "Expected business value and ROI",
        "success_metrics": [
            {{
                "metric": "Metric name",
                "target": "Target value",
                "measurement": "How to measure"
            }}
        ]
    }},

    "functional_requirements": {{
        "features": [
            {{
                "id": "FR-001",
                "name": "Feature name",
                "description": "Detailed description",
                "priority": "Must Have/Should Have/Could Have/Won't Have",
                "user_stories": ["Story 1", "Story 2"],
                "acceptance_criteria": ["Criterion 1", "Criterion 2"]
            }}
        ],
        "user_flows": [
            {{
                "flow_name": "Flow name",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "alternative_paths": ["Alternative 1"]
            }}
        ]
    }},

    "non_functional_requirements": {{
        "performance": [
            {{
                "requirement": "Performance requirement",
                "target": "Target metric"
            }}
        ],
        "security": ["Security requirement 1", "Security requirement 2"],
        "scalability": "Scalability requirements",
        "reliability": "Reliability and availability requirements",
        "usability": "Usability requirements",
        "accessibility": "Accessibility requirements (WCAG level)"
    }},

    "technical_specifications": {{
        "architecture": {{
            "overview": "Architecture overview",
            "components": [
                {{
                    "name": "Component name",
                    "description": "Component description",
                    "technology": "Technology choice",
                    "responsibilities": ["Responsibility 1"]
                }}
            ],
            "data_flow": "How data flows through the system"
        }},
        "technology_stack": {{
            "frontend": [
                {{
                    "technology": "Technology name",
                    "version": "Version",
                    "justification": "Why chosen"
                }}
            ],
            "backend": [
                {{
                    "technology": "Technology name",
                    "version": "Version",
                    "justification": "Why chosen"
                }}
            ],
            "database": [
                {{
                    "technology": "Technology name",
                    "type": "SQL/NoSQL/etc",
                    "justification": "Why chosen"
                }}
            ],
            "infrastructure": [
                {{
                    "component": "Component name",
                    "provider": "Provider name",
                    "justification": "Why chosen"
                }}
            ]
        }},
        "integrations": [
            {{
                "system": "External system name",
                "type": "API/Webhook/etc",
                "purpose": "Integration purpose",
                "requirements": ["Requirement 1"]
            }}
        ],
        "data_model": "Overview of data model and key entities"
    }},

    "ux_ui_requirements": {{
        "design_system": "Design system approach",
        "key_screens": [
            {{
                "screen": "Screen name",
                "purpose": "Purpose",
                "key_components": ["Component 1", "Component 2"]
            }}
        ],
        "responsive_design": "Mobile/tablet/desktop requirements",
        "accessibility_standards": "WCAG 2.1 AA or higher",
        "branding_guidelines": "Branding requirements"
    }},

    "quality_assurance": {{
        "testing_strategy": "Overall testing approach",
        "test_types": [
            {{
                "type": "Test type",
                "coverage_target": "Coverage percentage",
                "tools": ["Tool 1"]
            }}
        ],
        "quality_gates": [
            {{
                "gate": "Gate name",
                "criteria": "Pass criteria",
                "enforcement": "When enforced"
            }}
        ],
        "acceptance_process": "How features will be accepted"
    }},

    "implementation_plan": {{
        "phases": [
            {{
                "phase": "Phase name",
                "duration": "Duration estimate",
                "deliverables": ["Deliverable 1"],
                "dependencies": ["Dependency 1"]
            }}
        ],
        "sprints": {{
            "duration": "Sprint duration",
            "ceremonies": ["Ceremony 1", "Ceremony 2"]
        }},
        "milestones": [
            {{
                "milestone": "Milestone name",
                "date": "Target date",
                "criteria": "Completion criteria"
            }}
        ]
    }},

    "risks_and_mitigation": [
        {{
            "risk_id": "RISK-001",
            "category": "Technical/Business/Process/etc",
            "description": "Risk description",
            "probability": "High/Medium/Low",
            "impact": "High/Medium/Low",
            "mitigation_strategy": "How to mitigate",
            "contingency_plan": "Plan B if risk materializes",
            "owner": "Who owns this risk"
        }}
    ],

    "dependencies_and_constraints": {{
        "external_dependencies": [
            {{
                "dependency": "Dependency description",
                "provider": "Who provides it",
                "risk": "Risk if unavailable"
            }}
        ],
        "technical_constraints": ["Constraint 1", "Constraint 2"],
        "business_constraints": ["Constraint 1", "Constraint 2"],
        "resource_constraints": ["Constraint 1"]
    }},

    "team_and_roles": {{
        "required_roles": [
            {{
                "role": "Role name",
                "responsibilities": ["Responsibility 1"],
                "skills_required": ["Skill 1"],
                "allocation": "Full-time/Part-time/percentage"
            }}
        ],
        "team_structure": "How the team is organized",
        "collaboration_model": "How teams work together"
    }},

    "assumptions": [
        "Assumption 1",
        "Assumption 2",
        "Assumption 3"
    ],

    "out_of_scope": [
        "What is explicitly NOT included in this initiative"
    ],

    "approval_and_sign_off": {{
        "stakeholders": [
            {{
                "name": "Stakeholder role",
                "approval_required": "Yes/No",
                "sign_off_criteria": "What they need to approve"
            }}
        ],
        "approval_status": "Pending/Approved",
        "next_steps": ["Next step 1", "Next step 2"]
    }},

    "appendix": {{
        "glossary": [
            {{
                "term": "Technical term",
                "definition": "Definition"
            }}
        ],
        "references": [
            "Reference document 1",
            "Reference document 2"
        ]
    }}
}}

Generate a COMPLETE, PROFESSIONAL, PRODUCTION-READY technical requirements document.
Be specific, measurable, and actionable. Include all necessary details for development teams.

Provide ONLY the JSON, no additional text."""

        return prompt

    def generate_executive_summary(self, requirements_doc: str) -> str:
        """
        Generate a brief executive summary from full requirements.

        Args:
            requirements_doc: Full requirements document JSON.

        Returns:
            str: Executive summary in plain text.
        """
        try:
            doc = json.loads(requirements_doc)
            exec_summary = doc.get("executive_summary", {})

            summary = f"""
TECHNICAL REQUIREMENTS - EXECUTIVE SUMMARY
{'=' * 50}

{exec_summary.get('overview', 'N/A')}

BUSINESS OBJECTIVES:
{chr(10).join(f"  • {obj}" for obj in exec_summary.get('business_objectives', []))}

KEY DELIVERABLES:
{chr(10).join(f"  • {deliv}" for deliv in exec_summary.get('key_deliverables', []))}

TIMELINE: {exec_summary.get('timeline', 'N/A')}

BUDGET: {exec_summary.get('budget_considerations', 'N/A')}
"""
            return summary.strip()

        except Exception as e:
            self.logger.error(f"Error generating executive summary: {str(e)}")
            return "Error generating executive summary"
