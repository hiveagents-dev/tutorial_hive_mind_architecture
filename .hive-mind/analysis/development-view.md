# Development View - HiveMind Architecture Analysis

## Overview
The Development View describes the static organization of the software in its development environment, including module structure, dependencies, layering, and package organization.

---

## Directory Structure

```
tutorial_hive_mind/
│
├── backend/                              # Backend application (Python)
│   ├── Dockerfile                        # Docker image for backend
│   ├── requirements.txt                  # Python dependencies
│   ├── .env                              # Environment configuration
│   ├── cli.py                            # CLI entry point
│   ├── run_api.py                        # API server launcher
│   ├── test_api.py                       # API integration tests
│   │
│   ├── src/                              # Source code
│   │   ├── __init__.py
│   │   │
│   │   ├── agents/                       # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py            # BaseAgent abstract class
│   │   │   ├── worker_agents.py         # 6 worker agent classes
│   │   │   ├── coordinator_agent.py     # CoordinatorAgent class
│   │   │   └── supervisor_agent.py      # SupervisorAgent class
│   │   │
│   │   ├── api/                          # REST API layer
│   │   │   ├── __init__.py
│   │   │   ├── main.py                  # FastAPI application
│   │   │   ├── endpoints.py             # API endpoints
│   │   │   └── models.py                # Pydantic request/response models
│   │   │
│   │   ├── db/                           # Data persistence layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py              # SQLAlchemy setup
│   │   │   ├── models.py                # Database models
│   │   │   └── persistence.py           # Persistence service
│   │   │
│   │   ├── hivemind/                     # Core architecture components
│   │   │   ├── __init__.py
│   │   │   ├── architecture.py          # HiveMindArchitecture orchestrator
│   │   │   ├── communication.py         # A2A protocol & CommunicationBus
│   │   │   ├── consensus.py             # Consensus mechanisms
│   │   │   ├── methodology.py           # Methodology support
│   │   │   └── hierarchical_flow.py     # Hierarchical execution flow
│   │   │
│   │   └── utils/                        # Utility modules
│   │       ├── __init__.py
│   │       ├── config.py                # Configuration management
│   │       └── gemini_client.py         # Gemini API wrapper
│   │
│   └── examples/                         # Usage examples
│       └── example_execution.py
│
├── frontend/                             # Frontend application (React)
│   ├── Dockerfile                        # Docker image for frontend
│   ├── package.json                      # NPM dependencies
│   ├── vite.config.js                    # Vite configuration
│   ├── index.html                        # HTML entry point
│   │
│   └── src/                              # React source code
│       ├── main.jsx                      # React entry point
│       ├── App.jsx                       # Main app component
│       │
│       ├── api/                          # API client layer
│       │   └── client.js                 # Axios + WebSocket client
│       │
│       ├── components/                   # React components
│       │   ├── AgentContentView.jsx
│       │   ├── DashboardExecutive.jsx
│       │   ├── ResultSummary.jsx
│       │   └── SpecializedAgentsTabs.jsx
│       │
│       ├── context/                      # React Context
│       │   └── AppContext.jsx            # Global state management
│       │
│       └── pages/                        # Page components
│           ├── Dashboard.jsx
│           ├── Analyze.jsx
│           └── History.jsx
│
├── docs/                                 # Documentation
│   ├── ARCHITECTURE.md                   # Architecture documentation
│   ├── API_REFERENCE.md                  # API reference
│   └── TUTORIAL.md                       # Usage tutorial
│
├── .hive-mind/                           # Hive Mind shared memory
│   ├── hive.db                           # SQLite database
│   ├── memory.db                         # Memory store
│   ├── sessions/                         # Session data
│   └── analysis/                         # Analysis outputs
│       ├── logical-view.md
│       ├── process-view.md
│       ├── development-view.md
│       ├── physical-view.md
│       └── scenarios-view.md
│
├── docker-compose.yml                    # Docker orchestration
├── README.md                             # Main documentation
└── .gitignore                            # Git ignore rules
```

---

## Module Dependencies

### Backend Module Dependency Graph

