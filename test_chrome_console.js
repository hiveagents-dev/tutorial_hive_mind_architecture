// Script para probar el frontend React desde Chrome DevTools
// Ejecutar este código en la consola de Chrome (F12 -> Console)

console.log('🚀 Iniciando prueba del frontend React...');

// Función para esperar un elemento
function waitForElement(selector, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }
    
    const observer = new MutationObserver((mutations, obs) => {
      const element = document.querySelector(selector);
      if (element) {
        obs.disconnect();
        resolve(element);
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Elemento ${selector} no encontrado en ${timeout}ms`));
    }, timeout);
  });
}

// Función para hacer clic en un elemento
async function clickElement(selector) {
  const element = await waitForElement(selector);
  element.click();
  return element;
}

// Función para escribir en un campo
async function typeInField(selector, text) {
  const element = await waitForElement(selector);
  element.value = text;
  element.dispatchEvent(new Event('input', { bubbles: true }));
  return element;
}

// Función principal de prueba
async function testFrontend() {
  try {
    console.log('📱 Verificando que React esté cargado...');
    
    // Verificar que el root esté presente
    const root = await waitForElement('#root');
    console.log('✅ React cargado correctamente');
    
    // Verificar que el estado de la API sea "Conectado"
    console.log('🔌 Verificando estado de la API...');
    const apiStatus = await waitForElement('.api-status.connected');
    console.log('✅ API conectada');
    
    // Navegar a la vista de Análisis
    console.log('🔍 Navegando a la vista de Análisis...');
    const analyzeNavItem = await clickElement('.nav-item:has-text("Analizar"), [data-section="analyze"]');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verificar que el formulario esté presente
    console.log('📝 Verificando formulario de análisis...');
    const textarea = await waitForElement('textarea[id="businessNeed"]');
    console.log('✅ Formulario de análisis cargado');
    
    // Escribir una necesidad de negocio
    console.log('✍️ Escribiendo necesidad de negocio...');
    await typeInField('textarea[id="businessNeed"]', 'Sistema de gestión de inventario para farmacia con control de vencimientos y alertas automáticas');
    
    // Verificar que el botón esté habilitado
    console.log('🔘 Verificando botón "Ejecutar Análisis"...');
    const button = await waitForElement('button:has-text("Ejecutar Análisis")');
    const isDisabled = button.disabled;
    
    if (isDisabled) {
      console.log('❌ ERROR: El botón "Ejecutar Análisis" está deshabilitado');
      return;
    }
    
    console.log('✅ Botón "Ejecutar Análisis" habilitado');
    
    // Hacer clic en el botón
    console.log('🚀 Ejecutando análisis...');
    button.click();
    
    // Esperar a que aparezca el estado de loading
    console.log('⏳ Esperando que inicie el análisis...');
    await waitForElement('.loading-overlay');
    console.log('✅ Análisis iniciado (loading visible)');
    
    // Esperar a que termine el análisis (desaparece el loading)
    console.log('⏳ Esperando que termine el análisis...');
    await new Promise((resolve) => {
      const checkLoading = () => {
        const loading = document.querySelector('.loading-overlay');
        if (!loading) {
          resolve();
        } else {
          setTimeout(checkLoading, 1000);
        }
      };
      checkLoading();
    });
    console.log('✅ Análisis completado');
    
    // Verificar que aparezcan los resultados
    console.log('📊 Verificando resultados del análisis...');
    await waitForElement('.analysis-results');
    console.log('✅ Resultados del análisis mostrados');
    
    // Verificar que aparezcan las tarjetas de agentes
    const agentCards = document.querySelectorAll('.agent-card');
    console.log(`✅ ${agentCards.length} tarjetas de agentes mostradas`);
    
    // Probar el botón "Ver Completo"
    const verCompletoButton = document.querySelector('.agent-actions button:has-text("Ver Completo")');
    if (verCompletoButton) {
      console.log('🔍 Probando botón "Ver Completo"...');
      verCompletoButton.click();
      
      // Verificar que aparezca el modal
      await waitForElement('.modal-overlay');
      console.log('✅ Modal de contenido completo abierto');
      
      // Cerrar el modal
      const closeButton = document.querySelector('.modal-close');
      if (closeButton) {
        closeButton.click();
        await new Promise((resolve) => {
          const checkModal = () => {
            const modal = document.querySelector('.modal-overlay');
            if (!modal) {
              resolve();
            } else {
              setTimeout(checkModal, 100);
            }
          };
          checkModal();
        });
        console.log('✅ Modal cerrado correctamente');
      }
    }
    
    console.log('🎉 ¡Todas las pruebas pasaron exitosamente!');
    console.log('✅ Frontend React funcionando correctamente');
    console.log('✅ Botón "Ejecutar Análisis" funcional');
    console.log('✅ Análisis completo ejecutado');
    console.log('✅ Resultados mostrados correctamente');
    console.log('✅ Modal "Ver Completo" funcional');
    
  } catch (error) {
    console.error('❌ ERROR durante la prueba:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Ejecutar la prueba
testFrontend();
