import React, { useState, useEffect } from 'react';

const FILTERS = {
  all: { label: 'Todos', icon: 'fa-layer-group' },
  products: { label: 'Productos', icon: 'fa-box' },
  technical: { label: 'Técnico', icon: 'fa-code' },
  processes: { label: 'Procesos', icon: 'fa-tasks' },
  quality: { label: 'Calidad', icon: 'fa-shield-alt' },
  design: { label: 'Diseño', icon: 'fa-palette' }
};

const AGENT_CATEGORIES = {
  ProductManager: 'products',
  ProductOwner: 'products',
  UXUI_Designer: 'design',
  TechnicalLead: 'technical',
  ScrumMaster: 'processes',
  QA_Specialist: 'quality'
};

export function AgentFilters({ agents, onFilterChange }) {
  const [activeFilter, setActiveFilter] = useState('all');

  // Efecto para inicializar con todos los agentes
  useEffect(() => {
    if (agents && agents.length > 0 && activeFilter === 'all') {
      onFilterChange(agents);
    }
  }, [agents, activeFilter, onFilterChange]);

  const handleFilter = (filterKey) => {
    setActiveFilter(filterKey);
    const filtered = filterKey === 'all' 
      ? agents 
      : agents.filter(agent => {
          const category = AGENT_CATEGORIES[agent.agent_name] || 'all';
          return category === filterKey;
        });
    onFilterChange(filtered);
  };

  return (
    <div className="agent-filters">
      {Object.entries(FILTERS).map(([key, { label, icon }]) => (
        <button
          key={key}
          className={`filter-btn ${activeFilter === key ? 'active' : ''}`}
          onClick={() => handleFilter(key)}
        >
          <i className={`fas ${icon}`}></i>
          {label}
          {activeFilter === key && <i className="fas fa-check filter-check"></i>}
        </button>
      ))}
    </div>
  );
}