```
┌───────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                        │
├───────────────────────────────────────────────────────────┤
│  cli.py              run_api.py          test_api.py      │
│    │                    │                    │            │
│    └────────────────────┼────────────────────┘            │
└─────────────────────────┼───────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                     API LAYER                             │
├───────────────────────────────────────────────────────────┤
│  api/main.py                                              │
│    │                                                      │
│    ├──> api/endpoints.py                                 │
│    │      │                                               │
│    │      ├──> api/models.py (Pydantic)                  │
│    │      │                                               │
│    │      └──> hivemind/architecture.py                  │
│    │                                                      │
│    └──> db/database.py                                   │
│           │                                               │
│           ├──> db/models.py (SQLAlchemy)                 │
│           └──> db/persistence.py                         │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                ORCHESTRATION LAYER                        │
├───────────────────────────────────────────────────────────┤
│  hivemind/architecture.py                                │
│    │                                                      │
│    ├──> agents/base_agent.py                             │
│    │      │                                               │
│    │      ├──> agents/worker_agents.py                   │
│    │      ├──> agents/coordinator_agent.py               │
│    │      └──> agents/supervisor_agent.py                │
│    │                                                      │
│    ├──> hivemind/hierarchical_flow.py                    │
│    │      │                                               │
│    │      └──> agents/*                                  │
│    │                                                      │
│    ├──> hivemind/communication.py                        │
│    │                                                      │
│    ├──> hivemind/consensus.py                            │
│    │                                                      │
│    └──> hivemind/methodology.py                          │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                  AGENT LAYER                              │
├───────────────────────────────────────────────────────────┤
│  agents/base_agent.py (Abstract)                          │
│    │                                                      │
│    ├──> utils/gemini_client.py                           │
│    │                                                      │
│    └──> hivemind/methodology.py                          │
│           (MethodologyAdapter)                            │
│                                                           │
│  agents/worker_agents.py                                 │
│  agents/coordinator_agent.py                             │
│  agents/supervisor_agent.py                              │
│    │                                                      │
│    └──> agents/base_agent.py (inheritance)               │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                        │
├───────────────────────────────────────────────────────────┤
│  utils/gemini_client.py                                   │
│    │                                                      │
│    └──> google.generativeai (external)                   │
│                                                           │
│  utils/config.py                                          │
│    │                                                      │
│    └──> python-dotenv (external)                         │
│                                                           │
│  db/database.py                                           │
│    │                                                      │
│    ├──> sqlalchemy (external)                            │
│    └──> db/models.py                                     │
└───────────────────────────────────────────────────────────┘
```

### Frontend Module Dependencies

```
┌───────────────────────────────────────────────────────────┐
│                   ENTRY POINT                             │
├───────────────────────────────────────────────────────────┤
│  main.jsx                                                 │
│    │                                                      │
│    ├──> App.jsx                                           │
│    │                                                      │
│    └──> index.html                                        │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                         │
├───────────────────────────────────────────────────────────┤
│  App.jsx                                                  │
│    │                                                      │
│    ├──> context/AppContext.jsx (State)                   │
│    │                                                      │
│    └──> pages/*                                           │
│           ├──> Dashboard.jsx                              │
│           ├──> Analyze.jsx                                │
│           └──> History.jsx                                │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                COMPONENT LAYER                            │
├───────────────────────────────────────────────────────────┤
│  components/                                              │
│    ├──> AgentContentView.jsx                             │
│    ├──> DashboardExecutive.jsx                           │
│    ├──> ResultSummary.jsx                                │
│    └──> SpecializedAgentsTabs.jsx                        │
│           │                                               │
│           └──> context/AppContext.jsx (consume)          │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                   API CLIENT LAYER                        │
├───────────────────────────────────────────────────────────┤
│  api/client.js                                            │
│    │                                                      │
│    ├──> axios (HTTP)                                      │
│    │                                                      │
│    └──> WebSocket (streaming)                            │
└───────────────────────────────────────────────────────────┘
```

---

## Package Structure & Layering

### Backend Packages

#### 1. agents/ Package
**Purpose**: Agent implementations
**External Dependencies**:
- `pydantic` (data validation)
- `google.generativeai` (via GeminiClient)

**Internal Dependencies**:
- `utils.gemini_client`
- `hivemind.methodology`

**Key Classes**:
- `BaseAgent` (abstract base class)
- 6 worker agents (ProductManager, ProductOwner, etc.)
- `CoordinatorAgent`
- `SupervisorAgent`

**Design Pattern**: Template Method (BaseAgent defines template)

