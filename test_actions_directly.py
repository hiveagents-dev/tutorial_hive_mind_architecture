#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def test_actions_directly():
    print("🔍 Probando actions.analyzeBusinessNeed directamente...")
    
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
            
            # Inyectar código para probar actions.analyzeBusinessNeed directamente
            print("🔍 Probando actions.analyzeBusinessNeed directamente...")
            test_result = await page.evaluate("""
                async () => {
                    try {
                        // Buscar el botón de análisis
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const analyzeButton = buttons.find(btn => btn.textContent.includes('Ejecutar Análisis'));
                        
                        if (!analyzeButton) {
                            return { error: 'Botón no encontrado' };
                        }
                        
                        // Simular el clic del botón
                        analyzeButton.click();
                        
                        // Esperar un poco
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        
                        // Verificar si apareció el loading
                        const loading = document.querySelector('.loading-overlay');
                        
                        // Verificar si hay errores en la consola
                        const consoleErrors = [];
                        const originalError = console.error;
                        console.error = (...args) => {
                            consoleErrors.push(args.join(' '));
                            originalError.apply(console, args);
                        };
                        
                        // Verificar el estado del contexto
                        const contextState = {
                            loading: loading ? 'presente' : 'ausente',
                            buttonDisabled: analyzeButton.disabled
                        };
                        
                        return {
                            success: true,
                            contextState,
                            consoleErrors
                        };
                        
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message
                        };
                    }
                }
            """)
            
            print(f"Resultado de la prueba: {test_result}")
            
            # Esperar más tiempo para ver si aparece el loading
            await page.wait_for_timeout(5000)
            
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
            await page.screenshot(path="actions-test.png")
            print("📸 Screenshot guardado")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante la prueba: {e}")
            await page.screenshot(path="actions-test-error.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_actions_directly())
    print(f"\n🔍 RESULTADO DE LA PRUEBA: {'EXITOSO' if result else 'FALLIDO'}")
