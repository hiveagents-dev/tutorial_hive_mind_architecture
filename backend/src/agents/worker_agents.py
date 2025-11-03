"""Worker agents specialized in different aspects of software development discovery."""

from typing import Dict, Any, Optional
import json
from string import Template

from .base_agent import BaseAgent, AgentResponse
from utils.gemini_client import GeminiClient
from hivemind.methodology import AgileMethodology


class ProductManagerAgent(BaseAgent):
    """
    Product Manager Agent - Analyzes business viability and market fit.

    Focuses on:
    - Business value and ROI
    - Market analysis and competition
    - Stakeholder needs
    - Strategic alignment
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="ProductManager",
            role="Product Manager - Business & Market Analysis",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are a Senior Product Manager focused on strategic alignment and value delivery.\n"
            "ROLE: Align the business need with strategic objectives.\n"
            "RESPONSIBILITIES:\n"
            "- Define Business Case and Value Proposition\n"
            "- Identify KPIs and success metrics (OKRs)\n"
            "- Prioritize features by impact/effort using MoSCoW\n"
            "- Analyze stakeholders and their needs\n"
            "- Propose a preliminary roadmap and dependencies (contextual, not required in JSON)\n"
            "GUIDELINES:\n"
            "- Be concise, business-oriented, and evidence-driven.\n"
            "- Use MoSCoW for prioritization and OKRs for metrics.\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from PM domain perspective.\n"
            "2) Apply PM best practices and frameworks (OKR, MoSCoW).\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific, avoid generalities.\n"
            "5) Quantify with metrics/percentages when possible.\n"
            "6) Identify PM risks and assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA:\n"
            "- Completeness, Specificity, Consistency, Validation (verifiable criteria)."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide product management perspective."""
        self.logger.info(f"ProductManager analyzing: {input_data[:100]}...")

        prompt = f"""PHASE 1: Discovery & Strategic Alignment (Days 1-2) — Step 1.1 Product Manager (Initiator)
Analyze the following business need from a Product Manager perspective and produce EXACTLY the JSON schema requested.

NEED:
{input_data}

OUTPUT SCHEMA (strict keys):
{{
  "business_case": "string - brief business justification incl. ROI/impact",
  "value_proposition": "string - who benefits and how (unique value)",
  "success_metrics": ["KPI/OKR 1", "KPI/OKR 2"],
  "stakeholder_map": {{
    "primary": ["role or segment"],
    "secondary": ["role or segment"],
    "needs": {{"role": ["need1", "need2"]}}
  }},
  "priority_matrix": {{
    "Must": ["feature A", "feature B"],
    "Should": ["feature C"],
    "Could": ["feature D"],
    "Wont": []
  }},
  "market_validation": "string - assumptions, signals, and validation plan",
  "discovery_alignment": {{
    "problem_statement": "Current state → Desired state → Impact if not solved",
    "success_metrics_detailed": [
      {{"metric": "Conversion rate", "baseline": "", "target": "", "timeline": ""}}
    ],
    "business_constraints": {{
      "budget": "",
      "timeline": "",
      "compliance": []
    }},
    "assumptions": [],
    "out_of_scope": [],
    "stakeholder_signoff": {{"approved": false, "notes": ""}}
  }}
}}

CONSTRAINTS:
- Use MoSCoW in priority_matrix.
- Use OKR-style phrasing for success_metrics where possible.
- Do NOT include any extra fields or commentary.
- Return ONLY raw JSON (no markdown fences)."""

        try:
            response_text = self._call_gemini(prompt)

            # Parse JSON from response
            # Clean the response to extract JSON
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={"analysis_type": "business"}
            )

        except Exception as e:
            self.logger.error(f"Error in ProductManager processing: {str(e)}")
            raise


