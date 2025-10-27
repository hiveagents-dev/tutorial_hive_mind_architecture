#!/usr/bin/env python3
"""Script simple para probar la API REST"""

import requests
import json

def test_api_simple():
    """Probar la API con un caso simple"""
    
    print("🧪 PROBANDO API REST DE HIVEMIND")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # 1. Health Check
        print("\n1️⃣ Health Check")
        print("-" * 20)
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Status: {health['status']}")
            print(f"📊 Version: {health['version']}")
            print(f"🔗 Dependencies: {health['dependencies']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # 2. System Info
        print("\n2️⃣ System Info")
        print("-" * 20)
        response = requests.get(f"{base_url}/api/v1/info")
        if response.status_code == 200:
            info = response.json()
            print(f"🏷️  Name: {info['name']}")
            print(f"📊 Version: {info['version']}")
            print(f"📝 Description: {info['description']}")
            print(f"🔧 Features: {len(info['features'])} features")
            print(f"📋 Methodologies: {len(info['methodologies'])} methodologies")
        else:
            print(f"❌ System info failed: {response.status_code}")
            return False
        
        # 3. Methodologies
        print("\n3️⃣ Methodologies")
        print("-" * 20)
        response = requests.get(f"{base_url}/api/v1/methodologies")
        if response.status_code == 200:
            methodologies = response.json()
            for name, details in methodologies.items():
                print(f"📋 {name.upper()}: {details['description'][:50]}...")
        else:
            print(f"❌ Methodologies failed: {response.status_code}")
            return False
        
        # 4. Consensus Strategies
        print("\n4️⃣ Consensus Strategies")
        print("-" * 20)
        response = requests.get(f"{base_url}/api/v1/consensus-strategies")
        if response.status_code == 200:
            strategies = response.json()
            print(f"🎯 Available strategies: {list(strategies['strategies'].keys())}")
            print(f"⚙️  Default: {strategies['default']}")
        else:
            print(f"❌ Consensus strategies failed: {response.status_code}")
            return False
        
        print(f"\n🎉 TODAS LAS PRUEBAS BÁSICAS COMPLETADAS EXITOSAMENTE!")
        print("=" * 50)
        print("✅ Health check: OK")
        print("✅ System info: OK")
        print("✅ Methodologies: OK")
        print("✅ Consensus strategies: OK")
        print("\n💡 La API REST está funcionando correctamente!")
        print("📖 Documentación disponible en: http://127.0.0.1:8001/docs")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   source .venv/bin/activate && python run_api.py --host 127.0.0.1 --port 8001")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_api_simple()
    if success:
        print("\n🎉 ¡API REST funcionando correctamente!")
        exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron")
        exit(1)
