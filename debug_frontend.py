#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_frontend():
    print("🔍 Debugging frontend React con Playwright...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
        # Configurar console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda error: print(f"PAGE ERROR: {error}"))
        
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
            await page.wait_for_timeout(2000)
            
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
            
            # Verificar el estado del contexto antes de hacer clic
            print("🔍 Verificando estado del contexto...")
            context_state = await page.evaluate("""
                () => {
                    // Intentar acceder al estado del contexto
                    const root = document.querySelector('#root');
                    if (root && root._reactInternalFiber) {
                        return 'React fiber encontrado';
                    }
                    return 'No se puede acceder al estado interno';
                }
            """)
            print(f"Estado del contexto: {context_state}")
            
            # Hacer clic en el botón
            print("🚀 Ejecutando análisis...")
            await analyze_button.click()
            
            # Esperar un poco y verificar si hay errores en consola
            await page.wait_for_timeout(2000)
            
            # Verificar si aparece el loading overlay
            loading_exists = await page.locator(".loading-overlay").count() > 0
            print(f"Loading overlay presente: {loading_exists}")
            
            # Verificar si hay errores en la consola
            print("🔍 Verificando errores en consola...")
            
            # Verificar el estado de loading en el estado de React
            loading_state = await page.evaluate("""
                () => {
                    // Buscar elementos que indiquen loading
                    const loadingElements = document.querySelectorAll('.loading-overlay, .loading-spinner, [class*="loading"]');
                    return {
                        loadingElements: loadingElements.length,
                        loadingText: Array.from(loadingElements).map(el => el.textContent)
                    };
                }
            """)
            print(f"Estado de loading: {loading_state}")
            
            # Verificar si hay errores en el estado
            error_state = await page.evaluate("""
                () => {
                    const errorElements = document.querySelectorAll('.error-toast, .alert-error, [class*="error"]');
                    return {
                        errorElements: errorElements.length,
                        errorText: Array.from(errorElements).map(el => el.textContent)
                    };
                }
            """)
            print(f"Estado de errores: {error_state}")
            
            # Esperar más tiempo para ver si aparece el loading
            print("⏳ Esperando loading overlay...")
            try:
                await page.wait_for_selector(".loading-overlay", timeout=10000)
                print("✅ Loading overlay apareció")
            except:
                print("❌ Loading overlay no apareció en 10 segundos")
            
            # Tomar screenshot final
            await page.screenshot(path="debug-screenshot.png")
            print("📸 Screenshot de debug guardado")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante el debug: {e}")
            await page.screenshot(path="debug-error-screenshot.png")
            print("📸 Screenshot de error guardado")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(debug_frontend())
    print(f"\n🔍 RESULTADO DEL DEBUG: {'EXITOSO' if result else 'FALLIDO'}")
