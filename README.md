# HiveMind Architecture
## Discovery to Technical Requirements System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-4285F4)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Transform business needs into comprehensive technical requirements using a hierarchical multi-agent AI system powered by Google Gemini.

---

## Overview

This project implements a **HiveMind architecture with hierarchical consensus** to automatically transform business needs into detailed, production-ready technical requirements documents. The system orchestrates 6 specialized AI agents representing different roles in software development (Product Manager, Product Owner, UX/UI Designer, Scrum Master, Technical Lead, and QA Specialist) to analyze requirements from multiple perspectives and synthesize them into actionable technical specifications.

### Problem Solved

**From**: "We need to build a mobile app for sustainable fashion"
**To**: Complete technical requirements document with:
- Business objectives and success metrics
- Functional & non-functional requirements
- User stories with acceptance criteria
- Technical architecture and technology stack
- UX/UI specifications
- Testing strategy and quality gates
- Implementation plan with phases and milestones
- Risk assessment and mitigation strategies

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              SUPERVISOR AGENT                       │
│         (Level 3 - Final Decision)                  │
│     Generates Technical Requirements Document       │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│            COORDINATOR AGENT                        │
│        (Level 2 - Synthesis)                        │
│    Integrates & Resolves Conflicts                  │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────────────────────────────────────────┐
│              WORKER AGENTS (Level 1)                  │
├───────────────┬───────────────┬───────────────────────┤
│ Product       │ Product       │ UX/UI                 │
│ Manager       │ Owner         │ Designer              │
├───────────────┼───────────────┼───────────────────────┤
│ Scrum         │ Technical     │ QA                    │
│ Master        │ Lead          │ Specialist            │
└───────────────┴───────────────┴───────────────────────┘
```

**Key Features:**
- **6 Specialized Worker Agents** analyze from different perspectives
- **Coordinator Agent** synthesizes and resolves conflicts
- **Supervisor Agent** generates final authoritative document
- **Agent-to-Agent (A2A) Protocol** for transparent communication
- **Multiple Consensus Strategies** (Weighted Voting, Majority, etc.)
- **Structured JSON Output** ready for downstream processing

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tutorial_hive_mind

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
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

### Example Output

```
🐝 HiveMind Architecture - Discovery to Technical Requirements
═══════════════════════════════════════════════════════════════

[PHASE 1: Worker Agents Analysis]
  → ProductManager: Processing... ✓ (Confidence: 0.89)
  → ProductOwner: Processing... ✓ (Confidence: 0.92)
  → UXUI_Designer: Processing... ✓ (Confidence: 0.85)
  → ScrumMaster: Processing... ✓ (Confidence: 0.88)
  → TechnicalLead: Processing... ✓ (Confidence: 0.91)
  → QA_Specialist: Processing... ✓ (Confidence: 0.87)

[PHASE 2: Coordinator Synthesis]
  → Coordinator: Synthesizing 6 worker responses... ✓
  → Applying consensus strategy: weighted_voting... ✓ (Level: 88.7%)

[PHASE 3: Supervisor - Final Requirements]
  → Supervisor: Generating final technical requirements... ✓

═══════════════════════════════════════════════════════════════
✅ HIVEMIND EXECUTION COMPLETED
═══════════════════════════════════════════════════════════════
⏱  Execution Time: 45.32s
📊 Consensus Level: 88.7%
🎯 Final Confidence: 95.0%
```

---

## Project Structure

```
tutorial_hive_mind/
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── requirements.txt         # Python dependencies
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py             # CLI entry point
│   │
│   ├── agents/             # Agent implementations
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── worker_agents.py       # 6 specialized workers
│   │   ├── coordinator_agent.py   # Synthesis agent
│   │   └── supervisor_agent.py    # Final decision agent
│   │
│   ├── hivemind/           # HiveMind core
│   │   ├── architecture.py        # Main orchestrator
│   │   ├── consensus.py           # Consensus mechanisms
│   │   └── communication.py       # A2A protocol
│   │
│   └── utils/              # Utilities
│       ├── config.py              # Configuration management
│       └── gemini_client.py       # Gemini API wrapper
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md     # Architecture deep-dive
│   ├── API_REFERENCE.md    # API documentation
│   └── TUTORIAL.md         # Extension tutorial
│
└── examples/               # Usage examples
    └── example_execution.py
```

---

## Usage

### Command Line Interface

```bash
# Interactive mode (type or paste business need)
python src/main.py

# From file
python src/main.py --input business_need.txt --output requirements.json

# Different consensus strategy
python src/main.py --consensus majority

# Quiet mode (minimal output)
python src/main.py --quiet
```

### Programmatic Usage

```python
from utils.config import Config
from utils.gemini_client import GeminiClient
from hivemind.architecture import HiveMindArchitecture

# Initialize
config = Config()
gemini_client = GeminiClient(
    api_key=config.get_api_key(),
    model_name=config.gemini_model
)

hivemind = HiveMindArchitecture(gemini_client)

# Execute
business_need = """
We need to develop a mobile-first e-commerce platform
for sustainable fashion brands...
"""

result = hivemind.execute(business_need, verbose=True)

# Access results
requirements_json = result.supervisor_response.content
consensus_level = result.consensus_result.consensus_level
execution_time = result.execution_time
```

### REST API Interface

The system includes a complete REST API built with FastAPI, providing programmatic access to all HiveMind capabilities.

#### Starting the API Server

```bash
# Start the API server
python run_api.py

# Start with custom configuration
python run_api.py --host 0.0.0.0 --port 8080 --reload

