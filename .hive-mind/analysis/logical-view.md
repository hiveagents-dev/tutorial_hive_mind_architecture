# Logical View - HiveMind Architecture Analysis

## Overview
The Logical View describes the functionality of the HiveMind system in terms of key abstractions, components, and their relationships. This view represents the object-oriented decomposition of the system.

---

## Key Abstractions

### 1. Agent Hierarchy
**Abstract Base: BaseAgent**
- Location: `/backend/src/agents/base_agent.py`
- Purpose: Defines common interface for all agents in the system
- Key Methods:
  - `get_system_prompt()`: Abstract method returning agent-specific prompts
  - `get_adapted_system_prompt()`: Returns methodology-aware prompts
  - `process(input_data, context)`: Abstract method for processing input
  - `_call_gemini(prompt, system_instruction)`: Wrapper for LLM calls
  - `_create_response(content, confidence, metadata)`: Creates structured responses

**Concrete Implementations:**
1. **Worker Agents** (6 specialists) - Level 1
   - `ProductManagerAgent`: Business viability, KPIs, stakeholder analysis
   - `ProductOwnerAgent`: User stories, backlog, INVEST criteria
   - `UXUIAgent`: Journey maps, wireframes, design systems
   - `TechnicalLeadAgent`: C4 architecture, tech stack, NFRs
   - `ScrumMasterAgent`: Ceremonies, RAID log, Definition of Ready
   - `QASpecialistAgent`: Test strategy, coverage, automation

2. **CoordinatorAgent** - Level 2
   - Synthesizes outputs from 6 workers
   - Resolves conflicts between agent perspectives
   - Applies consensus mechanisms
   - Generates integrated view

3. **SupervisorAgent** - Level 3
   - Evaluates coordinator synthesis
   - Makes final authoritative decisions
   - Generates complete technical requirements document
   - Provides executive summary and recommendations

### 2. Communication Infrastructure
**CommunicationBus**
- Location: `/backend/src/hivemind/communication.py`
- Purpose: Manages agent-to-agent communication using A2A protocol
- Key Components:
  - `A2AMessage`: Pydantic model for standardized messages
  - `MessageType` Enum: REQUEST, RESPONSE, NOTIFICATION, ERROR
  - `MessagePriority` Enum: HIGH, MEDIUM, LOW
- Key Methods:
  - `send_message()`: Routes messages between agents
  - `get_conversation()`: Retrieves message history between agents
  - `get_message_thread()`: Gets parent-child message relationships
  - `get_statistics()`: Communication analytics
  - `export_log()`: Full communication trace

### 3. Consensus Mechanisms
**ConsensusManager**
- Location: `/backend/src/hivemind/consensus.py`
- Purpose: Applies different consensus strategies to agent responses
- Strategy Pattern Implementation:
  - `ConsensusEngine`: Abstract base for consensus strategies
  - `WeightedVotingConsensus`: Expertise-weighted voting
  - `MajorityConsensus`: Simple majority rule
  - `UnanimousConsensus`: All agents must agree
  - `ConfidenceThresholdConsensus`: Average confidence threshold

**ConsensusResult Model:**
- `achieved`: Boolean consensus flag
- `strategy_used`: Strategy applied
- `consensus_level`: Numerical level (0.0-1.0)
- `selected_responses`: Agreeing agents
- `conflicting_responses`: Dissenting agents
- `justification`: Human-readable explanation

### 4. Methodology Support
**MethodologyFactory**
- Location: `/backend/src/hivemind/methodology.py`
- Purpose: Provides multi-methodology support (Scrum, SAFe, Kanban)
- Key Components:
  - `AgileMethodology` Enum: SCRUM, SAFE, KANBAN
  - `MethodologyContext`: Dataclass with methodology-specific data
  - `MethodologyAdapter`: Adapts prompts and outputs per methodology
- Methodology-Specific Data:
  - Roles mapping (e.g., ProductManager -> Product Owner in Scrum)
  - Ceremonies (Sprint Planning, Daily Scrum, etc.)
  - Artifacts (Product Backlog, Sprint Backlog, etc.)
  - Metrics (Velocity, Burndown, etc.)

