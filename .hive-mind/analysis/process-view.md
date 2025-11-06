# Process View - HiveMind Architecture Analysis

## Overview
The Process View describes the dynamic behavior of the system at runtime, including concurrency, communication patterns, process flows, and system behavior during execution.

---

## Process Architecture

### System Processes

**Main Process: HiveMind Execution**
- Entry Point: `HiveMindArchitecture.execute()`
- Process Type: Synchronous sequential execution
- Thread Model: Single-threaded with sequential agent execution
- Duration: ~30-60 seconds per execution

**API Server Process**
- Entry Point: `uvicorn` running FastAPI application
- Process Type: Asynchronous event-driven (ASGI)
- Thread Model: Async/await with event loop
- Concurrency: Multiple concurrent requests via async handlers

---

## Execution Flow Diagrams

### 1. Main Execution Flow (Sequence Diagram)

```
User/Client
    │
    ├──[1. Initialize]─────> HiveMindArchitecture
    │                              │
    │                              ├──> Load MethodologyContext
    │                              ├──> Initialize CommunicationBus
    │                              ├──> Initialize ConsensusManager
    │                              ├──> Initialize HierarchicalExecutionFlow
    │                              └──> Initialize Agents (8 total)
    │
    ├──[2. Execute]──────────> HiveMindArchitecture.execute()
    │                              │
    │                              │
    │         ┌────────────────────┴────────────────────┐
    │         │                                         │
    │         │  PHASE 1: HIERARCHICAL WORKER EXECUTION │
    │         │                                         │
    │         ├──> HierarchicalExecutionFlow.execute_hierarchical_flow()
    │         │         │
    │         │         ├──[Phase 1: Business Foundation]──> ProductManager
    │         │         │                                        │
    │         │         │                                        ├──> CommunicationBus.send(REQUEST)
    │         │         │                                        ├──> GeminiClient.generate_content()
    │         │         │                                        ├──> CommunicationBus.send(RESPONSE)
    │         │         │                                        └──> Return AgentResponse
    │         │         │                                              (confidence: 0.89)
    │         │         │
    │         │         ├──[Phase 2: Product Definition]──> ProductOwner
    │         │         │      Input: Business Need + PM Context
    │         │         │                                        │
    │         │         │                                        ├──> Receive PM output as dependency
    │         │         │                                        ├──> CommunicationBus.send(REQUEST)
    │         │         │                                        ├──> GeminiClient.generate_content()
    │         │         │                                        ├──> CommunicationBus.send(RESPONSE)
    │         │         │                                        └──> Return AgentResponse
    │         │         │                                              (confidence: 0.92)
    │         │         │
    │         │         ├──[Phase 3: User Experience]──> UXUIAgent
    │         │         │      Input: Business Need + PO Context
    │         │         │                                        │
    │         │         │                                        └──> AgentResponse (confidence: 0.85)
    │         │         │
    │         │         ├──[Phase 4: Technical Foundation]──> TechnicalLead
    │         │         │      Input: Business Need + UX Context
    │         │         │                                        │
    │         │         │                                        └──> AgentResponse (confidence: 0.91)
    │         │         │
    │         │         ├──[Phase 5: Process Optimization]──> ScrumMaster
    │         │         │      Input: Business Need + Tech Context
    │         │         │                                        │
    │         │         │                                        └──> AgentResponse (confidence: 0.88)
    │         │         │
    │         │         └──[Phase 6: Quality Assurance]──> QASpecialist
    │         │                Input: Business Need + SM Context
    │         │                                                 │
    │         │                                                 └──> AgentResponse (confidence: 0.87)
    │         │
    │         │  Output: 6 Worker AgentResponses with preserved context
    │         │
    │         └────────────────────┬────────────────────┘
    │                              │
    │         ┌────────────────────┴────────────────────┐
    │         │                                         │
    │         │  PHASE 2: COORDINATOR SYNTHESIS         │
    │         │                                         │
    │         ├──> CoordinatorAgent.process()
    │         │         │
    │         │         ├──> Receive all 6 worker responses
    │         │         ├──> CommunicationBus.send(REQUEST)
    │         │         ├──> GeminiClient.generate_content()
    │         │         │      Prompt: Synthesize + resolve conflicts
    │         │         ├──> CommunicationBus.send(RESPONSE)
    │         │         └──> Return integrated synthesis
    │         │
    │         ├──> ConsensusManager.apply_consensus()
    │         │         │
    │         │         ├──> Select strategy: WeightedVoting
    │         │         ├──> Calculate weighted confidence
    │         │         │      weights = {PM: 1.2, PO: 1.1, UX: 1.0,
    │         │         │                 SM: 0.9, Tech: 1.3, QA: 1.0}
    │         │         │      consensus = Σ(conf × weight) / Σ(weight)
    │         │         └──> Return ConsensusResult
    │         │                (achieved: true, level: 0.887)
    │         │
    │         └────────────────────┬────────────────────┘
    │                              │
    │         ┌────────────────────┴────────────────────┐
    │         │                                         │
    │         │  PHASE 3: SUPERVISOR FINALIZATION       │
    │         │                                         │
    │         ├──> SupervisorAgent.process()
    │         │         │
    │         │         ├──> Receive coordinator synthesis
    │         │         ├──> CommunicationBus.send(REQUEST)
    │         │         ├──> GeminiClient.generate_content()
    │         │         │      Prompt: Generate final requirements
    │         │         ├──> CommunicationBus.send(RESPONSE)
    │         │         └──> Return final requirements document
    │         │                (confidence: 0.95)
    │         │
    │         └────────────────────┬────────────────────┘
    │                              │
    │                              ├──> Build HiveMindResult
    │                              │      • worker_responses (6)
    │                              │      • coordinator_response
    │                              │      • supervisor_response
    │                              │      • consensus_result
    │                              │      • communication_log
    │                              │      • execution_time
    │                              │      • metadata
    │                              │
    │<──[3. Return Result]────────┤
    │
    └──> HiveMindResult
```