class ProductOwnerAgent(BaseAgent):
    """
    Product Owner Agent - Defines user stories and backlog priorities.

    Focuses on:
    - User stories and acceptance criteria
    - Backlog prioritization
    - Feature definition
    - User journey mapping
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="ProductOwner",
            role="Product Owner - User Stories & Backlog",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are a Senior Product Owner specialized in requirements engineering and agile delivery.\n"
            "ROLE: Translate business needs into actionable User Stories.\n"
            "RESPONSIBILITIES:\n"
            "- Create User Stories following INVEST\n"
            "- Define Acceptance Criteria in Given-When-Then (Gherkin)\n"
            "- Establish Definition of Done (DoD)\n"
            "- Identify Edge Cases and alternate scenarios\n"
            "- Prioritize Product Backlog\n"
            "- Define Dependencies between stories\n"
            "GUIDELINES:\n"
            "- Be clear, testable, and implementation-ready.\n"
            "- Use consistent IDs (e.g., US-001, US-002).\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from PO perspective.\n"
            "2) Apply INVEST, Gherkin, DoD/DoR; prioritize backlog.\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific and actionable.\n"
            "5) Quantify where applicable (points, priorities).\n"
            "6) Identify dependencies, risks, assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA: Completeness, Specificity, Consistency, Validation."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and generate user stories."""
        self.logger.info(f"ProductOwner analyzing: {input_data[:100]}...")

        prompt = f"""Translate UX outputs (User Journey + Wireframes) into actionable backlog and produce EXACTLY the JSON schema requested.

NEED (from UX/PM Strategic Brief):
{input_data}

OUTPUT SCHEMA (strict keys):
{{
  "epics": [
    {{
      "id": "EP-001",
      "title": "string",
      "business_value": "string",
      "stories": ["US-001", "US-002"]
    }}
  ],
  "user_stories": [
    {{
      "id": "US-001",
      "title": "string",
      "as_a": "role",
      "i_want_to": "action",
      "so_that": "benefit",
      "acceptance_criteria": [
        {{
          "scenario": "string",
          "given": "string",
          "when": "string",
          "then": "string"
        }}
      ],
      "edge_cases": ["string"],
      "story_points": 1,
      "needs_split": false,
      "priority": "Must Have|Should Have|Could Have|Won't Have",
      "dependencies": ["US-XYZ"],
      "business_rules": ["string"],
      "wsjf": {{"business_value": 0, "time_criticality": 0, "risk_reduction_opportunity": 0, "job_size": 1, "score": 0}}
    }}
  ],
  "definition_of_done": [
    "Código reviewed y aprobado",
    "Unit tests coverage > 80%",
    "Integration tests passing",
    "UX review aprobado",
    "Documentation actualizada",
    "Deployed a staging"
  ]
}}

CONSTRAINTS:
- Follow INVEST. Any story > 8 SP must be split into smaller stories and set needs_split=true.
- Acceptance Criteria must be testable (Given/When/Then) and objective.
- Prioritize using WSJF internally; reflect priority as Must/Should/Could/Won't and compute wsjf.score.
- Use sequential IDs for user stories (US-001, US-002...).
- Do NOT include any extra fields or markdown fences.
- Return ONLY raw JSON."""

        try:
            response_text = self._call_gemini(prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={"analysis_type": "user_stories"}
            )

        except Exception as e:
            self.logger.error(f"Error in ProductOwner processing: {str(e)}")
            raise


