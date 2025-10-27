#!/bin/bash
# Script de utilidad para Docker Compose de HiveMind

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🐝 HiveMind Docker Compose Manager${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build          Construir las imágenes Docker"
    echo "  up             Iniciar servicios (API REST)"
    echo "  up-dev         Iniciar servicios en modo desarrollo"
    echo "  up-cli         Iniciar servicio CLI"
    echo "  up-test        Ejecutar pruebas automatizadas"
    echo "  down           Detener todos los servicios"
    echo "  logs           Mostrar logs de todos los servicios"
    echo "  logs-api       Mostrar logs del servicio API"
    echo "  shell          Abrir shell en el contenedor API"
    echo "  test           Ejecutar pruebas de la API"
    echo "  clean          Limpiar contenedores e imágenes"
    echo "  status         Mostrar estado de los servicios"
    echo "  health         Verificar salud de los servicios"
    echo ""
    echo "Ejemplos:"
    echo "  $0 up          # Iniciar API REST en puerto 8000"
    echo "  $0 up-dev      # Iniciar en modo desarrollo con hot-reload"
    echo "  $0 test        # Ejecutar pruebas automatizadas"
    echo "  $0 shell       # Abrir shell para debugging"
}

# Función para verificar si existe el archivo .env
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo -e "${YELLOW}   Copiando env.example a .env...${NC}"
        cp env.example .env
        echo -e "${RED}❌ IMPORTANTE: Edita el archivo .env y configura tu GOOGLE_API_KEY${NC}"
        echo -e "${RED}   Antes de continuar, ejecuta: nano .env${NC}"
        exit 1
    fi
    
    # Verificar que GOOGLE_API_KEY esté configurado
    if grep -q "your_gemini_api_key_here" .env; then
        echo -e "${RED}❌ ERROR: GOOGLE_API_KEY no está configurado en .env${NC}"
        echo -e "${RED}   Edita el archivo .env y configura tu API key de Gemini${NC}"
        exit 1
    fi
}

# Función para construir imágenes
build_images() {
    echo -e "${BLUE}🔨 Construyendo imágenes Docker...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Imágenes construidas exitosamente${NC}"
}

# Función para iniciar servicios
start_services() {
    local profile=$1
    echo -e "${BLUE}🚀 Iniciando servicios HiveMind...${NC}"
    
    if [ -n "$profile" ]; then
        docker-compose --profile $profile up -d
    else
        docker-compose up -d
    fi
    
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
    echo -e "${BLUE}📖 API REST disponible en: http://localhost:8002${NC}"
    echo -e "${BLUE}📚 Documentación: http://localhost:8002/docs${NC}"
    echo -e "${BLUE}❤️  Health check: http://localhost:8002/api/v1/health${NC}"
}

# Función para detener servicios
stop_services() {
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para mostrar logs
show_logs() {
    local service=$1
    if [ -n "$service" ]; then
        echo -e "${BLUE}📋 Mostrando logs de $service...${NC}"
        docker-compose logs -f $service
    else
        echo -e "${BLUE}📋 Mostrando logs de todos los servicios...${NC}"
        docker-compose logs -f
    fi
}

# Función para abrir shell
open_shell() {
    echo -e "${BLUE}🐚 Abriendo shell en contenedor API...${NC}"
    docker-compose exec hivemind-api /bin/bash
}

# Función para ejecutar pruebas
run_tests() {
    echo -e "${BLUE}🧪 Ejecutando pruebas automatizadas...${NC}"
    docker-compose --profile test up --abort-on-container-exit
    echo -e "${GREEN}✅ Pruebas completadas${NC}"
}

# Función para limpiar
clean_up() {
    echo -e "${YELLOW}🧹 Limpiando contenedores e imágenes...${NC}"
    docker-compose down --rmi all --volumes --remove-orphans
    docker system prune -f
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
}

# Función para verificar salud
check_health() {
    echo -e "${BLUE}❤️  Verificando salud de los servicios...${NC}"
    
    # Verificar si el servicio está corriendo
    if docker-compose ps | grep -q "hivemind-api.*Up"; then
        # Verificar health check
        if curl -f http://localhost:8002/api/v1/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API REST está funcionando correctamente${NC}"
        else
            echo -e "${RED}❌ API REST no responde correctamente${NC}"
        fi
    else
        echo -e "${RED}❌ Servicio API no está corriendo${NC}"
    fi
}

# Función para ejecutar análisis CLI
run_cli_analysis() {
    local business_need="$1"
    if [ -z "$business_need" ]; then
        echo -e "${RED}❌ ERROR: Debes proporcionar una necesidad de negocio${NC}"
        echo "Uso: $0 cli \"Tu necesidad de negocio aquí\""
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Ejecutando análisis CLI...${NC}"
    echo -e "${BLUE}📋 Necesidad de negocio: $business_need${NC}"
    
    docker-compose run --rm hivemind-cli python src/main.py \
        --business-need "$business_need" \
        --methodology scrum \
        --consensus-strategy weighted_voting \
        --verbose
}

# Main script
case "${1:-help}" in
    "build")
        check_env
        build_images
        ;;
    "up")
        check_env
        start_services
        ;;
    "up-dev")
        check_env
        start_services "dev"
        ;;
    "up-cli")
        check_env
        start_services "cli"
        ;;
    "up-test")
        check_env
        start_services "test"
        ;;
    "down")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "logs-api")
        show_logs "hivemind-api"
        ;;
    "shell")
        open_shell
        ;;
    "test")
        check_env
        run_tests
        ;;
    "clean")
        clean_up
        ;;
    "status")
        show_status
        ;;
    "health")
        check_health
        ;;
    "cli")
        check_env
        run_cli_analysis "$2"
        ;;
    "help"|*)
        show_help
        ;;
esac
