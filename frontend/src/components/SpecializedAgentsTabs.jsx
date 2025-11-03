import React, { useState } from 'react';
import { AgentContentView } from './AgentContentView';

/**
 * Obtiene el ícono del agente
 */
function getAgentIcon(agentName) {
  const icons = {
    'ProductManager': 'fas fa-chart-bar',
    'ProductOwner': 'fas fa-clipboard-list',
    'UXUI_Designer': 'fas fa-palette',
    'TechnicalLead': 'fas fa-microchip',
    'ScrumMaster': 'fas fa-stream',
    'QA_Specialist': 'fas fa-vial'
  };
  return icons[agentName] || 'fas fa-user-gear';
}

/**
 * Obtiene el label del agente
 */
function getAgentLabel(agentName) {
  const labels = {
    'ProductManager': 'Product Manager',
    'ProductOwner': 'Product Owner',
    'UXUI_Designer': 'UX/UI Designer',
    'TechnicalLead': 'Technical Lead',
    'ScrumMaster': 'Scrum Master',
    'QA_Specialist': 'QA Specialist'
  };
  return labels[agentName] || agentName;
}

/**
 * Componente de pestañas para agentes especializados
 * Muestra un agente por pestaña
 */
export function SpecializedAgentsTabs({ agents, formatAgentResponse, onShowFullContent }) {
  if (!agents || agents.length === 0) {
    return (
      <div className="no-agents">
        <p>No hay agentes especializados disponibles</p>
      </div>
    );
  }

  // Preparar las pestañas de agentes
  const agentTabs = agents.map((agent, idx) => {
    const agentData = formatAgentResponse ? formatAgentResponse(agent) : agent;
    if (!agentData) return null;
    
    const agentName = agentData.agent_name || `Agent ${idx + 1}`;
    const confidence = agentData.confidence || 0;
    const confidencePct = Math.round(confidence * 100);
    
    return {
      id: `agent-${idx}`,
      agent_name: agentName,
      icon: getAgentIcon(agentName),
      label: getAgentLabel(agentName),
      badge: confidencePct > 0 ? `${confidencePct}%` : null,
      agentData: agentData,
      content: (
        <div className="agent-tab-content">
          <div className="agent-header-info">
            <div className="agent-meta-info">
              <div className="meta-item">
                <i className="fas fa-shield-alt" aria-hidden="true"></i>
                <span>Confianza: <strong>{confidencePct}%</strong></span>
              </div>
              {agentData.timestamp && (
                <div className="meta-item">
                  <i className="fas fa-clock" aria-hidden="true"></i>
                  <span>{new Date(agentData.timestamp).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
          <div className="agent-full-content">
            <AgentContentView
              agentName={agentName}
              content={agentData.content}
              data={agentData.output_json || agentData.data}
            />
          </div>
        </div>
      )
    };
  }).filter(tab => tab !== null);

  const [activeTab, setActiveTab] = useState(agentTabs.length > 0 ? agentTabs[0].id : null);

  if (agentTabs.length === 0) {
    return (
      <div className="no-agents">
        <p>No hay agentes disponibles para mostrar</p>
      </div>
    );
  }

  return (
    <div className="specialized-agents-tabs" role="tablist" aria-label="Agentes Especializados">
      <div className="tabs-header">
        {agentTabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setActiveTab(tab.id);
              }
            }}
            aria-selected={activeTab === tab.id}
            aria-label={`${tab.label}${tab.badge ? ` - Confianza: ${tab.badge}` : ''}`}
            role="tab"
            tabIndex={activeTab === tab.id ? 0 : -1}
          >
            <i className={tab.icon} aria-hidden="true"></i>
            <span>{tab.label}</span>
            {tab.badge && (
              <span className={`tab-badge ${parseInt(tab.badge) >= 80 ? 'high' : parseInt(tab.badge) >= 60 ? 'medium' : 'low'}`}>
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="tabs-content">
        {agentTabs.find(tab => tab.id === activeTab)?.content}
      </div>
    </div>
  );
}

