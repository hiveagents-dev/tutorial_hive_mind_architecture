#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json

async def test_dispatch_directly():
    print("🔍 Probando dispatch directamente en el contexto React...")
    
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
            
            # Inyectar código para probar el dispatch directamente
            print("🔍 Probando dispatch directamente...")
            dispatch_result = await page.evaluate("""
                async () => {
                    try {
                        // Buscar el botón de análisis
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const analyzeButton = buttons.find(btn => btn.textContent.includes('Ejecutar Análisis'));
                        
                        if (!analyzeButton) {
                            return { error: 'Botón no encontrado' };
                        }
                        
                        // Verificar el estado inicial
                        const initialState = {
                            loading: document.querySelector('.loading-overlay') ? 'presente' : 'ausente',
                            error: document.querySelector('.error-toast') ? 'presente' : 'ausente'
                        };
                        
                        // Simular el clic del botón
                        analyzeButton.click();
                        
                        // Esperar un poco
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        // Verificar el estado después del clic
                        const afterClickState = {
                            loading: document.querySelector('.loading-overlay') ? 'presente' : 'ausente',
                            error: document.querySelector('.error-toast') ? 'presente' : 'ausente'
                        };
                        
                        // Verificar si hay elementos de loading en el DOM
                        const loadingElements = document.querySelectorAll('[class*="loading"], .loading-overlay, .loading-spinner');
                        const loadingInfo = Array.from(loadingElements).map(el => ({
                            className: el.className,
                            textContent: el.textContent,
                            visible: el.offsetParent !== null
                        }));
                        
                        return {
                            success: true,
                            initialState,
                            afterClickState,
                            loadingElements: loadingInfo,
                            buttonDisabled: analyzeButton.disabled
                        };
                        
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message
                        };
                    }
                }
            """)
            
            print(f"Resultado del dispatch: {dispatch_result}")
            
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
            await page.screenshot(path="dispatch-test.png")
            print("📸 Screenshot guardado")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR durante la prueba: {e}")
            await page.screenshot(path="dispatch-test-error.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_dispatch_directly())
    print(f"\n🔍 RESULTADO DE LA PRUEBA: {'EXITOSO' if result else 'FALLIDO'}")
