import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { apiClient } from '../api/client';
import { AgentContentView } from '../components/AgentContentView';
import { FullContentModal } from '../components/Modal';
import { DashboardExecutive } from '../components/DashboardExecutive';
import { ResultSummary } from '../components/ResultSummary';
import { ResultActions } from '../components/ResultActions';
import { CoordinatorSynthesis } from '../components/CoordinatorSynthesis';
import { SpecializedAgentsTabs } from '../components/SpecializedAgentsTabs';
import { ConsolidatedView } from '../components/ConsolidatedView';

export function History() {
  const { state, actions } = useApp();
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  // Cargar historial al montar el componente
  useEffect(() => {
    actions.loadHistoryFromDb();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleViewDetails = async (analysisId) => {
    setSelectedAnalysisId(analysisId);
    try {
      const analysis = await actions.loadAnalysisById(analysisId);
      setSelectedAnalysis(analysis);
    } catch (error) {
      console.error('Error loading analysis details:', error);
    }
  };

  const handleShowAgentContent = (agentData) => {
    actions.showFullContentModal(agentData);
  };

  const convertDbAnalysisToDisplay = (dbAnalysis) => {
    // Convertir el formato de BD al formato esperado por la UI
    const agentResponses = dbAnalysis.agent_responses || [];
    const workers = agentResponses.filter(ar => ar.agent_level === 'worker');
    const coordinator = agentResponses.find(ar => ar.agent_level === 'coordinator');
    const supervisor = agentResponses.find(ar => ar.agent_level === 'supervisor');

    // Función helper para parsear output_json de forma segura
    const safeParseJson = (jsonData) => {
      if (!jsonData) return null;
      if (typeof jsonData === 'object') return jsonData;
      if (typeof jsonData === 'string') {
        try {
          return JSON.parse(jsonData);
        } catch (e) {
          console.warn('Error parsing JSON:', e);
          return null;
        }
      }
      return null;
    };

    return {
      id: dbAnalysis.id,
      business_need: dbAnalysis.business_need || '',
      methodology: dbAnalysis.methodology || '',
      consensus_strategy: dbAnalysis.consensus_strategy || '',
      execution_time: dbAnalysis.execution_time || 0,
      success: dbAnalysis.success === 'true',
      final_confidence: dbAnalysis.final_confidence || 0,
      created_at: dbAnalysis.created_at,
      worker_responses: workers.map(ar => ({
        agent_name: ar.agent_name || 'Unknown',
        confidence: ar.confidence || 0,
        timestamp: ar.created_at,
        methodology: dbAnalysis.methodology || '',
        content: ar.output_content || '',
        content_length: ar.output_content?.length || 0,
        output_json: safeParseJson(ar.output_json)
      })),
      coordinator_response: coordinator ? {
        agent_name: coordinator.agent_name || 'Coordinator',
        confidence: coordinator.confidence || 0,
        timestamp: coordinator.created_at,
        methodology: dbAnalysis.methodology || '',
        content: coordinator.output_content || '',
        content_length: coordinator.output_content?.length || 0,
        output_json: safeParseJson(coordinator.output_json)
      } : null,
      supervisor_response: supervisor ? {
        agent_name: supervisor.agent_name || 'Supervisor',
        confidence: supervisor.confidence || 0,
        timestamp: supervisor.created_at,
        methodology: dbAnalysis.methodology || '',
        content: supervisor.output_content || '',
        content_length: supervisor.output_content?.length || 0,
        output_json: safeParseJson(supervisor.output_json)
      } : null,
      supervisor_response_content: safeParseJson(dbAnalysis.supervisor_response_content),
      metadata: dbAnalysis.metadata || {}
    };
  };

  // Helper para formatear respuesta de agente (igual que en Analyze.jsx)
  const formatAgentResponse = (agent, metadata = {}) => {
    if (!agent) return null;
    return {
      agent_name: agent.agent_name || 'Unknown Agent',
      confidence: agent.confidence || 0,
      timestamp: agent.timestamp || new Date().toISOString(),
      methodology: agent.methodology || 'unknown',
      content: agent.content || '',
      content_length: agent.content?.length || 0,
      output_json: agent.output_json || metadata.supervisor_response_content || metadata.output_json,
      data: agent.output_json || metadata.supervisor_response_content || metadata.output_json
    };
  };

  const handleExportPDF = () => {
    console.log('Exporting to PDF...');
    // TODO: Implementar exportación PDF
  };

  const handleCopyLink = () => {
    if (selectedAnalysis) {
      const url = `${window.location.origin}/history?analysis=${selectedAnalysis.id}`;
      navigator.clipboard.writeText(url).then(() => {
        console.log('Link copiado al portapapeles');
      });
    }
  };

  const handleGenerateNew = () => {
    setSelectedAnalysis(null);
    setSelectedAnalysisId(null);
    actions.setCurrentSection('analyze');
  };

  const handleShareResults = () => {
    console.log('Sharing results...');
    // TODO: Implementar compartir
  };

  const handleSaveTemplate = () => {
    console.log('Saving as template...');
    // TODO: Implementar guardar plantilla
  };

  // Si hay un análisis seleccionado, mostrar sus detalles
  if (selectedAnalysis) {
    const displayAnalysis = convertDbAnalysisToDisplay(selectedAnalysis);
    
    // Construir consensus_result desde los datos disponibles
    const workers = displayAnalysis.worker_responses || [];
    const avgConfidence = workers.length > 0 
      ? workers.reduce((sum, w) => sum + (w.confidence || 0), 0) / workers.length 
      : displayAnalysis.final_confidence || 0;
    
    const consensusResult = {
      achieved: avgConfidence >= 0.7,
      consensus_level: avgConfidence,
      justification: `Weighted voting consensus achieved. Average weighted confidence: ${avgConfidence.toFixed(2)}, Threshold: 0.70. ${workers.filter(w => (w.confidence || 0) >= 0.7).length} agents above threshold, ${workers.filter(w => (w.confidence || 0) < 0.7).length} below.`
    };

    // Crear objeto de análisis completo compatible con Analyze.jsx
    const fullAnalysis = {
      ...displayAnalysis,
      consensus_result: consensusResult
    };

    return (
      <div className="history-detail analyze">
        <div className="section-header">
          <button 
            className="btn btn-secondary"
            onClick={() => {
              setSelectedAnalysis(null);
              setSelectedAnalysisId(null);
            }}
          >
            <i className="fas fa-arrow-left"></i> Volver al Historial
          </button>
          <h1>
            <i className="fas fa-file-alt"></i> Análisis #{selectedAnalysis.id}
          </h1>
          <p>Análisis completo del {formatDate(selectedAnalysis.created_at)}</p>
        </div>

        {/* Dashboard Ejecutivo */}
        <DashboardExecutive analysis={fullAnalysis} />
        
        {/* Resumen Mejorado de Resultados */}
        <ResultSummary
          executionTime={displayAnalysis.execution_time || 0}
          methodology={displayAnalysis.methodology || 'Unknown'}
          consensusResult={consensusResult}
          onExportPDF={handleExportPDF}
          onCopyLink={handleCopyLink}
          onGenerateNew={handleGenerateNew}
        />

        {/* Acciones de Resultados */}
        <ResultActions
          onExportPDF={handleExportPDF}
          onCopyLink={handleCopyLink}
          onGenerateNew={handleGenerateNew}
          onShareResults={handleShareResults}
          onSaveTemplate={handleSaveTemplate}
        />

        {/* Vista Consolidada */}
        <div className="card">
          <div className="card-header">
            <h3>
              <i className="fas fa-users"></i> Análisis Detallado por Agentes
            </h3>
          </div>
          <div className="card-content">
            <ConsolidatedView 
              analysis={fullAnalysis} 
              viewMode="tabs"
            />
          </div>
        </div>

        {/* Vista de Agentes Especializados con Pestañas */}
        <div className="card">
          <div className="card-header">
            <h3>
              <i className="fas fa-users"></i> Agentes Especializados
            </h3>
          </div>
          <div className="card-content">
            <SpecializedAgentsTabs 
              agents={displayAnalysis.worker_responses || []}
              formatAgentResponse={formatAgentResponse}
              onShowFullContent={handleShowAgentContent}
            />
          </div>
        </div>

        {/* Síntesis del Coordinador */}
        {displayAnalysis.coordinator_response && (
          <div className="card">
            <CoordinatorSynthesis
              coordinator={formatAgentResponse(displayAnalysis.coordinator_response)}
              workers={(displayAnalysis.worker_responses || []).map(formatAgentResponse)}
              onShowFull={(coord) => handleShowAgentContent(coord)}
            />
          </div>
        )}

        {/* Respuesta del Supervisor */}
        {displayAnalysis.supervisor_response && (
          <div className="card">
            <div className="card-header">
              <h3><i className="fas fa-crown"></i> Decisión Final del Supervisor</h3>
            </div>
            <div className="card-content">
              <div className="agent-card supervisor-card">
                <div className="agent-header">
                  <h5>{displayAnalysis.supervisor_response.agent_name}</h5>
                  <div className="agent-meta">
                    <span className={`confidence ${displayAnalysis.supervisor_response.confidence > 0.8 ? 'high' : displayAnalysis.supervisor_response.confidence > 0.6 ? 'medium' : 'low'}`}>
                      {(displayAnalysis.supervisor_response.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="agent-content">
                  <AgentContentView 
                    agentName={displayAnalysis.supervisor_response.agent_name}
                    data={displayAnalysis.supervisor_response_content || displayAnalysis.supervisor_response.output_json || displayAnalysis.supervisor_response.content}
                    content={displayAnalysis.supervisor_response.content}
                  />
                  <div className="agent-actions">
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => handleShowAgentContent({
                        agent_name: displayAnalysis.supervisor_response.agent_name,
                        confidence: displayAnalysis.supervisor_response.confidence,
                        timestamp: displayAnalysis.supervisor_response.timestamp,
                        methodology: displayAnalysis.supervisor_response.methodology,
                        content: displayAnalysis.supervisor_response.content,
                        output_json: displayAnalysis.supervisor_response_content,
                        data: displayAnalysis.supervisor_response_content
                      })}
                    >
                      <i className="fas fa-expand"></i>
                      Ver Completo
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Vista de lista de historial
  return (
    <div className="history">
      <div className="section-header">
        <h2><i className="fas fa-history"></i> Historial de Análisis</h2>
        <div className="header-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => actions.loadHistoryFromDb()}
            disabled={state.historyLoading}
          >
            <i className="fas fa-sync-alt"></i> Actualizar
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="card filters-card">
        <div className="card-content">
          <div className="filters-grid">
            <div className="filter-item">
              <label>Metodología</label>
              <select
                value={state.historyFilters.methodology || ''}
                onChange={(e) => actions.loadHistoryFromDb({ methodology: e.target.value || null })}
              >
                <option value="">Todas</option>
                <option value="scrum">Scrum</option>
                <option value="safe">SAFe</option>
                <option value="kanban">Kanban</option>
              </select>
            </div>
            <div className="filter-item">
              <label>
                <input
                  type="checkbox"
                  checked={state.historyFilters.success_only}
                  onChange={(e) => actions.loadHistoryFromDb({ success_only: e.target.checked })}
                />
                Solo exitosos
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de análisis */}
      {state.historyLoading ? (
        <div className="card">
          <div className="card-content">
            <div className="loading-state">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Cargando historial...</p>
            </div>
          </div>
        </div>
      ) : state.historyFromDb.length === 0 ? (
        <div className="card">
          <div className="card-content">
            <div className="empty-state">
              <i className="fas fa-inbox"></i>
              <h3>No hay análisis en el historial</h3>
              <p>Ejecuta tu primer análisis para ver los resultados aquí</p>
              <button 
                className="btn btn-primary"
                onClick={() => actions.setCurrentSection('analyze')}
              >
                <i className="fas fa-play"></i> Ejecutar Análisis
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="history-list">
          {state.historyFromDb.map((analysis) => {
            const displayAnalysis = convertDbAnalysisToDisplay(analysis);
            const agentCount = (displayAnalysis.worker_responses?.length || 0) + 
                              (displayAnalysis.coordinator_response ? 1 : 0) + 
                              (displayAnalysis.supervisor_response ? 1 : 0);

            return (
              <div key={analysis.id} className="card history-item">
                <div className="card-header">
                  <div className="history-header">
                    <h3>
                      <i className="fas fa-chart-line"></i> Análisis #{analysis.id}
                    </h3>
                    <div className="history-meta">
                      <span className="meta-item">
                        <i className="fas fa-clock"></i> {formatDate(analysis.created_at)}
                      </span>
                      <span className="meta-item">
                        <i className="fas fa-project-diagram"></i> {analysis.methodology}
                      </span>
                      <span className="meta-item">
                        <i className="fas fa-stopwatch"></i> {analysis.execution_time.toFixed(2)}s
                      </span>
                      <span className="meta-item">
                        <i className="fas fa-users"></i> {agentCount} agentes
                      </span>
                      <span className={`meta-item badge ${analysis.success === 'true' ? 'badge-success' : 'badge-error'}`}>
                        {analysis.success === 'true' ? '✅ Exitoso' : '❌ Fallido'}
                      </span>
                      {analysis.final_confidence && (
                        <span className="meta-item">
                          <i className="fas fa-bullseye"></i> {(analysis.final_confidence * 100).toFixed(1)}% confianza
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="card-content">
                  <div className="business-need-preview">
                    <strong>Necesidad de Negocio:</strong>
                    <p>{analysis.business_need.substring(0, 200)}{analysis.business_need.length > 200 ? '...' : ''}</p>
                  </div>
                  
                  <div className="history-actions">
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleViewDetails(analysis.id)}
                    >
                      <i className="fas fa-eye"></i> Ver Detalles Completos
                    </button>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => {
                        const dataStr = JSON.stringify(analysis, null, 2);
                        const dataBlob = new Blob([dataStr], { type: 'application/json' });
                        const url = URL.createObjectURL(dataBlob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = `hivemind-analysis-${analysis.id}-${Date.now()}.json`;
                        link.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      <i className="fas fa-download"></i> Descargar JSON
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal para contenido completo */}
      <FullContentModal
        isOpen={state.showFullContentModal}
        onClose={actions.hideFullContentModal}
        agentData={state.fullContentData}
      />
    </div>
  );
}
