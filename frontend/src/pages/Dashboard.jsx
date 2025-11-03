import React from 'react';
import { useApp } from '../context/AppContext';

export function Dashboard() {
  const { state, actions } = useApp();

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <i className="fas fa-check-circle text-success"></i>;
      case 'error':
        return <i className="fas fa-exclamation-circle text-error"></i>;
      default:
        return <i className="fas fa-spinner fa-spin text-warning"></i>;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Conectado';
      case 'error':
        return 'Desconectado';
      default:
        return 'Verificando...';
    }
  };

  return (
    <div className="dashboard">
      <div className="section-header">
        <h2><i className="fas fa-tachometer-alt"></i> Dashboard</h2>
        <p>Monitoreo en tiempo real del sistema HiveMind</p>
      </div>
      
      <div className="dashboard-grid">
        {/* Estado del Sistema */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-server"></i> Estado del Sistema</h3>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={actions.refreshApiStatus}
              disabled={state.loading}
            >
              <i className="fas fa-sync-alt"></i>
              Actualizar
            </button>
          </div>
          <div className="card-content">
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">API REST:</span>
                <span className="status-value">
                  {getStatusIcon(state.apiStatus)}
                  {getStatusText(state.apiStatus)}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Modelo Gemini:</span>
                <span className="status-value">
                  {getStatusIcon(state.apiStatus)}
                  {getStatusText(state.apiStatus)}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Agentes Activos:</span>
                <span className="status-value">
                  <i className="fas fa-robot"></i>
                  6
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Metodología:</span>
                <span className="status-value">
                  <i className="fas fa-project-diagram"></i>
                  {state.selectedMethodology.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Metodologías Disponibles */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-project-diagram"></i> Metodologías Disponibles</h3>
          </div>
          <div className="card-content">
            <div className="methodology-list">
              {state.methodologies.length > 0 ? (
                state.methodologies.map(methodology => (
                  <div 
                    key={methodology.name}
                    className={`methodology-item ${state.selectedMethodology === methodology.name.toLowerCase() ? 'active' : ''}`}
                  >
                    <i className="fas fa-project-diagram"></i>
                    <div className="methodology-info">
                      <span className="methodology-name">{methodology.name}</span>
                      <span className="methodology-description">{methodology.description}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="methodology-item">
                  <i className="fas fa-spinner fa-spin"></i>
                  <span>Cargando metodologías...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Análisis Reciente */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-history"></i> Análisis Reciente</h3>
          </div>
          <div className="card-content">
            {state.currentAnalysis ? (
              <div className="recent-analysis">
                <div className="analysis-summary">
                  <div className="summary-item">
                    <strong>Metodología:</strong> {state.currentAnalysis.methodology}
                  </div>
                  <div className="summary-item">
                    <strong>Tiempo de ejecución:</strong> {state.currentAnalysis.execution_time.toFixed(2)}s
                  </div>
                  <div className="summary-item">
                    <strong>Consenso:</strong> 
                    <span className={`consensus ${state.currentAnalysis.consensus_result.achieved ? 'achieved' : 'not-achieved'}`}>
                      {state.currentAnalysis.consensus_result.achieved ? 'Alcanzado' : 'No alcanzado'}
                    </span>
                  </div>
                </div>
                <div className="analysis-actions">
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => actions.setCurrentSection('analyze')}
                  >
                    <i className="fas fa-eye"></i>
                    Ver Detalles
                  </button>
                </div>
              </div>
            ) : (
              <div className="no-analysis">
                <i className="fas fa-info-circle"></i>
                <p>No hay análisis recientes</p>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => actions.setCurrentSection('analyze')}
                >
                  <i className="fas fa-play"></i>
                  Ejecutar Análisis
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Estadísticas Rápidas */}
        <div className="card">
          <div className="card-header">
            <h3><i className="fas fa-chart-bar"></i> Estadísticas</h3>
          </div>
          <div className="card-content">
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{state.analysisHistory.length}</div>
                <div className="stat-label">Análisis Totales</div>
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
          </div>
        </div>
      </div>
    </div>
  );
}
