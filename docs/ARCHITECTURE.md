# HiveMind Architecture Documentation

## Documento de Arquitectura - Modelo 4+1 Vistas

Este documento describe la arquitectura del sistema HiveMind utilizando el **modelo de vistas arquitectónicas 4+1**, desarrollado por Philippe Kruchten. Este modelo proporciona múltiples vistas complementarias de una arquitectura de software, permitiendo a diferentes stakeholders (desarrolladores, arquitectos, gerentes de proyecto) entender el sistema desde diferentes perspectivas.

### Propósito del Documento

Este documento tiene como objetivo:
- Proporcionar una descripción completa y académica de la arquitectura HiveMind
- Servir como material de referencia para el aprendizaje de arquitecturas multi-agente AI
- Documentar decisiones de diseño y patrones arquitectónicos aplicados
- Facilitar la comprensión del sistema a diferentes niveles de abstracción

---

## Tabla de Contenidos

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Vista Lógica](#1-vista-lógica-logical-view)
3. [Vista de Proceso](#2-vista-de-proceso-process-view)
4. [Vista Física](#3-vista-física-physical-view)
5. [Vista de Desarrollo](#4-vista-de-desarrollo-development-view)
6. [Vista de Casos de Uso (+1)](#5-vista-de-casos-de-uso-use-case-view)
7. [Patrones Arquitectónicos](#patrones-arquitectónicos)
8. [Componentes del Sistema](#componentes-del-sistema)
9. [Mecanismos de Consenso](#mecanismos-de-consenso)
10. [Protocolo de Comunicación A2A](#protocolo-de-comunicación-a2a)
11. [Decisiones de Diseño](#decisiones-de-diseño)

---

## Visión General del Sistema

HiveMind es un **sistema multi-agente de inteligencia artificial** diseñado para transformar necesidades de negocio en requisitos técnicos y funcionales completos, siguiendo las mejores prácticas de SDLC Ágil (Software Development Life Cycle). El sistema implementa una **arquitectura jerárquica de consenso a tres niveles**, donde múltiples agentes especializados colaboran para producir documentación lista para desarrollo.

### Características Principales

- **Arquitectura Multi-Agente Jerárquica**: Tres niveles de agentes (Workers, Coordinator, Supervisor)
- **Flujo de Ejecución Jerárquico**: Ejecución secuencial siguiendo mejores prácticas de Product Management
- **Soporte Multi-Metodología**: Adaptación automática a Scrum, SAFe y Kanban
- **Protocolo A2A (Agent-to-Agent)**: Comunicación estandarizada entre agentes
- **Mecanismos de Consenso**: Múltiples estrategias para alcanzar acuerdo entre agentes
- **Integración con LLM**: Utilización de Google Gemini API para generación de contenido
- **Persistencia de Datos**: Almacenamiento en PostgreSQL con trazabilidad completa
- **Interfaces Múltiples**: CLI, REST API y Frontend Web (React)

### Arquitectura Jerárquica de Tres Niveles

```
┌─────────────────────────────────────────────────────────────┐
│                     SUPERVISOR AGENT                         │
│              (Nivel 3 - Decisión Final)                      │
│          Genera Documento de Requisitos Técnicos             │
│              Confianza: 0.95 (Autoridad Máxima)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Síntesis y Validación
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   COORDINATOR AGENT                          │
│              (Nivel 2 - Integración)                         │
│         Sintetiza y Resuelve Conflictos                      │
│         Aplica Mecanismo de Consenso                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Agrega                      Consenso
         │                               │
┌────────▼─────────────────────────────────────────────────────┐
│                    WORKER AGENTS                             │
│                 (Nivel 1 - Especialistas)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Product    │  │   Product    │  │    UX/UI     │      │
│  │   Manager    │  │    Owner     │  │   Designer   │      │
│  │              │  │              │  │              │      │
│  │ Business     │  │ User Stories │  │ User         │      │
│  │ Analysis     │  │ & Backlog    │  │ Experience   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Scrum     │  │  Technical   │  │      QA      │      │
│  │   Master     │  │     Lead     │  │  Specialist  │      │
│  │              │  │              │  │              │      │
│  │ Process &    │  │ Architecture │  │ Quality      │      │
│  │ Risk Mgmt    │  │ & Tech Stack │  │ Strategy     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## 1. Vista Lógica (Logical View)

La **Vista Lógica** describe la funcionalidad del sistema en términos de componentes de software y sus relaciones. Esta vista es relevante para desarrolladores y arquitectos de software.

### 1.1 Descomposición Funcional

El sistema HiveMind se estructura en las siguientes capas lógicas:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INTERFACES                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   CLI       │  │  REST API   │  │  Frontend   │        │
│  │   (Python)  │  │  (FastAPI)  │  │  (React)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE ORQUESTACIÓN                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         HiveMindArchitecture                        │   │
│  │  • Orquesta ejecución jerárquica                   │   │
│  │  • Gestiona ciclo de vida de agentes               │   │
│  │  • Coordina comunicación entre niveles             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  CAPA DE AGENTES│            │ CAPA DE SERVICIOS│
│                 │            │                 │
│ • Worker Agents │            │ • Communication │
│   (6 especial.) │            │   Bus           │
│ • Coordinator   │            │ • Consensus     │
│   Agent         │            │   Manager       │
│ • Supervisor    │            │ • Methodology   │
│   Agent         │            │   Factory       │
└─────────────────┘            └─────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE INFRAESTRUCTURA                    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Gemini    │  │ PostgreSQL  │  │ File System │        │
│  │   Client    │  │  Database   │  │  Storage    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Componentes Principales

#### 1.2.1 HiveMindArchitecture

**Responsabilidad**: Orquestador principal que coordina la ejecución de los tres niveles de agentes.

**Interfaces**:
- `execute(business_need: str) -> HiveMindResult`: Ejecuta el proceso completo
- `get_communication_statistics() -> Dict`: Obtiene estadísticas de comunicación
- `export_communication_log() -> str`: Exporta log de comunicación

**Dependencias**:
- `GeminiClient`: Para comunicación con LLM
- `CommunicationBus`: Para mensajería entre agentes
- `ConsensusManager`: Para aplicación de mecanismos de consenso
- `HierarchicalExecutionFlow`: Para ejecución secuencial de workers

#### 1.2.2 Capa de Agentes

**BaseAgent (Clase Abstracta)**:
- Define interfaz común para todos los agentes
- Gestiona comunicación con Gemini API
- Proporciona logging y manejo de errores
- Adapta prompts según metodología seleccionada

**Worker Agents (6 especialistas)**:
1. **ProductManagerAgent**: Análisis de viabilidad empresarial, KPIs, stakeholders
2. **ProductOwnerAgent**: User stories, backlog, criterios INVEST
3. **UXUIAgent**: Journey maps, wireframes, design system, accesibilidad
4. **TechnicalLeadAgent**: Arquitectura C4, tech stack, NFRs, patrones
5. **ScrumMasterAgent**: Ceremonias, RAID, Definition of Ready, releases
6. **QASpecialistAgent**: Test strategy, coverage, automation, quality gates

**CoordinatorAgent**:
- Sintetiza outputs de los 6 workers
- Identifica y resuelve conflictos
- Aplica mecanismo de consenso
- Genera vista integrada

**SupervisorAgent**:
- Evalúa síntesis del coordinator
- Valida completitud y viabilidad
- Toma decisiones finales
- Genera documento de requisitos técnicos

#### 1.2.3 Capa de Servicios

**CommunicationBus**:
- Routing de mensajes entre agentes
- Historial de mensajes
- Logging y analytics
- Soporte para protocolo A2A

**ConsensusManager**:
- Aplica estrategias de consenso (Weighted Voting, Majority, etc.)
- Evalúa acuerdo entre agentes
- Maneja desacuerdos

**MethodologyFactory**:
- Crea contextos específicos por metodología
- Mapea roles y artefactos
- Proporciona adaptación metodológica

**HierarchicalExecutionFlow**:
- Gestiona ejecución secuencial de workers
- Valida dependencias entre fases
- Preserva contexto entre fases

#### 1.2.4 Capa de Infraestructura

**GeminiClient**:
- Wrapper para Google Gemini API
- Manejo de rate limiting y retry
- Gestión de tokens y costos

**Database (PostgreSQL)**:
- Persistencia de análisis y resultados
- Historial de ejecuciones
- Trazabilidad completa

**PersistenceService**:
- Abstracción para operaciones de BD
- CRUD de análisis y respuestas de agentes
- Queries y filtros

### 1.3 Relaciones entre Componentes

```
HiveMindArchitecture
    │
    ├───► Worker Agents (6) ──► GeminiClient
    │         │
    │         └───► CommunicationBus
    │
    ├───► CoordinatorAgent ──► GeminiClient
    │         │
    │         ├───► ConsensusManager
    │         └───► CommunicationBus
    │
    ├───► SupervisorAgent ──► GeminiClient
    │         │
    │         └───► CommunicationBus
    │
    ├───► CommunicationBus ──► Message Log
    │
    └───► PersistenceService ──► PostgreSQL Database
```

---

## 2. Vista de Proceso (Process View)

La **Vista de Proceso** describe el comportamiento dinámico del sistema, mostrando cómo los componentes interactúan durante la ejecución. Esta vista es relevante para entender el flujo de trabajo y la concurrencia.

### 2.1 Flujo de Ejecución Principal

```
┌─────────────────────────────────────────────────────────────┐
│                    INICIO DEL PROCESO                       │
│                                                             │
│  1. Usuario proporciona:                                    │
│     • Business Need (descripción del negocio)              │
│     • Metodología (Scrum/SAFe/Kanban)                      │
│     • Estrategia de Consenso                               │
│                                                             │
│  2. Sistema inicializa:                                     │
│     • Carga configuración                                   │
│     • Inicializa Gemini Client                              │
│     • Crea contexto metodológico                            │
│     • Configura CommunicationBus                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          FASE 1: ANÁLISIS JERÁRQUICO DE WORKERS             │
│              (Ejecución Secuencial con Dependencias)        │
│                                                             │
│  Step 1: Business Foundation                                │
│  ├─> ProductManager.process()                              │
│  │   • Input: Business Need + Methodology Context          │
│  │   • Output: Business Analysis + Confidence              │
│  │   • Dependencias: Ninguna (fase inicial)                │
│  │                                                         │
│  Step 2: Product Definition                                 │
│  ├─> ProductOwner.process()                                │
│  │   • Input: Business Need + PM Output                    │
│  │   • Output: User Stories + Backlog                      │
│  │   • Dependencias: Step 1                                │
│  │                                                         │
│  Step 3: User Experience                                    │
│  ├─> UXUI_Designer.process()                               │
│  │   • Input: Business Need + PO Output                    │
│  │   • Output: UX Design + Wireframes                      │
│  │   • Dependencias: Step 2                                │
│  │                                                         │
│  Step 4: Technical Foundation                               │
│  ├─> TechnicalLead.process()                               │
│  │   • Input: Business Need + UX Output                    │
│  │   • Output: Architecture + Tech Stack                   │
│  │   • Dependencias: Step 3                                │
│  │                                                         │
│  Step 5: Process Optimization                               │
│  ├─> ScrumMaster.process()                                 │
│  │   • Input: Business Need + Tech Lead Output             │
│  │   • Output: Process + Risk Analysis                     │
│  │   • Dependencias: Step 4                                │
│  │                                                         │
│  Step 6: Quality Assurance                                  │
│  ├─> QA_Specialist.process()                               │
│  │   • Input: Business Need + SM Output                    │
│  │   • Output: Quality Strategy + Test Plan                │
│  │   • Dependencias: Step 5                                │
│                                                             │
│  Output: 6 Respuestas de Workers con Contexto Preservado   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          FASE 2: SÍNTESIS Y COORDINACIÓN                    │
│                                                             │
│  Coordinator.process()                                      │
│  ├─> Input: Business Need + 6 Worker Responses             │
│  ├─> Actividades:                                          │
│  │   • Identifica sinergias entre análisis                │
│  │   • Detecta conflictos e inconsistencias               │
│  │   • Resuelve conflictos usando metodología             │
│  │   • Crea síntesis integrada                            │
│  ├─> ConsensusManager.apply_consensus()                    │
│  │   • Aplica estrategia de consenso                      │
│  │   • Calcula nivel de acuerdo                           │
│  │   • Genera justificación                               │
│  └─> Output: Integrated Synthesis + Consensus Result       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          FASE 3: DECISIÓN FINAL Y DOCUMENTACIÓN             │
│                                                             │
│  Supervisor.process()                                       │
│  ├─> Input: Business Need + Coordinator Synthesis          │
│  ├─> Actividades:                                          │
│  │   • Evalúa síntesis del coordinator                    │
│  │   • Valida completitud y viabilidad                    │
│  │   • Toma decisiones finales                            │
│  │   • Genera documento de requisitos técnicos            │
│  │   • Aplica formato metodológico                        │
│  └─> Output: Final Technical Requirements Document         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENCIA Y RESPUESTA                 │
│                                                             │
│  PersistenceService.save_analysis()                         │
│  ├─> Guarda análisis en PostgreSQL                         │
│  ├─> Guarda respuestas de todos los agentes                │
│  ├─> Guarda log de comunicación                            │
│  └─> Genera ID único del análisis                          │
│                                                             │
│  Sistema retorna:                                           │
│  • HiveMindResult con todos los outputs                    │
│  • Communication Log completo                              │
│  • Metadata de ejecución                                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Comunicación A2A

Durante la ejecución, todos los agentes comunican a través del protocolo A2A:

```
System ──REQUEST──> Worker Agent
    │
    ├─> Message Type: REQUEST
    ├─> Content: Business Need + Methodology Context
    ├─> Priority: MEDIUM
    └─> Metadata: Agent-specific instructions

Worker Agent ──RESPONSE──> CommunicationBus
    │
    ├─> Message Type: RESPONSE
    ├─> Content: Analysis + Confidence Score
    ├─> Priority: MEDIUM
    └─> Metadata: Analysis type, methodology, timestamp

CommunicationBus ──LOG──> Message History
    │
    └─> Preserva para trazabilidad

System ──REQUEST──> Coordinator
    │
    ├─> Message Type: REQUEST
    ├─> Content: All worker responses + synthesis request
    ├─> Priority: HIGH
    └─> Metadata: Consensus requirements

Coordinator ──RESPONSE──> CommunicationBus
    │
    ├─> Message Type: RESPONSE
    ├─> Content: Integrated synthesis + consensus result
    ├─> Priority: HIGH
    └─> Metadata: Synthesis type, conflicts resolved

System ──REQUEST──> Supervisor
    │
    ├─> Message Type: REQUEST
    ├─> Content: Coordinator synthesis + finalization req
    ├─> Priority: HIGH
    └─> Metadata: Final authority requirements

Supervisor ──RESPONSE──> CommunicationBus
    │
    ├─> Message Type: RESPONSE
    ├─> Content: Final requirements document
    ├─> Priority: HIGH
    └─> Metadata: Document type, status: final
```

### 2.3 Preservación de Contexto

El sistema mantiene **contexto completo** en cada nivel:

**Nivel 1 (Workers)**:
- Cada worker recibe: Business Need + Methodology Context + Dependencias
- Output incluye: Análisis + Confidence + Metadata

**Nivel 2 (Coordinator)**:
- Recibe: Business Need + 6 Worker Responses (completos)
- Output incluye: Synthesis + Consensus Result + Conflicts Resolved

**Nivel 3 (Supervisor)**:
- Recibe: Business Need + Coordinator Synthesis + Consensus Results
- Output incluye: Final Document + Executive Summary + Recommendations

---

## 3. Vista Física (Physical View)

La **Vista Física** describe la topología del sistema, el despliegue y la infraestructura. Esta vista es relevante para DevOps y administradores de sistemas.

### 3.1 Arquitectura de Despliegue

El sistema HiveMind se despliega utilizando **Docker Compose**, proporcionando un entorno completo y reproducible:

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE NETWORK                    │
│                    (hivemind-network)                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Frontend Container                         │   │
│  │  • Nginx: Servidor web estático                     │   │
│  │  • React App (build production)                     │   │
│  │  • Puerto: 3002                                     │   │
│  │  • Volúmenes:                                        │   │
│  │    - ./frontend/dist → /usr/share/nginx/html        │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         │ HTTP/WebSocket                     │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Backend API Container                      │   │
│  │  • FastAPI Application                              │   │
│  │  • Uvicorn ASGI Server                              │   │
│  │  • Puerto: 8000 (interno) / 8002 (host)            │   │
│  │  • Variables de entorno:                            │   │
│  │    - GEMINI_API_KEY                                 │   │
│  │    - DATABASE_URL                                   │   │
│  │  • Volúmenes:                                        │   │
│  │    - ./logs → /app/logs                             │   │
│  │    - ./output → /app/output                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│         ┌───────────────┴───────────────┐                  │
│         │                               │                   │
│         ▼                               ▼                   │
│  ┌──────────────┐            ┌──────────────┐             │
│  │  PostgreSQL  │            │  Gemini API  │             │
│  │  Container   │            │  (External)  │             │
│  │              │            │              │             │
│  │  • PostgreSQL│            │  • Google    │             │
│  │    13        │            │    Gemini    │             │
│  │  • Puerto:   │            │    REST API  │             │
│  │    5432      │            │              │             │
│  │  • Database: │            │  • HTTPS     │             │
│  │    hivemind  │            │              │             │
│  │  • Usuario:  │            │              │             │
│  │    hivemind  │            │              │             │
│  └──────────────┘            └──────────────┘             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          CLI Container (Opcional)                   │   │
│  │  • CLI tool para análisis directo                   │   │
│  │  • Mismo código base que API                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Componentes de Infraestructura

#### 3.2.1 Frontend Container

**Tecnología**: Nginx + React (build estático)
**Puerto**: 3002 (host) → 80 (container)
**Origen**: `frontend/Dockerfile`

**Características**:
- Servidor web estático Nginx
- Aplicación React compilada (Vite build)
- Soporte para SPA (Single Page Application)
- Proxy de API configurado en Nginx

#### 3.2.2 Backend API Container

**Tecnología**: Python 3.11 + FastAPI + Uvicorn
**Puerto**: 8000 (container) → 8002 (host)
**Origen**: `backend/Dockerfile`

**Características**:
- Servidor ASGI con Uvicorn
- API REST con FastAPI
- WebSocket para streaming en tiempo real
- Integración con PostgreSQL
- Cliente Gemini para LLM

**Dependencias**:
- PostgreSQL (healthcheck antes de iniciar)
- Variables de entorno desde `.env`

#### 3.2.3 PostgreSQL Container

**Tecnología**: PostgreSQL 13
**Puerto**: 5432 (interno)
**Origen**: `postgres:13-alpine` (imagen oficial)

**Características**:
- Base de datos relacional
- Schemas para análisis y respuestas
- Índices para queries comunes
- Healthcheck para verificar disponibilidad

**Tablas Principales**:
- `analyses`: Análisis completos
- `agent_responses`: Respuestas individuales de agentes

#### 3.2.4 Servicios Externos

**Google Gemini API**:
- Endpoint: `https://generativelanguage.googleapis.com/v1beta`
- Autenticación: API Key
- Protocolo: HTTPS REST
- Rate Limiting: Implementado con exponential backoff

### 3.3 Volúmenes y Persistencia

**Volúmenes Compartidos**:
- `./logs` → `/app/logs`: Logs de aplicación
- `./output` → `/app/output`: Archivos de salida

**Persistencia de Datos**:
- PostgreSQL: Datos persistentes en volumen Docker
- Volumen nombrado: `tutorial_hive_mind_postgres_data`

### 3.4 Red y Comunicación

**Docker Network**: `hivemind-network`
- Red interna para comunicación entre contenedores
- Resolución DNS automática entre servicios
- Aislamiento de red externa

**Puertos Expuestos**:
- `3002`: Frontend (HTTP)
- `8002`: Backend API (HTTP + WebSocket)

---

## 4. Vista de Desarrollo (Development View)

La **Vista de Desarrollo** describe la organización del código, la estructura de módulos y las dependencias. Esta vista es relevante para desarrolladores.

### 4.1 Estructura del Proyecto

```
tutorial_hive_mind/
├── backend/                          # Backend (Python/FastAPI)
│   ├── Dockerfile                    # Imagen Docker para backend
│   ├── .env                          # Variables de entorno
│   ├── requirements.txt              # Dependencias Python
│   └── src/
│       ├── __init__.py
│       ├── main.py                   # CLI Entry Point
│       ├── agents/                   # Implementación de Agentes
│       │   ├── __init__.py
│       │   ├── base_agent.py         # Clase Base Abstracta
│       │   ├── worker_agents.py      # 6 Worker Agents
│       │   ├── coordinator_agent.py  # Coordinator Agent
│       │   └── supervisor_agent.py   # Supervisor Agent
│       ├── api/                      # API REST (FastAPI)
│       │   ├── __init__.py
│       │   ├── main.py               # FastAPI App
│       │   ├── endpoints.py          # REST Endpoints
│       │   └── models.py             # Pydantic Models
│       ├── db/                       # Capa de Persistencia
│       │   ├── __init__.py
│       │   ├── database.py           # SQLAlchemy Setup
│       │   ├── models.py             # SQLAlchemy Models
│       │   └── persistence.py        # Persistence Service
│       ├── hivemind/                 # Core Architecture
│       │   ├── __init__.py
│       │   ├── architecture.py       # HiveMindArchitecture
│       │   ├── communication.py      # A2A Protocol
│       │   ├── consensus.py          # Consensus Mechanisms
│       │   ├── methodology.py        # Methodology Support
│       │   └── hierarchical_flow.py  # Hierarchical Execution
│       └── utils/                    # Utilidades
│           ├── __init__.py
│           ├── config.py             # Configuration Management
│           └── gemini_client.py      # Gemini API Client
│
├── frontend/                         # Frontend (React/Vite)
│   ├── Dockerfile                    # Imagen Docker para frontend
│   ├── package.json                  # Dependencias NPM
│   ├── vite.config.js                # Configuración Vite
│   ├── index.html                    # HTML Entry Point
│   ├── styles*.css                   # Estilos CSS
│   └── src/
│       ├── main.jsx                  # React Entry Point
│       ├── App.jsx                   # Componente Principal
│       ├── api/                      # API Client
│       │   └── client.js             # Axios + WebSocket
│       ├── components/               # Componentes React
│       │   ├── AgentContentView.jsx
│       │   ├── DashboardExecutive.jsx
│       │   ├── ResultSummary.jsx
│       │   ├── SpecializedAgentsTabs.jsx
│       │   └── ...
│       ├── context/                  # Context API
│       │   └── AppContext.jsx        # Global State
│       └── pages/                    # Páginas
│           ├── Dashboard.jsx
│           ├── Analyze.jsx
│           └── History.jsx
│
├── docs/                             # Documentación
│   ├── ARCHITECTURE.md               # Este documento
│   ├── API_REFERENCE.md              # Referencia de API
│   └── TUTORIAL.md                   # Tutorial de uso
│
├── docker-compose.yml                # Orquestación Docker
└── README.md                         # Documentación principal
```

### 4.2 Módulos Principales

#### 4.2.1 Módulo `hivemind/architecture.py`

**Responsabilidad**: Orquestación principal del sistema

**Clases Principales**:
- `HiveMindArchitecture`: Clase principal de orquestación
- `HiveMindResult`: Modelo de resultado completo

**Dependencias**:
- `agents.*`: Todos los tipos de agentes
- `hivemind.communication`: CommunicationBus
- `hivemind.consensus`: ConsensusManager
- `hivemind.methodology`: MethodologyFactory
- `hivemind.hierarchical_flow`: HierarchicalExecutionFlow
- `utils.gemini_client`: GeminiClient

#### 4.2.2 Módulo `agents/`

**Responsabilidad**: Implementación de todos los agentes

**Jerarquía de Clases**:
```
BaseAgent (Abstract)
    │
    ├─── Worker Agents
    │     ├── ProductManagerAgent
    │     ├── ProductOwnerAgent
    │     ├── UXUIAgent
    │     ├── TechnicalLeadAgent
    │     ├── ScrumMasterAgent
    │     └── QASpecialistAgent
    │
    ├─── CoordinatorAgent
    └─── SupervisorAgent
```

**Características Comunes** (heredadas de BaseAgent):
- `process(input_data, context) -> AgentResponse`
- `get_system_prompt() -> str`
- `get_adapted_system_prompt() -> str` (metodología-aware)
- `_call_gemini(prompt, system_instruction) -> str`
- `_extract_confidence(response_text) -> float`

#### 4.2.3 Módulo `hivemind/communication.py`

**Responsabilidad**: Protocolo A2A y comunicación entre agentes

**Clases Principales**:
- `CommunicationBus`: Bus de mensajería
- `A2AMessage`: Modelo de mensaje (Pydantic)
- `MessageType`: Enum (REQUEST, RESPONSE, NOTIFICATION, ERROR)
- `MessagePriority`: Enum (HIGH, MEDIUM, LOW)

**Características**:
- Message routing
- Message history
- Thread tracking (parent-child relationships)
- Statistics and analytics

#### 4.2.4 Módulo `hivemind/consensus.py`

**Responsabilidad**: Mecanismos de consenso

**Clases Principales**:
- `ConsensusManager`: Gestiona aplicación de consenso
- `ConsensusStrategy`: Enum (WEIGHTED_VOTING, MAJORITY, UNANIMOUS, CONFIDENCE_THRESHOLD)
- `ConsensusResult`: Modelo de resultado (Pydantic)

#### 4.2.5 Módulo `hivemind/methodology.py`

**Responsabilidad**: Soporte multi-metodología

**Clases Principales**:
- `AgileMethodology`: Enum (SCRUM, SAFE, KANBAN)
- `MethodologyContext`: Dataclass con contexto metodológico
- `MethodologyFactory`: Factory para crear contextos
- `MethodologyAdapter`: Adapta prompts y outputs

#### 4.2.6 Módulo `hivemind/hierarchical_flow.py`

**Responsabilidad**: Ejecución jerárquica de workers

**Clases Principales**:
- `HierarchicalExecutionFlow`: Gestiona flujo secuencial
- Define orden de ejecución según dependencias
- Valida quality gates entre fases
- Preserva contexto entre fases

#### 4.2.7 Módulo `api/`

**Responsabilidad**: API REST y WebSocket

**Endpoints Principales**:
- `POST /api/v1/analyze`: Análisis REST (síncrono)
- `WebSocket /api/v1/ws/analyze`: Análisis streaming (asíncrono)
- `GET /api/v1/history`: Historial de análisis
- `GET /api/v1/analyses/{id}`: Análisis específico
- `GET /api/v1/health`: Health check
- `GET /api/v1/info`: Información del sistema

**Modelos**:
- `BusinessNeedRequest`: Request model
- `HiveMindResponseModel`: Response model
- `ErrorResponseModel`: Error model

#### 4.2.8 Módulo `db/`

**Responsabilidad**: Persistencia de datos

**Modelos SQLAlchemy**:
- `Analysis`: Modelo de análisis completo
- `AgentResponse`: Modelo de respuesta de agente

**Servicios**:
- `PersistenceService`: Abstracción para operaciones de BD
- `init_db()`: Inicialización de base de datos
- `get_db()`: Dependency injection para FastAPI

### 4.3 Dependencias Externas

**Python (Backend)**:
- `fastapi`: Framework web
- `uvicorn`: Servidor ASGI
- `sqlalchemy`: ORM
- `alembic`: Migrations (futuro)
- `google-genai`: Cliente Gemini
- `pydantic`: Validación de datos
- `python-dotenv`: Gestión de variables de entorno

**JavaScript (Frontend)**:
- `react`: Framework UI
- `react-dom`: DOM rendering
- `vite`: Build tool
- `axios`: HTTP client
- `websocket`: WebSocket client

**Infraestructura**:
- `docker`: Containerización
- `docker-compose`: Orquestación
- `postgres:13-alpine`: Base de datos
- `nginx:alpine`: Servidor web

---

## 5. Vista de Casos de Uso (Use Case View)

La **Vista de Casos de Uso** describe las interacciones entre usuarios y el sistema. Esta vista es relevante para product managers y stakeholders.

### 5.1 Actores Principales

**Usuario Final**:
- Product Manager
- Business Analyst
- Development Team Lead
- Scrum Master

**Sistema**:
- HiveMind Architecture
- Google Gemini API
- PostgreSQL Database

### 5.2 Casos de Uso Principales

#### CU-1: Ejecutar Análisis desde CLI

**Actor**: Usuario Final
**Precondiciones**: Sistema configurado con API key de Gemini

**Flujo Principal**:
1. Usuario ejecuta: `python src/main.py --business-need "..." --methodology scrum`
2. Sistema inicializa HiveMindArchitecture
3. Sistema ejecuta flujo jerárquico completo
4. Sistema muestra progreso en terminal
5. Sistema guarda resultado en archivo JSON
6. Sistema muestra resumen de resultados

**Flujo Alternativo** (Error):
- Si API key inválida → Error y aborto
- Si análisis falla → Log de error y resultado parcial

**Resultado Esperado**: Archivo JSON con requisitos técnicos completos

#### CU-2: Ejecutar Análisis desde REST API

**Actor**: Usuario Final (aplicación cliente)
**Precondiciones**: API corriendo y accesible

**Flujo Principal**:
1. Cliente envía POST a `/api/v1/analyze` con business_need
2. API valida request
3. API ejecuta análisis (síncrono)
4. API guarda resultado en PostgreSQL
5. API retorna JSON con resultado completo

**Flujo Alternativo** (Error):
- Si request inválido → 422 Unprocessable Entity
- Si análisis falla → 500 Internal Server Error con detalles

**Resultado Esperado**: Response JSON con `HiveMindResponseModel`

#### CU-3: Ejecutar Análisis con Streaming (WebSocket)

**Actor**: Usuario Final (Frontend)
**Precondiciones**: Frontend conectado a API

**Flujo Principal**:
1. Frontend establece conexión WebSocket a `/api/v1/ws/analyze`
2. Frontend envía `{"action": "start", "business_need": "...", ...}`
3. API ejecuta análisis en background
4. API emite mensajes de progreso:
   - `{"type": "progress", "phase": "workers", "agent": "ProductManager", ...}`
   - `{"type": "progress", "phase": "coordinator", ...}`
   - `{"type": "progress", "phase": "supervisor", ...}`
5. Frontend actualiza UI en tiempo real
6. API emite `{"type": "complete", "result": {...}}`
7. Frontend muestra resultado final

**Resultado Esperado**: UI actualizada en tiempo real con progreso y resultado final

#### CU-4: Consultar Historial de Análisis

**Actor**: Usuario Final
**Precondiciones**: Análisis previos guardados en BD

**Flujo Principal**:
1. Usuario accede a `/history` (Frontend) o `GET /api/v1/history` (API)
2. Sistema consulta PostgreSQL
3. Sistema retorna lista de análisis con metadata
4. Usuario puede filtrar por metodología, fecha, etc.
5. Usuario puede ver detalles de análisis específico

**Resultado Esperado**: Lista de análisis históricos con filtros y detalles

#### CU-5: Exportar Resultados

**Actor**: Usuario Final
**Precondiciones**: Análisis completado

**Flujo Principal**:
1. Usuario selecciona análisis
2. Usuario hace clic en "Exportar PDF" o "Descargar JSON"
3. Sistema genera formato solicitado
4. Sistema proporciona archivo descargable

**Resultado Esperado**: Archivo descargable (PDF o JSON)

### 5.3 Diagrama de Casos de Uso

```
┌─────────────────────────────────────────────────────────────┐
│                     ACTORES                                  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Usuario   │  │   Frontend   │  │  CLI Tool    │     │
│  │    Final     │  │   (React)    │  │  (Python)    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               SISTEMA HIVEMIND                      │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │  REST API    │  │  WebSocket   │               │   │
│  │  │  (FastAPI)   │  │  Endpoint    │               │   │
│  │  └──────────────┘  └──────────────┘               │   │
│  │         │                  │                        │   │
│  │         └────────┬─────────┘                        │   │
│  │                  │                                  │   │
│  │                  ▼                                  │   │
│  │  ┌─────────────────────────────────────┐           │   │
│  │  │   HiveMindArchitecture              │           │   │
│  │  │   • Orquestación                    │           │   │
│  │  │   • Gestión de agentes              │           │   │
│  │  │   • Comunicación                    │           │   │
│  │  └─────────────────────────────────────┘           │   │
│  │                  │                                  │   │
│  │         ┌────────┴────────┐                        │   │
│  │         │                 │                        │   │
│  │         ▼                 ▼                        │   │
│  │  ┌──────────┐    ┌──────────────┐                 │   │
│  │  │ Agentes  │    │ Persistence  │                 │   │
│  │  │ (3 Niv.) │    │  Service     │                 │   │
│  │  └──────────┘    └──────────────┘                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                │
│         ┌─────────────────┼─────────────────┐             │
│         │                 │                 │             │
│         ▼                 ▼                 ▼             │
│  ┌──────────┐    ┌──────────────┐  ┌──────────────┐     │
│  │ Gemini   │    │ PostgreSQL   │  │ File System  │     │
│  │ API      │    │  Database    │  │  Storage     │     │
│  └──────────┘    └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Patrones Arquitectónicos

### Patrón HiveMind

El **patrón HiveMind** es una arquitectura multi-agente donde:
- Múltiples agentes especializados trabajan independientemente
- Cada agente aporta una perspectiva única
- Una capa de coordinación sintetiza los outputs
- Una capa de supervisión toma decisiones finales

**Características Clave**:
- **Procesamiento Paralelo** (a nivel de workers, pero secuencial por dependencias)
- **Diversidad de Pensamiento**: Cada agente aporta expertise único
- **Consenso Jerárquico**: Decisión multi-nivel
- **Comunicación Transparente**: Todas las interacciones trazables vía A2A

### Patrón de Flujo Jerárquico

El sistema implementa un **flujo jerárquico** siguiendo mejores prácticas de Product Management:

**Orden de Ejecución**:
1. Business Foundation (ProductManager) - Sin dependencias
2. Product Definition (ProductOwner) - Depende de #1
3. User Experience (UXUI) - Depende de #2
4. Technical Foundation (TechnicalLead) - Depende de #3
5. Process Optimization (ScrumMaster) - Depende de #4
6. Quality Assurance (QA) - Depende de #5

**Quality Gates**:
- Cada fase valida sus dependencias
- Cada fase valida completitud de contexto
- Cada fase genera confidence score
- Sistema valida metodología compliance

### Patrón de Preservación de Contexto

El sistema mantiene **contexto completo** en cada nivel:

**Mecanismos**:
- Message History: Todas las comunicaciones A2A logueadas
- Parent-Child Relationships: Mensajes vinculados para trazabilidad
- Metadata Preservation: Cada mensaje lleva forward todo el contexto relevante
- Methodology Context: Información metodológica propagada en todos los niveles

### Patrón de Consenso Distribuido

El sistema implementa **consenso distribuido**:

**Estrategias**:
- **Weighted Voting**: Votación ponderada por expertise
- **Majority**: Mayoría simple
- **Unanimous**: Unanimidad requerida
- **Confidence Threshold**: Umbral de confianza promedio

**Aplicación**:
- ConsensusManager aplica estrategia seleccionada
- Coordinator genera síntesis basada en consenso
- Supervisor valida consenso antes de decisión final

---

## Componentes del Sistema

### Capa de Agentes

**BaseAgent (Abstract)**:
- Interfaz común para todos los agentes
- Gestiona comunicación con Gemini API
- Proporciona logging y manejo de errores
- Adapta prompts según metodología

**Worker Agents** (6 especialistas):
- ProductManagerAgent: Business analysis, KPIs, stakeholders
- ProductOwnerAgent: User stories, backlog, INVEST criteria
- UXUIAgent: Journey maps, wireframes, design system
- TechnicalLeadAgent: C4 architecture, tech stack, NFRs
- ScrumMasterAgent: Ceremonies, RAID, Definition of Ready
- QASpecialistAgent: Test strategy, coverage, automation

**CoordinatorAgent**:
- Sintetiza outputs de workers
- Resuelve conflictos
- Aplica consenso
- Genera vista integrada

**SupervisorAgent**:
- Evalúa síntesis
- Valida completitud
- Toma decisiones finales
- Genera documento final

### Capa de Servicios

**CommunicationBus**:
- Routing de mensajes
- Historial de mensajes
- Analytics y logging
- Soporte A2A protocol

**ConsensusManager**:
- Aplica estrategias de consenso
- Evalúa acuerdo entre agentes
- Maneja desacuerdos

**MethodologyFactory**:
- Crea contextos metodológicos
- Mapea roles y artefactos
- Proporciona adaptación

**HierarchicalExecutionFlow**:
- Gestiona ejecución secuencial
- Valida dependencias
- Preserva contexto

### Capa de Infraestructura

**GeminiClient**:
- Wrapper para Gemini API
- Rate limiting y retry
- Gestión de tokens

**Database (PostgreSQL)**:
- Persistencia de análisis
- Historial de ejecuciones
- Trazabilidad completa

**PersistenceService**:
- Abstracción para BD
- CRUD operations
- Queries y filtros

---

## Mecanismos de Consenso

### Weighted Voting (Por Defecto)

Cada agente tiene un peso basado en su expertise:

```python
weights = {
    "ProductManager": 1.2,  # Alto peso para decisiones de negocio
    "ProductOwner": 1.1,
    "UXUI_Designer": 1.0,
    "ScrumMaster": 0.9,
    "TechnicalLead": 1.3,   # Alto peso para decisiones técnicas
    "QA_Specialist": 1.0
}

consensus = Σ(confidence_i × weight_i) / Σ(weight_i)
```

### Majority Consensus

Cuenta agentes con confidence > threshold:
```python
agreeing = [agent for agent in agents if agent.confidence >= 0.6]
consensus_achieved = len(agreeing) / len(agents) > 0.5
```

### Confidence Threshold Consensus

Confianza promedio debe exceder umbral:
```python
avg_confidence = mean([agent.confidence for agent in agents])
consensus_achieved = avg_confidence >= 0.75
```

---

## Protocolo de Comunicación A2A

### Estructura de Mensaje A2A

```json
{
  "message_id": "msg_0001",
  "sender": "ProductManager",
  "recipient": "Coordinator",
  "message_type": "response",
  "priority": "high",
  "content": "Analysis complete with high confidence",
  "metadata": {
    "confidence": 0.92,
    "analysis_type": "business"
  },
  "timestamp": "2025-10-26T12:30:45",
  "parent_message_id": "msg_0000"
}
```

### Tipos de Mensaje

- **REQUEST**: Solicitud de acción
- **RESPONSE**: Respuesta a solicitud
- **NOTIFICATION**: Notificación (sin respuesta esperada)
- **ERROR**: Mensaje de error

### Niveles de Prioridad

- **HIGH**: Mensajes críticos (coordinator, supervisor)
- **MEDIUM**: Mensajes normales (workers)
- **LOW**: Mensajes informativos

---

## Decisiones de Diseño

### Por qué Soporte Multi-Metodología?

**Problema**: Organizaciones usan diferentes metodologías (Scrum, SAFe, Kanban) con roles, artefactos y procesos distintos.

**Solución**: Arquitectura methodology-aware que adapta comportamiento, roles y outputs.

**Beneficios**:
- Flexibilidad para trabajar con cualquier metodología
- Terminología y artefactos consistentes por metodología
- Mapeo apropiado de roles y responsabilidades
- Formatos de output específicos por metodología

### Por qué Flujo Jerárquico?

**Problema**: Ejecución paralela de workers sin considerar dependencias y orden lógico.

**Solución**: Ejecución secuencial siguiendo mejores prácticas de Product Management.

**Beneficios**:
- Dependencias explícitas entre fases
- Contexto preservado entre fases
- Quality gates en cada fase
- Alineación con procesos reales de desarrollo

### Por qué Tres Niveles?

**Nivel 1 (Workers)**: Asegura perspectivas diversas y especializadas
**Nivel 2 (Coordinator)**: Sintetiza sin perder matices
**Nivel 3 (Supervisor)**: Proporciona decisión autoritativa y final

**Racional**: Más niveles añadirían complejidad sin valor; menos niveles perderían beneficios de síntesis.

### Por qué API REST + WebSocket?

**REST API**: Para integraciones síncronas y consultas
**WebSocket**: Para streaming en tiempo real y actualizaciones incrementales

**Beneficios**:
- Flexibilidad para diferentes casos de uso
- Mejor UX con actualizaciones en tiempo real
- Compatibilidad con múltiples clientes

### Por qué PostgreSQL?

**Racional**:
- Datos estructurados (análisis, respuestas)
- Relaciones entre entidades (análisis → agent_responses)
- Consultas complejas (historial, filtros)
- ACID compliance para integridad

---

## Consideraciones de Escalabilidad

### Escalado Horizontal

- Añadir más worker agents para nuevas perspectivas
- Particionar workers por dominio
- Paralelizar ejecución de workers en múltiples máquinas

### Escalado Vertical

- Usar modelos más capaces (Gemini Pro → Ultra)
- Aumentar context windows para proyectos grandes
- Añadir caching para análisis repetidos

### Optimizaciones de Performance

- Cache de respuestas de workers para necesidades similares
- Batch API calls cuando sea posible
- Stream responses para feedback más rápido

---

## Seguridad y Privacidad

### Protección de Datos

- API keys almacenadas en variables de entorno
- No hay credenciales hardcodeadas
- Datos sensibles no logueados

### Seguridad de API

- Rate limiting manejado por Gemini SDK
- Retry logic con exponential backoff
- Error handling previene data leaks

---

## Extensiones Futuras

### Potenciales Mejoras

1. **Metodologías Adicionales**: LeSS, Nexus, DAD, Crystal
2. **Validación Metodológica**: Asegurar outputs alineados con mejores prácticas
3. **Soporte Metodología Custom**: Permitir a usuarios definir su propia metodología
4. **Plantillas Metodológicas**: Templates pre-construidos
5. **Refinamiento Iterativo**: Múltiples rondas de consenso
6. **Human-in-the-Loop**: Checkpoints de revisión manual
7. **Sistema de Aprendizaje**: Mejorar desde requisitos pasados
8. **Multi-idioma**: Soporte para inputs no-inglés
9. **Diagramas Visuales**: Auto-generar diagramas de arquitectura
10. **Optimización de Costos**: Selección de modelo basada en presupuesto

---

## Conclusión

La arquitectura HiveMind proporciona un enfoque robusto y escalable para transformar necesidades de negocio en requisitos técnicos a través de colaboración de agentes especializados y consenso jerárquico. El sistema soporta múltiples metodologías ágiles (Scrum, SAFe, Kanban) con adaptación automática de roles, artefactos y outputs.

**Beneficios Clave**:
- Análisis comprehensivo desde múltiples perspectivas
- Output estructurado adaptado a metodología elegida
- Proceso de decisión transparente
- Diseño escalable y extensible
- Comportamiento de agentes methodology-aware
- Selección y adaptación flexible de metodologías
- Terminología y artefactos consistentes por metodología

**Audiencia Objetivo**:
Este documento está diseñado para servir como material de referencia académico para el aprendizaje de arquitecturas multi-agente AI, proporcionando una descripción completa y estructurada siguiendo el modelo de vistas arquitectónicas 4+1.
