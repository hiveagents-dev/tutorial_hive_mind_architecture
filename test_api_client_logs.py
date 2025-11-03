#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def test_api_client_logs():
    print("🔍 Probando frontend con logs del cliente API...")
    
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
            
            # Esperar y capturar logs
            await page.wait_for_timeout(8000)
            
            # Mostrar logs de consola
            print("📝 LOGS DE CONSOLA:")
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
            
            print(f"Estado final: {final_state}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante la prueba: {e}")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_api_client_logs())
    print(f"\n🔍 RESULTADO: {'EXITOSO' if result else 'FALLIDO'}")
