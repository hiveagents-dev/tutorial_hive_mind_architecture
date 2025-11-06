# Scenarios View (+1) - HiveMind Architecture Analysis

## Overview
The Scenarios View describes key use cases that tie together all other architectural views (Logical, Process, Development, Physical). These scenarios validate the architecture and demonstrate how the system fulfills its requirements.

---

## Scenario 1: Complete Business Analysis via REST API

### Description
A Product Manager uses the REST API to analyze a new business need and receive comprehensive technical requirements for a mobile e-commerce platform.

### Actors
- **Primary**: Product Manager (via API client)
- **System**: HiveMind Architecture
- **External**: Google Gemini API

### Preconditions
- Docker containers running (frontend, API, database)
- Valid Gemini API key configured
- Database initialized

### Main Flow

#### 1. API Request (Physical View)
```
Client Application (Postman/Browser)
    │
    ├──> POST http://localhost:8002/api/v1/analyze
    │    Headers: Content-Type: application/json
    │    Body: {
    │      "business_need": "Mobile e-commerce for sustainable fashion",
    │      "methodology": "scrum",
    │      "consensus_strategy": "weighted_voting",
    │      "verbose": true
    │    }
    │
    └──> Network: Host → hivemind-api container (port 8002→8000)
```

#### 2. API Layer Processing (Logical View)
```
FastAPI Application (api/main.py)
    │
    ├──> Middleware: CORS, logging, error handling
    │
    ├──> Endpoint: POST /api/v1/analyze (api/endpoints.py)
    │      • Validate request via Pydantic model
    │      • Extract parameters
    │
    └──> Call: HiveMindArchitecture.execute()
```

#### 3. Orchestration (Process View)
```
HiveMindArchitecture.execute()
    │
    ├──> Initialize (Development View)
    │    • Load MethodologyContext (scrum)
    │    • Initialize CommunicationBus
    │    • Initialize ConsensusManager
    │    • Create 6 worker agents + coordinator + supervisor
    │
    ├──> PHASE 1: Sequential Worker Execution
    │    │
    │    ├──> Step 1: ProductManager
    │    │    Input: Business need + scrum methodology
    │    │    Process (Logical View):
    │    │      • CommunicationBus.send_message(REQUEST)
    │    │      • BaseAgent.process()
    │    │        → MethodologyAdapter.adapt_prompt()
    │    │        → GeminiClient.generate_content()
    │    │          → HTTP POST to Gemini API (Physical View)
    │    │      • Extract confidence score
    │    │      • CommunicationBus.send_message(RESPONSE)
    │    │    Output: Business analysis (confidence: 0.89)
    │    │
    │    ├──> Step 2: ProductOwner
    │    │    Input: Business need + PM output + scrum context
    │    │    Dependencies: ProductManager output (Process View)
    │    │    Process: Same as Step 1
    │    │    Output: User stories (confidence: 0.92)
    │    │
    │    ├──> Step 3: UXUIAgent
    │    │    Dependencies: ProductOwner output
    │    │    Output: UX design (confidence: 0.85)
    │    │
    │    ├──> Step 4: TechnicalLead
    │    │    Dependencies: UXUIAgent output
    │    │    Output: Architecture (confidence: 0.91)
    │    │
    │    ├──> Step 5: ScrumMaster
    │    │    Dependencies: TechnicalLead output
    │    │    Output: Process plan (confidence: 0.88)
    │    │
    │    └──> Step 6: QASpecialist
    │         Dependencies: ScrumMaster output
    │         Output: Quality strategy (confidence: 0.87)
    │
    ├──> PHASE 2: Coordinator Synthesis
    │    Process:
    │      • Receive all 6 worker responses
    │      • CoordinatorAgent.process()
    │        → Synthesize perspectives
    │        → Resolve conflicts
    │      • ConsensusManager.apply_consensus()
    │        → Strategy: WeightedVoting
    │        → Calculate: Σ(conf × weight) / Σ(weight)
    │        → Result: consensus_level = 0.887
    │    Output: Integrated synthesis + consensus
    │
    ├──> PHASE 3: Supervisor Finalization
    │    Process:
    │      • SupervisorAgent.process()
    │        → Validate synthesis
    │        → Make final decisions
    │        → Generate requirements document
    │    Output: Complete technical requirements (confidence: 0.95)
    │
    └──> Finalize
         • Build HiveMindResult
         • Export communication log
         • Calculate execution time
         • Return result
```

