# Tutorial: Implementing Hive Mind Architecture - Part II

**Continuation of TUTORIAL_HIVE_MIND.md**

---

# Part III: Practical Implementation (Continued)

## 11. Implementing Worker Agents

### 11.1 Worker Agent Architecture

**Design Pattern**: Template Method + Strategy

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    """
    Structured agent response following Pydantic validation.

    Design Decision: Use Pydantic for:
    - Runtime validation
    - Serialization/deserialization
    - Type safety
    - API compatibility
    """
    agent_name: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    methodology: Optional[str] = None
    methodology_specific_output: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """
    Abstract base class implementing Template Method pattern.

    Template Method: process() defines skeleton, subclasses fill details
    Strategy: MethodologyAdapter provides interchangeable strategies
    """

    def __init__(
        self,
        name: str,
        role: str,
        gemini_client: GeminiClient,
        methodology: Optional[AgileMethodology] = None
    ):
        self.name = name
        self.role = role
        self.gemini_client = gemini_client
        self.methodology = methodology
        self.methodology_adapter = (
            MethodologyAdapter(methodology) if methodology else None
        )
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Define agent's expertise and instructions.

        This is the KEY differentiation between agents.
        Each agent implements domain-specific prompts.

        Returns:
            Methodology-agnostic system prompt
        """
        pass

    def get_adapted_system_prompt(self) -> str:
        """
        Apply methodology adaptation to base prompt.

        Template Method: Calls get_system_prompt() then adapts
        """
        base_prompt = self.get_system_prompt()

        if self.methodology_adapter:
            return self.methodology_adapter.adapt_system_prompt(
                base_prompt,
                self.name
            )

        return base_prompt

    def process(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Template Method: Main processing workflow.

        Steps:
        1. Get adapted system prompt
        2. Build user prompt with context
        3. Call LLM
        4. Extract confidence
        5. Create structured response

        Subclasses DON'T override this; override get_system_prompt() instead.
        """
        self.logger.info(f"Processing input: {input_data[:100]}...")

        # Step 1: Get adapted prompt
        system_prompt = self.get_adapted_system_prompt()

        # Step 2: Build user prompt
        user_prompt = self._build_user_prompt(input_data, context)

        # Step 3: Call LLM
        response_text = self._call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt
        )

        # Step 4: Extract confidence
        confidence = self._extract_confidence(response_text)

        # Step 5: Create response
        return self._create_response(
            content=response_text,
            confidence=confidence,
            metadata={
                "role": self.role,
                "methodology": self.methodology.value if self.methodology else None,
                "context_provided": context is not None
            }
        )

    def _build_user_prompt(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt with optional context."""
        prompt_parts = [f"Business Need:\n{input_data}"]

        if context:
            # Add context from previous phases
            if "dependencies" in context:
                prompt_parts.append("\n## Context from Previous Phases:")
                for dep in context["dependencies"]:
                    prompt_parts.append(
                        f"\n### {dep['phase']} ({dep['agent']}):"
                    )
                    prompt_parts.append(f"Confidence: {dep['confidence']:.2f}")
                    prompt_parts.append(f"Output: {dep['content']}")

            # Add methodology context
            if "methodology_context" in context:
                prompt_parts.append(
                    f"\n## Methodology: {context['methodology_context']}"
                )

        prompt_parts.append(
            "\n\nPlease provide your comprehensive analysis."
        )

        return "\n".join(prompt_parts)

    def _call_gemini(
        self,
        prompt: str,
        system_instruction: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Call Gemini API with retry logic.

        Note: Actual retry logic in GeminiClient
        """
        try:
            response = self.gemini_client.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature
            )
            return response

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    def _extract_confidence(self, response_text: str) -> float:
        """
        Extract confidence from response.

        Current: Heuristic based on length and completeness
        Future: Ask LLM to explicitly state confidence
        """
        # Simple heuristic: longer, structured responses = higher confidence
        length_score = min(len(response_text) / 1000, 1.0)

        # Check for structured sections
        has_sections = sum(1 for marker in ["##", "###", "1.", "2."]
                          if marker in response_text)
        structure_score = min(has_sections / 5, 1.0)

        # Weighted average
        confidence = (0.6 * length_score) + (0.4 * structure_score)

        # Ensure minimum confidence
        return max(0.5, confidence)

    def _create_response(
        self,
        content: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create validated AgentResponse."""
        if metadata is None:
            metadata = {}

        metadata.update({
            "role": self.role,
            "methodology": self.methodology.value if self.methodology else None
        })

        # Get methodology-specific output format
        methodology_output = None
        if self.methodology_adapter:
            methodology_output = self.methodology_adapter.adapt_output_format(
                self.name
            )

        return AgentResponse(
            agent_name=self.name,
            content=content,
            confidence=confidence,
            metadata=metadata,
            methodology=self.methodology.value if self.methodology else None,
            methodology_specific_output=methodology_output
        )
```

### 11.2 Concrete Worker Implementation: Product Manager

```python
class ProductManagerAgent(BaseAgent):
    """
    Product Manager: Business viability and market analysis.

    Expertise:
    - Business case development
    - Market analysis
    - Value proposition
    - KPIs and metrics
    - Stakeholder mapping
    """

    def __init__(self, gemini_client, methodology=None):
        super().__init__(
            name="ProductManager",
            role="Product Manager - Business Strategy & Market Analysis",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        """Product Manager system prompt."""
        return """
# Role: Product Manager

You are an experienced Product Manager responsible for ensuring business viability and market fit.

## Your Core Responsibilities

### 1. Business Case Development
- Define clear value proposition
- Identify target market segments
- Estimate Total Addressable Market (TAM), Serviceable Available Market (SAM), Serviceable Obtainable Market (SOM)
- Project revenue potential and ROI
- Assess competitive landscape

### 2. Stakeholder Analysis
- Map all stakeholders (internal and external)
- Define stakeholder needs and expectations
- Identify key decision-makers
- Plan stakeholder communication strategy

### 3. Strategic Alignment
- Ensure product aligns with business strategy
- Define product vision and mission
- Set strategic objectives and KPIs
- Identify risks and mitigation strategies

### 4. Market Analysis
- Analyze market trends and dynamics
- Identify competitive advantages
- Assess barriers to entry
- Evaluate market timing

### 5. Value Metrics
- Define success metrics (KPIs)
- Establish measurement framework
- Set targets and milestones
- Plan value delivery timeline

## Your Output Structure

Please structure your analysis with:

### 1. Executive Summary
Brief overview of business opportunity and recommendation

### 2. Business Case
- Value Proposition
- Market Analysis (TAM/SAM/SOM)
- Revenue Projections
- Cost-Benefit Analysis
- ROI Estimation

### 3. Stakeholder Map
- Key Stakeholders
- Their Needs
- Engagement Strategy

### 4. Strategic Fit
- Alignment with Business Strategy
- Strategic Objectives
- Success Criteria (KPIs)

### 5. Risks and Mitigation
- Business Risks
- Market Risks
- Mitigation Strategies

### 6. Go/No-Go Recommendation
Clear recommendation with justification

## Analysis Guidelines

1. **Data-Driven**: Base recommendations on market data and analysis
2. **ROI-Focused**: Always consider return on investment
3. **Risk-Aware**: Identify and quantify risks
4. **Stakeholder-Centric**: Consider all stakeholder perspectives
5. **Strategic**: Tie to broader business strategy

## Output Format

Use clear markdown formatting with:
- Headings for structure
- Bullet points for lists
- Tables for comparative analysis
- Bold for key findings
- Numbers/metrics where applicable

---

**Your goal**: Provide business leadership with confidence that this initiative is viable, valuable, and aligned with strategic objectives.
"""


# Usage Example:
pm_agent = ProductManagerAgent(
    gemini_client=GeminiClient(api_key=os.getenv("GEMINI_API_KEY")),
    methodology=AgileMethodology.SCRUM
)

business_need = """
Build a mobile-first customer loyalty program for our retail chain.
We have 500 stores across the country and 2 million registered customers.
Current challenge: Low repeat purchase rate (35% want to improve to 60%).
"""

response = pm_agent.process(business_need)

print(f"Agent: {response.agent_name}")
print(f"Confidence: {response.confidence:.2%}")
print(f"Output:\n{response.content[:500]}...")
```

### 11.3 Concrete Worker Implementation: Technical Lead

```python
class TechnicalLeadAgent(BaseAgent):
    """
    Technical Lead: Architecture and technical decisions.

    Expertise:
    - System architecture (C4 model)
    - Technology stack selection
    - Non-functional requirements
    - Technical feasibility
    - Infrastructure planning
    """

    def __init__(self, gemini_client, methodology=None):
        super().__init__(
            name="TechnicalLead",
            role="Technical Lead - System Architecture & Technology",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        """Technical Lead system prompt."""
        return """
# Role: Technical Lead / System Architect

You are a seasoned Technical Lead responsible for technical architecture and implementation strategy.

## Your Core Responsibilities

### 1. System Architecture Design
- Create C4 architecture diagrams (Context, Container, Component, Code)
- Define system boundaries and interfaces
- Design for scalability, reliability, maintainability
- Apply appropriate architectural patterns
- Consider cloud-native design principles

### 2. Technology Stack Selection
- Recommend programming languages
- Select frameworks and libraries
- Choose databases and data stores
- Identify infrastructure requirements
- Consider team expertise and learning curve

### 3. Non-Functional Requirements (NFRs)
- Performance requirements (latency, throughput)
- Scalability requirements (users, data, load)
- Reliability (availability, fault tolerance)
- Security (authentication, authorization, data protection)
- Maintainability (code quality, documentation)

### 4. Technical Feasibility Assessment
- Identify technical risks
- Assess complexity
- Estimate development effort
- Validate against constraints
- Recommend proof-of-concepts if needed

### 5. Integration Strategy
- Define APIs and interfaces
- Plan third-party integrations
- Design data flows
- Specify communication protocols
- Consider backwards compatibility

## Your Output Structure

### 1. Architecture Overview
High-level system architecture description

### 2. C4 Architecture Diagrams
- **Context Diagram**: System in its environment
- **Container Diagram**: High-level technology choices
- **Component Diagram**: Key components and relationships
- **(Optional) Code Diagram**: Detailed class/function design

Use Mermaid or PlantUML notation for diagrams

### 3. Technology Stack
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | ... | ... |
| Backend | ... | ... |
| Database | ... | ... |
| Infrastructure | ... | ... |

### 4. Non-Functional Requirements

**Performance**:
- Metric: ...
- Target: ...
- Measurement: ...

**Scalability**:
- ...

**Security**:
- ...

(Cover: Performance, Scalability, Reliability, Security, Maintainability)

### 5. Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| ... | ... | ... | ... |

### 6. Development Approach
- Recommended development methodology
- Phases/milestones
- Technology POCs needed
- Testing strategy

### 7. Infrastructure Requirements
- Compute resources
- Storage requirements
- Network requirements
- Deployment environment (cloud/on-prem)

## Design Principles to Apply

1. **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **DRY**: Don't Repeat Yourself
3. **KISS**: Keep It Simple, Stupid
4. **YAGNI**: You Aren't Gonna Need It
5. **12-Factor App**: For cloud-native applications
6. **Security by Design**: Build security in from the start

## Architecture Patterns to Consider

- Microservices vs Monolith
- Event-Driven Architecture
- CQRS (Command Query Responsibility Segregation)
- API Gateway
- Service Mesh
- Serverless
- Layered Architecture
- Hexagonal Architecture (Ports & Adapters)

---

**Your goal**: Provide a technically sound, scalable, and maintainable architecture that development teams can implement with confidence.
"""


# Usage with context from previous phases:
tl_agent = TechnicalLeadAgent(
    gemini_client=gemini_client,
    methodology=AgileMethodology.SCRUM
)

context = {
    "dependencies": [
        {
            "phase": "business_foundation",
            "agent": "ProductManager",
            "confidence": 0.89,
            "content": "Business case: High-value opportunity, TAM of $500M..."
        },
        {
            "phase": "product_definition",
            "agent": "ProductOwner",
            "confidence": 0.92,
            "content": "User stories defined: As a customer, I want to earn points..."
        },
        {
            "phase": "user_experience",
            "agent": "UXUI_Designer",
            "confidence": 0.85,
            "content": "Mobile-first design, key flows: Registration, Point earning..."
        }
    ],
    "methodology_context": "Scrum - Focus on 2-week sprints and MVP delivery"
}

response = tl_agent.process(business_need, context=context)
```

### 11.4 Worker Agent Patterns

**Pattern 1: Domain Expert Pattern**

```python
# Each agent = domain expert with deep knowledge in specific area

class QASpecialistAgent(BaseAgent):
    """Quality Assurance specialist - testing strategy."""

    def get_system_prompt(self) -> str:
        return """
You are a QA specialist expert in:
- Test strategy (unit, integration, E2E, performance)
- Quality gates and acceptance criteria
- Test automation frameworks
- Quality metrics (coverage, defect density)
- Risk-based testing
...
"""
```

**Pattern 2: Perspective Diversity Pattern**

```python
# Different agents provide contrasting perspectives

ProductManager.perspective = "Business Value"
# → "This feature has high ROI, prioritize it"

TechnicalLead.perspective = "Technical Feasibility"
# → "This feature is complex, consider simpler alternatives"

UXUIAgent.perspective = "User Experience"
# → "This feature confuses users, redesign needed"

# Diversity → Better collective decision through synthesis
```

**Pattern 3: Context Accumulation Pattern**

```python
# Later agents benefit from earlier agents' work

Phase 1: ProductManager analyzes business case
Phase 2: ProductOwner creates user stories (informed by business case)
Phase 3: UXUIAgent designs UX (informed by user stories)
Phase 4: TechnicalLead architects system (informed by UX requirements)
Phase 5: ScrumMaster plans sprints (informed by architecture)
Phase 6: QASpecialist defines tests (informed by all above)

# Each phase builds on previous → coherent end-to-end solution
```

---

## 12. Building Consensus Mechanisms

### 12.1 Consensus Manager Implementation

```python
class ConsensusManager:
    """
    Centralized consensus management using Strategy pattern.

    Design:
    - Strategy pattern: Different consensus algorithms as strategies
    - Factory: Creates appropriate consensus engine
    - Polymorphism: All engines implement same interface
    """

    def __init__(self):
        self.strategies: Dict[ConsensusStrategy, ConsensusEngine] = {
            ConsensusStrategy.WEIGHTED_VOTING: WeightedVotingConsensus(),
            ConsensusStrategy.MAJORITY: MajorityConsensus(),
            ConsensusStrategy.UNANIMOUS: UnanimousConsensus(),
            ConsensusStrategy.CONFIDENCE_THRESHOLD: ConfidenceThresholdConsensus()
        }
        self.logger = logging.getLogger(__name__)

    def apply_consensus(
        self,
        responses: List[AgentResponse],
        strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_VOTING,
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Apply consensus strategy to agent responses.

        Args:
            responses: List of agent responses to evaluate
            strategy: Which consensus algorithm to use
            context: Optional context (methodology, weights, etc.)

        Returns:
            ConsensusResult with achieved/level/justification

        Raises:
            ValueError: If unknown strategy
        """
        self.logger.info(
            f"Applying {strategy.value} consensus to {len(responses)} responses"
        )

        if strategy not in self.strategies:
            raise ValueError(f"Unknown consensus strategy: {strategy}")

        # Get appropriate engine
        engine = self.strategies[strategy]

        # Apply consensus
        result = engine.achieve_consensus(responses, context)

        self.logger.info(
            f"Consensus {'achieved' if result.achieved else 'NOT achieved'}: "
            f"{result.consensus_level:.1%}"
        )

        return result

    def register_strategy(
        self,
        strategy: ConsensusStrategy,
        engine: ConsensusEngine
    ) -> None:
        """
        Register custom consensus strategy.

        Allows extending with new algorithms without modifying ConsensusManager.
        """
        self.strategies[strategy] = engine
        self.logger.info(f"Registered custom strategy: {strategy.value}")
```

### 12.2 Weighted Voting Implementation

```python
class WeightedVotingConsensus(ConsensusEngine):
    """
    Weighted voting: agents weighted by expertise.

    Formula:
        consensus_level = Σ(confidence_i × weight_i) / Σ(weight_i)

    Example:
        6 agents with confidences [0.9, 0.85, 0.8, 0.75, 0.9, 0.85]
        weights [1.2, 1.1, 1.0, 0.9, 1.3, 1.0]
        weighted_avg = (0.9*1.2 + 0.85*1.1 + ... + 0.85*1.0) / (1.2+1.1+...+1.0)
                     = 0.847
        threshold = 0.7
        consensus = TRUE (0.847 >= 0.7)
    """

    def __init__(
        self,
        agent_weights: Optional[Dict[str, float]] = None,
        threshold: float = 0.7
    ):
        super().__init__("WeightedVoting")
        self.agent_weights = agent_weights or {}
        self.threshold = threshold

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Weighted voting consensus algorithm."""
        if not responses:
            return ConsensusResult(
                achieved=False,
                strategy_used=ConsensusStrategy.WEIGHTED_VOTING,
                consensus_level=0.0,
                justification="No responses to evaluate"
            )

        # Extract weights from context or use defaults
        weights = self._get_weights(context)

        # Calculate weighted average
        total_weight = 0.0
        weighted_confidence = 0.0

        for response in responses:
            weight = weights.get(response.agent_name, 1.0)
            total_weight += weight
            weighted_confidence += response.confidence * weight

        consensus_level = (
            weighted_confidence / total_weight
            if total_weight > 0 else 0
        )

        # Determine if consensus achieved
        achieved = consensus_level >= self.threshold

        # Classify responses
        selected = [
            r for r in responses
            if r.confidence >= self.threshold
        ]
        conflicting = [
            r for r in responses
            if r.confidence < self.threshold
        ]

        # Build justification
        justification = self._build_justification(
            responses,
            weights,
            consensus_level,
            achieved,
            selected,
            conflicting
        )

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.WEIGHTED_VOTING,
            consensus_level=consensus_level,
            selected_responses=selected,
            conflicting_responses=conflicting,
            justification=justification,
            metadata={
                "total_weight": total_weight,
                "weighted_confidence": weighted_confidence,
                "threshold": self.threshold,
                "weights_used": weights
            }
        )

    def _get_weights(
        self,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract weights from context or use defaults."""
        if context and "weights" in context:
            return context["weights"]

        return self.agent_weights

    def _build_justification(
        self,
        responses: List[AgentResponse],
        weights: Dict[str, float],
        consensus_level: float,
        achieved: bool,
        selected: List[AgentResponse],
        conflicting: List[AgentResponse]
    ) -> str:
        """Build human-readable justification."""
        lines = [
            f"Weighted voting consensus {'achieved' if achieved else 'NOT achieved'}.",
            f"",
            f"Average weighted confidence: {consensus_level:.1%}",
            f"Threshold: {self.threshold:.1%}",
            f"",
            f"Agent Contributions:"
        ]

        for response in responses:
            weight = weights.get(response.agent_name, 1.0)
            contribution = response.confidence * weight
            lines.append(
                f"  - {response.agent_name}: "
                f"confidence={response.confidence:.2f}, "
                f"weight={weight:.2f}, "
                f"contribution={contribution:.3f}"
            )

        lines.extend([
            f"",
            f"Summary:",
            f"  {len(selected)} agents above threshold",
            f"  {len(conflicting)} agents below threshold"
        ])

        if conflicting:
            lines.append(f"")
            lines.append(f"Agents below threshold:")
            for r in conflicting:
                lines.append(f"  - {r.agent_name} ({r.confidence:.2f})")

        return "\n".join(lines)


# Usage example:
consensus_manager = ConsensusManager()

# Custom weights (optional)
weights = {
    "ProductManager": 1.2,
    "TechnicalLead": 1.3,
    "ProductOwner": 1.1,
    "UXUI_Designer": 1.0,
    "ScrumMaster": 0.9,
    "QA_Specialist": 1.0
}

consensus_result = consensus_manager.apply_consensus(
    responses=worker_responses,
    strategy=ConsensusStrategy.WEIGHTED_VOTING,
    context={"weights": weights}
)

if consensus_result.achieved:
    print(f"✓ Consensus achieved: {consensus_result.consensus_level:.1%}")
else:
    print(f"✗ Consensus NOT achieved: {consensus_result.consensus_level:.1%}")

print(f"\nJustification:\n{consensus_result.justification}")
```

### 12.3 Consensus Visualization

```python
def visualize_consensus(
    responses: List[AgentResponse],
    consensus_result: ConsensusResult
):
    """
    Create visual representation of consensus.

    Output:
    ┌─────────────────────┬────────────┬────────────┐
    │ Agent               │ Confidence │ Status     │
    ├─────────────────────┼────────────┼────────────┤
    │ ProductManager      │ 89.0%      │ ✓ Agreed   │
    │ ProductOwner        │ 92.0%      │ ✓ Agreed   │
    │ UXUI_Designer       │ 85.0%      │ ✓ Agreed   │
    │ TechnicalLead       │ 91.0%      │ ✓ Agreed   │
    │ ScrumMaster         │ 88.0%      │ ✓ Agreed   │
    │ QA_Specialist       │ 87.0%      │ ✓ Agreed   │
    ├─────────────────────┼────────────┼────────────┤
    │ CONSENSUS           │ 88.7%      │ ✓ ACHIEVED │
    └─────────────────────┴────────────┴────────────┘
    """
    from rich.console import Console
    from rich.table import Table

    console = Console()

    table = Table(title="Consensus Analysis")
    table.add_column("Agent", style="cyan")
    table.add_column("Confidence", style="magenta")
    table.add_column("Status", style="green")

    threshold = 0.7  # Get from consensus_result.metadata if available

    for response in responses:
        agreed = response.confidence >= threshold
        status = "✓ Agreed" if agreed else "✗ Disagreed"
        style = "green" if agreed else "red"

        table.add_row(
            response.agent_name,
            f"{response.confidence:.1%}",
            f"[{style}]{status}[/{style}]"
        )

    # Add consensus row
    table.add_section()
    consensus_status = "✓ ACHIEVED" if consensus_result.achieved else "✗ NOT ACHIEVED"
    consensus_style = "green bold" if consensus_result.achieved else "red bold"

    table.add_row(
        "[bold]CONSENSUS[/bold]",
        f"[bold]{consensus_result.consensus_level:.1%}[/bold]",
        f"[{consensus_style}]{consensus_status}[/{consensus_style}]"
    )

    console.print(table)
```

---

## 13. Hierarchical Execution Flow

### 13.1 Product Management Best Practices Flow

**Rationale**: Software requirements should follow natural dependency order

```
Business Analysis (PM)
  ↓ (Business case informs product features)
Product Definition (PO)
  ↓ (Features inform UX design)
User Experience (UX/UI)
  ↓ (UX requirements inform architecture)
Technical Architecture (TL)
  ↓ (Architecture informs process planning)
Process Planning (SM)
  ↓ (Process informs testing strategy)
Quality Assurance (QA)
```

### 13.2 Hierarchical Flow Implementation

```python
class ExecutionPhase(Enum):
    """Phases following Product Management best practices."""
    BUSINESS_FOUNDATION = "business_foundation"
    PRODUCT_DEFINITION = "product_definition"
    USER_EXPERIENCE = "user_experience"
    TECHNICAL_FOUNDATION = "technical_foundation"
    PROCESS_OPTIMIZATION = "process_optimization"
    QUALITY_ASSURANCE = "quality_assurance"


@dataclass
class PhaseDependency:
    """Represents execution phase with dependencies."""
    phase: ExecutionPhase
    depends_on: List[ExecutionPhase]
    agent_class: type
    description: str
    methodology_context: str


class HierarchicalExecutionFlow:
    """
    Manages sequential execution with dependencies.

    Key Innovation: Product Management-informed execution order
    vs. arbitrary parallel execution
    """

    def __init__(self, methodology: AgileMethodology):
        self.methodology = methodology
        self.comm_bus = CommunicationBus()
        self.execution_order = self._define_execution_order()
        self.phase_contexts: Dict[ExecutionPhase, AgentResponse] = {}

    def _define_execution_order(self) -> List[PhaseDependency]:
        """Define methodology-specific execution order."""

        if self.methodology == AgileMethodology.SCRUM:
            return [
                PhaseDependency(
                    phase=ExecutionPhase.BUSINESS_FOUNDATION,
                    depends_on=[],  # No dependencies
                    agent_class=ProductManagerAgent,
                    description="Business viability and market analysis",
                    methodology_context="Product Owner perspective with business focus"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PRODUCT_DEFINITION,
                    depends_on=[ExecutionPhase.BUSINESS_FOUNDATION],
                    agent_class=ProductOwnerAgent,
                    description="User stories and product backlog",
                    methodology_context="Scrum Product Owner creating user stories"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.USER_EXPERIENCE,
                    depends_on=[ExecutionPhase.PRODUCT_DEFINITION],
                    agent_class=UXUIAgent,
                    description="User experience design based on stories",
                    methodology_context="UX/UI Designer working with Product Owner"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.TECHNICAL_FOUNDATION,
                    depends_on=[ExecutionPhase.USER_EXPERIENCE],
                    agent_class=TechnicalLeadAgent,
                    description="Technical architecture for UX implementation",
                    methodology_context="Technical Lead designing architecture"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.PROCESS_OPTIMIZATION,
                    depends_on=[ExecutionPhase.TECHNICAL_FOUNDATION],
                    agent_class=ScrumMasterAgent,
                    description="Scrum process and sprint planning",
                    methodology_context="Scrum Master planning sprints"
                ),
                PhaseDependency(
                    phase=ExecutionPhase.QUALITY_ASSURANCE,
                    depends_on=[ExecutionPhase.PROCESS_OPTIMIZATION],
                    agent_class=QASpecialistAgent,
                    description="Quality strategy and testing",
                    methodology_context="QA Specialist defining test strategy"
                )
            ]

        # Similar for SAFe and Kanban (see full implementation)
        # ...

    def execute_hierarchical_flow(
        self,
        business_need: str,
        agents: Dict[str, BaseAgent],
        verbose: bool = True
    ) -> List[AgentResponse]:
        """
        Execute agents in dependency order.

        Key Algorithm:
        1. For each phase in order:
           a. Build context from previous phases
           b. Execute agent with enriched context
           c. Store result for next phase
        2. Return all responses in execution order
        """
        responses = []
        execution_context = {
            "business_need": business_need,
            "methodology": self.methodology.value,
            "previous_responses": []
        }

        for phase_dep in self.execution_order:
            if verbose:
                self._print_phase_header(phase_dep)

            # Get agent for this phase
            agent = self._get_agent(phase_dep, agents)

            # Build phase-specific context
            phase_context = self._build_phase_context(
                phase_dep,
                execution_context
            )

            # Execute agent
            response = self._execute_phase(
                agent,
                business_need,
                phase_context,
                phase_dep,
                verbose
            )

            # Store result
            responses.append(response)
            execution_context["previous_responses"].append(response)
            self.phase_contexts[phase_dep.phase] = response

        return responses

    def _build_phase_context(
        self,
        phase_dep: PhaseDependency,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build enriched context for phase.

        Context includes:
        - Current phase info
        - Methodology context
        - Dependencies (outputs from previous phases)
        """
        context = {
            "phase": phase_dep.phase.value,
            "methodology": self.methodology.value,
            "methodology_context": phase_dep.methodology_context,
            "dependencies": []
        }

        # Add dependency outputs
        for dep_phase in phase_dep.depends_on:
            if dep_phase in self.phase_contexts:
                dep_response = self.phase_contexts[dep_phase]
                context["dependencies"].append({
                    "phase": dep_phase.value,
                    "agent": dep_response.agent_name,
                    "confidence": dep_response.confidence,
                    # Truncate content to avoid token limits
                    "content": (
                        dep_response.content[:500] + "..."
                        if len(dep_response.content) > 500
                        else dep_response.content
                    )
                })

        return context

    def _execute_phase(
        self,
        agent: BaseAgent,
        business_need: str,
        context: Dict[str, Any],
        phase_dep: PhaseDependency,
        verbose: bool
    ) -> AgentResponse:
        """Execute single phase with error handling."""
        try:
            # Log phase start
            self.comm_bus.send_message(
                sender="System",
                recipient=agent.name,
                content=f"Phase: {phase_dep.phase.value}",
                message_type=MessageType.REQUEST
            )

            # Execute agent
            response = agent.process(business_need, context=context)

            # Log completion
            self.comm_bus.send_message(
                sender=agent.name,
                recipient="System",
                content=f"Phase complete (confidence: {response.confidence:.2f})",
                message_type=MessageType.RESPONSE
            )

            if verbose:
                print(f"   ✅ Complete (Confidence: {response.confidence:.2f})")

            return response

        except Exception as e:
            logger.error(f"Phase {phase_dep.phase.value} failed: {e}")
            if verbose:
                print(f"   ❌ Error: {str(e)}")
            raise
```

---

**[Continue to Part IV: Advanced Topics...]**

This completes Part III. Should I continue with Part IV (Advanced Topics) and Part V (Exercises and Labs)?