### 5. Hierarchical Execution Flow
**HierarchicalExecutionFlow**
- Location: `/backend/src/hivemind/hierarchical_flow.py`
- Purpose: Manages sequential execution with dependencies
- Key Components:
  - `ExecutionPhase` Enum: 6 phases (Business Foundation -> Quality Assurance)
  - `PhaseDependency`: Defines dependencies between phases
- Execution Order (Product Management Best Practices):
  1. Business Foundation (ProductManager) - No dependencies
  2. Product Definition (ProductOwner) - Depends on #1
  3. User Experience (UXUI) - Depends on #2
  4. Technical Foundation (TechnicalLead) - Depends on #3
  5. Process Optimization (ScrumMaster) - Depends on #4
  6. Quality Assurance (QA) - Depends on #5

### 6. Orchestration Layer
**HiveMindArchitecture**
- Location: `/backend/src/hivemind/architecture.py`
- Purpose: Main orchestrator coordinating all system components
- Key Responsibilities:
  - Initializes all agents with methodology context
  - Coordinates 3-level hierarchical execution
  - Manages communication bus
  - Applies consensus mechanisms
  - Produces final result with metadata
- Execution Flow:
  - Phase 1: Execute workers using HierarchicalExecutionFlow
  - Phase 2: Coordinator synthesizes worker outputs + apply consensus
  - Phase 3: Supervisor generates final requirements

**HiveMindResult Model:**
- `worker_responses`: List of 6 worker agent responses
- `coordinator_response`: Synthesis from coordinator
- `supervisor_response`: Final requirements document
- `consensus_result`: Consensus analysis
- `communication_log`: Complete A2A message history
- `execution_time`: Total execution time
- `metadata`: Methodology, strategy, timestamps

---

## Component Relationships

### Dependency Graph
```
HiveMindArchitecture
    ├─> HierarchicalExecutionFlow
    │   └─> Worker Agents (6)
    │       └─> BaseAgent
    │           └─> GeminiClient
    │           └─> MethodologyAdapter
    │
    ├─> CoordinatorAgent
    │   └─> BaseAgent
    │       └─> GeminiClient
    │       └─> MethodologyAdapter
    │
    ├─> SupervisorAgent
    │   └─> BaseAgent
    │       └─> GeminiClient
    │       └─> MethodologyAdapter
    │
    ├─> CommunicationBus
    │   └─> A2AMessage (Pydantic)
    │
    ├─> ConsensusManager
    │   └─> ConsensusEngine Strategies
    │
    └─> MethodologyFactory
        └─> MethodologyContext
```

