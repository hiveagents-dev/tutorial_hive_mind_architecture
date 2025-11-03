import React, { useState } from 'react';

export function PersonaCard({ persona, index }) {
  if (!persona || typeof persona === 'string') {
    return null;
  }

  const name = persona.name || persona.title || `Persona ${index + 1}`;
  const age = persona.age || persona.demographics?.age || 'N/A';
  const role = persona.role || persona.occupation || persona.description || '';
  const goals = Array.isArray(persona.goals) ? persona.goals : 
                persona.objectives ? (Array.isArray(persona.objectives) ? persona.objectives : [persona.objectives]) : [];
  const painPoints = Array.isArray(persona.pain_points) ? persona.pain_points : 
                     persona.challenges ? (Array.isArray(persona.challenges) ? persona.challenges : [persona.challenges]) : [];
  const needs = Array.isArray(persona.needs) ? persona.needs : [];
  const avatar = persona.avatar || getPersonaEmoji(role);
  const type = persona.type || 'Primary';

  return (
    <div className={`persona-card-enhanced ${type.toLowerCase()}`}>
      <div className="persona-header-enhanced">
        <div className="persona-avatar-enhanced">
          <div className="avatar-circle" role="img" aria-label={`Avatar de ${name}`}>
            {avatar}
          </div>
          {type && (
            <span 
              className="persona-type-badge" 
              aria-label={`Tipo de persona: ${type}`}
              role="status"
            >
              {type}
            </span>
          )}
        </div>
        <div className="persona-title-section">
          <h5>{name}</h5>
          <div className="persona-meta-enhanced">
            {age && (
              <span className="persona-age">
                <i className="fas fa-birthday-cake" aria-hidden="true"></i>
                <span>Edad: {age}</span>
              </span>
            )}
            {role && (
              <span className="persona-role">
                <i className="fas fa-briefcase" aria-hidden="true"></i>
                <span>{role}</span>
              </span>
            )}
          </div>
        </div>
      </div>
      
      <div className="persona-content-enhanced">
        {goals.length > 0 && (
          <div className="persona-section-enhanced goals">
            <h6>
              <i className="fas fa-bullseye" aria-hidden="true"></i>
              Objetivos ({goals.length})
            </h6>
            <ul className="goals-list">
              {goals.map((goal, idx) => (
                <li key={idx}>
                  <span className="goal-icon">✓</span>
                  <span>{typeof goal === 'string' ? goal : (goal.description || goal.goal || goal)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {needs.length > 0 && (
          <div className="persona-section-enhanced needs">
            <h6>
              <i className="fas fa-heart" aria-hidden="true"></i>
              Necesidades ({needs.length})
            </h6>
            <ul className="needs-list">
              {needs.slice(0, 3).map((need, idx) => (
                <li key={idx}>
                  <span className="need-icon">♥</span>
                  <span>{typeof need === 'string' ? need : need}</span>
                </li>
              ))}
              {needs.length > 3 && <li className="more-items">+{needs.length - 3} más...</li>}
            </ul>
          </div>
        )}
        
        {painPoints.length > 0 && (
          <div className="persona-section-enhanced painpoints">
            <h6>
              <i className="fas fa-exclamation-triangle" aria-hidden="true"></i>
              Pain Points ({painPoints.length})
            </h6>
            <ul className="painpoints-list">
              {painPoints.slice(0, 2).map((point, idx) => (
                <li key={idx}>
                  <span className="painpoint-icon">⚠</span>
                  <span>{typeof point === 'string' ? point : (point.description || point)}</span>
                </li>
              ))}
              {painPoints.length > 2 && <li className="more-items">+{painPoints.length - 2} más...</li>}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function getPersonaEmoji(role) {
  const emojis = {
    'madre': '👩‍🍼',
    'médico': '👨‍⚕️',
    'abuela': '👵',
    'profesional': '👔',
    'estudiante': '🎓',
    'default': '👤'
  };
  
  const lowerRole = (role || '').toLowerCase();
  for (const [key, emoji] of Object.entries(emojis)) {
    if (lowerRole.includes(key)) return emoji;
  }
  return emojis.default;
}

export function JourneyMap({ journeyMap }) {
  const [selectedStage, setSelectedStage] = React.useState(null);
  
  if (!journeyMap || (typeof journeyMap === 'string' && !Array.isArray(journeyMap))) {
    return null;
  }

  const stages = Array.isArray(journeyMap) ? journeyMap : 
                journeyMap.stages || journeyMap.user_journey || [];

  if (stages.length === 0) return null;

  return (
    <div className="journey-map-interactive">
      <div className="journey-header">
        <h4>
          <i className="fas fa-route" aria-hidden="true"></i>
          Customer Journey Map Interactivo
        </h4>
        <p className="journey-subtitle">Haz clic en cada etapa para ver más detalles</p>
      </div>
      
      <div className="journey-timeline-visual">
        <div className="timeline-line"></div>
        {stages.map((stage, index) => {
          const stageData = typeof stage === 'string' ? { name: stage } : stage;
          const stageName = stageData.name || stageData.stage || `Etapa ${index + 1}`;
          const emotion = stageData.emotion || stageData.feeling || '';
          const touchpoints = Array.isArray(stageData.touchpoints) ? stageData.touchpoints : 
                            stageData.touch_points ? (Array.isArray(stageData.touch_points) ? stageData.touch_points : [stageData.touch_points]) : [];
          const painPoints = Array.isArray(stageData.pain_points) ? stageData.pain_points : 
                           stageData.challenges ? (Array.isArray(stageData.challenges) ? stageData.challenges : [stageData.challenges]) : [];
          const opportunities = Array.isArray(stageData.opportunities) ? stageData.opportunities : 
                              stageData.opportunity ? (Array.isArray(stageData.opportunity) ? stageData.opportunity : [stageData.opportunity]) : [];
          const isSelected = selectedStage === index;

          return (
            <div 
              key={index} 
              className={`journey-stage-visual ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedStage(isSelected ? null : index)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedStage(isSelected ? null : index);
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`Etapa ${index + 1}: ${stageName}. ${isSelected ? 'Expandida' : 'Clic para expandir'}`}
              aria-expanded={isSelected}
            >
              <div className="stage-marker">
                <div className="stage-number-circle" aria-label={`Etapa número ${index + 1}`}>
                  {index + 1}
                </div>
                {emotion && (
                  <div 
                    className="stage-emotion-badge" 
                    aria-label={`Emoción: ${emotion}`}
                    role="img"
                  >
                    {getEmotionEmoji(emotion)}
                  </div>
                )}
              </div>
              <div className="stage-card">
                <h5 id={`stage-${index}-title`}>{stageName}</h5>
                {isSelected && (
                  <div className="stage-details-expanded">
                    {touchpoints.length > 0 && (
                      <div className="stage-detail-section">
                        <h6>
                          <i className="fas fa-hand-point-right" aria-hidden="true"></i>
                          Touchpoints
                        </h6>
                        <ul>
                          {touchpoints.map((tp, idx) => (
                            <li key={idx}>{tp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {painPoints.length > 0 && (
                      <div className="stage-detail-section painpoints">
                        <h6>
                          <i className="fas fa-exclamation-triangle" aria-hidden="true"></i>
                          Pain Points
                        </h6>
                        <ul>
                          {painPoints.map((pp, idx) => (
                            <li key={idx}>{pp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {opportunities.length > 0 && (
                      <div className="stage-detail-section opportunities">
                        <h6>
                          <i className="fas fa-lightbulb" aria-hidden="true"></i>
                          Oportunidades
                        </h6>
                        <ul>
                          {opportunities.map((opp, idx) => (
                            <li key={idx}>{opp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function getEmotionEmoji(emotion) {
  const emotions = {
    'ansiedad': '😰',
    'escepticismo': '🤔',
    'compromiso': '💪',
    'frustración': '😤',
    'alegría': '😊',
    'confianza': '😌'
  };
  const lower = (emotion || '').toLowerCase();
  return emotions[lower] || '😐';
}

export function WireframesGallery({ wireframes }) {
  const [selectedFrame, setSelectedFrame] = useState(null);
  
  if (!wireframes || (typeof wireframes === 'string' && !Array.isArray(wireframes))) {
    return null;
  }

  const frames = Array.isArray(wireframes) ? wireframes : 
                 wireframes.wireframes || wireframes.screens || [];

  if (frames.length === 0) return null;

  return (
    <div className="wireframes-gallery">
      <div className="wireframes-header">
        <h4><i className="fas fa-mobile-alt"></i> Galería de Wireframes</h4>
        <p className="wireframes-subtitle">{frames.length} pantallas identificadas</p>
      </div>
      <div className="wireframes-gallery-enhanced">
        {frames.map((frame, index) => {
          const frameData = typeof frame === 'string' ? { name: frame } : frame;
          const name = frameData.name || frameData.title || frameData.screen || `Pantalla ${index + 1}`;
          const notes = frameData.notes || frameData.description || frameData.purpose || '';
          const thumbnail = frameData.thumbnail || frameData.image || frameData.url || null;
          const url = frameData.url || frameData.link || null;
          const isSelected = (selectedFrame !== undefined && selectedFrame !== null) ? selectedFrame === index : false;

          return (
            <div 
              key={index} 
              className={`wireframe-card-enhanced ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedFrame(isSelected ? null : index)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedFrame(isSelected ? null : index);
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`${name}. ${isSelected ? 'Expandido' : 'Clic para ver detalles'}`}
              aria-expanded={isSelected}
            >
              <div className="wireframe-thumbnail-enhanced">
                {thumbnail ? (
                  <img src={thumbnail} alt={name} />
                ) : (
                  <div className="placeholder" aria-label="Placeholder de wireframe">
                    <i className="fas fa-mobile-alt" aria-hidden="true"></i>
                  </div>
                )}
                <div className="wireframe-overlay" aria-hidden="true">
                  <i className="fas fa-search-plus" aria-hidden="true"></i>
                  <span>Ver detalles</span>
                </div>
              </div>
              <div className="wireframe-info-enhanced">
                <h5>{name}</h5>
                {notes && <p>{notes}</p>}
                {url && (
                  <a 
                    href={url} 
                    target="_blank" 
                    rel="noreferrer noopener" 
                    className="wireframe-link"
                    onClick={(e) => e.stopPropagation()}
                    aria-label={`Abrir ${name} en Figma o Miro (se abre en nueva ventana)`}
                  >
                    <i className="fas fa-external-link-alt" aria-hidden="true"></i>
                    Abrir en Figma/Miro
                  </a>
                )}
                {isSelected && (
                  <div className="wireframe-details">
                    {frameData.components && Array.isArray(frameData.components) && (
                      <div className="wireframe-components">
                        <strong>Componentes:</strong>
                        <div className="components-tags">
                          {frameData.components.map((comp, idx) => (
                            <span key={idx} className="component-tag">{comp}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {frameData.interactions && (
                      <div className="wireframe-interactions">
                        <strong>Interacciones:</strong> {frameData.interactions}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <div className="wireframes-actions">
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Abrir todos los wireframes en Miro"
        >
          <i className="fas fa-external-link-alt" aria-hidden="true"></i>
          Abrir todo en Miro
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Descargar todos los wireframes como archivo ZIP"
        >
          <i className="fas fa-download" aria-hidden="true"></i>
          Descargar como ZIP
        </button>
        <button 
          className="btn btn-sm btn-secondary"
          aria-label="Exportar wireframes a Figma"
        >
          <i className="fab fa-figma" aria-hidden="true"></i>
          Exportar a Figma
        </button>
      </div>
    </div>
  );
}

export function DesignSystemGuide({ designSystem }) {
  if (!designSystem || typeof designSystem === 'string') {
    return null;
  }

  const colors = designSystem.colors || {};
  const typography = designSystem.typography || {};
  const spacing = designSystem.spacing || {};
  const components = designSystem.components || [];

  return (
    <div className="design-system-guide">
      <h4><i className="fas fa-palette"></i> Guía de Diseño</h4>
      
      {Object.keys(colors).length > 0 && (
        <div className="design-section">
          <h5>Paleta de Colores:</h5>
          <div className="colors-grid">
            {Object.entries(colors).map(([key, value]) => {
              const colorValue = typeof value === 'string' ? value : value.hex || value.value || '#000';
              return (
                <div key={key} className="color-item">
                  <div className="color-swatch" style={{ backgroundColor: colorValue }}></div>
                  <div className="color-info">
                    <strong>{key}</strong>
                    <span>{colorValue}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {(typography.fontFamily || typography.headings || typography.body) && (
        <div className="design-section">
          <h5>Tipografía:</h5>
          <ul className="design-list">
            {typography.headings && (
              <li><strong>Headings:</strong> {typeof typography.headings === 'string' ? typography.headings : (
                typography.headings?.fontFamily || typography.headings?.font || 
                (typeof typography.headings === 'object' ? Object.keys(typography.headings).join(', ') : String(typography.headings))
              )}</li>
            )}
            {typography.body && (
              <li><strong>Body:</strong> {typeof typography.body === 'string' ? typography.body : (
                typography.body?.fontFamily || typography.body?.font || 
                (typeof typography.body === 'object' ? Object.keys(typography.body).join(', ') : String(typography.body))
              )}</li>
            )}
            {typography.fontFamily && (
              <li><strong>Font Family:</strong> {typography.fontFamily}</li>
            )}
          </ul>
        </div>
      )}

      {spacing.base && (
        <div className="design-section">
          <h5>Espaciado:</h5>
          <ul className="design-list">
            <li><strong>Base:</strong> {spacing.base}</li>
            {spacing.scale && <li><strong>Escala:</strong> {spacing.scale}</li>}
          </ul>
        </div>
      )}

      <div className="design-actions">
        <button className="btn btn-sm btn-secondary"><i className="fas fa-download"></i> Exportar Design System</button>
        <button className="btn btn-sm btn-secondary"><i className="fab fa-figma"></i> Figma Link</button>
        <button className="btn btn-sm btn-secondary"><i className="fas fa-code"></i> Tokens CSS</button>
      </div>
    </div>
  );
}

