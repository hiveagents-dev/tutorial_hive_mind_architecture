import React from 'react';

export function ArchitectureDiagram({ architecture }) {
  if (!architecture) return null;

  const pattern = architecture.pattern || architecture.architecture_pattern || '';
  const c4Diagrams = architecture.c4_diagrams || {};
  const containers = c4Diagrams.containers || [];
  const components = c4Diagrams.components || [];

  return (
    <div className="architecture-diagram">
      <h4>
        <i className="fas fa-sitemap" aria-hidden="true"></i>
        Diagrama de Arquitectura
      </h4>
      {pattern && (
        <div className="arch-pattern">
          <strong>Patrón:</strong> {pattern}
        </div>
      )}
      
      <div className="arch-diagram-ascii">
        <pre className="ascii-art">
{`┌─────────────────────────────────────────────────┐
│ Frontend (React + Next.js)                      │
│ ├─ Dashboard Component                          │
│ ├─ Content Browser                              │
│ └─ User Profile Manager                         │
└────────────────────┬────────────────────────────┘
                     │
      ┌──────────────▼────────────────────────────┐
      │ API Gateway (Express + TypeScript)        │
      │ ├─ Rate Limiting                          │
      │ ├─ Authentication (JWT)                   │
      │ └─ Request/Response Logging               │
      └──────────────┬────────────────────────────┘
                     │
    ┌────────────────┴────────────────┐
    │                                 │
┌───▼────────┐              ┌─────────▼─────────┐
│ User       │              │ Content Service   │
│ Service    │              │                   │
│            │              │                   │
│ (Micro 1)  │              │ (Micro 2)         │
└───┬────────┘              └─────────┬─────────┘
    │                                 │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │ Event Bus (RabbitMQ / Kafka)    │
    │ [Async Communication]           │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │ Databases                        │
    │ ├─ PostgreSQL (Transactional)   │
    │ ├─ Redis (Caching)              │
    │ └─ Elasticsearch (Search)       │
    └─────────────────────────────────┘`}
        </pre>
      </div>

      <div className="arch-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Abrir diagrama en modo interactivo"
        >
          <i className="fas fa-expand" aria-hidden="true"></i>
          Modo interactivo
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver dependencias de arquitectura"
        >
          <i className="fas fa-link" aria-hidden="true"></i>
          Ver dependencias
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Exportar diagrama de arquitectura"
        >
          <i className="fas fa-download" aria-hidden="true"></i>
          Exportar
        </button>
      </div>
    </div>
  );
}

// Helper function para extraer valores string de objetos de tech stack
function safeExtractTechValue(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (typeof value === 'object') {
    // Buscar propiedades comunes que contengan el valor
    return value.framework || value.tech || value.name || value.primary || 
           value.provider || value.title || value.label || value.value ||
           (Array.isArray(value) ? value.map(v => safeExtractTechValue(v)).filter(v => v).join(', ') : null) ||
           null;
  }
  return null;
}

// Helper function para extraer rationale
function safeExtractRationale(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'object' && !Array.isArray(value)) {
    return typeof value.rationale === 'string' ? value.rationale : null;
  }
  return null;
}