### Layer Architecture
```
┌─────────────────────────────────────────────────────────┐
│                 INTERFACE LAYER                         │
│  CLI (cli.py) | REST API (FastAPI) | Frontend (React)  │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                        │
│         HiveMindArchitecture (architecture.py)          │
│    • Coordinates execution                              │
│    • Manages agent lifecycle                            │
│    • Applies consensus                                  │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────────┐        ┌────────▼────────────┐
│   AGENT LAYER       │        │  SERVICE LAYER      │
│  • BaseAgent        │        │  • CommunicationBus │
│  • Workers (6)      │        │  • ConsensusManager │
│  • Coordinator      │        │  • MethodologyFctry │
│  • Supervisor       │        │  • HierarchicalFlow │
└─────────────────────┘        └─────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│            INFRASTRUCTURE LAYER                         │
│  GeminiClient | PostgreSQL | PersistenceService        │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Input → Processing → Output

**Input Layer:**
- Business Need (string): User's description of requirement
- Methodology (enum): Scrum, SAFe, or Kanban
- Consensus Strategy (enum): Weighted voting, majority, etc.

**Processing Layer:**
1. **Worker Processing** (Sequential by dependency):
   - Each worker receives: business_need + methodology_context + dependencies
   - Each worker produces: AgentResponse with content + confidence + metadata
   - Context preserved and forwarded between phases

2. **Coordination Processing**:
   - Input: business_need + all 6 worker responses
   - Processing: Synthesis + conflict resolution
   - Output: Integrated synthesis + consensus result

3. **Supervision Processing**:
   - Input: business_need + coordinator synthesis + consensus
   - Processing: Final validation + decision making
   - Output: Complete technical requirements document

**Output Layer:**
- HiveMindResult with:
  - All agent responses (workers + coordinator + supervisor)
  - Consensus analysis
  - Communication log
  - Execution metadata

---

## Key Design Patterns

### 1. Template Method Pattern
- **BaseAgent** defines template for agent processing
- Subclasses implement specific behavior in `get_system_prompt()` and `process()`

### 2. Strategy Pattern
- **ConsensusManager** uses different consensus strategies
- Strategies are interchangeable at runtime

### 3. Factory Pattern
- **MethodologyFactory** creates methodology-specific contexts
- Encapsulates creation logic for different methodologies

### 4. Adapter Pattern
- **MethodologyAdapter** adapts agent prompts to specific methodologies
- Translates generic prompts to methodology-aware prompts

### 5. Observer/Mediator Pattern
- **CommunicationBus** mediates agent communication
- Agents don't communicate directly, all messages go through bus

### 6. Builder Pattern
- **HierarchicalExecutionFlow** builds execution context incrementally
- Each phase builds upon previous phases

---

## Component Responsibilities

### Agent Components
| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| ProductManagerAgent | Business viability analysis | Business need | Business analysis + confidence |
| ProductOwnerAgent | User stories + backlog | Business need + PM analysis | User stories + backlog |
| UXUIAgent | UX/UI design | Business need + PO output | UX design + wireframes |
| TechnicalLeadAgent | Architecture + tech stack | Business need + UX output | Architecture + NFRs |
| ScrumMasterAgent | Process + risk mgmt | Business need + Tech output | Process plan + RAID |
| QASpecialistAgent | Quality strategy | Business need + SM output | Test strategy + quality gates |
| CoordinatorAgent | Synthesis + conflict resolution | All worker outputs | Integrated synthesis |
| SupervisorAgent | Final decision + documentation | Coordinator synthesis | Requirements document |

### Service Components
| Component | Responsibility | Key Methods |
|-----------|---------------|-------------|
| CommunicationBus | Message routing + history | send_message, get_conversation, export_log |
| ConsensusManager | Consensus application | apply_consensus, register_strategy |
| MethodologyFactory | Methodology context creation | get_context, validate_methodology |
| HierarchicalExecutionFlow | Sequential execution mgmt | execute_hierarchical_flow, _build_phase_context |

---

## Quality Attributes

### Extensibility
- New agents can be added by extending BaseAgent
- New consensus strategies via ConsensusEngine interface
- New methodologies via MethodologyFactory

### Maintainability
- Clear separation of concerns (layers)
- Single Responsibility Principle in components
- DRY principle (shared base classes)

### Testability
- Dependency injection (GeminiClient passed to agents)
- Mock-friendly interfaces
- Pydantic models for validation

### Traceability
- Complete A2A communication log
- Parent-child message relationships
- Execution metadata and timestamps

---

## Interface Contracts

### AgentResponse Structure
```python
{
    "agent_name": str,
    "content": str,
    "confidence": float (0.0-1.0),
    "metadata": Dict[str, Any],
    "timestamp": str (ISO format),
    "methodology": str,
    "methodology_specific_output": Dict[str, Any]
}
```

### A2AMessage Structure
```python
{
    "message_id": str,
    "sender": str,
    "recipient": str,
    "message_type": MessageType,
    "priority": MessagePriority,
    "content": str,
    "metadata": Dict[str, Any],
    "timestamp": str (ISO format),
    "parent_message_id": Optional[str]
}
```

### ConsensusResult Structure
```python
{
    "achieved": bool,
    "strategy_used": ConsensusStrategy,
    "consensus_level": float (0.0-1.0),
    "selected_responses": List[AgentResponse],
    "conflicting_responses": List[AgentResponse],
    "justification": str,
    "metadata": Dict[str, Any]
}
```

---

## Analysis Summary

**Strengths:**
1. Clear hierarchical structure with well-defined levels
2. Strong separation of concerns across layers
3. Extensible design with multiple extension points
4. Comprehensive traceability through A2A protocol
5. Flexible methodology support
6. Multiple consensus strategies

**Key Abstractions:**
- BaseAgent: Common agent interface
- HiveMindArchitecture: System orchestrator
- CommunicationBus: Communication mediator
- ConsensusManager: Consensus coordinator
- MethodologyFactory: Methodology context provider

**Architecture Style:**
- Layered architecture with clear dependencies
- Object-oriented with extensive use of inheritance and composition
- Component-based with well-defined interfaces
- Event-driven communication through message bus
