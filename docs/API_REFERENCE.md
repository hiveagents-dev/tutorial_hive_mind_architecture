# API Reference

Complete reference for all classes and methods in the HiveMind system.

## Core Classes

### HiveMindArchitecture

Main orchestrator for the HiveMind system.

```python
from hivemind.architecture import HiveMindArchitecture
from utils.gemini_client import GeminiClient
from hivemind.consensus import ConsensusStrategy

# Initialize
gemini_client = GeminiClient(api_key="your-key")
hivemind = HiveMindArchitecture(
    gemini_client=gemini_client,
    consensus_strategy=ConsensusStrategy.WEIGHTED_VOTING
)

# Execute
result = hivemind.execute(business_need="...", verbose=True)
```

**Methods:**
- `execute(business_need, verbose)` → HiveMindResult
- `get_communication_statistics()` → dict
- `export_communication_log()` → str
- `get_agent_info()` → dict

---

## Agent Classes

### BaseAgent (Abstract)

Base class for all agents.

```python
from agents.base_agent import BaseAgent, AgentResponse

class CustomAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Your system prompt"

    def process(self, input_data, context=None) -> AgentResponse:
        # Your processing logic
        pass
```

**Abstract Methods:**
- `get_system_prompt()` → str
- `process(input_data, context)` → AgentResponse

**Methods:**
- `_call_gemini(prompt, system_instruction, temperature)` → str
- `communicate(message, recipient)` → str
- `get_info()` → dict

### Worker Agents

All worker agents follow the same interface:

**Available Workers:**
- `ProductManagerAgent` - Business & market analysis
- `ProductOwnerAgent` - User stories & backlog
- `UXUIAgent` - UX/UI design requirements
- `ScrumMasterAgent` - Process & risk management
- `TechnicalLeadAgent` - Architecture & technology
- `QASpecialistAgent` - Quality assurance & testing

**Usage:**
```python
from agents.worker_agents import ProductManagerAgent

agent = ProductManagerAgent(gemini_client)
response = agent.process(business_need)

print(f"Confidence: {response.confidence}")
print(f"Content: {response.content}")
```

### CoordinatorAgent

Synthesizes worker outputs.

```python
from agents.coordinator_agent import CoordinatorAgent

coordinator = CoordinatorAgent(gemini_client)

# Add worker responses
for response in worker_responses:
    coordinator.add_worker_response(response)

# Synthesize
synthesis = coordinator.process(business_need)
```

**Methods:**
- `add_worker_response(response)` → None
- `process(input_data, context)` → AgentResponse
- `get_synthesis_summary()` → dict
- `clear_responses()` → None

### SupervisorAgent

Generates final requirements.

```python
from agents.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(gemini_client)
result = supervisor.process(
    business_need,
    context={"coordinator_synthesis": synthesis.content}
)

# Generate executive summary
summary = supervisor.generate_executive_summary(result.content)
```

**Methods:**
- `process(input_data, context)` → AgentResponse
- `generate_executive_summary(requirements_doc)` → str

---

## Communication

### CommunicationBus

Manages agent-to-agent communication.

```python
from hivemind.communication import CommunicationBus, MessageType

bus = CommunicationBus()

# Send message
message = bus.send_message(
    sender="Agent1",
    recipient="Agent2",
    content="Hello",
    message_type=MessageType.REQUEST
)

# Get statistics
stats = bus.get_statistics()

# Export log
log = bus.export_log()
```

**Methods:**
- `send_message(sender, recipient, content, ...)` → A2AMessage
- `get_conversation(agent1, agent2)` → List[A2AMessage]
- `get_agent_messages(agent_name, direction)` → List[A2AMessage]
- `get_statistics()` → dict
- `export_log()` → str

---

## Consensus

### ConsensusManager

Applies consensus strategies.

```python
from hivemind.consensus import ConsensusManager, ConsensusStrategy

manager = ConsensusManager()

result = manager.apply_consensus(
    responses=worker_responses,
    strategy=ConsensusStrategy.WEIGHTED_VOTING
)

print(f"Consensus achieved: {result.achieved}")
print(f"Level: {result.consensus_level}")
```

**Methods:**
- `apply_consensus(responses, strategy, context)` → ConsensusResult
- `register_strategy(strategy, engine)` → None
- `get_available_strategies()` → List[str]

**Available Strategies:**
- `WEIGHTED_VOTING` - Weighted average of confidence
- `MAJORITY` - Simple majority rule
- `UNANIMOUS` - All must agree
- `CONFIDENCE_THRESHOLD` - Average exceeds threshold

---

## Utilities

### Config

Configuration management.

```python
from utils.config import Config

config = Config()
api_key = config.get_api_key()
model_config = config.get_model_config()
```

**Methods:**
- `get_api_key()` → str
- `get_model_config()` → dict

### GeminiClient

Google Gemini API client.

```python
from utils.gemini_client import GeminiClient

client = GeminiClient(
    api_key="your-key",
    model_name="gemini-1.5-pro-latest",
    temperature=0.7,
    max_tokens=2048
)

response = client.generate_content(
    prompt="Your prompt",
    system_instruction="System instruction"
)
```

**Methods:**
- `generate_content(prompt, system_instruction, temperature, max_tokens)` → str
- `generate_with_context(prompt, context, system_instruction)` → str
- `estimate_tokens(text)` → int
- `estimate_cost(input_tokens, output_tokens)` → float

---

## Data Models

### AgentResponse

```python
from agents.base_agent import AgentResponse

response = AgentResponse(
    agent_name="ProductManager",
    content="Analysis result...",
    confidence=0.85,
    metadata={"key": "value"}
)
```

**Attributes:**
- `agent_name: str` - Agent identifier
- `content: str` - Response content
- `confidence: float` - Confidence score (0-1)
- `metadata: Dict` - Additional data
- `timestamp: str` - ISO timestamp

### A2AMessage

```python
from hivemind.communication import A2AMessage, MessageType

message = A2AMessage(
    message_id="msg_001",
    sender="Agent1",
    recipient="Agent2",
    message_type=MessageType.REQUEST,
    content="Message content"
)
```

**Attributes:**
- `message_id: str`
- `sender: str`
- `recipient: str`
- `message_type: MessageType`
- `priority: MessagePriority`
- `content: str`
- `metadata: Dict`
- `timestamp: str`
- `parent_message_id: Optional[str]`

### ConsensusResult

```python
from hivemind.consensus import ConsensusResult

result = ConsensusResult(
    achieved=True,
    strategy_used=ConsensusStrategy.WEIGHTED_VOTING,
    consensus_level=0.82,
    justification="Explanation..."
)
```

**Attributes:**
- `achieved: bool`
- `strategy_used: ConsensusStrategy`
- `consensus_level: float`
- `selected_responses: List[AgentResponse]`
- `conflicting_responses: List[AgentResponse]`
- `justification: str`
- `metadata: Dict`

---

## CLI Usage

```bash
# Basic usage
python src/main.py

# With input file
python src/main.py --input business_need.txt

# Custom output path
python src/main.py --output requirements.json

# Different consensus strategy
python src/main.py --consensus majority

# Quiet mode
python src/main.py --quiet
```

**Arguments:**
- `--input, -i` - Input file path
- `--output, -o` - Output file path
- `--consensus, -c` - Consensus strategy
- `--quiet, -q` - Minimal output

---

## Error Handling

All methods may raise:
- `ValueError` - Invalid parameters
- `Exception` - API errors, processing failures

```python
try:
    result = hivemind.execute(business_need)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Execution error: {e}")
```

---

For more examples, see `examples/example_execution.py`.
