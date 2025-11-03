import React from 'react';
import { Tooltip } from './Tooltip';

export function DashboardExecutive({ analysis }) {
  if (!analysis) return null;

  const confidence = analysis.supervisor_response?.confidence || 0;
  const executionTime = analysis.execution_time || 0;
  const methodology = analysis.methodology || 'Unknown';

  // Calcular métricas
  const viability = Math.min(100, Math.round(confidence * 100));
  const complexity = Math.max(0, Math.min(100, Math.round((1 - confidence) * 70)));
  const estimatedSprints = Math.max(1, Math.round(executionTime / 300)); // Aproximación

  // Obtener riesgos desde supervisor o coordinator
  const supervisorData = analysis.supervisor_response?.output_json || 
                        analysis.supervisor_response?.data ||
                        (analysis.supervisor_response?.content ? JSON.parse(analysis.supervisor_response.content) : null);
  
  const risks = supervisorData?.risk_management?.risks || [];
  const highRisks = risks.filter(r => r.impact === 'High' || r.probability === 'High');
  const mediumRisks = risks.filter(r => r.impact === 'Medium' || r.probability === 'Medium');
  const lowRisks = risks.filter(r => r.impact === 'Low' && r.probability === 'Low');

  // Obtener consenso de workers
  const workers = analysis.worker_responses || [];
  const avgConfidence = workers.length > 0 
    ? workers.reduce((sum, w) => sum + (w.confidence || 0), 0) / workers.length 
    : 0;

  return (
    <div className="dashboard-executive">
      <div className="dashboard-header">
        <h2><i className="fas fa-chart-line"></i> Dashboard Ejecutivo</h2>
      </div>

      {/* Métricas principales */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <h3><i className="fas fa-check-circle"></i> Viabilidad</h3>
          </div>
          <div className="gauge-container">
            <div className="gauge" style={{ '--progress': viability }}>
              <div className="gauge-fill" style={{ width: `${viability}%` }}></div>
              <div className="gauge-value">{viability}%</div>
            </div>
          </div>
          <p className="metric-label">
            {viability >= 80 ? 'Muy Viable' : viability >= 60 ? 'Viable' : 'Revisar'}
          </p>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <h3><i className="fas fa-bolt"></i> Complejidad</h3>
          </div>
          <div className="gauge-container">
            <div className="gauge" style={{ '--progress': complexity }}>
              <div className="gauge-fill complexity" style={{ width: `${complexity}%` }}></div>
              <div className="gauge-value">{complexity}%</div>
            </div>
          </div>
          <p className="metric-label">
            {complexity >= 60 ? 'Alta' : complexity >= 30 ? 'Media' : 'Baja'}
          </p>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <h3><i className="fas fa-calendar-alt"></i> Timeline</h3>
          </div>
          <div className="timeline-info">
            <div className="timeline-value">{estimatedSprints} sprints</div>
            <div className="timeline-estimate">~{Math.round(estimatedSprints * 2 / 4)} meses</div>
          </div>
        </div>
      </div>

      {/* Consenso General */}
      <div className="consensus-card">
        <h3>
          <i className="fas fa-users"></i> 
          Consenso General: {Math.round(avgConfidence * 100)}% 
          <Tooltip content="Nivel de acuerdo promedio entre los 6 agentes especializados. Un consenso alto indica mayor confiabilidad en los resultados del análisis.">
            <i className="fas fa-info-circle help-icon"></i>
          </Tooltip>
          <i className="fas fa-check"></i>
        </h3>
        <div className="consensus-details">
          <span>{workers.length} agentes alineados</span>
          <span>|</span>
          <span>Confianza promedio: {avgConfidence.toFixed(2)}</span>
          <span>|</span>
          <span>Umbral: 0.70</span>
        </div>
      </div>

      {/* Matriz de Riesgos */}
      {(highRisks.length > 0 || mediumRisks.length > 0 || lowRisks.length > 0) && (
        <div className="risks-matrix">
          <h3><i className="fas fa-exclamation-triangle"></i> Riesgos Principales</h3>
          <div className="risks-grid">
            {highRisks.length > 0 && (
              <div className="risk-category high">
                <h4><i className="fas fa-circle" style={{ color: '#ef4444' }}></i> Alto</h4>
                <ul>
                  {highRisks.slice(0, 3).map((risk, idx) => (
                    <li key={idx}>
                      <strong>{typeof risk === 'string' ? risk : risk.description || risk.risk}</strong>
                      {typeof risk === 'object' && risk.mitigation && (
                        <span className="risk-mitigation">Mitigación: {risk.mitigation}</span>
                      )}
                    </li>
                  ))}
                  {highRisks.length > 3 && <li className="more-risks">+{highRisks.length - 3} más</li>}
                </ul>
              </div>
            )}
            {mediumRisks.length > 0 && (
              <div className="risk-category medium">
                <h4><i className="fas fa-circle" style={{ color: '#f59e0b' }}></i> Medio</h4>
                <ul>
                  {mediumRisks.slice(0, 3).map((risk, idx) => (
                    <li key={idx}>
                      <strong>{typeof risk === 'string' ? risk : risk.description || risk.risk}</strong>
                      {typeof risk === 'object' && risk.mitigation && (
                        <span className="risk-mitigation">Mitigación: {risk.mitigation}</span>
                      )}
                    </li>
                  ))}
                  {mediumRisks.length > 3 && <li className="more-risks">+{mediumRisks.length - 3} más</li>}
                </ul>
              </div>
            )}
            {lowRisks.length > 0 && (
              <div className="risk-category low">
                <h4><i className="fas fa-circle" style={{ color: '#10b981' }}></i> Bajo</h4>
                <ul>
                  {lowRisks.slice(0, 3).map((risk, idx) => (
                    <li key={idx}>
                      <strong>{typeof risk === 'string' ? risk : risk.description || risk.risk}</strong>
                    </li>
                  ))}
                  {lowRisks.length > 3 && <li className="more-risks">+{lowRisks.length - 3} más</li>}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Acciones del Dashboard */}
      <div className="dashboard-actions">
        <div className="action-group">
          <button className="btn btn-secondary">
            <i className="fas fa-file-import"></i>
            Importar
          </button>
          <button className="btn btn-secondary">
            <i className="fas fa-file-pdf"></i>
            Exportar PDF
          </button>
          <button className="btn btn-secondary">
            <i className="fas fa-link"></i>
            Copiar Enlace
          </button>
        </div>
        <button className="btn btn-secondary">
          <i className="fas fa-ellipsis-h"></i>
          Más
        </button>
      </div>
    </div>
  );
}