---

## State Transition Diagrams

### Agent State Machine

```
┌─────────────┐
│             │
│ INITIALIZED │
│             │
└──────┬──────┘
       │
       │ process() called
       ▼
┌─────────────┐
│             │
│ PROCESSING  │◄────┐
│             │     │
└──────┬──────┘     │ Retry on error
       │            │ (with backoff)
       │ Success    │
       ▼            │
┌─────────────┐     │
│             │     │
│  COMPLETED  │     │
│             │     │
└──────┬──────┘     │
       │            │
       │ Error      │
       ▼            │
┌─────────────┐     │
│             │─────┘
│   ERROR     │
│             │
└─────────────┘
```

### Execution Phase State Machine

```
                    ┌──────────────────┐
                    │                  │
              ┌────>│  BUSINESS_FOUND  │
              │     │                  │
              │     └────────┬─────────┘
              │              │
              │              │ PM completes
              │              ▼
┌─────────┐   │     ┌──────────────────┐
│         │   │     │                  │
│  IDLE   │───┴────>│ PRODUCT_DEFIN    │
│         │         │                  │
└─────────┘         └────────┬─────────┘
                             │
                             │ PO completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │ USER_EXPERIENCE  │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ UX completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │ TECH_FOUNDATION  │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ Tech completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │ PROCESS_OPTIM    │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ SM completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │ QUALITY_ASSUR    │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ QA completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │   COORDINATION   │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ Coordinator completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │   SUPERVISION    │
                    │                  │
                    └────────┬─────────┘
                             │
                             │ Supervisor completes
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │    COMPLETED     │
                    │                  │
                    └──────────────────┘
```

---

## Communication Patterns

### A2A Protocol Message Flow

**Message Exchange Pattern:**