#### 2. api/ Package
**Purpose**: REST API and WebSocket endpoints
**External Dependencies**:
- `fastapi` (web framework)
- `uvicorn` (ASGI server)
- `pydantic` (validation)

**Internal Dependencies**:
- `hivemind.architecture`
- `db.database`
- `db.persistence`

**Key Classes**:
- `FastAPI` app instance
- Pydantic request/response models
- API endpoint functions

**Design Pattern**: Dependency Injection (FastAPI)

#### 3. db/ Package
**Purpose**: Data persistence layer
**External Dependencies**:
- `sqlalchemy` (ORM)
- `psycopg2` (PostgreSQL driver)

**Internal Dependencies**: None (lowest layer)

**Key Classes**:
- `Analysis` (SQLAlchemy model)
- `AgentResponse` (SQLAlchemy model)
- `PersistenceService` (service layer)

**Design Pattern**: Repository Pattern

#### 4. hivemind/ Package
**Purpose**: Core architecture components
**External Dependencies**: None (pure Python)

**Internal Dependencies**:
- `agents.base_agent`
- `utils.gemini_client`

**Key Classes**:
- `HiveMindArchitecture` (main orchestrator)
- `CommunicationBus` (message routing)
- `ConsensusManager` (consensus strategies)
- `MethodologyFactory` (methodology contexts)
- `HierarchicalExecutionFlow` (execution management)

**Design Patterns**:
- Orchestrator (HiveMindArchitecture)
- Mediator (CommunicationBus)
- Strategy (ConsensusManager)
- Factory (MethodologyFactory)

#### 5. utils/ Package
**Purpose**: Utility functions and wrappers
**External Dependencies**:
- `google.generativeai` (Gemini SDK)
- `python-dotenv` (config)

**Internal Dependencies**: None (lowest layer)

**Key Classes**:
- `GeminiClient` (API wrapper)
- `Config` (configuration management)

**Design Pattern**: Adapter (GeminiClient)

---

## Dependency Rules

### Layered Architecture Rules

**Rule 1: Downward Dependencies Only**
- Higher layers depend on lower layers
- Lower layers NEVER depend on higher layers
- Example: `agents/` can depend on `utils/`, but not vice versa

**Rule 2: No Skip-Layer Dependencies**
- Layers should depend only on immediate lower layer
- Example: `api/` should use `hivemind/`, not directly use `agents/`
- Exception: All layers can use `utils/` (cross-cutting concern)

**Rule 3: Interface Layer Independence**
- CLI, API, and Frontend are independent interface adapters
- They all depend on `hivemind/` but not on each other

**Rule 4: Infrastructure Independence**
- Core domain logic (`agents/`, `hivemind/`) should not depend on infrastructure
- Infrastructure adapters (`db/`, `api/`) depend on core, not vice versa

### Dependency Inversion Examples

**Good:**
```python
# agents/base_agent.py
class BaseAgent:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client  # Dependency injected
```

**Bad:**
```python
# agents/base_agent.py
from utils.gemini_client import GeminiClient

class BaseAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()  # Hard dependency
```

---

## Build & Deployment Structure

### Python Dependencies (requirements.txt)

```txt
# Core Framework
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# LLM Integration
google-generativeai>=1.46.0

# Utilities
python-dotenv==1.0.0
rich==13.7.0

# ASGI Server
uvicorn[standard]==0.27.0

# Testing
pytest==7.4.4
httpx==0.26.0
```

### JavaScript Dependencies (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

