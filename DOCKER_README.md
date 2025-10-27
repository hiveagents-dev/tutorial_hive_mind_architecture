# 🐝 HiveMind Architecture - Docker Setup

## 🚀 Inicio Rápido con Docker

### 1. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar el archivo .env y configurar tu API key de Gemini
nano .env
```

**Importante**: Debes configurar tu API key real de Google Gemini en el archivo `.env`:

```env
GOOGLE_API_KEY=tu_api_key_real_aqui
```

### 2. Construir y Ejecutar

```bash
# Hacer ejecutable el script de gestión
chmod +x docker-manager.sh

# Construir las imágenes Docker
./docker-manager.sh build

# Iniciar el servicio API REST
./docker-manager.sh up
```

### 3. Probar el Sistema

```bash
# Verificar que el servicio esté funcionando
curl http://localhost:8002/api/v1/health

# Probar análisis de negocio
curl -X POST http://localhost:8002/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_need": "Necesitamos una aplicación móvil para gestionar tareas personales",
    "methodology": "scrum",
    "consensus_strategy": "weighted_voting",
    "verbose": false
  }'
```

## 📚 Documentación de la API

Una vez que el servicio esté funcionando, puedes acceder a:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/api/v1/health

## 🛠️ Comandos Disponibles

```bash
# Ver ayuda
./docker-manager.sh help

# Iniciar servicios
./docker-manager.sh up

# Iniciar en modo desarrollo (con hot-reload)
./docker-manager.sh up-dev

# Ver logs
./docker-manager.sh logs

# Ver logs del API
./docker-manager.sh logs-api

# Verificar salud
./docker-manager.sh health

# Detener servicios
./docker-manager.sh down

# Limpiar contenedores e imágenes
./docker-manager.sh clean
```

## 🔧 Servicios Disponibles

### hivemind-api (Puerto 8002)
- **Descripción**: API REST principal del sistema HiveMind
- **Puerto**: 8002
- **Endpoints**: 
  - `GET /api/v1/health` - Health check
  - `GET /api/v1/info` - Información del sistema
  - `POST /api/v1/analyze` - Análisis de necesidades de negocio
  - `POST /api/v1/example` - Ejemplo de análisis

### hivemind-cli (Profile: cli)
- **Descripción**: Interfaz de línea de comandos
- **Uso**: `./docker-manager.sh up-cli`

### hivemind-dev (Profile: dev)
- **Descripción**: Servicio de desarrollo con hot-reload
- **Puerto**: 8001
- **Uso**: `./docker-manager.sh up-dev`

### hivemind-test (Profile: test)
- **Descripción**: Pruebas automatizadas
- **Uso**: `./docker-manager.sh test`

## 📁 Estructura de Volúmenes

- `./logs` → `/app/logs` - Logs del sistema
- `./output` → `/app/output` - Archivos de salida
- `./examples` → `/app/examples` - Ejemplos (solo CLI)

## 🔐 Seguridad

- El contenedor ejecuta con usuario no-root (`hivemind`)
- Variables de entorno sensibles se cargan desde `.env`
- Health checks automáticos para monitoreo

## 🐛 Troubleshooting

### Error: "API key not valid"
```bash
# Verificar que la API key esté configurada correctamente
grep GOOGLE_API_KEY .env

# Debe mostrar tu API key real, no "your_gemini_api_key_here"
```

### Error: "Port already in use"
```bash
# Verificar qué está usando el puerto
lsof -i :8002

# Detener servicios anteriores
./docker-manager.sh down
```

### Error: "Container not found"
```bash
# Reconstruir las imágenes
./docker-manager.sh build

# O limpiar todo y empezar de nuevo
./docker-manager.sh clean
./docker-manager.sh build
./docker-manager.sh up
```

## 📊 Monitoreo

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f hivemind-api

# Verificar salud del servicio
./docker-manager.sh health
```

## 🎯 Casos de Uso

### Análisis Simple
```bash
curl -X POST http://localhost:8002/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_need": "Sistema de gestión de inventario para retail",
    "methodology": "scrum",
    "consensus_strategy": "weighted_voting"
  }'
```

### Análisis con Metodología SAFe
```bash
curl -X POST http://localhost:8002/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_need": "Plataforma empresarial de gestión de proyectos",
    "methodology": "safe",
    "consensus_strategy": "majority"
  }'
```

### Ejemplo Predefinido
```bash
curl -X POST http://localhost:8002/api/v1/example
```

---

**¡El sistema HiveMind está listo para usar con Docker! 🎉**