# Start in production mode
python run_api.py --host 0.0.0.0 --port 8000
```

#### API Endpoints

- **`GET /`** - Root endpoint with basic information
- **`GET /api/v1/health`** - Health check endpoint
- **`GET /api/v1/info`** - System information and capabilities
- **`GET /api/v1/methodologies`** - Available agile methodologies
- **`GET /api/v1/consensus-strategies`** - Available consensus strategies
- **`POST /api/v1/analyze`** - Main endpoint for business need analysis
- **`POST /api/v1/example`** - Run example analysis

#### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

#### Example API Usage

```python
import requests

# Analyze business need via API
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "business_need": "We need to create a mobile app for medical appointment booking",
    "methodology": "scrum",
    "consensus_strategy": "weighted_voting",
    "verbose": True
})

result = response.json()
print(f"Analysis completed in {result['execution_time']:.2f}s")
print(f"Consensus level: {result['consensus_result']['consensus_level']:.2f}")
```

#### Testing the API

```bash
# Run comprehensive API tests
python test_api.py

# Test with custom URL
python test_api.py --url http://localhost:8080
```

---

## Output Structure

The system generates a comprehensive JSON document with:

```json
{
  "document_metadata": { ... },
  "executive_summary": {
    "overview": "...",
    "business_objectives": [...],
    "key_deliverables": [...],
    "timeline": "..."
  },
  "business_requirements": { ... },
  "functional_requirements": {
    "features": [...]
  },
  "non_functional_requirements": { ... },
  "technical_specifications": {
    "architecture": { ... },
    "technology_stack": { ... }
  },
  "ux_ui_requirements": { ... },
  "quality_assurance": { ... },
  "implementation_plan": { ... },
  "risks_and_mitigation": [...],
  "dependencies_and_constraints": { ... }
}
```

---

## Key Concepts

### HiveMind Architecture

A multi-agent system where specialized agents collaborate through hierarchical consensus:
- **Parallel Processing**: Worker agents analyze independently
- **Diversity of Thought**: Each agent brings unique expertise
- **Hierarchical Synthesis**: Coordinator integrates perspectives
- **Final Authority**: Supervisor makes authoritative decisions

### Consensus Mechanisms

**Weighted Voting** (Default)
- Each agent has expertise-based weight
- Consensus = weighted average of confidence scores

**Majority**
- Simple majority of agreeing agents

**Unanimous**
- All agents must agree

**Confidence Threshold**
- Average confidence must exceed threshold

### Agent-to-Agent (A2A) Protocol

Standardized message format for inter-agent communication:
```python
{
  "message_id": "msg_0001",
  "sender": "ProductManager",
  "recipient": "Coordinator",
  "message_type": "response",
  "content": "...",
  "timestamp": "2025-10-26T12:30:45"
}
```

---

## Technology Stack

- **Python 3.11+**: Modern Python with type hints
- **Google Gemini API**: Advanced language model via `google-genai>=1.46.0`
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and settings management
- **Rich**: Beautiful terminal output
- **A2A Protocol**: Agent communication standard

---

## Documentation

### Architecture Documentation (4+1 Views)

Comprehensive architectural documentation following Philippe Kruchten's 4+1 view model:

- **[Overview](docs/architecture/overview.md)**: Introduction to the 4+1 architecture views
- **[Logical View](docs/architecture/logical-view.md)**: Components, responsibilities, and relationships
- **[Process View](docs/architecture/process-view.md)**: Runtime behavior, workflows, and communication
- **[Development View](docs/architecture/development-view.md)**: Code organization, modules, and build system
- **[Physical View](docs/architecture/physical-view.md)**: Deployment, infrastructure, and scaling
- **[Scenarios (+1)](docs/architecture/scenarios.md)**: Use cases, workflows, and user interactions

### Additional Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Original comprehensive architecture document
- **[API_REFERENCE.md](docs/API_REFERENCE.md)**: Complete API documentation
- **[TUTORIAL.md](docs/TUTORIAL.md)**: Guide to extending the system

---

## Examples

### Example 1: E-Commerce Platform

```bash
python src/main.py --input examples/ecommerce_need.txt
```

Generates complete technical requirements for a sustainable fashion e-commerce platform.

### Example 2: Custom Agent

See [TUTORIAL.md](docs/TUTORIAL.md) for how to add a custom `SecuritySpecialistAgent`.

---

## Troubleshooting

### API Key Not Found

```bash
# Check if API key is set
python -c "from utils.config import Config; print(Config().get_api_key())"
```

### Timeout Errors

Increase `MAX_TOKENS` in `.env`:
```
MAX_TOKENS=4096
```

### Low Consensus

- Provide more detailed business need description
- Try different consensus strategies
- Review worker responses for conflicts

---

## Performance

**Typical Execution:**
- **Time**: 30-60 seconds
- **API Calls**: 8 (6 workers + coordinator + supervisor)
- **Tokens**: ~15,000-25,000
- **Cost**: ~$0.03-$0.05 (depends on Gemini pricing)

**Optimizations:**
- Worker agents run in parallel
- Efficient prompt design
- Structured output format reduces parsing

---

## Contributing

Contributions welcome! Areas for improvement:
- Additional worker agents (Security, Data, DevOps)
- New consensus strategies
- Multi-language support
- Visual diagram generation
- Integration with project management tools

---

## Academic Context

This project demonstrates:
- **Multi-Agent Systems (MAS)**: Coordination and collaboration
- **Hierarchical Decision Making**: Three-level architecture
- **Consensus Mechanisms**: Various voting strategies
- **Agent Communication**: A2A protocol implementation
- **LLM Orchestration**: Managing multiple AI agents

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- Built with **Google Gemini** API
- Inspired by **HiveMind** and **Agent-to-Agent (A2A)** research
- Designed for **AI Agent Engineering** education

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: See `docs/` folder
- **Examples**: See `examples/` folder

---

**Happy HiveMinding!** 🐝
