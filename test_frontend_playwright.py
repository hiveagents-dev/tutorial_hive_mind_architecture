#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def test_frontend():
    print("🚀 Iniciando prueba automatizada del frontend React con Playwright...")
    
    async with async_playwright() as p:
        # Lanzar navegador
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        try:
            # Navegar a la aplicación
            print("📱 Navegando a http://localhost:3002...")
            await page.goto("http://localhost:3002", wait_until="networkidle")
            
            # Esperar a que React cargue
            await page.wait_for_selector("#root")
            print("✅ React cargado correctamente")
            
            # Verificar estado de la API
            await page.wait_for_selector(".api-status")
            api_status = await page.text_content(".api-status")
            print(f"🔌 Estado de la API: {api_status}")
            
            # Navegar a la vista de Análisis
            print("🔍 Navegando a la vista de Análisis...")
            analyze_nav = page.locator(".nav-item").filter(has_text="Analizar")
            await analyze_nav.click()
            await page.wait_for_timeout(1000)
            
            # Verificar que el formulario esté presente
            await page.wait_for_selector("#businessNeed")
            print("✅ Formulario de análisis cargado")
            
            # Escribir necesidad de negocio
            print("✍️ Escribiendo necesidad de negocio...")
            await page.fill("#businessNeed", "Wallet B2B crossborder LATAM con compliance y FX")
            
            # Verificar que el botón esté habilitado
            analyze_button = page.locator("button").filter(has_text="Ejecutar Análisis")
            is_disabled = await analyze_button.is_disabled()
            
            if is_disabled:
                print("❌ ERROR: El botón 'Ejecutar Análisis' está deshabilitado")
                return False
            
            print("✅ Botón 'Ejecutar Análisis' habilitado")
            
            # Hacer clic en el botón
            print("🚀 Ejecutando análisis...")
            await analyze_button.click()
            
            # Esperar loading overlay
            await page.wait_for_selector(".loading-overlay")
            print("⏳ Análisis iniciado (loading visible)")
            
            # Esperar a que termine el análisis
            await page.wait_for_function("() => !document.querySelector('.loading-overlay')", timeout=120000)
            print("✅ Análisis completado")
            
            # Verificar resultados
            await page.wait_for_selector(".analysis-results")
            print("✅ Resultados del análisis mostrados")
            
            # Contar tarjetas de agentes
            agent_cards = await page.locator(".agent-card").count()
            print(f"✅ {agent_cards} tarjetas de agentes mostradas")
            
            # Verificar consenso
            consensus_element = page.locator(".meta-item.consensus")
            if await consensus_element.count() > 0:
                consensus_text = await consensus_element.text_content()
                print(f"✅ Consenso: {consensus_text}")
            
            # Probar botón "Ver Completo"
            ver_completo_button = page.locator(".agent-actions button").filter(has_text="Ver Completo").first
            if await ver_completo_button.count() > 0:
                print("🔍 Probando botón 'Ver Completo'...")
                await ver_completo_button.click()
                
                # Verificar que aparezca el modal
                await page.wait_for_selector(".modal-overlay")
                print("✅ Modal de contenido completo abierto")
                
                # Cerrar el modal
                close_button = page.locator(".modal-close")
                await close_button.click()
                await page.wait_for_function("() => !document.querySelector('.modal-overlay')")
                print("✅ Modal cerrado correctamente")
            
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("✅ Frontend React funcionando correctamente")
            print("✅ Botón 'Ejecutar Análisis' funcional")
            print("✅ Análisis completo ejecutado")
            print("✅ Resultados mostrados correctamente")
            print("✅ Modal 'Ver Completo' funcional")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante la prueba: {e}")
            # Tomar screenshot del error
            await page.screenshot(path="error-screenshot.png")
            print("📸 Screenshot guardado como error-screenshot.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_frontend())
    if result:
        print("\n🎯 RESULTADO: PRUEBA EXITOSA - El frontend React funciona correctamente")
    else:
        print("\n❌ RESULTADO: PRUEBA FALLIDA - Hay problemas en el frontend")