```
1. System → Worker Agent (REQUEST)
   ┌────────────────────────────────────┐
   │ message_id: msg_0001               │
   │ sender: System                     │
   │ recipient: ProductManager          │
   │ message_type: REQUEST              │
   │ priority: MEDIUM                   │
   │ content: "Analyze business need"   │
   │ metadata: {phase, methodology}     │
   │ timestamp: 2025-11-06T10:00:00     │
   └────────────────────────────────────┘

2. Worker Agent → System (RESPONSE)
   ┌────────────────────────────────────┐
   │ message_id: msg_0002               │
   │ sender: ProductManager             │
   │ recipient: System                  │
   │ message_type: RESPONSE             │
   │ priority: MEDIUM                   │
   │ content: "Analysis complete"       │
   │ metadata: {confidence: 0.89}       │
   │ timestamp: 2025-11-06T10:00:15     │
   │ parent_message_id: msg_0001        │
   └────────────────────────────────────┘

3-12. [Repeat for other 5 workers]

13. System → Coordinator (REQUEST)
   ┌────────────────────────────────────┐
   │ message_id: msg_0013               │
   │ sender: System                     │
   │ recipient: Coordinator             │
   │ message_type: REQUEST              │
   │ priority: HIGH                     │
   │ content: "Synthesize responses"    │
   │ metadata: {worker_count: 6}        │
   │ timestamp: 2025-11-06T10:02:00     │
   └────────────────────────────────────┘

14. Coordinator → System (RESPONSE)
   ┌────────────────────────────────────┐
   │ message_id: msg_0014               │
   │ sender: Coordinator                │
   │ recipient: System                  │
   │ message_type: RESPONSE             │
   │ priority: HIGH                     │
   │ content: "Synthesis complete"      │
   │ metadata: {conflicts_resolved: 2}  │
   │ timestamp: 2025-11-06T10:02:30     │
   │ parent_message_id: msg_0013        │
   └────────────────────────────────────┘

15. System → Supervisor (REQUEST)
16. Supervisor → System (RESPONSE)
```

---

## Concurrency Model

### Sequential Execution with Dependencies

**Worker Phase:**
- **Pattern**: Sequential execution with explicit dependencies
- **Rationale**: Each phase requires output from previous phase
- **Concurrency**: None at worker level (sequential by design)
- **Parallelization Opportunity**: Could parallelize independent sub-analyses within each agent

**Coordinator Phase:**
- **Pattern**: Single coordinator processes all worker outputs
- **Concurrency**: None (single coordinator)

**Supervisor Phase:**
- **Pattern**: Single supervisor generates final document
- **Concurrency**: None (single supervisor)

### API Server Concurrency

**Request Handling:**
- **Model**: Asynchronous ASGI (FastAPI + uvicorn)
- **Concurrency**: Multiple concurrent API requests
- **Pattern**: Event loop with async/await
- **WebSocket**: Async streaming for real-time progress updates

---

## Performance Characteristics

### Execution Timing

**Phase Breakdown (Typical):**
```
Phase 1: Worker Execution (Sequential)
├─ ProductManager:     ~5s  (cumulative: 5s)
├─ ProductOwner:       ~6s  (cumulative: 11s)
├─ UXUIAgent:          ~5s  (cumulative: 16s)
├─ TechnicalLead:      ~7s  (cumulative: 23s)
├─ ScrumMaster:        ~5s  (cumulative: 28s)
└─ QASpecialist:       ~5s  (cumulative: 33s)

Phase 2: Coordination
└─ Coordinator:        ~8s  (cumulative: 41s)

Phase 3: Supervision
└─ Supervisor:         ~9s  (cumulative: 50s)

Total: ~50s (varies by LLM response time)
```

**Bottlenecks:**
1. **LLM API Calls**: Each agent waits for Gemini response (~5-10s each)
2. **Sequential Dependencies**: Cannot parallelize dependent phases
3. **Network Latency**: API calls to external Gemini service

