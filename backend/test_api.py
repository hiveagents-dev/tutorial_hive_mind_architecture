#!/usr/bin/env python3
"""Script para probar la API REST de HiveMind"""

import requests
import json
import time
from typing import Dict, Any

class HiveMindAPIClient:
    """Cliente para la API REST de HiveMind"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar estado del servicio"""
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema"""
        response = self.session.get(f"{self.base_url}/api/v1/info")
        response.raise_for_status()
        return response.json()
    
    def get_methodologies(self) -> Dict[str, Any]:
        """Obtener todas las metodologías"""
        response = self.session.get(f"{self.base_url}/api/v1/methodologies")
        response.raise_for_status()
        return response.json()
    
    def get_consensus_strategies(self) -> Dict[str, Any]:
        """Obtener estrategias de consenso"""
        response = self.session.get(f"{self.base_url}/api/v1/consensus-strategies")
        response.raise_for_status()
        return response.json()
    
    def analyze_business_need(
        self,
        business_need: str,
        methodology: str = "scrum",
        consensus_strategy: str = "weighted_voting",
        verbose: bool = True
    ) -> Dict[str, Any]:
        """Analizar necesidad de negocio"""
        payload = {
            "business_need": business_need,
            "methodology": methodology,
            "consensus_strategy": consensus_strategy,
            "verbose": verbose
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/analyze",
            json=payload,
            timeout=300  # 5 minutos timeout
        )
        response.raise_for_status()
        return response.json()
    
    def run_example(self) -> Dict[str, Any]:
        """Ejecutar ejemplo predefinido"""
        response = self.session.post(f"{self.base_url}/api/v1/example")
        response.raise_for_status()
        return response.json()


def test_api():
    """Probar la API REST"""
    print("🧪 PROBANDO API REST DE HIVEMIND")
    print("=" * 50)
    
    client = HiveMindAPIClient()
    
    try:
        # 1. Health Check
        print("\n1️⃣ Health Check")
        print("-" * 20)
        health = client.health_check()
        print(f"✅ Status: {health['status']}")
        print(f"📊 Version: {health['version']}")
        print(f"🔗 Dependencies: {health['dependencies']}")
        
        # 2. System Info
        print("\n2️⃣ System Info")
        print("-" * 20)
        info = client.get_system_info()
        print(f"🏷️  Name: {info['name']}")
        print(f"📊 Version: {info['version']}")
        print(f"📝 Description: {info['description']}")
        print(f"🔧 Features: {len(info['features'])} features")
        print(f"📋 Methodologies: {len(info['methodologies'])} methodologies")
        
        # 3. Methodologies
        print("\n3️⃣ Methodologies")
        print("-" * 20)
        methodologies = client.get_methodologies()
        for name, details in methodologies.items():
            print(f"📋 {name.upper()}: {details['description'][:50]}...")
        
        # 4. Consensus Strategies
        print("\n4️⃣ Consensus Strategies")
        print("-" * 20)
        strategies = client.get_consensus_strategies()
        print(f"🎯 Available strategies: {list(strategies['strategies'].keys())}")
        print(f"⚙️  Default: {strategies['default']}")
        
        # 5. Example Analysis
        print("\n5️⃣ Example Analysis")
        print("-" * 20)
        print("🔄 Ejecutando análisis de ejemplo...")
        start_time = time.time()
        
        example_result = client.run_example()
        
        execution_time = time.time() - start_time
        print(f"✅ Análisis completado en {execution_time:.2f}s")
        print(f"📊 Execution time: {example_result['execution_time']:.2f}s")
        print(f"🎯 Methodology: {example_result['methodology']}")
        print(f"🤝 Consensus level: {example_result['consensus_result']['consensus_level']:.2f}")
        print(f"👥 Workers: {len(example_result['worker_responses'])}")
        print(f"🎯 Final confidence: {example_result['supervisor_response']['confidence']:.2f}")
        
        # Mostrar resumen de workers
        print(f"\n📋 Workers Summary:")
        for worker in example_result['worker_responses']:
            print(f"   {worker['agent_name']}: {worker['confidence']:.2f} confidence")
        
        # 6. Custom Analysis
        print("\n6️⃣ Custom Analysis")
        print("-" * 20)
        
        custom_business_need = """
        Necesitamos desarrollar una plataforma de e-learning para una universidad.
        La plataforma debe permitir a los estudiantes acceder a cursos online,
        realizar exámenes, interactuar con profesores y obtener certificados.
        También debe incluir herramientas de administración para profesores.
        """
        
        print("🔄 Ejecutando análisis personalizado con SAFe...")
        start_time = time.time()
        
        custom_result = client.analyze_business_need(
            business_need=custom_business_need.strip(),
            methodology="safe",
            consensus_strategy="weighted_voting",
            verbose=True
        )
        
        execution_time = time.time() - start_time
        print(f"✅ Análisis personalizado completado en {execution_time:.2f}s")
        print(f"📊 Execution time: {custom_result['execution_time']:.2f}s")
        print(f"🎯 Methodology: {custom_result['methodology']}")
        print(f"🤝 Consensus level: {custom_result['consensus_result']['consensus_level']:.2f}")
        print(f"👥 Workers: {len(custom_result['worker_responses'])}")
        print(f"🎯 Final confidence: {custom_result['supervisor_response']['confidence']:.2f}")
        
        # Mostrar resumen de workers
        print(f"\n📋 Workers Summary:")
        for worker in custom_result['worker_responses']:
            print(f"   {worker['agent_name']}: {worker['confidence']:.2f} confidence")
        
        print(f"\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("=" * 50)
        print("✅ Health check: OK")
        print("✅ System info: OK")
        print("✅ Methodologies: OK")
        print("✅ Consensus strategies: OK")
        print("✅ Example analysis: OK")
        print("✅ Custom analysis: OK")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python run_api.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout en la solicitud")
        print("💡 El análisis puede tomar varios minutos, intenta de nuevo")
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print(f"📊 Status code: {e.response.status_code}")
        print(f"📝 Response: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Probar la API REST de HiveMind")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="URL base de la API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    print(f"🌐 Probando API en: {args.url}")
    
    success = test_api()
    
    if success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron")
        exit(1)


if __name__ == "__main__":
    main()
