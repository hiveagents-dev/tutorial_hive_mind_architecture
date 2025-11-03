import React, { useState } from 'react';
import { Tooltip } from './Tooltip';

export function ResultSummary({ 
  executionTime, 
  methodology, 
  consensusResult, 
  onExportPDF, 
  onCopyLink, 
  onGenerateNew 
}) {
  const [showTooltip, setShowTooltip] = useState(false);

  const getConsensusColor = (level) => {
    if (level >= 80) return '#10b981'; // Verde
    if (level >= 60) return '#f59e0b'; // Amarillo
    return '#ef4444'; // Rojo
  };

  const getConsensusLabel = (achieved, level) => {
    if (achieved) {
      if (level >= 80) return 'Consenso Excelente';
      if (level >= 60) return 'Consenso Bueno';
      return 'Consenso Básico';
    }
    return 'Sin Consenso';
  };

  const formatTime = (seconds) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = (seconds % 60).toFixed(1);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="result-summary">
      <div className="summary-header">
        <h3>
          <i className="fas fa-chart-line"></i>
          Resumen del Análisis
        </h3>
        <div className="summary-actions">
          <button 
            className="btn btn-sm btn-outline"
            onClick={onExportPDF}
            title="Exportar como PDF"
          >
            <i className="fas fa-file-pdf"></i>
            PDF
          </button>
          <button 
            className="btn btn-sm btn-outline"
            onClick={onCopyLink}
            title="Copiar enlace compartible"
          >
            <i className="fas fa-link"></i>
            Enlace
          </button>
          <button 
            className="btn btn-sm btn-outline"
            onClick={onGenerateNew}
            title="Generar nuevo análisis basado en este"
          >
            <i className="fas fa-plus"></i>
            Nuevo
          </button>
        </div>
      </div>

      <div className="summary-metrics">
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{formatTime(executionTime)}</div>
            <div className="metric-label">Tiempo de Ejecución</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-project-diagram"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{methodology?.toUpperCase() || 'N/A'}</div>
            <div className="metric-label">Metodología</div>
          </div>
        </div>

        <div className="metric-card consensus-card">
          <div className="metric-icon">
            <i className="fas fa-handshake"></i>
          </div>
          <div className="metric-content">
            <div className="consensus-indicator">
              <div className="consensus-bar">
                <div 
                  className="consensus-fill"
                  style={{ 
                    width: `${consensusResult?.consensus_level * 100 || 0}%`,
                    backgroundColor: getConsensusColor(consensusResult?.consensus_level * 100 || 0)
                  }}
                ></div>
              </div>
              <div className="consensus-details">
                <span className="consensus-level">
                  {Math.round((consensusResult?.consensus_level || 0) * 100)}%
                </span>
                <span 
                  className="consensus-label"
                  style={{ color: getConsensusColor(consensusResult?.consensus_level * 100 || 0) }}
                >
                  {getConsensusLabel(consensusResult?.achieved, consensusResult?.consensus_level * 100)}
                </span>
              </div>
            </div>
            <div className="metric-label">
              Consenso
              <div 
                className="help-trigger"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                <i className="fas fa-info-circle"></i>
                {showTooltip && (
                  <div className="tooltip">
                    <div className="tooltip-content">
                      <strong>Consenso Alcanzado</strong> significa que los 6 agentes especializados concuerdan en el análisis. 
                      Un nivel alto de consenso indica mayor confiabilidad en los resultados.
                    </div>
                    <div className="tooltip-arrow"></div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {consensusResult?.justification && (
        <div className="consensus-justification">
          <div className="justification-header">
            <i className="fas fa-lightbulb"></i>
            <span>Justificación del Consenso</span>
          </div>
          <div className="justification-content">
            {consensusResult.justification}
          </div>
        </div>
      )}
    </div>
  );
}