export function TechStackVisual({ techStack }) {
  if (!techStack || typeof techStack === 'string') {
    return null;
  }

  const categories = {
    'Frontend Layer': techStack.frontend || techStack.frontend_layer,
    'Backend Layer': techStack.backend || techStack.backend_layer,
    'Database': techStack.database,
    'Infrastructure': techStack.infrastructure,
    'DevOps': techStack.devops
  };

  return (
    <div className="tech-stack-visual">
      <h4><i className="fas fa-laptop-code"></i> Stack Tecnológico</h4>
      
      <div className="tech-categories">
        {Object.entries(categories).map(([categoryName, categoryData]) => {
          if (!categoryData) return null;
          
          // Normalizar categoryData a un array de items
          let items = [];
          if (typeof categoryData === 'string') {
            items = [{ tech: categoryData, rationale: null }];
          } else if (Array.isArray(categoryData)) {
            items = categoryData.map(item => {
              const techVal = safeExtractTechValue(item) || (typeof item === 'string' ? item : null);
              const ratioVal = safeExtractRationale(item);
              return {
                tech: techVal || 'N/A',
                rationale: ratioVal
              };
            });
          } else if (typeof categoryData === 'object' && categoryData !== null) {
            // CASO ESPECIAL: Si categoryData es directamente {framework: "...", rationale: "..."}
            // (formato del backend TechnicalLead)
            if ('framework' in categoryData || 'primary' in categoryData || 'tech' in categoryData) {
              const techVal = safeExtractTechValue(categoryData);
              const ratioVal = safeExtractRationale(categoryData);
              if (techVal) {
                items = [{ tech: techVal, rationale: ratioVal }];
              }
            } else {
              // Si es un objeto con múltiples entradas (ej: {react: {...}, vue: {...}})
              items = Object.entries(categoryData).map(([key, value]) => {
                let techValue = null;
                let rationaleValue = null;
                
                // Si value es un objeto con framework/rationale
                if (value && typeof value === 'object' && !Array.isArray(value)) {
                  if (value.framework && typeof value.framework === 'string') {
                    techValue = value.framework;
                    rationaleValue = typeof value.rationale === 'string' ? value.rationale : null;
                  } else {
                    techValue = safeExtractTechValue(value);
                    rationaleValue = safeExtractRationale(value);
                  }
                } else if (typeof value === 'string') {
                  techValue = value;
                } else {
                  techValue = safeExtractTechValue(value);
                  rationaleValue = safeExtractRationale(value);
                }
                
                return {
                  tech: techValue || key,
                  rationale: rationaleValue
                };
              });
            }
          }

          // Filtrar items sin tech válido
          items = items.filter(item => item.tech && item.tech !== 'N/A');

          if (items.length === 0) return null;

          return (
            <div key={categoryName} className="tech-category-card">
              <h5>{categoryName}</h5>
              <div className="tech-items-list">
                {items.map((item, idx) => {
                  const tech = typeof item.tech === 'string' ? item.tech : 
                              (item.tech ? String(item.tech) : 'N/A');
                  const rationale = typeof item.rationale === 'string' ? item.rationale : null;
                  
                  return (
                    <div key={idx} className="tech-item-detailed">
                      <div className="tech-name">{tech}</div>
                      {rationale && typeof rationale === 'string' && (
                        <div className="tech-rationale">
                          <i className="fas fa-info-circle" aria-hidden="true"></i>
                          {rationale}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="tech-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver comparativa de alternativas tecnológicas"
        >
          <i className="fas fa-balance-scale" aria-hidden="true"></i>
          Comparativa de alternativas
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver configuración detallada del stack tecnológico"
        >
          <i className="fas fa-cog" aria-hidden="true"></i>
          Ver configuración
        </button>
      </div>
    </div>
  );
}

export function NFRChecklist({ nfrs }) {
  if (!nfrs || typeof nfrs === 'string') {
    return null;
  }

  const nfrData = typeof nfrs === 'object' && !Array.isArray(nfrs) ? nfrs : {
    performance: Array.isArray(nfrs) ? nfrs : [],
    security: [],
    scalability: []
  };

  const categories = {
    'Performance': nfrData.performance || nfrData.performance_requirements || [],
    'Security': nfrData.security || nfrData.security_requirements || [],
    'Scalability': nfrData.scalability || nfrData.scalability_requirements || [],
    'Reliability': nfrData.reliability || nfrData.reliability_requirements || [],
    'Maintainability': nfrData.maintainability || nfrData.maintainability_requirements || []
  };

  return (
    <div className="nfr-checklist">
      <h4>
        <i className="fas fa-check-square" aria-hidden="true"></i>
        No Funcionales (Performance & Security)
      </h4>
      
      {Object.entries(categories).map(([categoryName, items]) => {
        if (!items || items.length === 0) return null;
        
        const requirements = Array.isArray(items) ? items : Object.entries(items).map(([key, value]) => 
          typeof value === 'string' ? value : `${key}: ${value.value || value.target || ''}`
        );

        return (
          <div key={categoryName} className="nfr-category">
            <h5>{categoryName}:</h5>
            <ul className="nfr-list">
              {requirements.map((req, idx) => {
                const reqText = typeof req === 'string' ? req : 
                               req.description || req.requirement || req.name || req.title || 
                               (typeof req === 'object' ? Object.keys(req).join(', ') : String(req));
                const isMet = typeof req === 'object' ? req.met || req.compliant : true;
                
                return (
                  <li key={idx} className={isMet ? 'nfr-met' : 'nfr-pending'}>
                    <i 
                      className={`fas fa-${isMet ? 'check-circle' : 'circle'}`}
                      aria-label={isMet ? 'Requisito cumplido' : 'Requisito pendiente'}
                      aria-hidden="true"
                    ></i>
                    {reqText}
                    {isMet && <span className="nfr-checkmark">✓</span>}
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}

      <div className="nfr-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver detalles de implementación de requisitos no funcionales"
        >
          <i className="fas fa-info-circle" aria-hidden="true"></i>
          Detalles de implementación
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver estrategia de monitoreo de requisitos no funcionales"
        >
          <i className="fas fa-chart-line" aria-hidden="true"></i>
          Monitoreo
        </button>
      </div>
    </div>
  );
}