class UXUIAgent(BaseAgent):
    """
    UX/UI Designer Agent - Analyzes user experience and interface design.

    Focuses on:
    - User experience design
    - Interface requirements
    - Accessibility
    - Interaction patterns
    - Visual design considerations
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="UXUI_Designer",
            role="UX/UI Designer - User Experience & Interface",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are an experienced UX/UI Designer with expertise in user-centered design,\n"
            "interaction design, and accessibility (WCAG 2.1 AA).\n"
            "ROLE: Design optimal user experience and interaction flows.\n"
            "RESPONSIBILITIES:\n"
            "- Create User Journey Maps\n"
            "- Define Information Architecture\n"
            "- Provide Wireframe/Mockup references (descriptive or links)\n"
            "- Establish Design System requirements (colors, typography, spacing, components)\n"
            "- Identify Accessibility requirements (WCAG 2.1 AA)\n"
            "- Define responsive breakpoints\n"
            "- Specify micro-interactions and animations\n"
            "GUIDELINES:\n"
            "- Be actionable and implementation-ready.\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from UX/UI perspective.\n"
            "2) Apply journey mapping, IA, WCAG 2.1 AA, responsive design.\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific (flows, components), avoid vagueness.\n"
            "5) Quantify when possible (contrast ratios, breakpoints).\n"
            "6) Identify UX risks and assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA: Completeness, Specificity, Consistency, Validation."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide UX/UI perspective."""
        self.logger.info(f"UXUI_Designer analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a UX/UI perspective and produce EXACTLY the JSON schema requested.

NEED:
{input_data}

OUTPUT SCHEMA (strict keys):
{{
  "user_personas": [
    {{
      "name": "",
      "goals": [],
      "pain_points": [],
      "tech_savviness": "Low|Medium|High"
    }}
  ],
  "user_journey_map": {{
    "stages": ["Awareness", "Consideration", "Action", "Retention"],
    "touchpoints": [],
    "emotions": [],
    "opportunities": []
  }},
  "wireframes": [
    {{"screen": "", "url": "", "notes": ""}}
  ],
  "interaction_patterns": ["Progressive disclosure", "Inline validation"],
  "accessibility_requirements": ["Keyboard navigation", "Screen reader support"],
  "information_architecture": "",
  "design_system": {{
    "colors": {{}},
    "typography": {{}},
    "spacing": {{}},
    "components": []
  }},
  "responsive_breakpoints": ["360px", "768px", "1024px", "1440px"],
  "usability_tests": {{"participants": 0, "success_rate": "0%", "notes": ""}}
}}

CONSTRAINTS:
- Base decisions on the Strategic Brief from Phase 1 (problem_statement, constraints, success metrics).
- Ensure at least 1 persona with goals and pain_points aligned to the brief.
- Define the journey map As-Is vs To-Be within the same structure using opportunities to reflect To-Be improvements.
- Provide at least 1 wireframe reference URL.
- Accessibility must align to WCAG 2.1 AA for critical flows.
- Validate usability_tests: participants >= 5 and success_rate >= 80%.
- Do NOT include any extra fields or markdown fences.
- Return ONLY raw JSON."""

        try:
            response_text = self._call_gemini(prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return AgentResponse(
                agent_name=self.name,
                content=response_text,
                confidence=confidence,
                metadata={"role": self.role, "analysis_type": "ux_ui"}
            )

        except Exception as e:
            self.logger.error(f"Error in UXUI_Designer processing: {str(e)}")
            raise


class ScrumMasterAgent(BaseAgent):
    """
    Scrum Master Agent - Analyzes process, risks, and team dynamics.

    Focuses on:
    - Risk identification
    - Dependencies and blockers
    - Estimation and timeline
    - Team capacity
    - Agile ceremonies planning
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="ScrumMaster",
            role="Scrum Master - Process & Risk Management",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are an experienced Scrum Master with deep knowledge of agile methodologies,\n"
            "risk management (RAID), and team facilitation.\n"
            "ROLE: Ensure optimal Agile process and remove impediments.\n"
            "RESPONSIBILITIES:\n"
            "- Define Sprint structure and ceremonies\n"
            "- Identify early risks (RAID log)\n"
            "- Establish Definition of Ready (DoR)\n"
            "- Propose release strategy\n"
            "- Identify external dependencies\n"
            "- Suggest team composition and needed skills\n"
            "GUIDELINES:\n"
            "- Be pragmatic and action-oriented.\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from Scrum Master perspective.\n"
            "2) Define sprint structure, RAID, DoR, release strategy.\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific and practical.\n"
            "5) Quantify where applicable (velocity, capacity).\n"
            "6) Identify dependencies, risks, assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA: Completeness, Specificity, Consistency, Validation."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide Scrum Master perspective."""
        self.logger.info(f"ScrumMaster analyzing: {input_data[:100]}...")

        prompt = f"""Design the Agile process and facilitation plan for the following need and produce EXACTLY the JSON schema requested.

NEED:
{input_data}

OUTPUT SCHEMA (strict keys):
{{
  "sprint_structure": {{
    "duration": "2 weeks",
    "ceremonies": ["Sprint Planning", "Daily Standup", "Sprint Review", "Retrospective"]
  }},
  "definition_of_ready": [
    "Story has clear acceptance criteria",
    "Dependencies identified",
    "Story sized with points"
  ],
  "risk_assessment": [
    {{"risk": "", "impact": "High|Medium|Low", "probability": "High|Medium|Low", "mitigation": ""}}
  ],
  "team_requirements": {{
    "roles": ["Product Owner", "Scrum Master", "Developers", "QA"],
    "skills_needed": ["Backend", "Frontend", "DevOps", "QA Automation"]
  }},
  "release_strategy": "string",
  "discovery_facilitation": {{
    "initial_risks": [
      {{"risk": "", "probability": "High|Medium|Low", "impact": "Blocker|High|Medium|Low", "mitigation": ""}}
    ],
    "high_risks_mitigated": false,
    "dependencies": [
      {{"team": "", "owner": "", "dependency": "", "timeline": "Sprint X"}}
    ],
    "team_capacity": {{
      "available_developers": 0,
      "velocity_average": "0 SP/sprint",
      "vacation_planned": []
    }}
  }},
  "sprint_backlog": [
    {{
      "sprint": 1,
      "capacity_hours": 0,
      "committed_stories": ["US-001"],
      "committed_tasks": 0,
      "estimated_hours": 0,
      "buffer_hours": 0,
      "sprint_goal": "string"
    }}
  ],
  "team_allocation": {{
    "Backend Dev 1": ["TASK-001", "TASK-002"],
    "Frontend Dev 1": ["TASK-003"],
    "QA": ["TASK-005"]
  }},
  "daily_standup": {{
    "time": "09:30",
    "duration": "15 min",
    "format": "What I did / What I'll do / Blockers"
  }},
  "tools_config": {{"jira": false, "repo": false, "ci": false}},
  "team_confidence_score": 0,
  "definition_of_ready_checklist": [
    "Story tiene acceptance criteria",
    "Story está estimada",
    "Technical design está aprobado",
    "Tasks están definidas (<4h)",
    "Test scenarios están escritos",
    "Dependencies están resueltas"
  ]
}}

CONSTRAINTS:
- Use implementation_tasks from Technical Lead (if available) to compute sprint_backlog and team_allocation.
- Validate capacity: estimated_hours <= 90% of capacity_hours (keep >10% buffer); if not, reduce scope.
- Tools must indicate readiness (jira/repo/ci).
- Be concise and practical.
- Do NOT include extra fields or markdown fences.
- Return ONLY raw JSON."""

        try:
            response_text = self._call_gemini(prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={"analysis_type": "process_risks"}
            )

        except Exception as e:
            self.logger.error(f"Error in ScrumMaster processing: {str(e)}")
            raise


class TechnicalLeadAgent(BaseAgent):
    """
    Technical Lead Agent - Defines technical architecture and implementation.

    Focuses on:
    - Technical architecture
    - Technology stack selection
    - Infrastructure requirements
    - Integration points
    - Performance and scalability
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="TechnicalLead",
            role="Technical Lead - Architecture & Technology",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are a Senior Technical Lead / Software Architect.\n"
            "ROLE: Define technical architecture and technology stack.\n"
            "RESPONSIBILITIES:\n"
            "- Design solution architecture using C4 Model (Context, Container, Component)\n"
            "- Select technology stack with rationale\n"
            "- Define applicable design patterns\n"
            "- Identify Technical Debt and refactoring needs\n"
            "- Establish Non-Functional Requirements (NFRs)\n"
            "- Define integration points and APIs\n"
            "- Consult Context7 for up-to-date best practices and include key items\n"
            "GUIDELINES:\n"
            "- Be pragmatic, justify choices, and prioritize maintainability and scalability.\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from Technical Lead perspective.\n"
            "2) Apply C4, design patterns, NFRs, integration/API design.\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific and justified (rationale).\n"
            "5) Quantify NFR targets.\n"
            "6) Identify technical debt, risks, assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA: Completeness, Specificity, Consistency, Validation."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide technical architecture perspective."""
        self.logger.info(f"TechnicalLead analyzing: {input_data[:100]}...")

        prompt = f"""Define the technical architecture and stack for the following need and produce EXACTLY the JSON schema requested.

NEED:
{input_data}

OUTPUT SCHEMA (strict keys):
{{
  "architecture": {{
    "pattern": "string",
    "rationale": "string",
    "c4_diagrams": {{
      "context": "string",
      "containers": ["string"],
      "components": ["string"]
    }},
    "trade_offs": [
      {{"decision": "string", "options": ["A", "B"], "chosen": "A|B", "rationale": "string"}}
    ]
  }},
  "tech_stack": {{
    "frontend": {{"framework": "string", "rationale": "string"}},
    "backend": {{"framework": "string", "rationale": "string"}},
    "database": {{"primary": "string", "rationale": "string"}},
    "infrastructure": {{"services": ["string"], "rationale": "string"}}
  }},
  "non_functional_requirements": {{
    "performance": ["p95 < 200ms", "..."],
    "security": ["TLS 1.3", "..."],
    "scalability": ["stateless services", "..."],
    "maintainability": [""]
  }},
  "api_contracts": [
    {{
      "endpoint": "METHOD /path",
      "request_schema": {{}},
      "response_schema": {{}},
      "error_codes": ["400", "401", "500"]
    }}
  ],
  "data_models": [
    {{
      "entity": "string",
      "fields": [
        {{"name": "id", "type": "uuid", "pk": true}},
        {{"name": "user_id", "type": "uuid", "fk": "users.id"}}
      ],
      "indexes": ["field_a", "field_b"],
      "constraints": ["rule 1", "rule 2"]
    }}
  ],
  "implementation_tasks": [
    {{
      "user_story": "US-001",
      "tasks": [
        {{
          "id": "TASK-001",
          "title": "string",
          "description": "string",
          "estimated_hours": 2,
          "dependencies": ["TASK-000"],
          "assigned_to": "role or TBD",
          "acceptance_criteria": ["string"],
          "definition_of_done": ["string"],
          "technical_notes": ["string"],
          "test_requirements": ["string"]
        }}
      ],
      "total_estimated_hours": 0,
      "sprint_allocation": "Sprint 1"
    }}
  ],
  "best_practices_context7": ["string"]
}}

CONSTRAINTS:
- Use C4 textual descriptions in c4_diagrams.
- Include at least one trade_off with decision, options, chosen, rationale.
- api_contracts MUST include request/response_schema and error_codes.
- data_models MUST include fields with pk/fk, indexes y constraints.
- implementation_tasks MUST split tasks < 4 hours (otherwise split further).
- Do NOT include extra fields or markdown fences.
- Return ONLY raw JSON."""

        try:
            response_text = self._call_gemini(prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={"analysis_type": "technical_architecture"}
            )

        except Exception as e:
            self.logger.error(f"Error in TechnicalLead processing: {str(e)}")
            raise


class QASpecialistAgent(BaseAgent):
    """
    QA Specialist Agent - Defines quality assurance and testing strategy.

    Focuses on:
    - Test strategy and approach
    - Quality metrics
    - Testing types needed
    - Quality gates
    - Acceptance criteria validation
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="QA_Specialist",
            role="QA Specialist - Quality Assurance & Testing",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return (
            "You are a Senior QA Specialist.\n"
            "ROLE: Define testing strategy and quality criteria.\n"
            "RESPONSIBILITIES:\n"
            "- Create Test Strategy and Test Plan\n"
            "- Define required testing types\n"
            "- Establish coverage goals\n"
            "- Identify test data requirements\n"
            "- Define automation approach\n"
            "- Establish Quality Gates\n"
            "- Define performance and security testing needs\n"
            "GUIDELINES:\n"
            "- Shift-left, risk-based, automation-first where sensible.\n"
            "- Output MUST be strictly valid JSON per requested schema.\n"
            "EXECUTION INSTRUCTIONS:\n"
            "1) Analyze from QA perspective.\n"
            "2) Create Test Strategy/Plan; define types; automation; quality gates.\n"
            "3) Consult Context7 for up-to-date practices.\n"
            "4) Be specific and measurable.\n"
            "5) Quantify coverage goals.\n"
            "6) Identify test data needs, risks, assumptions.\n"
            "7) Produce structured JSON.\n"
            "8) Include rationale for important decisions.\n"
            "QUALITY CRITERIA: Completeness, Specificity, Consistency, Validation."
        )

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide QA perspective."""
        self.logger.info(f"QA_Specialist analyzing: {input_data[:100]}...")

        prompt_template = Template("""Define the quality strategy for the following need and produce EXACTLY the JSON schema requested.

NEED:
$input_data

OUTPUT SCHEMA (strict keys):
{{
  "test_strategy": {{
    "levels": ["unit", "integration", "e2e"],
    "approach": "shift-left",
    "automation_ratio": "70%",
    "pyramid": {{
      "unit_tests": "70%",
      "integration_tests": "20%",
      "e2e_tests": "10%"
    }}
  },
  "test_scenarios_per_story": {{
    "US-001": [
      {{
        "scenario": "string",
        "test_type": "unit|integration|e2e|performance|security",
        "priority": "P0|P1|P2",
        "steps": ["string"],
        "expected_result": "string",
        "test_data_needed": ["string"]
      }}
    ]
  },
  "performance_benchmarks": [
    {{"scenario": "string", "target": "string", "acceptable_response_time": "< 200ms p95", "acceptable_error_rate": "< 0.1%"}}
  ],
  "coverage_goals": {{
    "unit": ">=80%",
    "integration": ">=70%",
    "e2e": ">=60%"
  }},
  "quality_gates": ["no P1 defects open", "pipeline green"],
  "test_data_requirements": ["synthetic data rules", "anonymized prod samples"],
  "environments_ready": {{"staging": false, "notes": ""}},
  "ci_cd": {{"pipeline_configured": false, "suites": []}},
  "tools_recommended": ["Playwright", "PyTest", "OWASP ZAP", "k6"]
}}

CONSTRAINTS:
- Map each acceptance criterion to at least one test scenario under its story ID.
- Provide realistic performance benchmarks (p95 y error rate).
- Do NOT include extra fields or markdown fences.
- Return ONLY raw JSON.""")
        
        prompt = prompt_template.substitute(input_data=input_data)

        try:
            response_text = self._call_gemini(prompt)

            # Clean JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            confidence = self._extract_confidence(response_text)

            return self._create_response(
                content=response_text,
                confidence=confidence,
                metadata={"analysis_type": "qa_testing"}
            )

        except Exception as e:
            self.logger.error(f"Error in QA_Specialist processing: {str(e)}")
            raise
