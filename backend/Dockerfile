# Dockerfile para HiveMind Architecture
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="HiveMind Team"
LABEL description="Sistema multi-agente para transformar necesidades de negocio en requisitos técnicos"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/backend/src

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY backend/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del backend
COPY backend/ /app/backend/

# Crear directorio para logs
RUN mkdir -p /app/logs /app/output

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash hivemind && \
    chown -R hivemind:hivemind /app
USER hivemind

# Exponer puerto para la API REST
EXPOSE 8000

# Comando por defecto (puede ser sobrescrito)
CMD ["python", "backend/cli.py", "--help"]

# Health check para la API REST
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1