#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def capture_js_errors():
    print("🔍 Capturando errores de JavaScript en tiempo real...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        # Capturar todos los errores y logs
        errors = []
        logs = []
        
        page.on("console", lambda msg: logs.append(f"CONSOLE {msg.type}: {msg.text}"))
        page.on("pageerror", lambda error: errors.append(f"PAGE ERROR: {error}"))
        page.on("requestfailed", lambda req: errors.append(f"REQUEST FAILED: {req.url} - {req.failure}"))
        
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
            
            # Hacer clic en el botón y capturar errores
            print("🚀 Ejecutando análisis y capturando errores...")
            analyze_button = page.locator("button").filter(has_text="Ejecutar Análisis")
            await analyze_button.click()
            
            # Esperar y capturar errores
            await page.wait_for_timeout(5000)
            
            # Verificar si hay errores
            if errors:
                print("❌ ERRORES ENCONTRADOS:")
                for error in errors:
                    print(f"   {error}")
            else:
                print("✅ No se encontraron errores de JavaScript")
            
            # Verificar logs
            if logs:
                print("📝 LOGS DE CONSOLA:")
                for log in logs:
                    print(f"   {log}")
            
            # Verificar el estado del loading
            loading_state = await page.evaluate("""
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
            print(f"Estado final: {loading_state}")
            
            # Tomar screenshot
            await page.screenshot(path="js-errors-screenshot.png")
            print("📸 Screenshot guardado")
            
            return len(errors) == 0
            
        except Exception as e:
            print(f"❌ ERROR durante la captura: {e}")
            await page.screenshot(path="capture-error-screenshot.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(capture_js_errors())
    print(f"\n🔍 RESULTADO: {'SIN ERRORES' if result else 'CON ERRORES'}")
