"""Worker agents specialized in different aspects of software development discovery."""

from typing import Dict, Any, Optional
import json

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
        return """You are an experienced Product Manager with deep expertise in product strategy,
business analysis, and market research.

Your role is to analyze software development needs from a BUSINESS perspective:
- Evaluate business value and potential ROI
- Identify target market and user segments
- Analyze competitive landscape
- Define success metrics and KPIs
- Assess strategic alignment with company goals
- Identify key stakeholders and their needs

Provide structured analysis focusing on WHY this product/feature matters from a business standpoint.
Be analytical, data-driven, and focused on business outcomes."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide product management perspective."""
        self.logger.info(f"ProductManager analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a Product Management perspective:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "business_value": "Clear statement of business value",
    "target_market": "Description of target market and users",
    "competitive_analysis": "Analysis of competitive landscape",
    "success_metrics": ["Metric 1", "Metric 2", "Metric 3"],
    "strategic_alignment": "How this aligns with business strategy",
    "stakeholders": ["Stakeholder 1", "Stakeholder 2"],
    "risks_and_opportunities": "Key business risks and opportunities",
    "recommendations": "Strategic recommendations"
}}

Provide ONLY the JSON, no additional text."""

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
        return """You are an experienced Product Owner expert in agile methodologies,
user story writing, and backlog management.

Your role is to translate business needs into ACTIONABLE USER STORIES:
- Write clear, testable user stories with acceptance criteria
- Prioritize features using frameworks like MoSCoW or RICE
- Define epic structure and feature breakdown
- Map user journeys and flows
- Identify dependencies between stories
- Estimate relative complexity

Focus on WHAT needs to be built and HOW to structure the work.
Use agile best practices and clear, actionable language."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and generate user stories."""
        self.logger.info(f"ProductOwner analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need and create user stories:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "epics": [
        {{
            "name": "Epic name",
            "description": "Epic description",
            "priority": "High/Medium/Low"
        }}
    ],
    "user_stories": [
        {{
            "title": "As a [user], I want [goal], so that [benefit]",
            "acceptance_criteria": ["Criterion 1", "Criterion 2"],
            "priority": "Must/Should/Could/Won't",
            "complexity": "High/Medium/Low",
            "dependencies": ["Story ID if any"]
        }}
    ],
    "user_journeys": ["Journey 1 description", "Journey 2 description"],
    "feature_priorities": "Explanation of prioritization approach",
    "backlog_structure": "How to organize the backlog"
}}

Provide ONLY the JSON, no additional text."""

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
        return """You are an experienced UX/UI Designer with expertise in user-centered design,
interface design, and accessibility.

Your role is to analyze USER EXPERIENCE AND INTERFACE requirements:
- Define user personas and their needs
- Map user flows and interaction patterns
- Identify key UI components and screens
- Define accessibility requirements (WCAG compliance)
- Specify information architecture
- Identify design system needs
- Define responsive design requirements

Focus on creating intuitive, accessible, and delightful user experiences.
Consider usability, accessibility, and visual consistency."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide UX/UI perspective."""
        self.logger.info(f"UXUI_Designer analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a UX/UI perspective:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "user_personas": [
        {{
            "name": "Persona name",
            "description": "Persona description",
            "goals": ["Goal 1", "Goal 2"],
            "pain_points": ["Pain 1", "Pain 2"]
        }}
    ],
    "user_flows": ["Flow 1 description", "Flow 2 description"],
    "key_screens": ["Screen 1", "Screen 2", "Screen 3"],
    "ui_components": ["Component 1", "Component 2"],
    "accessibility_requirements": ["Requirement 1", "Requirement 2"],
    "information_architecture": "Structure and navigation approach",
    "design_system_needs": "Design system requirements",
    "responsive_requirements": "Mobile, tablet, desktop considerations",
    "ux_considerations": "Key UX principles and considerations"
}}

Provide ONLY the JSON, no additional text."""

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
        return """You are an experienced Scrum Master with deep knowledge of agile methodologies,
risk management, and team facilitation.

Your role is to analyze PROJECT EXECUTION AND RISKS:
- Identify risks and mitigation strategies
- Map dependencies and potential blockers
- Estimate timeline and sprint planning
- Assess team capacity needs
- Define agile ceremonies and processes
- Identify collaboration requirements
- Plan incremental delivery approach