**Optimization Opportunities:**
1. Cache similar business needs
2. Parallelize independent analyses within agents
3. Use streaming responses for faster partial results
4. Implement speculative execution for predictable paths

---

## Data Flow Analysis

### Context Preservation Pattern

**Phase 1 → Phase 2:**
```python
# ProductManager output
pm_response = {
    "agent_name": "ProductManager",
    "content": "Business analysis...",
    "confidence": 0.89,
    "metadata": {...}
}

# ProductOwner receives as dependency
po_context = {
    "phase": "product_definition",
    "methodology": "scrum",
    "dependencies": [
        {
            "phase": "business_foundation",
            "agent": "ProductManager",
            "confidence": 0.89,
            "content": "Business analysis..." (truncated to 500 chars)
        }
    ],
    "previous_responses": [pm_response]
}
```

**Context Growth:**
- Each phase adds its output to context
- Subsequent phases receive cumulative context
- Content truncated to prevent token overflow
- Full responses available via `previous_responses`

---

## Error Handling & Recovery

### Error Propagation

```
Agent Error
    │
    ├──> Log error
    │
    ├──> Retry logic (GeminiClient)
    │    • Exponential backoff
    │    • Max 3 retries
    │
    ├──> If retry fails
    │    └──> Raise exception
    │
    └──> HiveMindArchitecture catches
         │
         ├──> Log to communication bus
         │
         ├──> Mark execution as failed
         │
         └──> Return partial result with error metadata
```

### Quality Gates

**Phase Validation:**
1. Check dependency outputs available
2. Validate confidence scores
3. Verify content completeness
4. Check methodology compliance

**Consensus Validation:**
1. Check consensus achievement
2. Validate consensus level
3. Review conflicting responses
4. Ensure minimum agreement threshold

---

## Real-Time Streaming (WebSocket)

### Progress Update Flow

```
Client establishes WebSocket connection
    │
    ├──> Server receives start message
    │
    ├──> Execute HiveMind in background task
    │
    ├──> Emit progress events:
    │    │
    │    ├──> {"type": "progress", "phase": "workers",
    │    │     "agent": "ProductManager", "status": "processing"}
    │    │
    │    ├──> {"type": "progress", "phase": "workers",
    │    │     "agent": "ProductManager", "status": "complete",
    │    │     "confidence": 0.89}
    │    │
    │    ├──> [Repeat for other 5 workers]
    │    │
    │    ├──> {"type": "progress", "phase": "coordinator",
    │    │     "status": "processing"}
    │    │
    │    ├──> {"type": "progress", "phase": "coordinator",
    │    │     "status": "complete"}
    │    │
    │    ├──> {"type": "progress", "phase": "supervisor",
    │    │     "status": "processing"}
    │    │
    │    └──> {"type": "progress", "phase": "supervisor",
    │         "status": "complete"}
    │
    └──> Emit complete event:
         {"type": "complete", "result": {...}}
```

---

## Thread Safety & Synchronization

### Current Implementation
- **Single-threaded execution** for main HiveMind flow
- **No shared mutable state** between executions
- **Stateless agents** (no instance variables modified during execution)
- **Thread-safe communication bus** (append-only message list)

### API Server Thread Safety
- **Async/await model** in FastAPI
- **Independent execution contexts** per request
- **Database connections** managed via connection pool
- **No global state mutation**

---

## Process Analysis Summary

**Execution Model:**
- Sequential hierarchical execution with explicit dependencies
- Single-threaded for consistency and traceability
- Asynchronous API layer for concurrent request handling

**Communication:**
- Message-based via A2A protocol
- Complete traceability via communication bus
- Parent-child message relationships for context

**Performance:**
- ~50s average execution time
- Dominated by LLM API calls
- Sequential dependencies prevent parallelization

**Reliability:**
- Retry logic for transient failures
- Error propagation with partial results
- Quality gates at each phase

**Scalability:**
- Horizontal scaling via multiple API server instances
- Stateless design enables load balancing
- Database as shared persistence layer
