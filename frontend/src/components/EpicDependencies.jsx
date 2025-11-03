import React from 'react';

/**
 * Componente para visualizar diagramas de dependencia entre Epics
 */
export function EpicDependencies({ epics }) {
  if (!epics || !Array.isArray(epics) || epics.length === 0) {
    return null;
  }

  // Extraer todas las dependencias
  const dependencies = [];
  const epicMap = new Map();

  epics.forEach(epic => {
    const epicId = epic.id || epic.name || `EPIC-${epics.indexOf(epic)}`;
    epicMap.set(epicId, epic);
    
    if (epic.dependencies && Array.isArray(epic.dependencies)) {
      epic.dependencies.forEach(dep => {
        dependencies.push({
          from: epicId,
          to: dep.id || dep,
          type: dep.type || 'blocking'
        });
      });
    }
  });

  if (dependencies.length === 0) {
    return (
      <div className="epic-dependencies-diagram">
        <h4><i className="fas fa-project-diagram"></i> Dependencias entre Epics</h4>
        <p className="muted">No se identificaron dependencias entre epics.</p>
      </div>
    );
  }

  // Agrupar por epic origen
  const dependenciesByEpic = new Map();
  dependencies.forEach(dep => {
    if (!dependenciesByEpic.has(dep.from)) {
      dependenciesByEpic.set(dep.from, []);
    }
    dependenciesByEpic.get(dep.from).push(dep);
  });

  return (
    <div className="epic-dependencies-diagram">
      <h4>
        <i className="fas fa-project-diagram" aria-hidden="true"></i>
        Diagrama de Dependencias entre Epics
      </h4>
      <p className="dependencies-subtitle">
        <span className="sr-only">Descripción: </span>
        Visualización de relaciones y dependencias entre epics del proyecto
      </p>
      
      <div className="dependencies-graph">
        {Array.from(dependenciesByEpic.entries()).map(([epicId, deps]) => {
          const epic = epicMap.get(epicId);
          if (!epic) return null;

          return (
            <div key={epicId} className="dependency-node">
              <div className="dependency-node-info">
                <h5>{epic.name || epicId}</h5>
                <div className="epic-id">{epicId}</div>
                {epic.description && (
                  <p className="epic-description-small">{epic.description}</p>
                )}
              </div>
              
              <div className="dependency-arrows">
                <i className="fas fa-arrow-right"></i>
              </div>
              
              <div className="dependency-list">
                {deps.map((dep, idx) => {
                  const targetEpic = epicMap.get(dep.to);
                  const depType = dep.type === 'blocking' ? 'Bloqueante' : 
                                dep.type === 'soft' ? 'Suave' : 'Dependencia';
                  
                  return (
                    <div key={idx} className="dependency-item">
                      <span 
                        className={`dependency-type-badge ${dep.type || 'blocking'}`}
                        aria-label={`Tipo de dependencia: ${depType}`}
                        role="status"
                      >
                        {depType}
                      </span>
                      <span className="dependency-arrow" aria-hidden="true">→</span>
                      <span className="dependency-target">
                        {targetEpic ? (targetEpic.name || dep.to) : dep.to}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      
      {epics.some(e => !dependenciesByEpic.has(e.id || e.name)) && (
        <div className="independent-epics">
          <h5>Epics Independientes</h5>
          <div className="independent-list">
            {epics
              .filter(e => !dependenciesByEpic.has(e.id || e.name))
              .map((epic, idx) => (
                <span 
                  key={idx} 
                  className="independent-tag"
                  role="status"
                  aria-label={`Epic independiente: ${epic.name || epic.id}`}
                >
                  {epic.name || epic.id}
                </span>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
}