#### 4. Persistence (Development View)
```
PersistenceService.save_analysis()
    │
    ├──> Create Analysis record (db/models.py)
    │    • business_need
    │    • methodology: "scrum"
    │    • consensus_strategy: "weighted_voting"
    │    • execution_time: 48.5s
    │    • final_confidence: 0.95
    │    • metadata
    │
    ├──> Create AgentResponse records (8 total)
    │    • 6 worker responses
    │    • 1 coordinator response
    │    • 1 supervisor response
    │
    └──> Commit to PostgreSQL (Physical View)
         Database: hivemind-postgres container
```

#### 5. API Response
```
Response:
{
  "success": true,
  "analysis_id": 42,
  "worker_responses": [...],
  "coordinator_response": {...},
  "supervisor_response": {
    "agent_name": "Supervisor",
    "content": "{ /* Complete requirements document */ }",
    "confidence": 0.95
  },
  "consensus_result": {
    "achieved": true,
    "consensus_level": 0.887,
    "strategy_used": "weighted_voting"
  },
  "execution_time": 48.5,
  "metadata": {...}
}
```

### Postconditions
- Technical requirements document generated
- Analysis stored in database with ID 42
- Communication log preserved
- All 8 agent responses persisted

### View Integration

**Logical View:**
- Components: HiveMindArchitecture, 8 agents, CommunicationBus, ConsensusManager
- Interfaces: BaseAgent, ConsensusEngine, PersistenceService

**Process View:**
- Sequential execution with dependencies
- A2A message flow (16 messages)
- State transitions: IDLE → PROCESSING → COMPLETED

**Development View:**
- Modules: api/, hivemind/, agents/, db/
- Dependencies: FastAPI → HiveMindArchitecture → BaseAgent → GeminiClient

**Physical View:**
- Containers: hivemind-api, hivemind-postgres
- External API: Google Gemini (8 calls)
- Storage: PostgreSQL volume

---

## Scenario 2: Real-Time Analysis via WebSocket

### Description
A user interacts with the frontend web UI to analyze a business need and receives real-time progress updates during the 50-second execution.

### Actors
- **Primary**: End User (via web browser)
- **System**: Frontend (React), Backend (FastAPI), HiveMind
- **External**: Google Gemini API

### Main Flow

#### 1. User Initiates Analysis (Physical View)
```
Browser (http://localhost:3002)
    │
    ├──> User navigates to /analyze page
    │
    ├──> User fills form:
    │    • Business need: "Patient appointment booking system"
    │    • Methodology: SAFe
    │    • Consensus: Majority
    │
    └──> User clicks "Analyze"
```

#### 2. WebSocket Connection (Process View)
```
React Component (pages/Analyze.jsx)
    │
    ├──> API Client (api/client.js)
    │    • Establish WebSocket connection
    │    • URL: ws://localhost:8002/api/v1/ws/analyze
    │
    └──> WebSocket established
         Connection: hivemind-frontend → hivemind-api
```

