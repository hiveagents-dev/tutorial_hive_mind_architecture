#!/usr/bin/env python3
"""
Script de prueba para el Frontend HiveMind
Simula la interacción del usuario con la interfaz web
"""

import requests
import json
import time
from datetime import datetime

class HiveMindFrontendTester:
    def __init__(self, frontend_url="http://localhost:3002", api_url="http://localhost:8002"):
        self.frontend_url = frontend_url
        self.api_url = api_url
        self.test_results = []
    
    def test_frontend_access(self):
        """Prueba el acceso al frontend"""
        print("🌐 Probando acceso al Frontend...")
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Frontend accesible correctamente")
                return True
            else:
                print(f"❌ Frontend no accesible: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accediendo al frontend: {e}")
            return False
    
    def test_api_connection(self):
        """Prueba la conexión con la API"""
        print("🔌 Probando conexión con la API...")
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API conectada: {data['status']}")
                return True
            else:
                print(f"❌ API no responde: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando con la API: {e}")
            return False
    
    def test_api_info(self):
        """Prueba el endpoint de información de la API"""
        print("📊 Probando información de metodologías...")
        try:
            response = requests.get(f"{self.api_url}/api/v1/info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                methodologies = data.get('methodologies', [])
                print(f"✅ Metodologías disponibles: {len(methodologies)}")
                for method in methodologies:
                    print(f"   - {method['name']}: {method['description']}")
                return True
            else:
                print(f"❌ Error obteniendo información: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en endpoint de información: {e}")
            return False
    
    def test_analysis_request(self, business_need, methodology="scrum"):
        """Prueba un análisis completo"""
        print(f"🔍 Probando análisis: '{business_need[:50]}...'")
        print(f"📋 Metodología: {methodology}")
        
        start_time = time.time()
        
        try:
            payload = {
                "business_need": business_need,
                "methodology": methodology,
                "consensus_strategy": "weighted_voting",
                "verbose": True
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/analyze",
                json=payload,
                timeout=300  # 5 minutos timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "success": True,
                    "duration": duration,
                    "methodology": data.get("methodology"),
                    "execution_time": data.get("execution_time"),
                    "consensus_achieved": data.get("consensus_result", {}).get("achieved"),
                    "consensus_level": data.get("consensus_result", {}).get("consensus_level"),
                    "worker_responses": len(data.get("worker_responses", [])),
                    "business_need": business_need
                }
                
                print(f"✅ Análisis completado exitosamente")
                print(f"   ⏱️  Tiempo total: {duration:.2f}s")
                print(f"   ⚡ Tiempo ejecución: {data.get('execution_time', 0):.2f}s")
                print(f"   🤝 Consenso: {'Sí' if result['consensus_achieved'] else 'No'} ({result['consensus_level']*100:.1f}%)")
                print(f"   👥 Agentes worker: {result['worker_responses']}")
                
                # Mostrar resumen de respuestas de agentes
                worker_responses = data.get("worker_responses", [])
                print(f"   📋 Resumen de agentes:")
                for agent in worker_responses:
                    confidence = agent.get("confidence", 0) * 100
                    print(f"      - {agent.get('agent_name', 'Unknown')}: {confidence:.1f}% confianza")
                
                self.test_results.append(result)
                return True
                
            else:
                print(f"❌ Error en análisis: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Timeout en el análisis (más de 5 minutos)")
            return False
        except Exception as e:
            print(f"❌ Error durante análisis: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Ejecuta una batería completa de pruebas"""
        print("🚀 Iniciando pruebas completas del Frontend HiveMind")
        print("=" * 60)
        
        tests = [
            ("Acceso Frontend", self.test_frontend_access),
            ("Conexión API", self.test_api_connection),
            ("Información API", self.test_api_info),
        ]
        
        # Ejecutar pruebas básicas
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            success = test_func()
            if not success:
                print(f"❌ Prueba fallida: {test_name}")
                return False
        
        # Ejecutar análisis de prueba
        test_cases = [
            "Necesitamos una plataforma de e-learning para capacitar empleados en habilidades técnicas",
            "Queremos desarrollar una aplicación móvil para gestión de inventario en tiempo real",
            "Necesitamos un sistema de CRM para gestionar clientes y ventas"
        ]
        
        print(f"\n🔍 Ejecutando {len(test_cases)} análisis de prueba")
        print("-" * 40)
        
        for i, business_need in enumerate(test_cases, 1):
            print(f"\n📊 Análisis {i}/{len(test_cases)}")
            success = self.test_analysis_request(business_need)
            if not success:
                print(f"❌ Análisis {i} falló")
                return False
            
            # Pausa entre análisis
            if i < len(test_cases):
                print("⏳ Esperando 5 segundos antes del siguiente análisis...")
                time.sleep(5)
        
        # Resumen final
        print(f"\n🎉 Pruebas completadas exitosamente!")
        print("=" * 60)
        print(f"📊 Resumen de resultados:")
        print(f"   ✅ Análisis exitosos: {len(self.test_results)}")
        print(f"   ⏱️  Tiempo promedio: {sum(r['duration'] for r in self.test_results)/len(self.test_results):.2f}s")
        print(f"   🤝 Consenso promedio: {sum(r['consensus_level'] for r in self.test_results)/len(self.test_results)*100:.1f}%")
        
        return True
    
    def generate_report(self):
        """Genera un reporte detallado de las pruebas"""
        if not self.test_results:
            return "No hay resultados para reportar"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": self.frontend_url,
            "api_url": self.api_url,
            "total_tests": len(self.test_results),
            "successful_tests": len([r for r in self.test_results if r["success"]]),
            "average_duration": sum(r["duration"] for r in self.test_results) / len(self.test_results),
            "average_consensus": sum(r["consensus_level"] for r in self.test_results) / len(self.test_results),
            "test_results": self.test_results
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)

def main():
    """Función principal"""
    print("🐝 HiveMind Frontend Tester")
    print("=" * 40)
    
    tester = HiveMindFrontendTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n📄 Generando reporte...")
            report = tester.generate_report()
            
            # Guardar reporte
            with open("frontend_test_report.json", "w", encoding="utf-8") as f:
                f.write(report)
            
            print(f"✅ Reporte guardado en: frontend_test_report.json")
            print(f"\n🌐 Frontend disponible en: http://localhost:3002")
            print(f"📖 API disponible en: http://localhost:8002")
            print(f"📚 Documentación API: http://localhost:8002/docs")
            
        else:
            print(f"\n❌ Las pruebas fallaron. Revisa los logs anteriores.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
