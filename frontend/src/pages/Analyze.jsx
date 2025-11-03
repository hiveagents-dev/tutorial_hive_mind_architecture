import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { ContentPreview } from '../components/StructuredContent';
import { FullContentModal } from '../components/Modal';
import { SelectField } from '../components/SelectField';
import { TextAreaField } from '../components/TextAreaField';
import { ActionButton } from '../components/ActionButton';
import { ExampleLoader } from '../components/ExampleLoader';
import { ResultSummary } from '../components/ResultSummary';
import { ResultActions } from '../components/ResultActions';
import { AgentCard } from '../components/AgentCard';
import { CoordinatorSynthesis } from '../components/CoordinatorSynthesis';
import { DashboardExecutive } from '../components/DashboardExecutive';
import { AgentFilters } from '../components/AgentFilters';
import { ConsolidatedView } from '../components/ConsolidatedView';
import { Tooltip } from '../components/Tooltip';
import { SpecializedAgentsTabs } from '../components/SpecializedAgentsTabs';

export function Analyze() {
  const { state, actions } = useApp();
  const [businessNeed, setBusinessNeed] = useState('');
  const [filteredAgents, setFilteredAgents] = useState(null); // null = mostrar todos
  const [isBusinessNeedValid, setIsBusinessNeedValid] = useState(false);
  
  // Debug del estado
  console.log('🔍 Analyze render - loading:', state.loading, 'businessNeed:', businessNeed, 'disabled:', state.loading || !businessNeed.trim());

  const handleAnalyze = async () => {
    console.log('🔍 handleAnalyze llamado - loading:', state.loading, 'businessNeed:', businessNeed);
    
    if (!businessNeed.trim()) {
      actions.setError('Por favor, ingresa una necesidad de negocio');
      return;
    }

    try {
      // Usar WebSocket para análisis con streaming
      console.log('🚀 Iniciando análisis con WebSocket...');
      actions.analyzeBusinessNeedWS(businessNeed);
    } catch (error) {
      console.error('Error during analysis:', error);
      actions.setError('Error durante el análisis: ' + error.message);
    }
  };

  const handleLoadExample = (example) => {
    setBusinessNeed(example.businessNeed);
    actions.setSelectedMethodology(example.methodology);
    actions.setSelectedConsensusStrategy(example.consensus);
  };

  const handleExampleAnalysis = async () => {
    try {
      await actions.runExampleAnalysis();
    } catch (error) {
      console.error('Error during example analysis:', error);
    }
  };

  const handleShowFullContent = (agentData) => {
    actions.showFullContentModal(agentData);
  };

  const handleExportPDF = () => {
    console.log('Exporting to PDF...');
    // Aquí se implementaría la lógica de exportación a PDF
    actions.setError('Función de exportación PDF en desarrollo');
  };

  const handleCopyLink = () => {
    console.log('Copying link...');
    // La lógica de copiado se maneja en el componente ResultActions
  };

  const handleGenerateNew = () => {
    console.log('Generating new analysis...');
    // Limpiar el formulario para un nuevo análisis
    setBusinessNeed('');
    actions.setCurrentAnalysis(null);
  };

  const handleShareResults = () => {
    console.log('Sharing results...');
    actions.setError('Función de compartir en desarrollo');
  };

  const handleSaveTemplate = () => {
    console.log('Saving as template...');
    actions.setError('Función de guardar plantilla en desarrollo');
  };

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

  return (
    <div className="analyze">
      <a href="#main-content" className="skip-to-content">
        Saltar al contenido principal
      </a>
      <div className="section-header">
        <h1>
          <i className="fas fa-search" aria-hidden="true"></i>
          Análisis de Necesidades de Negocio
        </h1>
        <p>Transforma necesidades de negocio en requisitos técnicos completos</p>
      </div>

      {/* Formulario de Análisis */}
      <div className="card">
        <div className="card-header">
          <h3><i className="fas fa-edit"></i> Configuración del Análisis</h3>
        </div>
        <div className="card-content">
          <div className="form-grid">
            <SelectField
              label="Metodología Ágil"
              id="methodology"
              value={state.selectedMethodology}
              onChange={(e) => actions.setSelectedMethodology(e.target.value)}
              options={state.methodologies.map(methodology => ({
                value: methodology.name.toLowerCase(),
                label: methodology.name
              }))}
              helpText="Define cómo se organizarán los sprints y el flujo de trabajo del proyecto"
              required
            />

            <SelectField
              label={
                <>
                  Estrategia de Consenso
                  <Tooltip content="Define cómo los agentes del sistema alcanzan acuerdo. La Votación Ponderada asigna diferentes pesos según la especialidad de cada agente.">
                    <i className="fas fa-info-circle help-icon"></i>
                  </Tooltip>
                </>
              }
              id="consensus"
              value={state.selectedConsensusStrategy}
              onChange={(e) => actions.setSelectedConsensusStrategy(e.target.value)}
              options={[
                { value: 'weighted_voting', label: 'Votación Ponderada' },
                { value: 'majority', label: 'Mayoría' },
                { value: 'unanimous', label: 'Unánime' },
                { value: 'confidence_threshold', label: 'Umbral de Confianza' }
              ]}
              helpText="Cómo se resuelven desacuerdos entre agentes durante el análisis"
              required
            />
          </div>

          <TextAreaField
            label="Necesidad de Negocio"
            id="businessNeed"
            value={businessNeed}
            onChange={(e) => setBusinessNeed(e.target.value)}
            placeholder="Describe detalladamente la necesidad de negocio que quieres analizar. Incluye contexto, objetivos, restricciones y cualquier información relevante..."
            helpText="Proporciona una descripción clara y detallada de la necesidad de negocio para obtener mejores resultados"
            maxLength={1000}
            minLength={10}
            showCounter={true}
            required
            rows={4}
            onValidationChange={setIsBusinessNeedValid}
          />

          <div className="form-actions">
            <ActionButton
              type="primary"
              size="medium"
              loading={state.loading}
              disabled={state.loading || !isBusinessNeedValid}
              icon="fas fa-play"
              onClick={handleAnalyze}
            >
              {state.loading ? 'Analizando...' : 'Ejecutar Análisis'}
            </ActionButton>

            <ExampleLoader
              onLoadExample={handleLoadExample}
              disabled={state.loading}
            />

            <ActionButton
              type="secondary"
              size="medium"
              disabled={state.loading}
              icon="fas fa-magic"
              onClick={handleExampleAnalysis}
            >
              Análisis de Ejemplo
            </ActionButton>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {state.error && (
        <div className="alert alert-error">
          <i className="fas fa-exclamation-circle"></i>
          {state.error}
        </div>
      )}

      {/* Resultados del Análisis */}
      {state.currentAnalysis && (
        <div 
          className="analysis-results" 
          data-testid="analysis-results"
          id="main-content"
          role="region"
          aria-label="Resultados del análisis"
        >
          {/* Dashboard Ejecutivo Mejorado */}
          <DashboardExecutive analysis={state.currentAnalysis} />
          
          {/* Resumen Mejorado de Resultados */}
          <ResultSummary
            executionTime={state.currentAnalysis.execution_time}
            methodology={state.currentAnalysis.methodology}
            consensusResult={state.currentAnalysis.consensus_result}
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

          <div className="card">
            <div className="card-header">
              <h3>
                <i className="fas fa-users"></i> Análisis Detallado por Agentes
                <Tooltip content="Vista consolidada: Explora todos los análisis sin necesidad de abrir múltiples modales. Cambia entre vista de pestañas y acordeón según tu preferencia.">
                  <i className="fas fa-info-circle help-icon"></i>
                </Tooltip>
              </h3>
            </div>
            <div className="card-content">
              {/* Vista Consolidada - Nueva opción principal */}
              <ConsolidatedView 
                analysis={state.currentAnalysis} 
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
                agents={state.currentAnalysis.worker_responses || []}
                formatAgentResponse={formatAgentResponse}
                onShowFullContent={handleShowFullContent}
              />
            </div>
          </div>

          {/* Síntesis del Coordinador - Centro de Inteligencia */}
          {state.currentAnalysis.coordinator_response && (
            <div className="card">
              <CoordinatorSynthesis
                coordinator={formatAgentResponse(state.currentAnalysis.coordinator_response)}
                workers={(state.currentAnalysis.worker_responses || []).map(formatAgentResponse)}
                onShowFull={(coord) => handleShowFullContent(coord)}
              />
            </div>
          )}

          {/* Respuesta del Supervisor */}
          {state.currentAnalysis.supervisor_response && (
            <div className="card">
              <div className="card-header">
                <h3><i className="fas fa-crown"></i> Decisión Final del Supervisor</h3>
              </div>
              <div className="card-content">
                <div className="agent-card supervisor-card">
                  <div className="agent-header">
                    <h5>{state.currentAnalysis.supervisor_response.agent_name}</h5>
                    <div className="agent-meta">
                      <span className={`confidence ${state.currentAnalysis.supervisor_response.confidence > 0.8 ? 'high' : state.currentAnalysis.supervisor_response.confidence > 0.6 ? 'medium' : 'low'}`}>
                        {(state.currentAnalysis.supervisor_response.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="agent-content">
                    <ContentPreview content={state.currentAnalysis.supervisor_response.content} />
                    <div className="agent-actions">
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => handleShowFullContent(formatAgentResponse(
                          state.currentAnalysis.supervisor_response,
                          state.currentAnalysis.metadata || {}
                        ))}
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
