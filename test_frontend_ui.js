#!/usr/bin/env node

// Script para probar el frontend React desde la UI
const puppeteer = require('puppeteer');

async function testFrontend() {
  console.log('🚀 Iniciando prueba del frontend React...');
  
  const browser = await puppeteer.launch({ 
    headless: false, // Mostrar el navegador
    devtools: true,  // Abrir DevTools
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Configurar console logging
  page.on('console', msg => {
    console.log('CONSOLE:', msg.text());
  });
  
  // Configurar error logging
  page.on('pageerror', error => {
    console.error('PAGE ERROR:', error.message);
  });
  
  try {
    console.log('📱 Navegando a http://localhost:3002...');
    await page.goto('http://localhost:3002', { waitUntil: 'networkidle0' });
    
    // Esperar a que React cargue
    await page.waitForSelector('#root', { timeout: 10000 });
    console.log('✅ React cargado correctamente');
    
    // Verificar que el estado de la API sea "Conectado"
    await page.waitForSelector('.api-status.connected', { timeout: 10000 });
    console.log('✅ API conectada');
    
    // Navegar a la vista de Análisis
    console.log('🔍 Navegando a la vista de Análisis...');
    await page.click('li[data-section="analyze"], .nav-item:has-text("Analizar")');
    await page.waitForTimeout(1000);
    
    // Verificar que el formulario esté presente
    await page.waitForSelector('textarea[id="businessNeed"]', { timeout: 5000 });
    console.log('✅ Formulario de análisis cargado');
    
    // Escribir una necesidad de negocio
    console.log('✍️ Escribiendo necesidad de negocio...');
    await page.type('textarea[id="businessNeed"]', 'Sistema de gestión de inventario para farmacia con control de vencimientos');
    
    // Verificar que el botón esté habilitado
    const button = await page.$('button:has-text("Ejecutar Análisis")');
    const isDisabled = await page.evaluate(el => el.disabled, button);
    
    if (isDisabled) {
      console.log('❌ ERROR: El botón "Ejecutar Análisis" está deshabilitado');
      return;
    }
    
    console.log('✅ Botón "Ejecutar Análisis" habilitado');
    
    // Hacer clic en el botón
    console.log('🚀 Ejecutando análisis...');
    await button.click();
    
    // Esperar a que aparezca el estado de loading
    await page.waitForSelector('.loading-overlay', { timeout: 5000 });
    console.log('⏳ Análisis iniciado (loading visible)');
    
    // Esperar a que termine el análisis (desaparece el loading)
    await page.waitForFunction(() => !document.querySelector('.loading-overlay'), { timeout: 120000 });
    console.log('✅ Análisis completado');
    
    // Verificar que aparezcan los resultados
    await page.waitForSelector('.analysis-results', { timeout: 10000 });
    console.log('✅ Resultados del análisis mostrados');
    
    // Verificar que aparezcan las tarjetas de agentes
    await page.waitForSelector('.agent-card', { timeout: 5000 });
    const agentCards = await page.$$('.agent-card');
    console.log(`✅ ${agentCards.length} tarjetas de agentes mostradas`);
    
    // Probar el botón "Ver Completo"
    const verCompletoButton = await page.$('.agent-actions button:has-text("Ver Completo")');
    if (verCompletoButton) {
      console.log('🔍 Probando botón "Ver Completo"...');
      await verCompletoButton.click();
      
      // Verificar que aparezca el modal
      await page.waitForSelector('.modal-overlay', { timeout: 5000 });
      console.log('✅ Modal de contenido completo abierto');
      
      // Cerrar el modal
      await page.click('.modal-close');
      await page.waitForFunction(() => !document.querySelector('.modal-overlay'), { timeout: 5000 });
      console.log('✅ Modal cerrado correctamente');
    }
    
    console.log('🎉 ¡Todas las pruebas pasaron exitosamente!');
    
  } catch (error) {
    console.error('❌ ERROR durante la prueba:', error.message);
    
    // Tomar screenshot del error
    await page.screenshot({ path: 'error-screenshot.png' });
    console.log('📸 Screenshot guardado como error-screenshot.png');
  } finally {
    await browser.close();
  }
}

// Ejecutar solo si puppeteer está disponible
if (require.main === module) {
  testFrontend().catch(console.error);
}

module.exports = testFrontend;
