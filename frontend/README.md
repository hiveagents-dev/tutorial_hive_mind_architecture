# Frontend HiveMind Architecture

## Descripción

Interfaz web moderna y responsive para interactuar con el sistema HiveMind Architecture. Proporciona una experiencia de usuario completa para gestionar análisis de necesidades de negocio y visualizar resultados de agentes AI.

## Características

### 🎯 Funcionalidades Principales

- **Dashboard en Tiempo Real**: Monitoreo del estado del sistema y métricas
- **Formulario de Análisis**: Interfaz intuitiva para ingresar necesidades de negocio
- **Selector de Metodologías**: Soporte para Scrum, SAFe y Kanban
- **Visualización de Resultados**: Presentación detallada de análisis de agentes
- **Historial de Análisis**: Gestión y revisión de análisis anteriores
- **Configuración Avanzada**: Personalización del sistema

### 🎨 Diseño y UX

- **Diseño Responsive**: Optimizado para desktop, tablet y móvil
- **Tema Claro/Oscuro**: Soporte para múltiples temas visuales
- **Interfaz Moderna**: Diseño limpio con componentes interactivos
- **Notificaciones Toast**: Feedback inmediato de acciones del usuario
- **Loading States**: Indicadores de progreso durante análisis

### 🔧 Integración Técnica

- **API REST**: Integración completa con el backend HiveMind
- **Almacenamiento Local**: Persistencia de configuraciones e historial
- **Auto-refresh**: Actualización automática del estado del sistema
- **Manejo de Errores**: Gestión robusta de errores de conexión

## Estructura de Archivos

```
frontend/
├── index.html          # Página principal de la aplicación
├── styles.css          # Estilos CSS con diseño responsive
├── script.js           # Lógica JavaScript de la aplicación
└── README.md           # Documentación del frontend
```

## Uso

### 1. Acceso a la Aplicación

Abre `index.html` en tu navegador web o sirve los archivos desde un servidor web:

```bash
# Opción 1: Servidor Python simple
cd frontend
python -m http.server 8080

# Opción 2: Servidor Node.js (si tienes http-server instalado)
npx http-server -p 8080

# Opción 3: Abrir directamente
open index.html
```

### 2. Configuración Inicial

1. **Verificar Conexión**: El sistema verificará automáticamente la conexión con la API
2. **Configurar URL**: Si es necesario, ajusta la URL de la API en Configuración
3. **Seleccionar Tema**: Elige entre tema claro, oscuro o automático

### 3. Realizar Análisis

1. **Navegar a "Nuevo Análisis"**
2. **Ingresar Necesidad de Negocio**: Describe detalladamente el requerimiento
3. **Seleccionar Metodología**: Elige entre Scrum, SAFe o Kanban
4. **Configurar Consenso**: Define la estrategia de consenso
5. **Ejecutar Análisis**: Haz clic en "Iniciar Análisis"

### 4. Revisar Resultados

- **Vista Modal**: Los resultados se muestran en una ventana modal
- **Detalles por Agente**: Información específica de cada agente worker
- **Síntesis del Coordinador**: Resumen integrado de todos los agentes
- **Decisión Final**: Resultado final del supervisor
- **Descargar JSON**: Exportar resultados en formato JSON

## Secciones de la Aplicación

### 📊 Dashboard

- **Estado del Sistema**: Conexión API, estado de Gemini, agentes activos
- **Metodologías Disponibles**: Lista de metodologías soportadas
- **Análisis Recientes**: Acceso rápido a análisis anteriores

### 🔍 Nuevo Análisis

- **Formulario Completo**: Campos para necesidad de negocio, metodología y configuración
- **Información de Metodología**: Detalles dinámicos sobre la metodología seleccionada
- **Validación en Tiempo Real**: Verificación de campos requeridos

### 📚 Historial

- **Lista de Análisis**: Todos los análisis realizados anteriormente
- **Filtros**: Por metodología y fecha
- **Acciones**: Ver, descargar o eliminar análisis
- **Búsqueda**: Encontrar análisis específicos

### ⚙️ Configuración

- **Configuración General**: URL de API, timeout, auto-refresh
- **Apariencia**: Tema, idioma
- **Persistencia**: Configuraciones guardadas localmente

## API Integration

### Endpoints Utilizados

- `GET /api/v1/health` - Verificación de estado del sistema
- `GET /api/v1/info` - Información de metodologías disponibles
- `POST /api/v1/analyze` - Ejecución de análisis de necesidades de negocio
- `POST /api/v1/example` - Análisis de ejemplo (opcional)

### Manejo de Respuestas

```javascript
// Ejemplo de respuesta de análisis
{
  "success": true,
  "execution_time": 45.2,
  "methodology": "scrum",
  "consensus_result": {
    "consensus_level": 0.85,
    "achieved": true,
    "strategy_used": "weighted_voting",
    "justification": "Consenso alcanzado con alta confianza"
  },
  "worker_responses": [...],
  "coordinator_response": {...},
  "supervisor_response": {...}
}
```

