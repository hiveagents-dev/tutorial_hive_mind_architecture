import React from 'react';
import { useApp } from '../context/AppContext';

export function Settings() {
  const { state, actions } = useApp();

  const handleMethodologyChange = (methodology) => {
    actions.setSelectedMethodology(methodology);
  };

  const handleConsensusStrategyChange = (strategy) => {
    actions.setSelectedConsensusStrategy(strategy);
  };

  const handleRefreshApi = async () => {
    await actions.refreshApiStatus();
  };

  const clearHistory = () => {
    if (window.confirm('¿Estás seguro de que quieres limpiar todo el historial de análisis?')) {
      // Implementar limpieza del historial
      console.log('Historial limpiado');
    }
  };

  const exportData = () => {
    const data = {
      settings: {
        selectedMethodology: state.selectedMethodology,
        selectedConsensusStrategy: state.selectedConsensusStrategy,
      },
      analysisHistory: state.analysisHistory,
      exportDate: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hivemind-settings-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="settings">
      <div className="section-header">
        <h2><i className="fas fa-cog"></i> Configuración</h2>
        <p>Personaliza el comportamiento del sistema HiveMind</p>
      </div>

      <div className="settings-grid">
        {/* Configuración General */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-sliders-h"></i> Configuración General</h3>
          </div>
          <div className="card-content">
            <div className="form-group">
              <label htmlFor="defaultMethodology">Metodología Ágil por Defecto:</label>
              <select
                id="defaultMethodology"
                value={state.selectedMethodology}
                onChange={(e) => handleMethodologyChange(e.target.value)}
                className="form-control"
              >
                {state.methodologies.map(methodology => (
                  <option key={methodology.name} value={methodology.name.toLowerCase()}>
                    {methodology.name}
                  </option>
                ))}
              </select>
              <small className="form-help">
                Metodología ágil que se utilizará por defecto para nuevos análisis
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="defaultConsensus">Estrategia de Consenso por Defecto:</label>
              <select
                id="defaultConsensus"
                value={state.selectedConsensusStrategy}
                onChange={(e) => handleConsensusStrategyChange(e.target.value)}
                className="form-control"
              >
                <option value="weighted_voting">Votación Ponderada</option>
                <option value="majority">Mayoría</option>
                <option value="unanimous">Unánime</option>
                <option value="confidence_threshold">Umbral de Confianza</option>
              </select>
              <small className="form-help">
                Estrategia utilizada para alcanzar consenso entre agentes
              </small>
            </div>
          </div>
        </div>

        {/* Estado del Sistema */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-server"></i> Estado del Sistema</h3>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={handleRefreshApi}
              disabled={state.loading}
            >
              <i className="fas fa-sync-alt"></i>
              Actualizar
            </button>
          </div>
          <div className="card-content">
            <div className="status-list">
              <div className="status-item">
                <span className="status-label">API REST:</span>
                <span className={`status-value ${state.apiStatus}`}>
                  <i className={`fas fa-circle ${state.apiStatus === 'connected' ? 'text-success' : state.apiStatus === 'error' ? 'text-error' : 'text-warning'}`}></i>
                  {state.apiStatus === 'connected' ? 'Conectado' : state.apiStatus === 'error' ? 'Desconectado' : 'Verificando...'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Modelo Gemini:</span>
                <span className={`status-value ${state.apiStatus}`}>
                  <i className={`fas fa-circle ${state.apiStatus === 'connected' ? 'text-success' : state.apiStatus === 'error' ? 'text-error' : 'text-warning'}`}></i>
                  {state.apiStatus === 'connected' ? 'Conectado' : state.apiStatus === 'error' ? 'Desconectado' : 'Verificando...'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Agentes Activos:</span>
                <span className="status-value">
                  <i className="fas fa-robot text-success"></i>
                  6
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Información de Metodologías */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-info-circle"></i> Metodologías Disponibles</h3>
          </div>
          <div className="card-content">
            <div className="methodology-info">
              {state.methodologies.map(methodology => (
                <div key={methodology.name} className="methodology-detail">
                  <h4>{methodology.name}</h4>
                  <p>{methodology.description}</p>
                  <div className="methodology-roles">
                    <strong>Roles:</strong>
                    <ul>
                      {methodology.roles_mapping && Object.entries(methodology.roles_mapping).map(([role, description]) => (
                        <li key={role}>
                          <strong>{role}:</strong> {description}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Gestión de Datos */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-database"></i> Gestión de Datos</h3>
          </div>
          <div className="card-content">
            <div className="data-stats">
              <div className="stat-item">
                <div className="stat-value">{state.analysisHistory.length}</div>
                <div className="stat-label">Análisis en Historial</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {state.analysisHistory.filter(a => a.consensus_result.achieved).length}
                </div>
                <div className="stat-label">Consensos Exitosos</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {state.analysisHistory.length > 0 
                    ? (state.analysisHistory.reduce((acc, a) => acc + a.execution_time, 0) / state.analysisHistory.length).toFixed(1)
                    : 0
                  }s
                </div>
                <div className="stat-label">Tiempo Promedio</div>
              </div>
            </div>

            <div className="data-actions">
              <button 
                className="btn btn-primary"
                onClick={exportData}
                disabled={state.analysisHistory.length === 0}
              >
                <i className="fas fa-download"></i>
                Exportar Datos
              </button>
              <button 
                className="btn btn-danger"
                onClick={clearHistory}
                disabled={state.analysisHistory.length === 0}
              >
                <i className="fas fa-trash"></i>
                Limpiar Historial
              </button>
            </div>
          </div>
        </div>

        {/* Información de la Aplicación */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-info"></i> Información de la Aplicación</h3>
          </div>
          <div className="card-content">
            <div className="app-info">
              <div className="info-item">
                <strong>Versión:</strong> 1.0.0
              </div>
              <div className="info-item">
                <strong>Framework:</strong> React + Vite
              </div>
              <div className="info-item">
                <strong>API Backend:</strong> FastAPI + Python
              </div>
              <div className="info-item">
                <strong>Modelo IA:</strong> Google Gemini
              </div>
              <div className="info-item">
                <strong>Arquitectura:</strong> HiveMind Multi-Agent
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