### Docker Build Structure

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ backend/
CMD ["python", "backend/run_api.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Code Organization Principles

### 1. Single Responsibility Principle (SRP)
- Each module has ONE reason to change
- Example: `gemini_client.py` only handles Gemini API calls
- Example: `consensus.py` only handles consensus mechanisms

### 2. Open/Closed Principle (OCP)
- Open for extension, closed for modification
- Example: New consensus strategies can be added without modifying ConsensusManager
- Example: New agents can be added without modifying HiveMindArchitecture

### 3. Liskov Substitution Principle (LSP)
- All agents extend BaseAgent and can be substituted
- Worker agents are interchangeable in HierarchicalExecutionFlow

### 4. Interface Segregation Principle (ISP)
- Small, focused interfaces
- Example: ConsensusEngine only requires `achieve_consensus()` method

### 5. Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- Example: Agents depend on GeminiClient interface, not implementation details

---

## Module Cohesion & Coupling

### High Cohesion Examples

**agents/ package:**
- All components related to agent behavior
- Single purpose: agent implementations
- High functional cohesion

**hivemind/ package:**
- All components related to orchestration
- Single purpose: system coordination
- High sequential cohesion

### Low Coupling Examples

**agents/ ↔ hivemind/:**
- Agents don't know about HiveMindArchitecture
- HiveMindArchitecture uses agents via BaseAgent interface
- Communication via method calls and return values

**api/ ↔ hivemind/:**
- API doesn't know internal agent structure
- Depends only on HiveMindArchitecture interface
- Communication via HiveMindResult objects

---

## Testing Structure

### Test Organization

```
backend/
├── test_api.py                    # API integration tests
└── src/
    ├── agents/
    │   └── test_agents.py        # Agent unit tests
    ├── hivemind/
    │   ├── test_architecture.py  # Orchestration tests
    │   ├── test_consensus.py     # Consensus tests
    │   └── test_methodology.py   # Methodology tests
    └── utils/
        └── test_gemini_client.py # Client tests
```

### Test Dependencies

**Unit Tests:**
- Use mocks for external dependencies (GeminiClient)
- Test individual components in isolation

**Integration Tests:**
- Test full HiveMind execution
- Use test database (in-memory SQLite)
- Mock only external APIs (Gemini)

**End-to-End Tests:**
- Test via REST API
- Use Docker Compose test profile
- Test full stack integration

---

## Configuration Management

### Environment Configuration

**Development:**
```
.env
├── GEMINI_API_KEY=<key>
├── GEMINI_MODEL=gemini-flash-lite-latest
├── TEMPERATURE=0.7
├── MAX_TOKENS=4000
├── DATABASE_URL=postgresql://...
└── API_HOST=0.0.0.0
```

**Docker Compose:**
- Backend: Environment variables from `.env`
- PostgreSQL: Environment variables inline
- Frontend: Build-time configuration

**Production Considerations:**
- Use environment-specific configs
- Secrets management (AWS Secrets Manager, etc.)
- Feature flags for gradual rollout

---

## Version Control Strategy

### Git Structure

**.gitignore:**
```
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# Dependencies
node_modules/

# Build artifacts
dist/
build/
*.log

# Database
*.db
*.db-shm
*.db-wal
```

### Branching Strategy

**Main Branch:**
- Production-ready code
- Protected, requires PR reviews

**Development Branch:**
- Integration branch for features
- Continuous integration tests

**Feature Branches:**
- `feature/agent-name`
- `feature/consensus-strategy`
- Merged to development via PR

---

## Development Tools & IDE Support

### Python Development

**IDE:** PyCharm, VSCode
**Linting:** flake8, pylint
**Formatting:** black, isort
**Type Checking:** mypy

**Example pyproject.toml:**
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

### JavaScript Development

**IDE:** VSCode
**Linting:** ESLint
**Formatting:** Prettier

**Example .eslintrc.json:**
```json
{
  "extends": ["react-app"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "warn"
  }
}
```

---

## Documentation Structure

### Code Documentation

**Python Docstrings:**
```python
def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
    """
    Process input and generate response.

    Args:
        input_data: Input data to process.
        context: Optional contextual information.

    Returns:
        AgentResponse: Structured response from the agent.

    Raises:
        ValueError: If input_data is empty.
        APIError: If Gemini API call fails.
    """
```

**Markdown Documentation:**
- `/docs/ARCHITECTURE.md`: System architecture
- `/docs/API_REFERENCE.md`: API documentation
- `/docs/TUTORIAL.md`: Usage guide
- `/README.md`: Quick start guide

---

## Development View Summary

**Package Organization:**
- Clear separation of concerns across packages
- Layered architecture with strict dependency rules
- High cohesion within packages, low coupling between packages

**Key Principles:**
- SOLID principles applied throughout
- Dependency injection for flexibility
- Interface-based design for extensibility

**Build & Deployment:**
- Docker-based containerization
- Multi-stage builds for frontend
- Environment-based configuration

**Development Practices:**
- Comprehensive testing at multiple levels
- Code quality tools (linting, formatting, type checking)
- Version control with clear branching strategy

**Scalability:**
- Modular design supports horizontal scaling
- Clear interfaces enable component replacement
- Plugin architecture for new agents/strategies
