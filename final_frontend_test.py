#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def final_frontend_test():
    print("🎯 PRUEBA FINAL COMPLETA DEL FRONTEND REACT")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        # Capturar logs de consola
        logs = []
        page.on("console", lambda msg: logs.append(f"CONSOLE {msg.type}: {msg.text}"))
        
        try:
            # Navegar a la aplicación
            print("📱 Navegando a http://localhost:3002...")
            await page.goto("http://localhost:3002", wait_until="networkidle")
            
            # Esperar a que React cargue
            await page.wait_for_selector("#root")
            print("✅ React cargado correctamente")
            
            # Navegar a la vista de Análisis
            print("🔍 Navegando a la vista de Análisis...")
            analyze_nav = page.locator(".nav-item").filter(has_text="Analizar")
            await analyze_nav.click()
            await page.wait_for_timeout(2000)
            
            # Escribir necesidad de negocio
            print("✍️ Escribiendo necesidad de negocio...")
            await page.fill("#businessNeed", "Wallet B2B crossborder LATAM con compliance y FX")
            
            # Hacer clic en el botón
            print("🚀 Ejecutando análisis...")
            analyze_button = page.locator("button").filter(has_text="Ejecutar Análisis")
            await analyze_button.click()
            
            # Esperar a que aparezca el loading overlay
            print("⏳ Esperando loading overlay...")
            try:
                await page.wait_for_selector(".loading-overlay", timeout=10000)
                print("✅ Loading overlay apareció")
            except:
                print("❌ Loading overlay no apareció en 10 segundos")
            
            # Esperar a que termine el análisis
            print("⏳ Esperando que termine el análisis...")
            try:
                await page.wait_for_function("() => !document.querySelector('.loading-overlay')", timeout=120000)
                print("✅ Análisis completado")
            except:
                print("❌ Análisis no completado en 2 minutos")
            
            # Verificar resultados
            try:
                await page.wait_for_selector(".analysis-results", timeout=10000)
                print("✅ Resultados del análisis mostrados")
            except:
                print("❌ Resultados del análisis no aparecieron")
            
            # Contar tarjetas de agentes
            agent_cards = await page.locator(".agent-card").count()
            print(f"✅ {agent_cards} tarjetas de agentes mostradas")
            
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
            
            # Mostrar logs de consola
            print("\n📝 LOGS DE CONSOLA:")
            for log in logs:
                print(f"   {log}")
            
            # Verificar estado final
            final_state = await page.evaluate("""
                () => {
                    const loading = document.querySelector('.loading-overlay');
                    const error = document.querySelector('.error-toast');
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const analyzeButton = buttons.find(btn => btn.textContent.includes('Ejecutar Análisis'));
                    
                    return {
                        loading: loading ? 'presente' : 'ausente',
                        error: error ? error.textContent : 'ninguno',
                        buttonDisabled: analyzeButton ? analyzeButton.disabled : 'no encontrado'
                    };
                }
            """)
            
            print(f"\nEstado final: {final_state}")
            
            print("\n🎉 ¡PRUEBA FINAL COMPLETADA!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante la prueba: {e}")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(final_frontend_test())
    print(f"\n🏆 RESULTADO FINAL: {'✅ EXITOSO' if result else '❌ FALLIDO'}")
