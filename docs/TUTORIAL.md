# HiveMind Tutorial

Step-by-step guide to using and extending the HiveMind system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Adding a Custom Worker Agent](#adding-a-custom-worker-agent)
4. [Creating Custom Consensus Strategies](#creating-custom-consensus-strategies)
5. [Customizing Prompts](#customizing-prompts)
6. [Integration Examples](#integration-examples)

---

## Getting Started

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### First Run

```bash
# Run with example
python examples/example_execution.py

# Or run interactively
python src/main.py
```

---

## Basic Usage

### Command Line

```bash
# Interactive mode
python src/main.py

# From file
python src/main.py --input my_need.txt --output my_requirements.json

# Different consensus strategy
python src/main.py --consensus majority
```

### Programmatic Usage

```python
from utils.config import Config
from utils.gemini_client import GeminiClient
from hivemind.architecture import HiveMindArchitecture

# Initialize
config = Config()
client = GeminiClient(
    api_key=config.get_api_key(),
    model_name=config.gemini_model
)

hivemind = HiveMindArchitecture(client)

# Execute
result = hivemind.execute(
    business_need="Build a mobile app for...",
    verbose=True
)

# Access results
print(result.supervisor_response.content)
print(f"Execution time: {result.execution_time}s")
```

---

## Adding a Custom Worker Agent

### Step 1: Create Agent Class

Create `src/agents/custom_agents.py`:

```python
from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentResponse
from ..utils.gemini_client import GeminiClient


class SecuritySpecialistAgent(BaseAgent):
    """Security specialist focused on security requirements."""

    def __init__(self, gemini_client: GeminiClient):
        super().__init__(
            name="SecuritySpecialist",
            role="Security Specialist - Security & Compliance",
            gemini_client=gemini_client
        )

    def get_system_prompt(self) -> str:
        return """You are an experienced Security Specialist with expertise in
application security, data protection, and compliance.

Your role is to analyze SECURITY AND COMPLIANCE requirements:
- Identify security threats and vulnerabilities
- Define authentication and authorization requirements
- Specify data encryption needs
- Ensure compliance with regulations (GDPR, HIPAA, etc.)
- Define security monitoring and incident response

Focus on protecting users and data while enabling functionality."""

    def process(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Analyze security requirements."""

        prompt = f\"\"\"Analyze the following from a Security perspective:

NEED:
{input_data}

Provide JSON with:
- security_threats
- authentication_requirements
- authorization_model
- data_protection
- compliance_requirements
- security_monitoring
- incident_response

Provide ONLY the JSON.\"\"\"

        response_text = self._call_gemini(prompt)

        # Clean JSON
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        confidence = self._extract_confidence(response_text)

        return AgentResponse(
            agent_name=self.name,
            content=response_text,
            confidence=confidence,
            metadata={"role": self.role, "analysis_type": "security"}
        )
```

### Step 2: Register Agent in Architecture

Edit `src/hivemind/architecture.py`:

```python
from ..agents.custom_agents import SecuritySpecialistAgent

class HiveMindArchitecture:
    def __init__(self, gemini_client, consensus_strategy):
        # ... existing code ...

        # Add your custom agent
        self.worker_agents = [
            ProductManagerAgent(gemini_client),
            ProductOwnerAgent(gemini_client),
            UXUIAgent(gemini_client),
            ScrumMasterAgent(gemini_client),
            TechnicalLeadAgent(gemini_client),
            QASpecialistAgent(gemini_client),
            SecuritySpecialistAgent(gemini_client)  # Added
        ]
```

### Step 3: Test Your Agent

```python
from utils.config import Config
from utils.gemini_client import GeminiClient
from agents.custom_agents import SecuritySpecialistAgent

config = Config()
client = GeminiClient(api_key=config.get_api_key())
agent = SecuritySpecialistAgent(client)

response = agent.process("Build a banking app...")
print(response.content)
```

---

## Creating Custom Consensus Strategies

### Step 1: Implement Consensus Engine

Create custom strategy:

```python
from hivemind.consensus import ConsensusEngine, ConsensusResult, ConsensusStrategy
from agents.base_agent import AgentResponse
from typing import List, Optional, Dict, Any


class ExpertPriorityConsensus(ConsensusEngine):
    """Prioritizes expert agents for specific domains."""

    def __init__(self, domain_experts: Dict[str, List[str]]):
        """
        Args:
            domain_experts: Map of domains to expert agent names
                e.g., {"security": ["TechnicalLead", "SecuritySpecialist"]}
        """
        super().__init__("ExpertPriority")
        self.domain_experts = domain_experts

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Achieve consensus by prioritizing domain experts."""

        # Determine domain from context
        domain = context.get("domain", "general") if context else "general"

        # Get expert agents for this domain
        experts = self.domain_experts.get(domain, [])

        # Calculate weighted confidence
        total_weight = 0
        weighted_conf = 0

        for response in responses:
            weight = 2.0 if response.agent_name in experts else 1.0
            total_weight += weight
            weighted_conf += response.confidence * weight

        consensus_level = weighted_conf / total_weight if total_weight > 0 else 0
        achieved = consensus_level >= 0.7

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.WEIGHTED_VOTING,  # Or create new enum
            consensus_level=consensus_level,
            selected_responses=[r for r in responses if r.confidence >= 0.7],
            conflicting_responses=[r for r in responses if r.confidence < 0.7],
            justification=f"Expert priority consensus (domain: {domain}): {consensus_level:.2%}"
        )
```

### Step 2: Register Strategy

```python
from hivemind.consensus import ConsensusManager

manager = ConsensusManager()

# Register custom strategy
custom_engine = ExpertPriorityConsensus(
    domain_experts={
        "security": ["TechnicalLead", "SecuritySpecialist"],
        "ux": ["UXUI_Designer", "ProductOwner"]
    }
)

manager.register_strategy(
    ConsensusStrategy.WEIGHTED_VOTING,  # Or create new enum value
    custom_engine
)
```

---

## Customizing Prompts

### Modify System Prompts

Edit agent's `get_system_prompt()` method:

```python
def get_system_prompt(self) -> str:
    return """You are a [ROLE] specialized in [EXPERTISE].

Your analysis must include:
1. [Aspect 1]
2. [Aspect 2]
3. [Aspect 3]

Output format: [SPECIFY FORMAT]

Be [TONE/STYLE]."""
```

### Adjust Processing Logic

Modify `process()` method for custom output structure:

```python
def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
    # Add context-aware prompting
    additional_context = context.get("industry", "") if context else ""

    prompt = f"""Analyze for {additional_context} industry:

{input_data}

Focus on industry-specific requirements."""

    response_text = self._call_gemini(prompt)

    # Custom confidence calculation
    confidence = self._calculate_custom_confidence(response_text, context)

    return AgentResponse(
        agent_name=self.name,
        content=response_text,
        confidence=confidence,
        metadata={"industry": additional_context}
    )
```

---

## Integration Examples

### Integrate with CI/CD

```python
# scripts/generate_requirements.py
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import Config
from utils.gemini_client import GeminiClient
from hivemind.architecture import HiveMindArchitecture

def generate_requirements_from_ci():
    # Read from environment or file
    business_need = Path("business_need.txt").read_text()

    # Initialize
    config = Config()
    client = GeminiClient(api_key=config.get_api_key())
    hivemind = HiveMindArchitecture(client)

    # Execute
    result = hivemind.execute(business_need, verbose=False)

    # Save to standardized location
    output = Path("docs/technical_requirements.json")
    output.write_text(result.supervisor_response.content)

    # Return exit code based on consensus
    if result.consensus_result.consensus_level < 0.7:
        print("WARNING: Low consensus level")
        sys.exit(1)

    print("✓ Requirements generated successfully")
    sys.exit(0)

if __name__ == "__main__":
    generate_requirements_from_ci()
```

### Web API Integration

```python
from flask import Flask, request, jsonify
from hivemind.architecture import HiveMindArchitecture

app = Flask(__name__)

@app.route("/api/generate-requirements", methods=["POST"])
def generate_requirements():
    data = request.json
    business_need = data.get("business_need")

    # Initialize HiveMind
    client = GeminiClient(api_key=CONFIG.get_api_key())
    hivemind = HiveMindArchitecture(client)

    # Execute
    result = hivemind.execute(business_need, verbose=False)

    return jsonify({
        "requirements": result.supervisor_response.content,
        "consensus_level": result.consensus_result.consensus_level,
        "execution_time": result.execution_time
    })
```

---

## Troubleshooting

### API Key Issues

```bash
# Check if API key is set
python -c "from utils.config import Config; print(Config().get_api_key())"
```

### Timeout Errors

Increase max_tokens in `.env`:
```
MAX_TOKENS=4096
```

### Low Confidence Scores

- Make business need more detailed
- Add industry/domain context
- Try different consensus strategies
- Adjust agent weights

---

## Best Practices

1. **Detailed Business Needs**: More context = better requirements
2. **Appropriate Consensus**: Choose strategy based on use case
3. **Review Outputs**: Always human-review AI-generated requirements
4. **Iterative Refinement**: Run multiple times with feedback
5. **Save Communication Logs**: Useful for debugging and auditing

---

## Next Steps

- Explore `examples/example_execution.py` for complete example
- Read `docs/ARCHITECTURE.md` for deeper understanding
- Check `docs/API_REFERENCE.md` for all available APIs
- Contribute custom agents for your domain!

---

## Community & Support

- GitHub Issues: Report bugs or request features
- Documentation: Check docs/ folder
- Examples: See examples/ folder

Happy HiveMinding! 🐝
