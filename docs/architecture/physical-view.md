# Physical View - HiveMind Architecture

## Overview

The **Physical View** describes the system's deployment topology, infrastructure components, and hardware/software mapping. This view addresses **where** the system runs and how components are distributed across physical or virtual infrastructure.

**Target Audience**: DevOps Engineers, System Administrators, Infrastructure Architects, SRE Teams

---

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Container Architecture](#container-architecture)
3. [Network Topology](#network-topology)
4. [Infrastructure Components](#infrastructure-components)
5. [Deployment Strategies](#deployment-strategies)
6. [Scaling and Performance](#scaling-and-performance)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Security Architecture](#security-architecture)
9. [Disaster Recovery](#disaster-recovery)

---

## Deployment Architecture

### High-Level Deployment Topology

```mermaid
graph TB
    subgraph "User Layer"
        USER[End Users<br/>Web Browsers/CLI]
    end

    subgraph "Load Balancing Layer"
        LB[Load Balancer<br/>nginx/HAProxy]
    end

    subgraph "Application Layer"
        FE1[Frontend Container 1<br/>nginx:alpine]
        FE2[Frontend Container 2<br/>nginx:alpine]
        BE1[Backend Container 1<br/>Python 3.11]
        BE2[Backend Container 2<br/>Python 3.11]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL 16<br/>Primary)]
        DBR[(PostgreSQL 16<br/>Replica)]
        CACHE[Redis Cache<br/>Optional]
    end

    subgraph "External Services"
        GEMINI[Google Gemini API<br/>generativelanguage.googleapis.com]
    end

    subgraph "Storage Layer"
        LOGS[Logs Volume<br/>/var/log]
        OUTPUT[Output Volume<br/>/app/output]
    end

    USER -->|HTTPS| LB
    LB -->|HTTP| FE1
    LB -->|HTTP| FE2
    FE1 -->|REST/WS| BE1
    FE2 -->|REST/WS| BE2
    BE1 -->|SQL| DB
    BE2 -->|SQL| DB
    DB -.->|Replication| DBR
    BE1 -->|HTTPS| GEMINI
    BE2 -->|HTTPS| GEMINI
    BE1 --> LOGS
    BE1 --> OUTPUT
    BE1 -.->|Cache| CACHE

    style USER fill:#e1f5ff
    style LB fill:#fff4e1
    style FE1 fill:#e8f5e9
    style BE1 fill:#e8f5e9
    style DB fill:#ffe0e0
    style GEMINI fill:#fff9c4
```

---

## Container Architecture

### Docker Compose Deployment

The system uses Docker Compose for orchestration in development and small-scale production deployments.

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "hivemind-network (Bridge)"
            FRONTEND[frontend<br/>nginx:alpine<br/>Port: 3002:80]
            BACKEND[backend<br/>python:3.11-slim<br/>Port: 8002:8000]
            DB[postgres<br/>postgres:16-alpine<br/>Port: 5432 internal]
        end

        subgraph "Volumes"
            PGDATA[postgres_data<br/>Database persistence]
            LOGS[./logs<br/>Application logs]
            OUTPUT[./output<br/>Generated files]
        end
    end

    subgraph "External"
        GEMINI[Gemini API<br/>HTTPS]
    end

    FRONTEND -.->|HTTP| BACKEND
    BACKEND -->|PostgreSQL| DB
    DB -->|Persist| PGDATA
    BACKEND -->|Write| LOGS
    BACKEND -->|Write| OUTPUT
    BACKEND -->|HTTPS| GEMINI

    style FRONTEND fill:#4ecdc4
    style BACKEND fill:#ff6b6b
    style DB fill:#a8e6cf
    style GEMINI fill:#ffd93d
```

### Container Specifications

#### Frontend Container
```yaml
Service: frontend
Image: hivemind-frontend:latest
Base: nginx:alpine
Ports: 3002 (host) → 80 (container)
Resources:
  Memory: 128 MB
  CPU: 0.25 cores
Volumes:
  - ./frontend/dist:/usr/share/nginx/html:ro
Health Check:
  HTTP GET http://localhost/
  Interval: 30s
  Timeout: 3s
  Retries: 3
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

#### Backend Container
```yaml
Service: backend
Image: hivemind-backend:latest
Base: python:3.11-slim
Ports: 8002 (host) → 8000 (container)
Resources:
  Memory: 512 MB
  CPU: 1.0 cores
Environment:
  - GEMINI_API_KEY
  - DATABASE_URL
  - LOG_LEVEL=INFO
Volumes:
  - ./logs:/app/logs
  - ./output:/app/output
Health Check:
  HTTP GET http://localhost:8000/api/v1/health
  Interval: 30s
  Timeout: 5s
  Retries: 3
Depends On:
  - database (healthy)
```

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/src ./src
COPY backend/cli.py .
COPY backend/run_api.py .

# Create directories
RUN mkdir -p /app/logs /app/output

EXPOSE 8000

CMD ["python", "run_api.py"]
```

---

#### Database Container
```yaml
Service: postgres
Image: postgres:16-alpine
Ports: 5432 (internal only)
Resources:
  Memory: 256 MB
  CPU: 0.5 cores
Environment:
  - POSTGRES_DB=hivemind
  - POSTGRES_USER=hivemind
  - POSTGRES_PASSWORD=<secure_password>
Volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
Health Check:
  pg_isready -U hivemind
  Interval: 10s
  Timeout: 5s
  Retries: 5
```

---

### Complete Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: hivemind-frontend
    ports:
      - "3002:80"
    depends_on:
      - backend
    networks:
      - hivemind-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: hivemind-backend
    ports:
      - "8002:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://hivemind:${DB_PASSWORD}@postgres:5432/hivemind
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - hivemind-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  postgres:
    image: postgres:16-alpine
    container_name: hivemind-db
    environment:
      - POSTGRES_DB=hivemind
      - POSTGRES_USER=hivemind
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/src/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - hivemind-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hivemind"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local

networks:
  hivemind-network:
    driver: bridge
```

### Additional Development Services

The system includes additional Docker services for development, testing, and CLI usage:

#### hivemind-cli (CLI Service)
```yaml
Service: hivemind-cli
Purpose: Command-line interface for direct analysis
Base: Same as backend (python:3.11-slim)
Volumes:
  - ./logs:/app/logs
  - ./output:/app/output
  - ./backend/examples:/app/backend/examples
Profile: cli (requires --profile cli to start)
Command: python backend/cli.py --help
```

**Usage**:
```bash
# Run CLI analysis
docker-compose --profile cli run hivemind-cli python backend/cli.py --input examples/business_need.txt
```

#### hivemind-dev (Development Server)
```yaml
Service: hivemind-dev
Purpose: Development server with hot-reload
Port: 8001:8000
Volumes:
  - .:/app (entire codebase mounted)
  - ./logs:/app/logs
  - ./output:/app/output
Profile: dev (requires --profile dev to start)
Environment:
  - API_RELOAD=true
  - API_LOG_LEVEL=debug
Command: python backend/run_api.py --host 0.0.0.0 --port 8000 --reload
```

**Usage**:
```bash
# Start development server with hot-reload
docker-compose --profile dev up hivemind-dev
```

#### hivemind-test (Testing Service)
```yaml
Service: hivemind-test
Purpose: Automated testing against API
Depends On: hivemind-api
Profile: test (requires --profile test to start)
Command: python backend/test_api.py --url http://hivemind-api:8000
```

**Usage**:
```bash
# Run automated tests
docker-compose --profile test run hivemind-test
```

**Service Profiles Summary**:

| Service | Profile | Purpose | Port | Auto-start |
|---------|---------|---------|------|------------|
| hivemind-frontend | default | Web UI | 3002 | Yes |
| hivemind-api | default | REST API | 8002 | Yes |
| postgres | default | Database | Internal | Yes |
| hivemind-cli | cli | CLI tool | - | No |
| hivemind-dev | dev | Dev server | 8001 | No |
| hivemind-test | test | Testing | - | No |

---

## Network Topology

### Network Architecture

```mermaid
graph TB
    subgraph "External Network (Internet)"
        CLIENT[Client<br/>Browser/CLI]
        GEMINI[Gemini API<br/>443/HTTPS]
    end

    subgraph "DMZ / Load Balancer"
        LB[Load Balancer<br/>80/443]
    end

    subgraph "Application Network (Private)"
        subgraph "Frontend Subnet (10.0.1.0/24)"
            FE[Frontend<br/>10.0.1.10:80]
        end

        subgraph "Backend Subnet (10.0.2.0/24)"
            BE[Backend<br/>10.0.2.10:8000]
        end

        subgraph "Database Subnet (10.0.3.0/24)"
            DB[(Database<br/>10.0.3.10:5432)]
        end
    end

    CLIENT -->|HTTPS/443| LB
    LB -->|HTTP/80| FE
    FE -->|HTTP/8000| BE
    BE -->|PostgreSQL/5432| DB
    BE -->|HTTPS/443| GEMINI

    style CLIENT fill:#e1f5ff
    style LB fill:#fff4e1
    style FE fill:#e8f5e9
    style BE fill:#ffe0e0
    style DB fill:#f3e5f5
    style GEMINI fill:#fff9c4
```

### Port Mappings

| Service | Internal Port | External Port | Protocol | Access |
|---------|--------------|---------------|----------|--------|
| Frontend | 80 | 3002 | HTTP | Public |
| Backend API | 8000 | 8002 | HTTP/WS | Internal |
| PostgreSQL | 5432 | - | PostgreSQL | Internal only |
| Gemini API | - | 443 | HTTPS | External |

### Network Security Groups

```yaml
# Frontend Security Group
Ingress:
  - Port: 80, 443
    Source: 0.0.0.0/0 (Public)
    Protocol: TCP
Egress:
  - Port: 8000
    Destination: Backend subnet
    Protocol: TCP

# Backend Security Group
Ingress:
  - Port: 8000
    Source: Frontend subnet
    Protocol: TCP
Egress:
  - Port: 5432
    Destination: Database subnet
    Protocol: TCP
  - Port: 443
    Destination: 0.0.0.0/0 (Gemini API)
    Protocol: TCP

# Database Security Group
Ingress:
  - Port: 5432
    Source: Backend subnet
    Protocol: TCP
Egress:
  - None (database is isolated)
```

---

## Infrastructure Components

### Component Inventory

```mermaid
graph TD
    subgraph "Compute Resources"
        APP[Application Servers<br/>Docker Host<br/>4 vCPU, 8 GB RAM]
        DB_HOST[Database Server<br/>2 vCPU, 4 GB RAM]
    end

    subgraph "Storage Resources"
        BLOCK[Block Storage<br/>SSD, 100 GB<br/>Database data]
        OBJECT[Object Storage<br/>Logs & outputs]
    end

    subgraph "Network Resources"
        LB_NET[Load Balancer<br/>2 nodes]
        VPC[Virtual Private Cloud<br/>10.0.0.0/16]
    end

    subgraph "External Services"
        DNS[DNS Provider]
        GEMINI_EXT[Gemini API]
        MONITOR[Monitoring Service]
    end

    APP --> BLOCK
    APP --> OBJECT
    DB_HOST --> BLOCK
    LB_NET --> APP
    VPC --> LB_NET
    VPC --> APP
    VPC --> DB_HOST
    APP --> GEMINI_EXT
    APP --> MONITOR

    style APP fill:#4ecdc4
    style DB_HOST fill:#ff6b6b
    style GEMINI_EXT fill:#ffd93d
```

### Infrastructure Sizing

#### Development Environment
```yaml
Frontend:
  CPU: 0.25 cores
  Memory: 128 MB
  Storage: 100 MB
  Replicas: 1

Backend:
  CPU: 1 core
  Memory: 512 MB
  Storage: 1 GB
  Replicas: 1

Database:
  CPU: 0.5 cores
  Memory: 256 MB
  Storage: 5 GB
  Replicas: 1

Total:
  CPU: 1.75 cores
  Memory: 896 MB
  Storage: 6.1 GB
```

#### Production Environment
```yaml
Frontend:
  CPU: 0.5 cores
  Memory: 256 MB
  Storage: 200 MB
  Replicas: 2

Backend:
  CPU: 2 cores
  Memory: 2 GB
  Storage: 10 GB
  Replicas: 3

Database:
  CPU: 2 cores
  Memory: 4 GB
  Storage: 100 GB
  Replicas: 1 (Primary) + 1 (Replica)

Load Balancer:
  CPU: 1 core
  Memory: 1 GB
  Replicas: 2

Total:
  CPU: 12 cores
  Memory: 15 GB
  Storage: 120 GB
```

---

## Deployment Strategies

### Development Deployment

```bash
# Local development deployment
docker-compose -f docker-compose.dev.yml up

# Hot reload enabled
# Volumes mounted for live code updates
# Debug logging enabled
```

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile.dev
    volumes:
      - ./backend/src:/app/src  # Live code mounting
    environment:
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    command: python run_api.py --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend/src:/app/src  # Live code mounting
    command: npm run dev
```

---

### Staging Deployment

```bash
# Staging environment (pre-production)
docker-compose -f docker-compose.staging.yml up -d

# Production-like configuration
# Test data seeded
# Monitoring enabled
```

---

### Production Deployment

#### Blue-Green Deployment Strategy

```mermaid
graph TB
    subgraph "Production Traffic"
        LB[Load Balancer]
    end

    subgraph "Blue Environment (Current)"
        BLUE_FE[Frontend v1.0]
        BLUE_BE[Backend v1.0]
    end

    subgraph "Green Environment (New)"
        GREEN_FE[Frontend v1.1]
        GREEN_BE[Backend v1.1]
    end

    subgraph "Shared Resources"
        DB[(Database)]
    end

    LB -->|100% Traffic| BLUE_FE
    LB -.->|0% Traffic| GREEN_FE

    BLUE_FE --> BLUE_BE
    GREEN_FE --> GREEN_BE

    BLUE_BE --> DB
    GREEN_BE --> DB

    style BLUE_FE fill:#4ecdc4
    style BLUE_BE fill:#4ecdc4
    style GREEN_FE fill:#95e1d3
    style GREEN_BE fill:#95e1d3
```

**Deployment Steps**:
1. Deploy new version to Green environment
2. Run smoke tests on Green
3. Gradually shift traffic: 10% → 50% → 100%
4. Monitor metrics and error rates
5. If successful, decommission Blue
6. If issues, instant rollback to Blue

---

#### Rolling Update Strategy

```mermaid
sequenceDiagram
    participant LB as Load Balancer
    participant BE1 as Backend Instance 1
    participant BE2 as Backend Instance 2
    participant BE3 as Backend Instance 3

    Note over LB,BE3: Initial State: v1.0 on all instances

    LB->>BE1: Remove from pool
    Note over BE1: Update to v1.1
    BE1->>LB: Health check passed
    LB->>BE1: Add back to pool

    LB->>BE2: Remove from pool
    Note over BE2: Update to v1.1
    BE2->>LB: Health check passed
    LB->>BE2: Add back to pool

    LB->>BE3: Remove from pool
    Note over BE3: Update to v1.1
    BE3->>LB: Health check passed
    LB->>BE3: Add back to pool

    Note over LB,BE3: Final State: v1.1 on all instances
```

---

### Kubernetes Deployment (Future)

```yaml
# kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hivemind-backend
  namespace: hivemind
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: hivemind-backend
  template:
    metadata:
      labels:
        app: hivemind-backend
        version: v1.0
    spec:
      containers:
      - name: backend
        image: hivemind-backend:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: hivemind-secrets
              key: gemini-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hivemind-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: hivemind-backend-service
  namespace: hivemind
spec:
  selector:
    app: hivemind-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hivemind-backend-hpa
  namespace: hivemind
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hivemind-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Scaling and Performance

### Horizontal Scaling

```mermaid
graph LR
    LB[Load Balancer]

    subgraph "Auto-Scaling Group"
        BE1[Backend 1<br/>Active]
        BE2[Backend 2<br/>Active]
        BE3[Backend 3<br/>Active]
        BE4[Backend 4<br/>Standby]
    end

    DB[(Database<br/>Primary)]
    DBR[(Database<br/>Read Replica)]

    LB --> BE1
    LB --> BE2
    LB --> BE3

    BE1 --> DB
    BE2 --> DB
    BE3 --> DB

    BE1 -.-> DBR
    BE2 -.-> DBR
    BE3 -.-> DBR

    DB -.-> DBR

    style BE1 fill:#4ecdc4
    style BE2 fill:#4ecdc4
    style BE3 fill:#4ecdc4
    style BE4 fill:#ddd
```

### Auto-Scaling Rules

```yaml
# Auto-scaling configuration
scaling_policies:
  backend:
    min_instances: 2
    max_instances: 10
    target_cpu_utilization: 70%
    target_memory_utilization: 80%
    scale_up:
      threshold: 80%
      cooldown: 300s
      step: 2 instances
    scale_down:
      threshold: 30%
      cooldown: 600s
      step: 1 instance

  frontend:
    min_instances: 2
    max_instances: 5
    target_cpu_utilization: 60%
    scale_up:
      threshold: 70%
      cooldown: 180s
      step: 1 instance
    scale_down:
      threshold: 20%
      cooldown: 300s
      step: 1 instance
```

### Database Scaling

```yaml
# Database scaling strategy
database:
  primary:
    size: db.t3.medium
    storage: 100 GB SSD
    connections: 100
    backup: Daily, 7-day retention

  read_replicas:
    count: 1
    size: db.t3.small
    lag_threshold: 5s
    auto_failover: enabled

  connection_pooling:
    max_connections: 100
    min_idle: 10
    max_idle: 20
    timeout: 30s
```

---

## Monitoring and Observability

### Monitoring Stack

```mermaid
graph TB
    subgraph "Application Layer"
        APP[HiveMind Backend]
        FE[Frontend]
    end

    subgraph "Monitoring Stack"
        PROM[Prometheus<br/>Metrics Collection]
        GRAF[Grafana<br/>Visualization]
        LOKI[Loki<br/>Log Aggregation]
        ALERT[Alertmanager<br/>Alerting]
    end

    subgraph "External Services"
        SLACK[Slack]
        EMAIL[Email]
        PAGER[PagerDuty]
    end

    APP -->|Metrics| PROM
    APP -->|Logs| LOKI
    FE -->|Metrics| PROM

    PROM --> GRAF
    LOKI --> GRAF
    PROM --> ALERT

    ALERT --> SLACK
    ALERT --> EMAIL
    ALERT --> PAGER

    style PROM fill:#e6522c
    style GRAF fill:#f46800
    style LOKI fill:#00a4ef
```

### Key Metrics

```yaml
# Application Metrics
metrics:
  business:
    - analysis_executions_total
    - analysis_execution_duration_seconds
    - consensus_level_average
    - final_confidence_average
    - agent_responses_per_execution

  system:
    - http_requests_total
    - http_request_duration_seconds
    - http_request_size_bytes
    - http_response_size_bytes
    - websocket_connections_active

  infrastructure:
    - container_cpu_usage_percent
    - container_memory_usage_bytes
    - container_network_transmit_bytes
    - container_disk_usage_bytes

  database:
    - postgresql_connections_active
    - postgresql_transactions_total
    - postgresql_query_duration_seconds
    - postgresql_database_size_bytes

  external:
    - gemini_api_calls_total
    - gemini_api_duration_seconds
    - gemini_api_errors_total
    - gemini_tokens_used_total
```

### Logging Strategy

```python
# Structured logging configuration
logging_config = {
    "version": 1,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "/app/logs/hivemind.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

---

## Security Architecture

### Security Layers

```mermaid
graph TD
    subgraph "Edge Security"
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]
        SSL[SSL/TLS Termination]
    end

    subgraph "Network Security"
        FW[Firewall]
        NSG[Network Security Groups]
        VPN[VPN Gateway]
    end

    subgraph "Application Security"
        AUTH[Authentication]
        AUTHZ[Authorization]
        SECRETS[Secrets Management]
        ENCRYPT[Data Encryption]
    end

    subgraph "Data Security"
        DB_ENCRYPT[Database Encryption]
        BACKUP[Encrypted Backups]
        ACCESS_LOG[Access Logging]
    end

    WAF --> FW
    DDoS --> FW
    SSL --> FW
    FW --> NSG
    NSG --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> SECRETS
    SECRETS --> DB_ENCRYPT
    DB_ENCRYPT --> BACKUP
    ENCRYPT --> BACKUP
    ACCESS_LOG --> BACKUP

    style WAF fill:#ff6b6b
    style AUTH fill:#4ecdc4
    style DB_ENCRYPT fill:#ffd93d
```

### Secret Management

```yaml
# Secrets configuration
secrets:
  gemini_api_key:
    source: environment_variable
    env_var: GEMINI_API_KEY
    rotation: manual
    encryption: at_rest

  database_password:
    source: secrets_manager
    key: hivemind/db/password
    rotation: 90_days
    encryption: at_rest_and_transit

  api_keys:
    source: vault
    path: hivemind/api/keys
    rotation: on_demand
    encryption: at_rest_and_transit
```

### Network Security

```yaml
# Firewall rules
firewall_rules:
  - name: allow-https-ingress
    direction: ingress
    protocol: tcp
    port: 443
    source: 0.0.0.0/0
    action: allow

  - name: allow-backend-internal
    direction: ingress
    protocol: tcp
    port: 8000
    source: frontend_subnet
    action: allow

  - name: allow-database-internal
    direction: ingress
    protocol: tcp
    port: 5432
    source: backend_subnet
    action: allow

  - name: deny-all-else
    direction: ingress
    protocol: all
    source: 0.0.0.0/0
    action: deny
```

---

## Disaster Recovery

### Backup Strategy

```yaml
# Backup configuration
backup:
  database:
    frequency: daily
    retention: 30 days
    type: full
    encryption: aes-256
    storage: s3_bucket

  application_state:
    frequency: hourly
    retention: 7 days
    type: incremental
    items:
      - logs
      - analysis_outputs

  configuration:
    frequency: on_change
    retention: indefinite
    type: versioned
    items:
      - docker-compose.yml
      - .env
      - nginx.conf
```

### Recovery Procedures

```mermaid
flowchart TD
    INCIDENT[Incident Detected] --> ASSESS{Assess Severity}

    ASSESS -->|Critical| DR_ACTIVATE[Activate DR Plan]
    ASSESS -->|High| FAILOVER[Failover to Replica]
    ASSESS -->|Medium| RESTORE[Restore from Backup]
    ASSESS -->|Low| FIX[Apply Fix]

    DR_ACTIVATE --> DR_SITE[Switch to DR Site]
    DR_SITE --> VERIFY_DR[Verify Services]

    FAILOVER --> PROMOTE[Promote Replica to Primary]
    PROMOTE --> VERIFY_FAIL[Verify Services]

    RESTORE --> SELECT_BACKUP[Select Backup Point]
    SELECT_BACKUP --> RESTORE_DB[Restore Database]
    RESTORE_DB --> VERIFY_RESTORE[Verify Services]

    FIX --> TEST_FIX[Test Fix]
    TEST_FIX --> DEPLOY_FIX[Deploy Fix]

    VERIFY_DR --> MONITOR
    VERIFY_FAIL --> MONITOR
    VERIFY_RESTORE --> MONITOR
    DEPLOY_FIX --> MONITOR

    MONITOR[Monitor & Document]
```

### Recovery Time Objectives (RTO)

| Component | RTO | RPO | Strategy |
|-----------|-----|-----|----------|
| Frontend | 5 minutes | 0 | Blue-green deployment |
| Backend | 15 minutes | 1 hour | Backup + redeploy |
| Database | 30 minutes | 5 minutes | Replica failover |
| Complete System | 1 hour | 1 hour | DR site activation |

---

## Cloud Provider Mappings

### AWS Deployment

```yaml
# AWS infrastructure mapping
aws:
  compute:
    frontend: ECS Fargate
    backend: ECS Fargate or EC2
    database: RDS PostgreSQL

  networking:
    vpc: Custom VPC
    subnets: Public + Private
    load_balancer: Application Load Balancer

  storage:
    logs: CloudWatch Logs
    outputs: S3 bucket
    database: RDS storage

  monitoring:
    metrics: CloudWatch
    logs: CloudWatch Logs
    alerts: SNS

  security:
    secrets: AWS Secrets Manager
    encryption: KMS
    identity: IAM roles
```

### GCP Deployment

```yaml
# GCP infrastructure mapping
gcp:
  compute:
    frontend: Cloud Run
    backend: Cloud Run or GKE
    database: Cloud SQL PostgreSQL

  networking:
    vpc: Custom VPC
    load_balancer: Cloud Load Balancing

  storage:
    logs: Cloud Logging
    outputs: Cloud Storage
    database: Cloud SQL storage

  monitoring:
    metrics: Cloud Monitoring
    logs: Cloud Logging
    alerts: Cloud Monitoring alerts

  security:
    secrets: Secret Manager
    encryption: Cloud KMS
    identity: IAM + Service Accounts
```

### Azure Deployment

```yaml
# Azure infrastructure mapping
azure:
  compute:
    frontend: Azure Container Instances
    backend: Azure Container Instances or AKS
    database: Azure Database for PostgreSQL

  networking:
    vnet: Custom VNet
    load_balancer: Azure Load Balancer

  storage:
    logs: Azure Monitor Logs
    outputs: Blob Storage
    database: PostgreSQL storage

  monitoring:
    metrics: Azure Monitor
    logs: Log Analytics
    alerts: Azure Monitor Alerts

  security:
    secrets: Key Vault
    encryption: Azure Encryption
    identity: Managed Identities
```

---

## References

- Docker Best Practices
- Kubernetes Documentation
- Cloud Architecture Patterns
- Site Reliability Engineering (Google)
- The Twelve-Factor App

---

**Next**: [Scenarios →](./scenarios.md)
