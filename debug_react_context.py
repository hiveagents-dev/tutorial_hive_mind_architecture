#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_react_context():
    print("🔍 Debugging React Context directamente...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, devtools=True)
        page = await browser.new_page()
        
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
            
            # Inyectar código de debug en el contexto React
            print("🔍 Inyectando código de debug...")
            debug_result = await page.evaluate("""
                () => {
                    // Buscar el botón de análisis
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const analyzeButton = buttons.find(btn => btn.textContent.includes('Ejecutar Análisis'));
                    
                    if (!analyzeButton) {
                        return { error: 'Botón no encontrado' };
                    }
                    
                    // Verificar si el botón tiene el event listener
                    const hasClickListener = analyzeButton.onclick !== null;
                    
                    // Simular el clic y capturar errores
                    let clickError = null;
                    try {
                        analyzeButton.click();
                    } catch (e) {
                        clickError = e.message;
                    }
                    
                    // Verificar el estado después del clic
                    const loading = document.querySelector('.loading-overlay');
                    const error = document.querySelector('.error-toast');
                    
                    return {
                        buttonFound: true,
                        hasClickListener,
                        clickError,
                        loadingPresent: loading !== null,
                        errorPresent: error !== null,
                        buttonDisabled: analyzeButton.disabled
                    };
                }
            """)
            
            print(f"Resultado del debug: {debug_result}")
            
            # Esperar un poco más para ver si aparece el loading
            await page.wait_for_timeout(3000)
            
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
            
            # Tomar screenshot
            await page.screenshot(path="react-context-debug.png")
            print("📸 Screenshot guardado")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante el debug: {e}")
            await page.screenshot(path="react-debug-error.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(debug_react_context())
    print(f"\n🔍 RESULTADO DEL DEBUG: {'EXITOSO' if result else 'FALLIDO'}")
