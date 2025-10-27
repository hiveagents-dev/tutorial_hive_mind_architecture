#!/usr/bin/env python3
"""Script para ejecutar la API REST de HiveMind"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.main import run_server

def main():
    """Función principal para ejecutar la API"""
    parser = argparse.ArgumentParser(
        description="HiveMind Architecture API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_api.py                    # Ejecutar en localhost:8000
  python run_api.py --host 0.0.0.0     # Ejecutar en todas las interfaces
  python run_api.py --port 3000        # Ejecutar en puerto 3000
  python run_api.py --reload           # Ejecutar con auto-reload
  python run_api.py --host 0.0.0.0 --port 8080 --reload  # Configuración completa
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para ejecutar el servidor (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto para ejecutar el servidor (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Ejecutar con auto-reload para desarrollo"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Nivel de logging (default: info)"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Verificar configuración
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️  Archivo .env no encontrado. Usando configuración por defecto.")
        logger.info("💡 Crea un archivo .env con tu API key de Gemini:")
        logger.info("   GEMINI_API_KEY=tu_api_key_aqui")
    
    # Mostrar información de inicio
    logger.info("🐝 HiveMind Architecture API Server")
    logger.info("=" * 50)
    logger.info(f"🌐 Host: {args.host}")
    logger.info(f"🔌 Puerto: {args.port}")
    logger.info(f"🔄 Auto-reload: {'Sí' if args.reload else 'No'}")
    logger.info(f"📊 Log level: {args.log_level}")
    logger.info("=" * 50)
    
    if args.reload:
        logger.info("🚀 Iniciando servidor en modo desarrollo...")
    else:
        logger.info("🚀 Iniciando servidor en modo producción...")
    
    logger.info(f"📖 Documentación disponible en: http://{args.host}:{args.port}/docs")
    logger.info(f"🔍 API Info disponible en: http://{args.host}:{args.port}/api/v1/info")
    logger.info(f"❤️  Health check disponible en: http://{args.host}:{args.port}/api/v1/health")
    
    try:
        # Ejecutar servidor
        run_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error ejecutando servidor: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
