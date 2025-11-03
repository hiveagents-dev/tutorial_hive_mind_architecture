#!/bin/bash

echo "🚀 Probando Frontend React de HiveMind..."
echo "=========================================="

# Verificar que el frontend esté sirviendo
echo "📱 Verificando que el frontend esté sirviendo..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002)
if [ "$FRONTEND_RESPONSE" != "200" ]; then
    echo "❌ ERROR: Frontend no está sirviendo (HTTP $FRONTEND_RESPONSE)"
    exit 1
fi
echo "✅ Frontend sirviendo correctamente (HTTP $FRONTEND_RESPONSE)"

# Verificar que el HTML contenga React
echo "🔍 Verificando que React esté cargado..."
REACT_CHECK=$(curl -s http://localhost:3002 | grep -o 'assets/index-[^"]*\.js')
if [ -z "$REACT_CHECK" ]; then
    echo "❌ ERROR: No se encontró el bundle de React"
    exit 1
fi
echo "✅ Bundle de React encontrado: $REACT_CHECK"

# Verificar que la API esté funcionando
echo "🔌 Verificando conexión con la API..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/api/v1/health)
if [ "$API_RESPONSE" != "200" ]; then
    echo "❌ ERROR: API no está respondiendo (HTTP $API_RESPONSE)"
    exit 1
fi
echo "✅ API respondiendo correctamente (HTTP $API_RESPONSE)"

# Probar un análisis completo
echo "🧪 Ejecutando análisis de prueba..."
ANALYSIS_RESPONSE=$(curl -s -X POST http://localhost:8002/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_need": "Sistema de gestión de inventario para farmacia con control de vencimientos y alertas automáticas",
    "methodology": "scrum",
    "consensus_strategy": "weighted_voting",
    "verbose": true
  }')

# Verificar que el análisis sea exitoso
SUCCESS=$(echo "$ANALYSIS_RESPONSE" | jq -r '.success // false')
if [ "$SUCCESS" != "true" ]; then
    echo "❌ ERROR: Análisis falló"
    echo "Respuesta: $ANALYSIS_RESPONSE"
    exit 1
fi

echo "✅ Análisis ejecutado exitosamente"

# Extraer información del análisis
EXECUTION_TIME=$(echo "$ANALYSIS_RESPONSE" | jq -r '.execution_time // 0')
CONSENSUS_ACHIEVED=$(echo "$ANALYSIS_RESPONSE" | jq -r '.consensus_result.achieved // false')
WORKER_COUNT=$(echo "$ANALYSIS_RESPONSE" | jq -r '.worker_responses | length')

echo "📊 Resultados del análisis:"
echo "   - Tiempo de ejecución: ${EXECUTION_TIME}s"
echo "   - Consenso alcanzado: $CONSENSUS_ACHIEVED"
echo "   - Agentes worker: $WORKER_COUNT"

# Verificar que todos los agentes respondieron
if [ "$WORKER_COUNT" != "6" ]; then
    echo "❌ ERROR: Se esperaban 6 agentes worker, se encontraron $WORKER_COUNT"
    exit 1
fi
echo "✅ Todos los 6 agentes worker respondieron"

# Verificar que el coordinador y supervisor respondieron
COORDINATOR_RESPONSE=$(echo "$ANALYSIS_RESPONSE" | jq -r '.coordinator_response.agent_name // "none"')
SUPERVISOR_RESPONSE=$(echo "$ANALYSIS_RESPONSE" | jq -r '.supervisor_response.agent_name // "none"')

if [ "$COORDINATOR_RESPONSE" = "none" ] || [ "$SUPERVISOR_RESPONSE" = "none" ]; then
    echo "❌ ERROR: Coordinador o Supervisor no respondieron"
    exit 1
fi
echo "✅ Coordinador y Supervisor respondieron correctamente"

# Verificar que el contenido JSON sea válido y estructurado
echo "🔍 Verificando estructura del contenido JSON..."
FIRST_AGENT_CONTENT=$(echo "$ANALYSIS_RESPONSE" | jq -r '.worker_responses[0].content // ""')
if [ -z "$FIRST_AGENT_CONTENT" ]; then
    echo "❌ ERROR: Contenido del primer agente está vacío"
    exit 1
fi

# Verificar que el contenido sea JSON válido
if ! echo "$FIRST_AGENT_CONTENT" | jq . > /dev/null 2>&1; then
    echo "❌ ERROR: Contenido del agente no es JSON válido"
    exit 1
fi
echo "✅ Contenido JSON válido y estructurado"

# Verificar que el frontend pueda parsear el JSON
echo "🎨 Verificando compatibilidad con el frontend..."
JSON_KEYS=$(echo "$FIRST_AGENT_CONTENT" | jq -r 'keys | length')
if [ "$JSON_KEYS" -lt 3 ]; then
    echo "❌ ERROR: JSON del agente tiene muy pocas claves ($JSON_KEYS)"
    exit 1
fi
echo "✅ JSON tiene estructura rica ($JSON_KEYS claves)"

echo ""
echo "🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!"
echo "=========================================="
echo "✅ Frontend React sirviendo correctamente"
echo "✅ API REST funcionando"
echo "✅ Análisis completo ejecutado"
echo "✅ Todos los agentes respondieron"
echo "✅ JSON estructurado y válido"
echo "✅ Compatible con el frontend"
echo ""
echo "🌐 URLs de acceso:"
echo "   Frontend: http://localhost:3002"
echo "   API: http://localhost:8002"
echo "   Docs: http://localhost:8002/docs"
echo ""
echo "💡 Para probar manualmente:"
echo "   1. Abre http://localhost:3002 en Chrome"
echo "   2. Ve a la vista 'Analizar'"
echo "   3. Escribe una necesidad de negocio"
echo "   4. Pulsa 'Ejecutar Análisis'"
echo "   5. Verifica que aparezcan los resultados"
echo "   6. Prueba los botones 'Ver Completo'"
