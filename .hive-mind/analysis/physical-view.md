# Physical View - HiveMind Architecture Analysis

## Overview
The Physical View describes the physical topology and deployment of the HiveMind system, including hardware, network configuration, containerization, and infrastructure components.

---

## Deployment Architecture

### Container-Based Architecture (Docker Compose)

```
┌────────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                                │
│  Operating System: Linux/macOS/Windows                             │
│  Docker Engine: 24.0+                                               │
│  Docker Compose: 2.0+                                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   DOCKER NETWORK                             │  │
│  │                (hivemind-network)                            │  │
│  │                  Bridge Driver                                │  │
│  │                                                              │  │
│  │  ┌─────────────────────────────────────────────────────┐    │  │
│  │  │  hivemind-frontend Container                        │    │  │
│  │  │  ┌────────────────────────────────────────────┐     │    │  │
│  │  │  │  Nginx 1.25 (Alpine)                       │     │    │  │
│  │  │  │  • Serves static React build                │     │    │  │
│  │  │  │  • Port: 80 (internal)                      │     │    │  │
│  │  │  │  • Health: GET /                            │     │    │  │
│  │  │  └────────────────────────────────────────────┘     │    │  │
│  │  │  Port Mapping: 3002:80                              │    │  │
│  │  └────────────────┬────────────────────────────────────┘    │  │
│  │                   │ HTTP/WebSocket                           │  │
│  │                   │                                          │  │
│  │  ┌────────────────▼────────────────────────────────────┐    │  │
│  │  │  hivemind-api Container                            │    │  │
│  │  │  ┌────────────────────────────────────────────┐     │    │  │
│  │  │  │  Python 3.11-slim                          │     │    │  │
│  │  │  │  • FastAPI application                     │     │    │  │
│  │  │  │  • Uvicorn ASGI server                     │     │    │  │
│  │  │  │  • HiveMind orchestration                  │     │    │  │
│  │  │  │  • Port: 8000 (internal)                   │     │    │  │
│  │  │  │  • Health: GET /api/v1/health              │     │    │  │
│  │  │  └────────────────────────────────────────────┘     │    │  │
│  │  │  Port Mapping: 8002:8000                            │    │  │
│  │  │  Volumes:                                            │    │  │
│  │  │    • ./logs → /app/logs                             │    │  │
│  │  │    • ./output → /app/output                         │    │  │
│  │  └────────────────┬────────────────────────────────────┘    │  │
│  │                   │ PostgreSQL Protocol                      │  │
│  │                   │                                          │  │
│  │  ┌────────────────▼────────────────────────────────────┐    │  │
│  │  │  hivemind-postgres Container                        │    │  │
│  │  │  ┌────────────────────────────────────────────┐     │    │  │
│  │  │  │  PostgreSQL 16 (Alpine)                    │     │    │  │
│  │  │  │  • Database: hivemind                      │     │    │  │
│  │  │  │  • User: hivemind                          │     │    │  │
│  │  │  │  • Port: 5432 (internal only)              │     │    │  │
│  │  │  │  • Health: pg_isready                      │     │    │  │
│  │  │  └────────────────────────────────────────────┘     │    │  │
│  │  │  Volume: postgres_data (persistent)                 │    │  │
│  │  └─────────────────────────────────────────────────────┘    │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  hivemind-cli Container (Optional)                   │   │  │
│  │  │  • CLI tool for direct analysis                      │   │  │
│  │  │  • Same image as API                                 │   │  │
│  │  │  • Profile: cli                                      │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  hivemind-dev Container (Optional)                   │   │  │
│  │  │  • Development mode with hot-reload                  │   │  │
│  │  │  • Port: 8001:8000                                   │   │  │
│  │  │  • Profile: dev                                      │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  External Connection:                                               │
│  Backend → Google Gemini API (HTTPS)                               │
│           https://generativelanguage.googleapis.com/v1beta          │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Container Specifications

### 1. hivemind-frontend Container

**Base Image:** `nginx:alpine`
**Build Strategy:** Multi-stage build
- Stage 1: Build React app with Node.js 18
- Stage 2: Serve with Nginx

**Resources:**
- CPU: 0.5 cores (default)
- Memory: 256 MB (default)
- Storage: ~50 MB (image + static files)

**Networking:**
- Internal Port: 80
- External Port: 3002
- Protocol: HTTP, WebSocket (proxied)

**Configuration:**
- Nginx config: Default with SPA routing
- React build: Production optimized (minified)

**Health Check:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost/"]
interval: 30s
timeout: 10s
retries: 3
start_period: 10s
```

