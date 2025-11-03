import React, { useState } from 'react';
import { AgentContentView } from './AgentContentView';

/**
 * Componente de pestañas para vista consolidada
 */
function Tabs({ tabs, activeTab, onTabChange }) {
  return (
    <div className="tabs-container" role="tablist" aria-label="Secciones de análisis">
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onTabChange(tab.id);
              }
            }}
            aria-selected={activeTab === tab.id}
            aria-label={`${tab.label}${tab.badge ? ` - ${tab.badge}` : ''}`}
            role="tab"
            tabIndex={activeTab === tab.id ? 0 : -1}
          >
            <i className={tab.icon} aria-hidden="true"></i>
            <span>{tab.label}</span>
            {tab.badge && (
              <span className="tab-badge" aria-label={`${tab.badge} elementos`}>
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="tabs-content">
        {tabs.find(tab => tab.id === activeTab)?.content}
      </div>
    </div>
  );
}

/**
 * Componente de acordeón para vista consolidada alternativa
 */
function Accordion({ items, defaultOpen = [] }) {
  const [openItems, setOpenItems] = useState(new Set(defaultOpen));

  const toggleItem = (id) => {
    const newOpen = new Set(openItems);
    if (newOpen.has(id)) {
      newOpen.delete(id);
    } else {
      newOpen.add(id);
    }
    setOpenItems(newOpen);
  };

  return (
    <div className="accordion-container">
      {items.map((item) => {
        const isOpen = openItems.has(item.id);
        return (
          <div key={item.id} className={`accordion-item ${isOpen ? 'open' : ''}`}>
            <button
              className="accordion-header"
              onClick={() => toggleItem(item.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleItem(item.id);
                }
              }}
              aria-expanded={isOpen}
              aria-label={`${item.label}${item.badge ? ` - ${item.badge}` : ''}. ${isOpen ? 'Expandido' : 'Colapsado'}`}
              tabIndex={0}
            >
              <div className="accordion-title">
                <i className={item.icon} aria-hidden="true"></i>
                <span>{item.label}</span>
                {item.badge && (
                  <span className="accordion-badge" aria-label={`Nivel de confianza: ${item.badge}`}>
                    {item.badge}
                  </span>
                )}
              </div>
              <i 
                className={`fas fa-chevron-${isOpen ? 'up' : 'down'} accordion-icon`} 
                aria-hidden="true"
                aria-label={isOpen ? 'Colapsar sección' : 'Expandir sección'}
              ></i>
            </button>
            {isOpen && (
              <div className="accordion-content">
                {item.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

/**
 * Vista consolidada que muestra todos los análisis sin necesidad de clics adicionales
 */
export function ConsolidatedView({ analysis, viewMode = 'tabs' }) {
  if (!analysis) return null;

  const workerAgents = (analysis.worker_responses || []).map((agent, idx) => ({
    id: `worker-${idx}`,
    agent_name: agent.agent_name || `Agent ${idx + 1}`,
    agent_role: agent.agent_role || agent.agent_name,
    icon: getAgentIcon(agent.agent_name),
    label: getAgentLabel(agent.agent_name),
    badge: agent.confidence ? `${Math.round(agent.confidence * 100)}%` : null,
    content: (
      <div className="consolidated-agent-view">
        <AgentContentView
          agentName={agent.agent_name}
          content={agent.content}
          data={agent.output_json || agent.data}
        />
      </div>
    )
  }));

  const tabs = [
    {
      id: 'workers',
      icon: 'fas fa-users',
      label: 'Agentes Especializados',
      badge: workerAgents.length,
      content: (
        <div className="consolidated-workers-view">
          {workerAgents.map((agent) => (
            <div key={agent.id} className="consolidated-agent-section">
              <div className="agent-section-header">
                <h4>
                  <i className={agent.icon}></i>
                  {agent.label}
                  {agent.badge && <span className="confidence-badge">{agent.badge}</span>}
                </h4>
              </div>
              {agent.content}
            </div>
          ))}
        </div>
      )
    },
    ...(analysis.coordinator_response ? [{
      id: 'coordinator',
      icon: 'fas fa-sitemap',
      label: 'Síntesis del Coordinador',
      badge: '✓',
      content: (
        <div className="consolidated-coordinator-view">
          <AgentContentView
            agentName={analysis.coordinator_response.agent_name}
            content={analysis.coordinator_response.content}
            data={analysis.coordinator_response.output_json || analysis.coordinator_response.data}
          />
        </div>
      )
    }] : []),
    ...(analysis.supervisor_response ? [{
      id: 'supervisor',
      icon: 'fas fa-crown',
      label: 'Decisión Final',
      badge: analysis.supervisor_response.confidence ? `${Math.round(analysis.supervisor_response.confidence * 100)}%` : null,
      content: (
        <div className="consolidated-supervisor-view">
          <AgentContentView
            agentName={analysis.supervisor_response.agent_name}
            content={analysis.supervisor_response.content}
            data={analysis.supervisor_response.output_json || analysis.supervisor_response.data}
          />
        </div>
      )
    }] : [])
  ];

  const accordionItems = [
    ...workerAgents.map(agent => ({
      ...agent,
      id: agent.id
    })),
    ...(analysis.coordinator_response ? [{
      id: 'coordinator',
      icon: 'fas fa-sitemap',
      label: 'Síntesis del Coordinador',
      badge: '✓',
      content: (
        <div className="consolidated-coordinator-view">
          <AgentContentView
            agentName={analysis.coordinator_response.agent_name}
            content={analysis.coordinator_response.content}
            data={analysis.coordinator_response.output_json || analysis.coordinator_response.data}
          />
        </div>
      )
    }] : []),
    ...(analysis.supervisor_response ? [{
      id: 'supervisor',
      icon: 'fas fa-crown',
      label: 'Decisión Final del Supervisor',
      badge: analysis.supervisor_response.confidence ? `${Math.round(analysis.supervisor_response.confidence * 100)}%` : null,
      content: (
        <div className="consolidated-supervisor-view">
          <AgentContentView
            agentName={analysis.supervisor_response.agent_name}
            content={analysis.supervisor_response.content}
            data={analysis.supervisor_response.output_json || analysis.supervisor_response.data}
          />
        </div>
      )
    }] : [])
  ];

  const [activeTab, setActiveTab] = useState('workers');
  const [currentViewMode, setCurrentViewMode] = useState(viewMode);

  return (
    <div className="consolidated-view">
      <div className="consolidated-view-header">
        <h2>
          <i className="fas fa-layer-group" aria-hidden="true"></i>
          Vista Consolidada del Análisis
        </h2>
        <div className="view-mode-toggle">
          <button
            className={`view-mode-btn ${currentViewMode === 'tabs' ? 'active' : ''}`}
            onClick={() => setCurrentViewMode('tabs')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setCurrentViewMode('tabs');
              }
            }}
            aria-label="Cambiar a vista de pestañas"
            aria-pressed={currentViewMode === 'tabs'}
            title="Vista de pestañas"
          >
            <i className="fas fa-folder" aria-hidden="true"></i>
            Pestañas
          </button>
          <button
            className={`view-mode-btn ${currentViewMode === 'accordion' ? 'active' : ''}`}
            onClick={() => setCurrentViewMode('accordion')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setCurrentViewMode('accordion');
              }
            }}
            aria-label="Cambiar a vista de acordeón"
            aria-pressed={currentViewMode === 'accordion'}
            title="Vista de acordeón"
          >
            <i className="fas fa-bars" aria-hidden="true"></i>
            Acordeón
          </button>
        </div>
      </div>

      {currentViewMode === 'tabs' ? (
        <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      ) : (
        <Accordion items={accordionItems} defaultOpen={['coordinator', 'supervisor']} />
      )}
    </div>
  );
}

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

