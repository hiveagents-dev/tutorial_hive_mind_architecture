import React from 'react';

export function SprintRoadmap({ sprintBacklog, sprintStructure }) {
  if (!sprintBacklog && !sprintStructure) return null;

  const sprints = Array.isArray(sprintBacklog) ? sprintBacklog : 
                 sprintBacklog?.sprints || sprintBacklog || [];

  const sprintDuration = sprintStructure?.duration || '2 weeks';

  if (sprints.length === 0) return null;

  return (
    <div className="sprint-roadmap">
      <h4>
        <i className="fas fa-calendar-alt" aria-hidden="true"></i>
        Roadmap de Sprints ({sprintDuration} c/u)
      </h4>
      
      <div className="sprints-timeline">
        {sprints.map((sprint, index) => {
          const sprintNum = sprint.sprint || index + 1;
          const committed = sprint.committed || sprint.committed_stories?.length > 0;
          const stories = sprint.committed_stories || sprint.stories || [];
          const goal = sprint.sprint_goal || sprint.goal || '';
          const progress = sprint.progress || calculateProgress(sprint);
          const risks = sprint.risks || sprint.risk_level || 'none';
          const dependencies = sprint.dependencies || [];

          return (
            <div key={index} className="sprint-card">
              <div className="sprint-header">
                <div className="sprint-number">SPRINT {sprintNum}</div>
                <div className="sprint-meta">
                  <span className="sprint-period">Sem {sprintNum * 2 - 1}-{sprintNum * 2}</span>
                  {getRiskBadge(risks)}
                </div>
              </div>
              
              <div className="sprint-progress">
                <div 
                  className="progress-bar" 
                  role="progressbar"
                  aria-valuenow={progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Progreso del sprint ${sprintNum}: ${progress}%`}
                >
                  <div 
                    className="progress-fill" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <span className="progress-text" aria-label={`Progreso del sprint: ${progress}%`}>
                  {progress}%
                </span>
              </div>

              {goal && (
                <div className="sprint-goal">
                  <strong>Sprint Goal:</strong> {goal}
                </div>
              )}

              {stories.length > 0 && (
                <div className="sprint-stories">
                  <ul>
                    {stories.slice(0, 3).map((story, idx) => {
                      const storyId = typeof story === 'string' ? story : story.id || story.title || '';
                      return <li key={idx}>• {storyId}</li>;
                    })}
                    {stories.length > 3 && <li className="more-stories">+ {stories.length - 3} más</li>}
                  </ul>
                </div>
              )}

              {dependencies.length > 0 && (
                <div className="sprint-dependencies">
                  <i className="fas fa-exclamation-triangle" aria-hidden="true"></i>
                  <strong>Dependencia:</strong> {dependencies[0]}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="roadmap-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Abrir calendario interactivo de sprints"
        >
          <i className="fas fa-calendar" aria-hidden="true"></i>
          Calendario interactivo
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Exportar roadmap como diagrama de Gantt"
        >
          <i className="fas fa-project-diagram" aria-hidden="true"></i>
          Exportar Gantt
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver capacidad del equipo"
        >
          <i className="fas fa-users" aria-hidden="true"></i>
          Ver capacidad
        </button>
      </div>
    </div>
  );
}

function calculateProgress(sprint) {
  if (sprint.progress) return sprint.progress;
  if (sprint.estimated_hours && sprint.committed_hours) {
    return Math.round((sprint.committed_hours / sprint.estimated_hours) * 100);
  }
  return 30 + (sprint.sprint || 1) * 15; // Fallback
}

function getRiskBadge(risks) {
  if (!risks || risks === 'none') return null;
  const riskLevel = typeof risks === 'string' ? risks : risks.level || 'medium';
  
  const badges = {
    high: (
      <span className="risk-badge high" role="status" aria-label="Alto riesgo">
        <i className="fas fa-circle" aria-hidden="true"></i>
        ALTO RIESGO
      </span>
    ),
    medium: (
      <span className="risk-badge medium" role="status" aria-label="Riesgo medio">
        <i className="fas fa-circle" aria-hidden="true"></i>
        M
      </span>
    ),
    low: (
      <span className="risk-badge low" role="status" aria-label="En track">
        <i className="fas fa-circle" aria-hidden="true"></i>
        🟢 En track
      </span>
    )
  };
  
  return badges[riskLevel] || badges.medium;
}

export function RiskMatrix({ risks }) {
  if (!risks || (typeof risks === 'string' && !Array.isArray(risks))) {
    return null;
  }

  const riskList = Array.isArray(risks) ? risks : 
                   risks.risks || risks.risk_assessment || [];

  if (riskList.length === 0) return null;

  // Categorizar riesgos
  const categorized = {
    critical: [],
    high: [],
    medium: [],
    low: []
  };

  riskList.forEach(risk => {
    const riskData = typeof risk === 'string' ? { risk, impact: 'Medium', probability: 'Medium' } : risk;
    const impact = (riskData.impact || 'Medium').toLowerCase();
    const probability = (riskData.probability || 'Medium').toLowerCase();

    if ((impact === 'high' || impact === 'blocker') && (probability === 'high' || probability === 'high')) {
      categorized.critical.push(riskData);
    } else if (impact === 'high' || probability === 'high') {
      categorized.high.push(riskData);
    } else if (impact === 'medium' || probability === 'medium') {
      categorized.medium.push(riskData);
    } else {
      categorized.low.push(riskData);
    }
  });

  return (
    <div className="risk-matrix-visual">
      <h4>
        <i className="fas fa-exclamation-triangle" aria-hidden="true"></i>
        Matriz de Riesgos
      </h4>
      
      <div className="risk-matrix-grid">
        <div className="matrix-header">
          <div></div>
          <div className="matrix-label">Bajo</div>
          <div className="matrix-label">Medio</div>
          <div className="matrix-label">Alto</div>
        </div>
        <div className="matrix-row">
          <div className="matrix-label">Alto</div>
          <div className="matrix-cell low">{categorized.low.length}</div>
          <div className="matrix-cell medium">{categorized.medium.length}</div>
          <div className="matrix-cell high">{categorized.high.length}</div>
        </div>
        <div className="matrix-row">
          <div className="matrix-label">Medio</div>
          <div className="matrix-cell low">{categorized.low.length}</div>
          <div className="matrix-cell medium">{categorized.medium.length}</div>
          <div className="matrix-cell high">{categorized.high.length}</div>
        </div>
        <div className="matrix-row">
          <div className="matrix-label">Bajo</div>
          <div className="matrix-cell low">{categorized.low.length}</div>
          <div className="matrix-cell medium">{categorized.medium.length}</div>
          <div className="matrix-cell high">{categorized.high.length}</div>
        </div>
      </div>

      {categorized.critical.length > 0 && (
        <div className="risk-critical">
          <h5>
            <i className="fas fa-exclamation-circle" aria-hidden="true"></i>
            Riesgos Críticos:
          </h5>
          <ul>
            {categorized.critical.map((risk, idx) => (
              <li key={idx}>
                <strong>{typeof risk === 'string' ? risk : risk.risk}</strong>
                {risk.mitigation && <span> → {risk.mitigation}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="risk-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Ver plan detallado de mitigación de riesgos"
        >
          <i className="fas fa-file-alt" aria-hidden="true"></i>
          Ver plan detallado
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Exportar RAID log completo"
        >
          <i className="fas fa-download" aria-hidden="true"></i>
          Exportar RAID log
        </button>
      </div>
    </div>
  );
}

export function CeremoniesCalendar({ ceremonies, sprintStructure }) {
  if (!ceremonies && !sprintStructure) return null;

  const ceremonyList = Array.isArray(ceremonies) ? ceremonies : 
                       ceremonies?.ceremonies || 
                       sprintStructure?.ceremonies || [];

  if (ceremonyList.length === 0) return null;

  const defaultCeremonies = [
    { day: 'Lunes', time: '09:00 - 09:15', name: 'Sprint Planning (Primera sesión)' },
    { day: 'Martes', time: '10:00 - 10:15', name: 'Daily Standup' },
    { day: 'Miércoles', time: '10:00 - 10:15', name: 'Daily Standup' },
    { day: 'Jueves', time: '10:00 - 10:15', name: 'Daily Standup' },
    { day: 'Viernes', time: '10:00 - 10:15', name: 'Daily Standup' },
    { day: 'Viernes', time: '14:00 - 15:00', name: 'Sprint Review + Retrospective' }
  ];

  const calendarItems = ceremonyList.length > 0 ? ceremonyList.map((c, idx) => {
    if (typeof c === 'string') {
      return { ...defaultCeremonies[idx] || defaultCeremonies[0], name: c };
    }
    return {
      day: c.day || defaultCeremonies[idx]?.day || 'Lunes',
      time: c.time || c.duration || defaultCeremonies[idx]?.time || '09:00',
      name: c.name || c.ceremony || c
    };
  }) : defaultCeremonies;

  return (
    <div className="ceremonies-calendar">
      <h4>
        <i className="fas fa-calendar-check" aria-hidden="true"></i>
        Ceremonias Ágiles
      </h4>
      
      <div className="ceremonies-list">
        {calendarItems.map((ceremony, idx) => (
          <div key={idx} className="ceremony-item">
            <div className="ceremony-day">{ceremony.day}:</div>
            <div className="ceremony-time">[{ceremony.time}]</div>
            <div className="ceremony-name">{ceremony.name}</div>
          </div>
        ))}
      </div>

      <div className="ceremonies-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Agregar ceremonias ágiles a calendario personal"
        >
          <i className="fas fa-calendar-plus" aria-hidden="true"></i>
          Agregar al calendario
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Compartir calendario de ceremonias"
        >
          <i className="fas fa-share" aria-hidden="true"></i>
          Compartir
        </button>
      </div>
    </div>
  );
}