**Persistence:** None (stateless static server)

---

### 2. hivemind-api Container

**Base Image:** `python:3.11-slim`
**Build Strategy:** Single-stage with requirements

**Resources:**
- CPU: 1-2 cores (default)
- Memory: 512 MB - 1 GB
- Storage: ~500 MB (image + dependencies)

**Networking:**
- Internal Port: 8000
- External Port: 8002
- Protocol: HTTP, WebSocket

**Environment Variables:**
```yaml
GEMINI_API_KEY: <from .env>
GEMINI_MODEL: gemini-flash-lite-latest
TEMPERATURE: 0.7
MAX_TOKENS: 4000
DATABASE_URL: postgresql://hivemind:password@postgres:5432/hivemind
API_HOST: 0.0.0.0
API_PORT: 8000
API_RELOAD: false
API_LOG_LEVEL: info
```

**Volumes:**
```yaml
volumes:
  - ./logs:/app/logs              # Log files
  - ./output:/app/output          # Analysis outputs
```

**Health Check:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
interval: 30s
timeout: 10s
retries: 3
start_period: 40s
```

**Dependencies:**
- Waits for PostgreSQL health check
- Initializes database schema on startup

**Process:**
- Command: `python backend/run_api.py --host 0.0.0.0 --port 8000`
- PID 1: Python process
- Restart: `unless-stopped`

---

### 3. hivemind-postgres Container

**Base Image:** `postgres:16-alpine`

**Resources:**
- CPU: 1 core (default)
- Memory: 256 MB - 512 MB
- Storage: Variable (persistent volume)

**Networking:**
- Internal Port: 5432 (not exposed to host)
- Protocol: PostgreSQL wire protocol

**Environment Variables:**
```yaml
POSTGRES_DB: hivemind
POSTGRES_USER: hivemind
POSTGRES_PASSWORD: hivemind_password
PGDATA: /var/lib/postgresql/data/pgdata
```

**Volumes:**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data  # Named volume
```

**Health Check:**
```yaml
test: ["CMD-SHELL", "pg_isready -U hivemind"]
interval: 10s
timeout: 5s
retries: 5
```

**Persistence:**
- Named Docker volume: `postgres_data`
- Survives container restarts
- Data location: `/var/lib/docker/volumes/postgres_data`

**Database Schema:**
- Tables: `analyses`, `agent_responses`
- Indexes: On created_at, methodology, agent_name
- Relationships: analyses (1) → agent_responses (N)

---

### 4. hivemind-cli Container (Optional)

**Profile:** `cli` (not started by default)

**Base Image:** Same as hivemind-api
**Command:** `python backend/cli.py --help`

**Usage:**
```bash
# Start CLI container
docker-compose --profile cli run hivemind-cli

# Execute analysis
docker-compose --profile cli run hivemind-cli \
  python backend/cli.py --business-need "..."
```

**Volumes:**
```yaml
volumes:
  - ./logs:/app/logs
  - ./output:/app/output
  - ./backend/examples:/app/backend/examples
```

---

### 5. hivemind-dev Container (Optional)

**Profile:** `dev` (for development)

**Differences from Production:**
- Hot-reload enabled (`API_RELOAD=true`)
- Source code mounted as volume (live updates)
- Debug logging (`API_LOG_LEVEL=debug`)
- Port: 8001 (to avoid conflict with production)

**Usage:**
```bash
# Start development environment
docker-compose --profile dev up hivemind-dev
```

**Volumes:**
```yaml
volumes:
  - .:/app                        # Full source mount
  - ./logs:/app/logs
  - ./output:/app/output
```

---

## Network Architecture

### Docker Network Configuration

**Network Name:** `hivemind-network`
**Driver:** `bridge`
**Subnet:** Auto-assigned by Docker (typically 172.x.x.x)

**DNS Resolution:**
- Containers resolve each other by service name
- Example: API connects to `postgres:5432`
- Frontend connects to `hivemind-api:8000`

**Isolation:**
- Internal communication within network
- External access only via exposed ports
- PostgreSQL not accessible from host (security)