#### 3. Analysis Execution with Streaming (Logical + Process View)
```
Backend WebSocket Handler (api/endpoints.py)
    │
    ├──> Receive start message
    │    {
    │      "action": "start",
    │      "business_need": "...",
    │      "methodology": "safe",
    │      "consensus_strategy": "majority"
    │    }
    │
    ├──> Execute HiveMind in background task (async)
    │    │
    │    └──> For each phase, emit progress events:
    │
    ├──> Event 1: ProductManager processing
    │    {
    │      "type": "progress",
    │      "phase": "workers",
    │      "agent": "ProductManager",
    │      "status": "processing",
    │      "timestamp": "..."
    │    }
    │
    ├──> Event 2: ProductManager complete
    │    {
    │      "type": "progress",
    │      "phase": "workers",
    │      "agent": "ProductManager",
    │      "status": "complete",
    │      "confidence": 0.89
    │    }
    │
    ├──> Events 3-12: Other 5 workers (processing + complete)
    │
    ├──> Event 13: Coordinator processing
    │    {
    │      "type": "progress",
    │      "phase": "coordinator",
    │      "status": "processing"
    │    }
    │
    ├──> Event 14: Coordinator complete
    │    {
    │      "type": "progress",
    │      "phase": "coordinator",
    │      "status": "complete",
    │      "consensus_level": 0.75
    │    }
    │
    ├──> Events 15-16: Supervisor (processing + complete)
    │
    └──> Final Event: Complete
         {
           "type": "complete",
           "result": { /* Full HiveMindResult */ },
           "analysis_id": 43
         }
```

#### 4. Frontend Updates (Development View)
```
React Component receives WebSocket messages
    │
    ├──> Update AppContext state (context/AppContext.jsx)
    │    • currentPhase: "workers" | "coordinator" | "supervisor"
    │    • agentStatuses: Map<agent, status>
    │    • progress: 0-100%
    │
    ├──> Components re-render (Logical View)
    │    • SpecializedAgentsTabs: Show agent progress
    │    • ResultSummary: Update metrics
    │    • AgentContentView: Display outputs
    │
    └──> User sees real-time updates
         Timeline:
         0s:  "ProductManager processing..."
         5s:  "ProductManager complete ✓"
         5s:  "ProductOwner processing..."
         11s: "ProductOwner complete ✓"
         ...
         41s: "Coordinator synthesizing..."
         48s: "Supervisor finalizing..."
         50s: "Analysis complete! 🎉"
```

#### 5. Display Results
```
Frontend displays complete results
    │
    ├──> Executive Dashboard (components/DashboardExecutive.jsx)
    │    • Confidence scores
    │    • Consensus level
    │    • Execution time
    │
    ├──> Agent Outputs (components/SpecializedAgentsTabs.jsx)
    │    • Tabs for each agent
    │    • Detailed analysis per agent
    │
    └──> Export Options
         • Download JSON
         • Copy to clipboard
         • Share link
```

### View Integration

**Logical View:**
- Frontend components: Dashboard, Analyze, SpecializedAgentsTabs
- Backend: WebSocket endpoint, async execution

**Process View:**
- Asynchronous WebSocket communication
- Event-driven UI updates
- Concurrent execution (backend) + reactive UI (frontend)

**Development View:**
- Frontend: React + Vite + Axios
- Backend: FastAPI + WebSocket support
- State management: React Context API

**Physical View:**
- Containers: hivemind-frontend, hivemind-api
- Network: WebSocket over TCP
- Real-time data flow

---

## Scenario 3: Multi-Methodology Comparison

### Description
A system architect compares how the same business need is analyzed under different methodologies (Scrum, SAFe, Kanban) to choose the best fit.

### Main Flow

#### 1. Execute Analysis with Scrum
```
CLI Command:
$ python backend/cli.py \
    --business-need "Cloud migration project" \
    --methodology scrum \
    --output scrum_analysis.json
```

**Methodology Adaptation (Logical View):**
- MethodologyFactory.get_context(SCRUM)
- MethodologyAdapter adapts prompts:
  - Roles: Product Owner, Scrum Master
  - Artifacts: Product Backlog, Sprint Backlog
  - Ceremonies: Sprint Planning, Daily Scrum
  - Metrics: Velocity, Burndown

**Output Structure:**
```json
{
  "supervisor_response": {
    "content": {
      "product_backlog": [...],
      "sprint_planning": {...},
      "definition_of_done": {...},
      "sprint_structure": {
        "duration": "2 weeks",
        "ceremonies": [...]
      }
    }
  }
}
```

