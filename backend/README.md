# HiveMind Backend

Este directorio contiene todo el código backend del sistema HiveMind Architecture, incluyendo la API REST, CLI, y la lógica de negocio del sistema multi-agente.

## 📁 Estructura del Backend

```
backend/
├── src/                    # Código fuente principal
│   ├── agents/            # Agentes especializados
│   ├── hivemind/          # Arquitectura HiveMind
│   ├── api/               # API REST (FastAPI)
│   └── utils/             # Utilidades y configuración
├── cli.py                 # Interfaz de línea de comandos
├── run_api.py             # Servidor API REST
├── test_api.py            # Pruebas de la API
├── requirements.txt       # Dependencias Python
├── setup.sh               # Script de configuración
├── examples/              # Ejemplos de uso
└── README.md              # Este archivo
```

## 🚀 Uso Rápido

### CLI (Línea de Comandos)
```bash
cd backend
python cli.py --business-need "Tu necesidad de negocio aquí" --methodology scrum
```

### API REST
```bash
cd backend
python run_api.py --host 0.0.0.0 --port 8000
```

### Con Docker (desde la raíz del proyecto)
```bash
# Construir imagen
./docker-manager.sh build

# Iniciar API REST
./docker-manager.sh up

# Iniciar CLI
./docker-manager.sh up-cli
```

## 🔧 Configuración

1. **Variables de entorno**: Configura `GOOGLE_API_KEY` en el archivo `.env` en la raíz del proyecto
2. **Dependencias**: Instala con `pip install -r requirements.txt`
3. **Configuración**: Usa `setup.sh` para configuración inicial

## 📊 Servicios Disponibles

- **API REST**: Puerto 8002 (producción) / 8001 (desarrollo)
- **CLI**: Interfaz de línea de comandos
- **Health Check**: `/api/v1/health`
- **Documentación**: `/docs` (Swagger UI)

## 🧪 Pruebas

```bash
# Pruebas de la API
python test_api.py --url http://localhost:8002

# Pruebas con Docker
./docker-manager.sh test
```

## 📝 Metodologías Soportadas

- **Scrum**: Framework ágil tradicional
- **SAFe**: Scaled Agile Framework
- **Kanban**: Gestión de flujo de trabajo

## 🔄 Estrategias de Consenso

- **weighted_voting**: Votación ponderada
- **majority**: Mayoría simple
- **unanimous**: Consenso unánime
- **confidence_threshold**: Umbral de confianza

---

Para más información, consulta la documentación principal en `/docs/` o el README principal del proyecto.