### Port Mapping

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| Frontend | 80 | 3002 | HTTP |
| API | 8000 | 8002 | HTTP/WebSocket |
| PostgreSQL | 5432 | (not exposed) | PostgreSQL |
| Dev API | 8000 | 8001 | HTTP/WebSocket |

---

## Storage Architecture

### Volume Types

**Named Volumes:**
```yaml
postgres_data:
  driver: local
  # Location: /var/lib/docker/volumes/postgres_data
```

**Bind Mounts:**
```yaml
./logs → /app/logs          # Application logs
./output → /app/output      # Analysis outputs
```

### Data Persistence

**Persistent Data:**
- PostgreSQL database (named volume)
- Analysis history
- Agent responses
- Communication logs (in database)

**Ephemeral Data:**
- Container file system
- Log files (bind mount, but can be cleared)
- Output files (bind mount, but can be cleared)

**Backup Strategy:**
- PostgreSQL: `pg_dump` to external storage
- Logs: Rotate and archive
- Outputs: Copy to external storage if needed

---

## External Dependencies

### Google Gemini API

**Endpoint:** `https://generativelanguage.googleapis.com/v1beta`
**Protocol:** HTTPS REST
**Authentication:** API Key (Bearer token)

**Network Flow:**
```
Backend Container
    │
    ├──> DNS Resolution (generativelanguage.googleapis.com)
    │
    ├──> TLS Handshake (HTTPS)
    │
    ├──> POST /v1beta/models/gemini-*/generateContent
    │    Headers:
    │      Authorization: Bearer <API_KEY>
    │      Content-Type: application/json
    │
    └──> Response (JSON)
```

**Rate Limiting:**
- Handled by Gemini SDK
- Exponential backoff on errors
- Max retries: 3

**Failure Handling:**
- Network timeout: 30 seconds
- Connection errors: Retry with backoff
- API errors: Propagate to caller

---

## Scalability & Load Balancing

### Horizontal Scaling

**Frontend:**
```yaml
deploy:
  replicas: 3
```
- Multiple Nginx containers
- External load balancer (e.g., Nginx, HAProxy)
- Session affinity not required (stateless)

**API:**
```yaml
deploy:
  replicas: 3-5
```
- Multiple FastAPI containers
- Load balancer distributes requests
- Stateless design enables easy scaling

**Database:**
- Single PostgreSQL instance (default)
- Read replicas for read-heavy workloads
- Connection pooling (SQLAlchemy)

### Vertical Scaling

**Resource Limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

**Database Tuning:**
- `shared_buffers`: 256 MB
- `effective_cache_size`: 1 GB
- `max_connections`: 100

---

## High Availability

### Container Restart Policy

```yaml
restart: unless-stopped
```

**Behavior:**
- Automatic restart on failure
- Persists across Docker daemon restarts
- Manual stop prevents auto-restart

### Health Monitoring

**Health Checks:**
- All containers have health checks
- Unhealthy containers automatically restarted
- Health status visible via `docker ps`

**Monitoring Strategy:**
- Docker health checks for basic monitoring
- External monitoring (Prometheus, Grafana) for production
- Log aggregation (ELK stack, Splunk)

### Failure Scenarios

**Frontend Failure:**
- Impact: Web UI unavailable
- Recovery: Automatic container restart (~10s)
- Mitigation: Multiple replicas with load balancer

**API Failure:**
- Impact: API requests fail
- Recovery: Automatic container restart (~40s)
- Mitigation: Multiple replicas, request retry

**Database Failure:**
- Impact: All operations fail
- Recovery: Automatic container restart + data recovery
- Mitigation: Database clustering (future), regular backups

**Gemini API Failure:**
- Impact: Analysis requests fail
- Recovery: Retry with exponential backoff
- Mitigation: Queue system for deferred processing

---

## Security Architecture

### Network Security

**Container Isolation:**
- Containers communicate via bridge network
- PostgreSQL not exposed to host network
- Only API and Frontend exposed externally

**Firewall Rules:**
```
Allow:
  - 3002/tcp (Frontend HTTP)
  - 8002/tcp (API HTTP/WebSocket)

Deny:
  - 5432/tcp (PostgreSQL - internal only)
  - All other ports
```

### Data Security