#### 2. Execute Analysis with SAFe
```
CLI Command:
$ python backend/cli.py \
    --business-need "Cloud migration project" \
    --methodology safe \
    --output safe_analysis.json
```

**Methodology Adaptation:**
- MethodologyFactory.get_context(SAFE)
- MethodologyAdapter adapts prompts:
  - Roles: Product Manager (Portfolio), PO (Program)
  - Artifacts: Portfolio Backlog, Program Backlog
  - Ceremonies: PI Planning, System Demo
  - Metrics: Program Predictability, Feature Delivery Rate

**Output Structure:**
```json
{
  "supervisor_response": {
    "content": {
      "features": [...],
      "epic_breakdown": {...},
      "program_increment": {
        "duration": "10 weeks",
        "iterations": 5
      },
      "architectural_runway": {...}
    }
  }
}
```

#### 3. Execute Analysis with Kanban
```
CLI Command:
$ python backend/cli.py \
    --business-need "Cloud migration project" \
    --methodology kanban \
    --output kanban_analysis.json
```

**Methodology Adaptation:**
- MethodologyFactory.get_context(KANBAN)
- MethodologyAdapter adapts prompts:
  - Roles: Service Request Manager, Flow Manager
  - Artifacts: Kanban Board, Work Item Types
  - Ceremonies: Replenishment Meeting, Flow Review
  - Metrics: Lead Time, Cycle Time, Throughput

**Output Structure:**
```json
{
  "supervisor_response": {
    "content": {
      "work_items": [...],
      "wip_limits": {
        "todo": 10,
        "in_progress": 5,
        "review": 3
      },
      "flow_metrics": {...},
      "kanban_board": {...}
    }
  }
}
```

#### 4. Comparison Analysis
```python
# Load results
scrum_result = json.load(open('scrum_analysis.json'))
safe_result = json.load(open('safe_analysis.json'))
kanban_result = json.load(open('kanban_analysis.json'))

# Compare
comparison = {
    "scrum": {
        "confidence": scrum_result['supervisor_response']['confidence'],
        "consensus": scrum_result['consensus_result']['consensus_level'],
        "structure": "Sprint-based, 2-week iterations",
        "best_for": "Small-medium teams, iterative delivery"
    },
    "safe": {
        "confidence": safe_result['supervisor_response']['confidence'],
        "consensus": safe_result['consensus_result']['consensus_level'],
        "structure": "Program Increment, 10-week cycles",
        "best_for": "Large organizations, portfolio management"
    },
    "kanban": {
        "confidence": kanban_result['supervisor_response']['confidence'],
        "consensus": kanban_result['consensus_result']['consensus_level'],
        "structure": "Continuous flow, WIP limits",
        "best_for": "Continuous delivery, operations teams"
    }
}

# Decision
print(f"Best methodology: {max(comparison, key=lambda k: comparison[k]['confidence'])}")
```

### View Integration

**Logical View:**
- MethodologyFactory: Creates methodology-specific contexts
- MethodologyAdapter: Adapts agent prompts and outputs
- Different agent behaviors per methodology

**Process View:**
- Same execution flow for all methodologies
- Different prompts and contexts
- Methodology-aware agent responses

**Development View:**
- Methodology support in hivemind/methodology.py
- Extensible design for new methodologies
- Configuration-driven behavior

**Physical View:**
- Same infrastructure for all methodologies
- Environment variable: DEFAULT_METHODOLOGY
- No infrastructure changes needed

---

## Scenario 4: Error Handling & Recovery

### Description
An analysis fails due to Gemini API rate limiting, and the system handles the error gracefully with retry logic.

### Main Flow

#### 1. Initial Execution
```
HiveMindArchitecture.execute()
    │
    └──> ProductManager.process()
         │
         └──> GeminiClient.generate_content()
              │
              └──> HTTP POST to Gemini API
                   Response: 429 Too Many Requests
```