Focus on HOW the team will execute and what could go wrong.
Be proactive in identifying risks and planning mitigation."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide Scrum Master perspective."""
        self.logger.info(f"ScrumMaster analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a Scrum Master perspective:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "identified_risks": [
        {{
            "risk": "Risk description",
            "impact": "High/Medium/Low",
            "probability": "High/Medium/Low",
            "mitigation": "Mitigation strategy"
        }}
    ],
    "dependencies": ["Dependency 1", "Dependency 2"],
    "potential_blockers": ["Blocker 1", "Blocker 2"],
    "timeline_estimate": "Rough timeline estimate",
    "sprint_structure": "Proposed sprint structure and duration",
    "team_capacity_needs": "Skills and roles needed",
    "agile_ceremonies": ["Ceremony 1", "Ceremony 2"],
    "collaboration_requirements": "How teams need to work together",
    "incremental_delivery_plan": "How to deliver value incrementally",
    "success_factors": ["Factor 1", "Factor 2"]
}}

Provide ONLY the JSON, no additional text."""

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
        return """You are an experienced Technical Lead / Software Architect with expertise in
system design, technology selection, and infrastructure planning.

Your role is to define TECHNICAL ARCHITECTURE AND IMPLEMENTATION:
- Design system architecture and components
- Select appropriate technology stack
- Define infrastructure and deployment requirements
- Identify integration points and APIs
- Specify performance and scalability requirements
- Define security considerations
- Plan data architecture and storage
- Identify technical risks and constraints

Focus on HOW to technically implement the solution.
Be pragmatic, consider trade-offs, and prioritize maintainability."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide technical architecture perspective."""
        self.logger.info(f"TechnicalLead analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a Technical Lead perspective:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "architecture_overview": "High-level architecture description",
    "system_components": [
        {{
            "name": "Component name",
            "description": "Component description",
            "technology": "Proposed technology"
        }}
    ],
    "technology_stack": {{
        "frontend": ["Technology 1", "Technology 2"],
        "backend": ["Technology 1", "Technology 2"],
        "database": ["Technology 1"],
        "infrastructure": ["Technology 1", "Technology 2"]
    }},
    "infrastructure_requirements": "Cloud, hosting, DevOps needs",
    "integration_points": ["Integration 1", "Integration 2"],
    "apis_and_services": ["API 1", "API 2"],
    "performance_requirements": "Performance and scalability needs",
    "security_considerations": ["Security requirement 1", "Security requirement 2"],
    "data_architecture": "Data model and storage approach",
    "technical_risks": ["Risk 1", "Risk 2"],
    "technical_constraints": ["Constraint 1", "Constraint 2"]
}}

Provide ONLY the JSON, no additional text."""

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
        return """You are an experienced QA Specialist with expertise in test strategy,
quality assurance, and testing methodologies.

Your role is to define QUALITY ASSURANCE AND TESTING APPROACH:
- Define comprehensive test strategy
- Identify types of testing needed (unit, integration, e2e, performance, security)
- Specify quality metrics and KPIs
- Define quality gates and acceptance criteria
- Plan test automation approach
- Identify testing tools and frameworks
- Define bug tracking and reporting process
- Specify non-functional testing requirements

Focus on ensuring QUALITY and catching issues early.
Be thorough, systematic, and risk-aware in your testing approach."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process business need and provide QA perspective."""
        self.logger.info(f"QA_Specialist analyzing: {input_data[:100]}...")

        prompt = f"""Analyze the following software development need from a QA Specialist perspective:

NEED:
{input_data}

Provide your analysis in the following JSON format:
{{
    "test_strategy": "Overall testing approach and philosophy",
    "testing_types": [
        {{
            "type": "Unit/Integration/E2E/Performance/Security/etc",
            "description": "What to test and why",
            "priority": "High/Medium/Low"
        }}
    ],
    "quality_metrics": ["Metric 1", "Metric 2", "Metric 3"],
    "quality_gates": ["Gate 1", "Gate 2"],
    "test_automation_approach": "Automation strategy and tools",
    "testing_tools": ["Tool 1", "Tool 2"],
    "test_environments": ["Environment 1", "Environment 2"],
    "acceptance_criteria_validation": "How to validate acceptance criteria",
    "non_functional_requirements": ["NFR 1", "NFR 2"],
    "bug_tracking_process": "Bug reporting and tracking approach",
    "quality_risks": ["Risk 1", "Risk 2"]
}}

Provide ONLY the JSON, no additional text."""

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