**Secrets Management:**
- API keys in environment variables (`.env` file)
- `.env` file in `.gitignore`
- Production: Use Docker secrets or external vault

**TLS/SSL:**
- Gemini API: HTTPS enforced
- Frontend/API: HTTP (behind reverse proxy in production)
- Production: Add Nginx reverse proxy with TLS

**Database Security:**
- Password authentication required
- Network access restricted to Docker network
- No superuser access from application

### Container Security

**Base Images:**
- Official images only (postgres, python, nginx)
- Alpine variants for smaller attack surface
- Regular image updates

**User Privileges:**
- Non-root user in containers (best practice)
- Minimal permissions for processes

**Vulnerability Scanning:**
- `docker scan` for known vulnerabilities
- Regular image updates

---

## Production Deployment Considerations

### Infrastructure Requirements

**Minimum Specs:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- Network: 100 Mbps

**Recommended Specs:**
- CPU: 8 cores
- RAM: 16 GB
- Storage: 200 GB SSD
- Network: 1 Gbps

### Cloud Deployment Options

**AWS:**
- ECS/Fargate for container orchestration
- RDS PostgreSQL for database
- ALB for load balancing
- CloudWatch for monitoring

**Google Cloud:**
- GKE for Kubernetes orchestration
- Cloud SQL for database
- Cloud Load Balancing
- Cloud Monitoring

**Azure:**
- AKS for Kubernetes
- Azure Database for PostgreSQL
- Application Gateway
- Azure Monitor

### Kubernetes Migration

**Kubernetes Resources:**
```yaml
# API Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hivemind-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hivemind-api
  template:
    spec:
      containers:
      - name: api
        image: hivemind-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hivemind-secrets
              key: database-url

# Service
apiVersion: v1
kind: Service
metadata:
  name: hivemind-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: hivemind-api
```

---

## Monitoring & Observability

### Logging

**Container Logs:**
```bash
# View logs
docker-compose logs -f hivemind-api

# Export logs
docker-compose logs hivemind-api > api.log
```

**Log Aggregation:**
- Stdout/stderr captured by Docker
- Centralized logging with Fluentd/Logstash
- Log retention: 30 days

### Metrics

**Container Metrics:**
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

**Application Metrics:**
- Request rate
- Response time
- Error rate
- Active connections

**Tools:**
- Docker stats
- Prometheus + Grafana
- Application Performance Monitoring (APM)

### Tracing

**Distributed Tracing:**
- Trace ID in logs
- Request flow tracking
- A2A message tracing

**Tools:**
- OpenTelemetry
- Jaeger
- Zipkin

---

## Disaster Recovery

### Backup Strategy

**Database Backup:**
```bash
# Daily automated backup
docker exec hivemind-postgres pg_dump -U hivemind hivemind > backup.sql

# Restore
docker exec -i hivemind-postgres psql -U hivemind hivemind < backup.sql
```

**Frequency:**
- Full backup: Daily
- Incremental: Hourly
- Retention: 30 days

**Storage:**
- Local: NAS/SAN
- Cloud: S3, GCS, Azure Blob

### Recovery Procedures

**Container Failure:**
1. Automatic restart via Docker
2. Check health status
3. Review logs for errors

**Data Corruption:**
1. Stop containers
2. Restore database from backup
3. Restart containers
4. Verify data integrity

**Complete Failure:**
1. Provision new infrastructure
2. Deploy containers
3. Restore database
4. Restore volumes
5. Verify functionality

**Recovery Time Objective (RTO):** < 1 hour
**Recovery Point Objective (RPO):** < 1 hour (hourly backups)

---

## Physical View Summary

**Deployment Model:**
- Containerized microservices architecture
- Docker Compose for orchestration
- Bridge networking for internal communication

**Infrastructure:**
- 3 main containers (Frontend, API, Database)
- 2 optional containers (CLI, Dev)
- Named volumes for persistence
- Bind mounts for logs/outputs

**Scalability:**
- Horizontal scaling for frontend and API
- Vertical scaling for database
- Load balancing for high availability

**Security:**
- Network isolation via Docker network
- Secrets management via environment variables
- TLS for external communication

**Monitoring:**
- Health checks for all containers
- Centralized logging
- Metrics collection

**Production Ready:**
- Kubernetes migration path available
- Cloud deployment options documented
- Backup and recovery procedures defined