#### 2. Retry Logic (Process View)
```
GeminiClient.generate_content()
    │
    ├──> Catch exception: google.api_core.exceptions.ResourceExhausted
    │
    ├──> Retry attempt 1
    │    • Wait: 1 second (exponential backoff)
    │    • Retry HTTP POST
    │    • Response: 429 Too Many Requests
    │
    ├──> Retry attempt 2
    │    • Wait: 2 seconds
    │    • Retry HTTP POST
    │    • Response: 429 Too Many Requests
    │
    └──> Retry attempt 3
         • Wait: 4 seconds
         • Retry HTTP POST
         • Response: 200 OK (success!)
```

#### 3. Continue Execution
```
ProductManager.process() continues
    │
    ├──> Receive Gemini response
    │
    ├──> Extract confidence
    │
    └──> Return AgentResponse (success)

Execution continues normally with other agents...
```

#### 4. Persistent Failure Scenario
```
If all 3 retries fail:
    │
    ├──> GeminiClient raises exception
    │
    ├──> ProductManager.process() catches exception
    │
    ├──> Log error: "Failed to call Gemini API after 3 retries"
    │
    ├──> CommunicationBus.send_message(ERROR)
    │
    ├──> HiveMindArchitecture.execute() catches exception
    │
    ├──> Build partial HiveMindResult
    │    • worker_responses: [] (empty)
    │    • error_metadata: {
    │        "phase": "workers",
    │        "agent": "ProductManager",
    │        "error": "API rate limit exceeded"
    │      }
    │
    └──> Return result with success=false

API Response:
{
  "success": false,
  "error": "Analysis failed during worker phase",
  "details": {
    "agent": "ProductManager",
    "reason": "API rate limit exceeded after retries"
  },
  "partial_result": {...}
}
```

### View Integration

**Logical View:**
- GeminiClient: Encapsulates retry logic
- Error propagation through agent hierarchy
- Graceful degradation

**Process View:**
- Retry state machine: PROCESSING → RETRY → ERROR/SUCCESS
- Exponential backoff timing
- Error recovery flow

**Development View:**
- utils/gemini_client.py: Retry implementation
- Exception handling in agents/base_agent.py
- Error models in api/models.py

**Physical View:**
- Network errors handled at infrastructure level
- External API failure resilience
- No data loss (partial results saved)

---

## Scenario 5: Scalability Test - Concurrent Requests

### Description
Multiple users submit analyses simultaneously, and the system handles concurrent requests efficiently.

### Main Flow

#### 1. Initial State (Physical View)
```
Docker Compose:
  • hivemind-api: 3 replicas (scaled)
  • Load balancer: Nginx (external)
  • Database: PostgreSQL (single instance with connection pool)
```

#### 2. Concurrent Requests
```
Time: 10:00:00

User 1 → POST /api/v1/analyze (business_need: "E-commerce")
User 2 → POST /api/v1/analyze (business_need: "Healthcare")
User 3 → POST /api/v1/analyze (business_need: "FinTech")

Load Balancer distributes:
  • User 1 → hivemind-api-1
  • User 2 → hivemind-api-2
  • User 3 → hivemind-api-3
```

#### 3. Parallel Execution (Process View)
```
Each API instance executes independently:

hivemind-api-1:
  • HiveMindArchitecture instance (stateless)
  • Workers → Coordinator → Supervisor
  • Database connection from pool
  • Duration: ~50s

hivemind-api-2:
  • Independent HiveMindArchitecture instance
  • Own workers, coordinator, supervisor
  • Separate database connection
  • Duration: ~52s

hivemind-api-3:
  • Independent HiveMindArchitecture instance
  • Own agents
  • Separate database connection
  • Duration: ~48s
```

#### 4. Database Concurrency (Development View)
```
PostgreSQL Connection Pool (SQLAlchemy):
  • Max connections: 10
  • Current connections: 3 (one per API instance)
  • No contention (writes to different rows)

Transactions:
  • Each analysis in separate transaction
  • Isolation level: READ COMMITTED
  • No deadlocks (no shared resources)
```

