# Development View - HiveMind Architecture

## Overview

The **Development View** describes the system's code organization, module structure, and software management concerns. This view addresses the **how the code is organized** for development, build, and maintenance.

**Target Audience**: Software Developers, Build Engineers, Development Team Leads

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Module Organization](#module-organization)
3. [Package Dependencies](#package-dependencies)
4. [Build System](#build-system)
5. [Development Workflow](#development-workflow)
6. [Code Standards](#code-standards)
7. [Testing Strategy](#testing-strategy)
8. [Configuration Management](#configuration-management)

---

## Project Structure

### High-Level Directory Layout

```
tutorial_hive_mind/
├── .claude/                      # Claude Code CLI configuration
├── .claude-flow/                 # Claude Flow data
├── .git/                         # Git version control
├── .github/                      # GitHub workflows (future)
├── .hive-mind/                   # HiveMind runtime data
├── .venv/                        # Python virtual environment
│
├── backend/                      # Backend Python application
│   ├── Dockerfile                # Backend container image
│   ├── .env                      # Environment variables
│   ├── requirements.txt          # Python dependencies
│   ├── cli.py                    # CLI entry point
│   ├── run_api.py               # API server launcher
│   ├── test_api.py              # API tests
│   │
│   ├── src/                      # Source code
│   │   ├── __init__.py
│   │   │
│   │   ├── agents/               # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py    # Abstract base class
│   │   │   ├── worker_agents.py # 6 worker specialists
│   │   │   ├── coordinator_agent.py
│   │   │   └── supervisor_agent.py
│   │   │
│   │   ├── api/                  # REST API
│   │   │   ├── __init__.py
│   │   │   ├── main.py          # FastAPI application
│   │   │   ├── endpoints.py     # API route handlers
│   │   │   └── models.py        # Pydantic models
│   │   │
│   │   ├── db/                   # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # SQLAlchemy setup
│   │   │   ├── models.py        # ORM models
│   │   │   └── persistence.py   # Data access layer
│   │   │
│   │   ├── hivemind/             # Core architecture
│   │   │   ├── __init__.py
│   │   │   ├── architecture.py  # Main orchestrator
│   │   │   ├── communication.py # A2A protocol
│   │   │   ├── consensus.py     # Consensus mechanisms
│   │   │   ├── methodology.py   # Methodology support
│   │   │   └── hierarchical_flow.py # Execution flow
│   │   │
│   │   └── utils/                # Utilities
│   │       ├── __init__.py
│   │       ├── config.py        # Configuration
│   │       └── gemini_client.py # LLM client
│   │
│   └── examples/                 # Usage examples
│       └── example_execution.py
│
├── frontend/                     # React web application
│   ├── Dockerfile               # Frontend container image
│   ├── package.json             # NPM dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── index.html               # HTML entry point
│   ├── styles.css               # Global styles
│   │
│   └── src/                     # React source code
│       ├── main.jsx             # React entry point
│       ├── App.jsx              # Main App component
│       │
│       ├── api/                 # API client
│       │   └── client.js
│       │
│       ├── components/          # React components
│       │   ├── AgentContentView.jsx
│       │   ├── DashboardExecutive.jsx
│       │   ├── ResultSummary.jsx
│       │   └── SpecializedAgentsTabs.jsx
│       │
│       ├── context/             # React Context
│       │   └── AppContext.jsx
│       │
│       └── pages/               # Page components
│           ├── Dashboard.jsx
│           ├── Analyze.jsx
│           └── History.jsx
│
├── docs/                        # Documentation
│   ├── architecture/            # Architecture docs (4+1 views)
│   │   ├── overview.md
│   │   ├── logical-view.md
│   │   ├── process-view.md
│   │   ├── development-view.md (this file)
│   │   ├── physical-view.md
│   │   └── scenarios.md
│   │
│   ├── ARCHITECTURE.md          # Original architecture doc
│   ├── API_REFERENCE.md         # API documentation
│   └── TUTORIAL.md              # Extension tutorial
│
├── logs/                        # Application logs
├── output/                      # Generated outputs
│
├── docker-compose.yml           # Docker orchestration
├── .dockerignore               # Docker ignore rules
├── .gitignore                  # Git ignore rules
├── README.md                   # Project README
└── requirements.txt            # Root Python dependencies

```

---

## Module Organization

### Backend Module Structure

```mermaid
graph TD
    subgraph "Application Layer"
        CLI[cli.py]
        API[api/main.py]
    end

    subgraph "Domain Layer"
        ARCH[hivemind/architecture.py]
        AGENTS[agents/*]
        FLOW[hivemind/hierarchical_flow.py]
    end

    subgraph "Service Layer"
        COMM[hivemind/communication.py]
        CONS[hivemind/consensus.py]
        METH[hivemind/methodology.py]
    end

    subgraph "Infrastructure Layer"
        GEMINI[utils/gemini_client.py]
        DB[db/persistence.py]
        CONFIG[utils/config.py]
    end

    CLI --> ARCH
    API --> ARCH
    ARCH --> AGENTS
    ARCH --> FLOW
    ARCH --> COMM
    ARCH --> CONS
    FLOW --> METH
    AGENTS --> GEMINI
    AGENTS --> COMM
    ARCH --> DB
    DB --> CONFIG
    AGENTS --> CONFIG

    style ARCH fill:#ff6b6b
    style AGENTS fill:#4ecdc4
```

### Module Dependencies Matrix

| Module | Depends On | Exported APIs |
|--------|-----------|---------------|
| **cli.py** | architecture, config | `main()` |
| **api/main.py** | architecture, models, endpoints | FastAPI app |
| **api/endpoints.py** | architecture, models | Route handlers |
| **architecture.py** | agents, communication, consensus, flow | `HiveMindArchitecture` |
| **base_agent.py** | gemini_client, methodology | `BaseAgent` |
| **worker_agents.py** | base_agent | 6 agent classes |
| **coordinator_agent.py** | base_agent, consensus | `CoordinatorAgent` |
| **supervisor_agent.py** | base_agent | `SupervisorAgent` |
| **communication.py** | - | `CommunicationBus`, `A2AMessage` |
| **consensus.py** | base_agent | `ConsensusManager` |
| **methodology.py** | - | `MethodologyFactory` |
| **hierarchical_flow.py** | agents, communication, methodology | `HierarchicalExecutionFlow` |
| **gemini_client.py** | config | `GeminiClient` |
| **persistence.py** | database, models | `PersistenceService` |
| **config.py** | - | `Config` |

---

## Package Dependencies

### Backend Dependencies (Python)

#### Core Dependencies
```txt
# requirements.txt

# Framework
fastapi>=0.104.1              # Web framework
uvicorn[standard]>=0.24.0     # ASGI server
pydantic>=2.12.2              # Data validation

# LLM Integration
google-genai>=1.46.0          # Google Gemini API (recommended)

# Database
sqlalchemy>=2.0.23            # ORM
psycopg2-binary>=2.9.9        # PostgreSQL driver
alembic>=1.13.1               # Database migrations

# Utilities
python-dotenv>=1.1.1          # Environment variables
rich>=13.9.4                  # Terminal output
typing-extensions>=4.15.0     # Type hints
requests>=2.32.5              # HTTP client

# Development
pytest>=7.4.4                 # Testing framework
pytest-asyncio>=0.23.3        # Async testing
black>=23.12.1                # Code formatting
flake8>=7.0.0                 # Linting
mypy>=1.8.0                   # Type checking
```

#### Dependency Graph
```mermaid
graph TD
    APP[Application Code]
    FAST[FastAPI]
    UVI[Uvicorn]
    PYD[Pydantic]
    GEMINI[google-genai]
    SQL[SQLAlchemy]
    PSY[psycopg2]

    APP --> FAST
    APP --> PYD
    APP --> GEMINI
    APP --> SQL
    FAST --> PYD
    FAST --> UVI
    SQL --> PSY

    style APP fill:#4ecdc4
    style FAST fill:#009688
    style GEMINI fill:#ffd93d
```

---

### Frontend Dependencies (JavaScript)

#### Core Dependencies
```json
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2",
    "ws": "^8.16.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

#### Build Tool Chain
```mermaid
graph LR
    SRC[src/*.jsx] --> VITE[Vite]
    VITE --> BUNDLE[dist/assets]
    BUNDLE --> NGINX[Nginx Server]

    style VITE fill:#646cff
    style NGINX fill:#009639
```

---

## Build System

### Backend Build Process

#### Development Build
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python backend/cli.py

# Or run API server
python backend/run_api.py --reload
```

#### Production Build
```bash
# Build Docker image
docker build -t hivemind-backend:latest -f backend/Dockerfile .

# Run container
docker run -p 8000:8000 --env-file .env hivemind-backend:latest
```

#### Docker Multi-Stage Build
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/src ./src
COPY backend/cli.py .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Run application
CMD ["python", "cli.py"]
```

---

### Frontend Build Process

#### Development Build
```bash
cd frontend
npm install
npm run dev
```

#### Production Build
```bash
cd frontend
npm run build

# Output: frontend/dist/
# - index.html
# - assets/*.js
# - assets/*.css
```

#### Docker Build
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

### Docker Compose Orchestration

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8002:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://hivemind:password@db:5432/hivemind
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3002:80"
    depends_on:
      - backend

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=hivemind
      - POSTGRES_USER=hivemind
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hivemind"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  default:
    name: hivemind-network
```

#### Build Commands
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Development Workflow

### Local Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd tutorial_hive_mind

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# 5. Initialize database (if using)
python -c "from backend.src.db.database import init_db; init_db()"

# 6. Run backend
python backend/cli.py

# 7. In separate terminal, run frontend
cd frontend
npm install
npm run dev
```

---

### Git Workflow

#### Branch Strategy
```
main (production-ready)
  ├── develop (integration branch)
      ├── feature/agent-improvements
      ├── feature/new-consensus-strategy
      ├── bugfix/api-error-handling
      └── hotfix/critical-bug
```

#### Commit Conventions
```bash
# Format: <type>(<scope>): <subject>

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style (formatting, etc.)
refactor: Code refactoring
test:     Adding tests
chore:    Maintenance tasks

# Examples:
git commit -m "feat(agents): Add SecuritySpecialistAgent"
git commit -m "fix(consensus): Correct weighted voting calculation"
git commit -m "docs(architecture): Update logical view"
```

---

### Code Review Process

```mermaid
graph LR
    A[Create Branch] --> B[Develop Feature]
    B --> C[Write Tests]
    C --> D[Run Linters]
    D --> E{Pass?}
    E -->|No| B
    E -->|Yes| F[Create PR]
    F --> G[Code Review]
    G --> H{Approved?}
    H -->|No| B
    H -->|Yes| I[Merge to Develop]
    I --> J[CI/CD Pipeline]
```

---

## Code Standards

### Python Code Standards (PEP 8)

#### Formatting with Black
```bash
# Format all Python files
black backend/src/

# Check formatting
black --check backend/src/
```

#### Linting with Flake8
```bash
# Run linter
flake8 backend/src/

# Configuration in .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
ignore = E203,W503
```

#### Type Checking with MyPy
```bash
# Run type checker
mypy backend/src/

# Configuration in mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

### Code Style Guidelines

#### Naming Conventions
```python
# Classes: PascalCase
class ProductManagerAgent(BaseAgent):
    pass

# Functions/Methods: snake_case
def execute_hierarchical_flow(business_need: str) -> List[AgentResponse]:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# Private methods: _leading_underscore
def _build_prompt(self, context: Dict) -> str:
    pass
```

#### Documentation Standards
```python
def process(
    self,
    input_data: str,
    context: Optional[Dict[str, Any]] = None
) -> AgentResponse:
    """
    Process input and generate agent response.

    Args:
        input_data: The business need description to analyze.
        context: Optional contextual information including:
            - previous_responses: List of prior agent responses
            - methodology: Selected agile methodology
            - phase: Current execution phase

    Returns:
        AgentResponse: Structured response containing:
            - content: Analysis text
            - confidence: Confidence score (0.0-1.0)
            - metadata: Additional context

    Raises:
        ValueError: If input_data is empty
        APIError: If Gemini API call fails

    Example:
        >>> agent = ProductManagerAgent(gemini_client)
        >>> response = agent.process("Build e-commerce platform")
        >>> print(response.confidence)
        0.89
    """
```

---

### JavaScript/React Code Standards

#### ESLint Configuration
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "no-unused-vars": "warn",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

#### Component Structure
```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * AgentContentView displays the content from a single agent response.
 *
 * @param {Object} props - Component props
 * @param {string} props.agentName - Name of the agent
 * @param {string} props.content - Agent response content
 * @param {number} props.confidence - Confidence score (0-1)
 */
const AgentContentView = ({ agentName, content, confidence }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="agent-content-view">
      <h3>{agentName}</h3>
      <div className="confidence-score">
        Confidence: {(confidence * 100).toFixed(1)}%
      </div>
      <div className={`content ${expanded ? 'expanded' : 'collapsed'}`}>
        {content}
      </div>
      <button onClick={() => setExpanded(!expanded)}>
        {expanded ? 'Show Less' : 'Show More'}
      </button>
    </div>
  );
};

AgentContentView.propTypes = {
  agentName: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  confidence: PropTypes.number.isRequired
};

export default AgentContentView;
```

---

## Testing Strategy

### Backend Testing

#### Unit Tests Structure
```
backend/
└── tests/
    ├── __init__.py
    ├── test_agents/
    │   ├── test_base_agent.py
    │   ├── test_worker_agents.py
    │   ├── test_coordinator.py
    │   └── test_supervisor.py
    ├── test_hivemind/
    │   ├── test_architecture.py
    │   ├── test_communication.py
    │   ├── test_consensus.py
    │   └── test_hierarchical_flow.py
    └── test_utils/
        ├── test_config.py
        └── test_gemini_client.py
```

#### Example Unit Test
```python
# tests/test_agents/test_base_agent.py
import pytest
from agents.base_agent import BaseAgent, AgentResponse
from utils.gemini_client import GeminiClient

class TestAgent(BaseAgent):
    """Concrete implementation for testing."""
    def get_system_prompt(self) -> str:
        return "Test agent prompt"

    def process(self, input_data, context=None):
        return self._create_response(
            content="Test response",
            confidence=0.85
        )

def test_agent_initialization():
    """Test agent initialization."""
    client = GeminiClient(api_key="test_key")
    agent = TestAgent("TestAgent", "Test Role", client)

    assert agent.name == "TestAgent"
    assert agent.role == "Test Role"
    assert agent.gemini_client == client

def test_agent_process():
    """Test agent processing."""
    client = GeminiClient(api_key="test_key")
    agent = TestAgent("TestAgent", "Test Role", client)

    response = agent.process("test input")

    assert isinstance(response, AgentResponse)
    assert response.agent_name == "TestAgent"
    assert response.confidence == 0.85
    assert response.content == "Test response"

def test_extract_confidence():
    """Test confidence extraction."""
    client = GeminiClient(api_key="test_key")
    agent = TestAgent("TestAgent", "Test Role", client)

    # Test short response
    short_confidence = agent._extract_confidence("short")
    assert short_confidence >= 0.5

    # Test long response
    long_text = "x" * 1500
    long_confidence = agent._extract_confidence(long_text)
    assert long_confidence > short_confidence
```

#### Integration Tests
```python
# tests/test_integration/test_full_flow.py
import pytest
from hivemind.architecture import HiveMindArchitecture
from utils.gemini_client import GeminiClient
from utils.config import Config

@pytest.mark.integration
def test_complete_execution_flow():
    """Test complete HiveMind execution flow."""
    config = Config()
    gemini_client = GeminiClient(
        api_key=config.get_api_key(),
        model_name="gemini-pro"
    )

    hivemind = HiveMindArchitecture(gemini_client)

    business_need = "Build a simple task management web application"
    result = hivemind.execute(business_need, verbose=False)

    # Verify result structure
    assert result.worker_responses is not None
    assert len(result.worker_responses) == 6
    assert result.coordinator_response is not None
    assert result.supervisor_response is not None
    assert result.consensus_result is not None

    # Verify consensus
    assert result.consensus_result.achieved is True
    assert result.consensus_result.consensus_level > 0.7

    # Verify execution metadata
    assert result.execution_time > 0
    assert result.metadata["worker_count"] == 6
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/src --cov-report=html

# Run specific test file
pytest tests/test_agents/test_base_agent.py

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v

# Run fast tests (skip integration)
pytest -m "not integration"
```

---

### Frontend Testing

#### Component Testing with React Testing Library
```jsx
// src/components/__tests__/AgentContentView.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AgentContentView from '../AgentContentView';

describe('AgentContentView', () => {
  const mockProps = {
    agentName: 'ProductManager',
    content: 'Test content for product manager analysis',
    confidence: 0.89
  };

  it('renders agent name and confidence', () => {
    render(<AgentContentView {...mockProps} />);

    expect(screen.getByText('ProductManager')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 89.0%')).toBeInTheDocument();
  });

  it('toggles content expansion on button click', () => {
    render(<AgentContentView {...mockProps} />);

    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Show More');

    fireEvent.click(button);
    expect(button).toHaveTextContent('Show Less');

    fireEvent.click(button);
    expect(button).toHaveTextContent('Show More');
  });
});
```

---

## Configuration Management

### Environment Variables

```bash
# .env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional - Gemini Configuration
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=8192

# Optional - Database
DATABASE_URL=postgresql://hivemind:password@localhost:5432/hivemind

# Optional - API Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Optional - Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration Class
```python
# backend/src/utils/config.py
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Application configuration."""

    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)

        # Required settings
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

        # Gemini settings
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        self.gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.gemini_max_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))

        # Database settings
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")

        # API settings
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))
        self.api_reload: bool = os.getenv("API_RELOAD", "false").lower() == "true"

        # Logging settings
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = os.getenv("LOG_FORMAT", "text")

    def get_api_key(self) -> str:
        """Get Gemini API key, raise if not set."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        return self.gemini_api_key

    def validate(self):
        """Validate configuration."""
        required = ["gemini_api_key"]
        missing = [key for key in required if not getattr(self, key)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
```

---

## Development Tools

### IDE Configuration

#### VS Code Settings
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm Settings
- Enable PEP 8 inspections
- Configure Black as external tool
- Set line length to 100
- Enable pytest as test runner

---

## Continuous Integration (Future)

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run linters
        run: |
          black --check backend/src
          flake8 backend/src
          mypy backend/src
      - name: Run tests
        run: |
          pytest --cov=backend/src
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run linters
        run: |
          cd frontend
          npm run lint
      - name: Run tests
        run: |
          cd frontend
          npm test
      - name: Build
        run: |
          cd frontend
          npm run build

  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker-compose build
      - name: Run Docker Compose
        run: |
          docker-compose up -d
          sleep 10
          docker-compose ps
          docker-compose down
```

---

## References

- Clean Code (Robert C. Martin)
- The Pragmatic Programmer (Hunt & Thomas)
- Python PEP 8 Style Guide
- React Best Practices
- Docker Best Practices

---

**Next**: [Physical View →](./physical-view.md)