## Personalización

### Temas

La aplicación soporta múltiples temas:

- **Claro**: Tema por defecto con colores claros
- **Oscuro**: Tema oscuro para uso nocturno
- **Automático**: Sigue la preferencia del sistema

### Configuración Avanzada

- **URL de API**: Configurable para diferentes entornos
- **Timeout**: Tiempo máximo de espera para análisis
- **Auto-refresh**: Actualización automática del estado
- **Idioma**: Soporte para múltiples idiomas

## Almacenamiento Local

### Datos Persistidos

- **Historial de Análisis**: Últimos 50 análisis realizados
- **Configuraciones**: Preferencias del usuario
- **Estado de la Aplicación**: Configuraciones de sesión

### Gestión de Datos

```javascript
// Ejemplo de almacenamiento
localStorage.setItem('hivemind-history', JSON.stringify(analysisHistory));
localStorage.setItem('hivemind-settings', JSON.stringify(userSettings));
```

## Responsive Design

### Breakpoints

- **Desktop**: > 1024px - Layout completo con sidebar
- **Tablet**: 768px - 1024px - Layout adaptado
- **Mobile**: < 768px - Layout vertical optimizado

### Adaptaciones Móviles

- **Navegación**: Menú horizontal deslizable
- **Formularios**: Campos optimizados para touch
- **Modales**: Adaptados a pantallas pequeñas
- **Botones**: Tamaños apropiados para dedos

## Notificaciones

### Tipos de Toast

- **Success**: Operaciones exitosas (verde)
- **Error**: Errores y fallos (rojo)
- **Warning**: Advertencias (amarillo)
- **Info**: Información general (azul)

### Auto-dismiss

Las notificaciones se eliminan automáticamente después de 5 segundos, con opción de cierre manual.

## Manejo de Errores

### Errores de Conexión

- **API Desconectada**: Indicador visual en el header
- **Timeout**: Manejo de análisis que exceden el tiempo límite
- **Errores HTTP**: Mensajes específicos según el código de error

### Recuperación Automática

- **Reintentos**: Reintento automático de conexión
- **Fallback**: Modo offline con funcionalidades limitadas
- **Notificaciones**: Información clara sobre problemas

## Rendimiento

### Optimizaciones

- **Lazy Loading**: Carga diferida de contenido pesado
- **Debouncing**: Optimización de eventos de entrada
- **Caching**: Almacenamiento local de datos frecuentes
- **Compresión**: Estilos y scripts optimizados

### Métricas

- **Tiempo de Carga**: < 2 segundos en conexiones normales
- **Tamaño**: ~50KB de recursos estáticos
- **Compatibilidad**: Navegadores modernos (Chrome, Firefox, Safari, Edge)

## Compatibilidad

### Navegadores Soportados

- **Chrome**: 80+
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

### Características Requeridas

- **ES6+**: Soporte para JavaScript moderno
- **CSS Grid**: Layout responsivo
- **Fetch API**: Comunicación con backend
- **LocalStorage**: Persistencia de datos

## Desarrollo

### Estructura del Código

```javascript
class HiveMindApp {
    constructor() {
        // Inicialización de la aplicación
    }
    
    init() {
        // Configuración inicial
    }
    
    setupEventListeners() {
        // Manejo de eventos
    }
    
    async submitAnalysis() {
        // Envío de análisis
    }
    
    showAnalysisResults(result) {
        // Visualización de resultados
    }
}
```

### Extensibilidad

- **Módulos**: Estructura modular para fácil extensión
- **Eventos**: Sistema de eventos personalizable
- **Plugins**: Soporte para funcionalidades adicionales
- **Themes**: Sistema de temas extensible

## Troubleshooting

### Problemas Comunes

1. **API No Conecta**
   - Verificar que el backend esté ejecutándose
   - Comprobar la URL de la API en configuración
   - Revisar CORS si hay problemas de dominio

2. **Análisis No Completa**
   - Verificar la API key de Gemini
   - Comprobar timeout en configuración
   - Revisar logs del backend

3. **Datos No Persisten**
   - Verificar que localStorage esté habilitado
   - Comprobar espacio disponible en el navegador
   - Limpiar datos corruptos si es necesario

### Logs de Debug

```javascript
// Habilitar logs detallados
localStorage.setItem('hivemind-debug', 'true');
```

## Contribución

### Mejoras Sugeridas

- **Tests**: Implementar tests unitarios y de integración
- **PWA**: Convertir en Progressive Web App
- **Offline**: Soporte para modo offline
- **Internacionalización**: Soporte completo para múltiples idiomas

### Estándares de Código

- **ESLint**: Linting de JavaScript
- **Prettier**: Formateo de código
- **CSS**: Metodología BEM para estilos
- **Comentarios**: Documentación inline

## Licencia

Este frontend es parte del proyecto HiveMind Architecture y sigue la misma licencia del proyecto principal.