#### 5. Resource Utilization (Physical View)
```
System Metrics during load:
  CPU: 60% (8 cores)
    • API instances: 45%
    • PostgreSQL: 10%
    • Gemini API calls: 5%

  Memory: 4 GB / 16 GB
    • API instances: 3 GB (1 GB each)
    • PostgreSQL: 512 MB
    • Nginx: 50 MB

  Network: 5 Mbps
    • Gemini API calls: 3 Mbps
    • Database: 1 Mbps
    • Client responses: 1 Mbps
```

#### 6. Results
```
Time: 10:00:50

User 1 receives: analysis_id=44 (success, 50s)
User 2 receives: analysis_id=45 (success, 52s)
User 3 receives: analysis_id=46 (success, 48s)

Database:
  • 3 new analysis records
  • 24 new agent_response records (8 per analysis)
  • No conflicts, all committed successfully
```

### Scalability Insights

**Horizontal Scaling (Physical View):**
- Linear scaling: 3 replicas = 3x throughput
- Stateless design enables easy scaling
- No session affinity required

**Bottlenecks:**
- Gemini API: Rate limits (60 requests/minute)
- Database: Connection pool (10 connections)
- CPU: Moderate usage, room for growth

**Optimization Opportunities:**
- Cache Gemini responses for similar needs
- Read replicas for database
- Queue system for peak loads

---

## Cross-Cutting Scenarios

### Scenario 6: Monitoring & Observability

**Monitoring Flow:**
1. Health checks (every 30s)
2. Metrics collection (Prometheus)
3. Log aggregation (Fluentd)
4. Alerting (PagerDuty)
5. Dashboard (Grafana)

**Traced Request:**
- Trace ID: `trace-12345`
- Spans: API → HiveMind → Workers → Gemini
- Duration: 48.5s
- A2A messages: 16
- Database queries: 9

### Scenario 7: Database Migration

**Migration Flow:**
1. Create new schema version (Alembic)
2. Generate migration script
3. Test on staging database
4. Apply to production (zero-downtime)
5. Verify data integrity

---

## Scenario Analysis Summary

### Key Architectural Qualities Validated

**Scenario 1 (REST API):**
- Validates all 4 views
- Demonstrates complete execution flow
- Shows methodology adaptation

**Scenario 2 (WebSocket):**
- Real-time communication
- Asynchronous processing
- Event-driven architecture

**Scenario 3 (Multi-Methodology):**
- Flexibility and extensibility
- Configuration-driven behavior
- Adapter pattern effectiveness

**Scenario 4 (Error Handling):**
- Resilience and reliability
- Graceful degradation
- Error recovery mechanisms

**Scenario 5 (Scalability):**
- Horizontal scaling
- Concurrent request handling
- Resource efficiency

### Architecture Strengths Demonstrated

1. **Modularity**: Clear separation of concerns across views
2. **Flexibility**: Multiple methodologies, consensus strategies
3. **Scalability**: Horizontal scaling, stateless design
4. **Reliability**: Error handling, retry logic, health checks
5. **Observability**: Logging, tracing, monitoring
6. **Extensibility**: Plugin architecture for agents and strategies

### Alignment with 4+1 Views

Each scenario demonstrates integration across multiple views:
- **Logical**: Component interactions and interfaces
- **Process**: Runtime behavior and state transitions
- **Development**: Code organization and modules
- **Physical**: Infrastructure and deployment
- **Scenarios**: Ties everything together

---

## Conclusion

The Scenarios View validates that the HiveMind architecture successfully addresses:
- Business requirements transformation
- Multi-methodology support
- Real-time user interaction
- Error resilience
- Scalability under load
- Cross-cutting concerns (monitoring, security, etc.)

All scenarios demonstrate coherent integration across the 4 architectural views, confirming the architecture's soundness and completeness.
