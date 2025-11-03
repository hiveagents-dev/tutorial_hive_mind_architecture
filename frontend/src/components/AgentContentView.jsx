import React from 'react';
import { PersonaCard, JourneyMap, WireframesGallery, DesignSystemGuide } from './UXVisualizations';
import { ArchitectureDiagram, TechStackVisual, NFRChecklist } from './TechnicalVisualizations';
import { SprintRoadmap, RiskMatrix, CeremoniesCalendar } from './AgileVisualizations';
import { EpicDependencies } from './EpicDependencies';

function parseJson(content) {
  if (content && typeof content === 'object') return content;
  if (!content || typeof content !== 'string') return null;

  const raw = String(content).trim();

  // 1) Intento directo
  try { return JSON.parse(raw); } catch {}

  // 2) Remover fences ```json ... ```
  const fenced = raw.match(/```[a-zA-Z]*\n([\s\S]*?)```/);
  if (fenced && fenced[1]) {
    const inner = fenced[1].trim();
    try { return JSON.parse(inner); } catch {}
  }

  // 3) Extraer substring entre primera '{' y última '}'
  const start = raw.indexOf('{');
  const end = raw.lastIndexOf('}');
  if (start !== -1 && end !== -1 && end > start) {
    let sub = raw.substring(start, end + 1);
    // Normalizaciones comunes
    sub = sub.replace(/&quot;/g, '"').replace(/&apos;/g, "'");
    sub = sub.replace(/[“”]/g, '"').replace(/[‘’]/g, "'");
    // Quitar comas colgantes simples ,}\n o ,]\n
    sub = sub.replace(/,\s*}/g, '}').replace(/,\s*]/g, ']');

    // 3.1) Intento de prefijo JSON balanceado más largo
    const fixed = longestBalancedJson(sub);
    if (fixed) {
      try { return JSON.parse(fixed); } catch {}
    }

    // 3.2) Intento de parseo directo del sub
    try { return JSON.parse(sub); } catch {}
  }

  return null;
}

// Retorna el mayor prefijo de 'text' que forme un JSON balanceado (brackets/strings)
function longestBalancedJson(text) {
  let depth = 0;
  let inStr = false;
  let esc = false;
  let lastGood = -1;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inStr) {
      if (esc) { esc = false; continue; }
      if (ch === '\\') { esc = true; continue; }
      if (ch === '"') { inStr = false; }
      continue;
    } else {
      if (ch === '"') { inStr = true; continue; }
      if (ch === '{' || ch === '[') depth++;
      else if (ch === '}' || ch === ']') depth = Math.max(0, depth - 1);
      if (depth === 0 && ch === '}') lastGood = i + 1;
    }
  }
  if (lastGood > 0) return text.slice(0, lastGood);
  return null;
}

function Section({ title, icon, children, className = '' }) {
  return (
    <section className={`agent-section ${className}`} aria-labelledby={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}>
      <h4 
        id={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
        className="agent-section-title"
      >
        {icon && (
          <span 
            className="icon" 
            dangerouslySetInnerHTML={{ __html: icon }}
            aria-hidden="true"
          />
        )}
        {title}
      </h4>
      <div className="agent-section-body">{children}</div>
    </section>
  );
}

function List({ items }) {
  if (!Array.isArray(items) || items.length === 0) return null;
  return (
    <ul className="agent-list">
      {items.map((it, idx) => (
        <li key={idx}>
          <span className="bullet">▸</span>
          <span>
            {typeof it === 'string' ? it : (
              typeof it === 'object' && it !== null ? (
                // Renderizar objeto de forma humanizada
                <span className="list-item-object">
                  {it.title || it.name || it.description || it.label || it.scenario || 
                   (it.goal && `Objetivo: ${it.goal}`) ||
                   (it.requirement && `Requisito: ${it.requirement}`) ||
                   `${Object.keys(it).slice(0, 2).join(', ')}...`}
                </span>
              ) : String(it)
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}

function ProductManagerView({ data }) {
  return (
    <div className="agent-structured">
      {data.business_value && (<Section title="💼 Valor de Negocio" className="sec-blue"><p>{data.business_value}</p></Section>)}
      {data.target_market && (<Section title="🎯 Mercado Objetivo" className="sec-green"><p>{data.target_market}</p></Section>)}
      {data.competitive_analysis && (<Section title="🔍 Análisis Competitivo" className="sec-purple"><p>{data.competitive_analysis}</p></Section>)}
      {Array.isArray(data.success_metrics) && (<Section title="📊 Métricas de Éxito" className="sec-amber"><List items={data.success_metrics} /></Section>)}
      {data.strategic_alignment && (<Section title="🧭 Alineación Estratégica" className="sec-indigo"><p>{data.strategic_alignment}</p></Section>)}
      {Array.isArray(data.stakeholders) && (<Section title="👥 Stakeholders" className="sec-pink"><List items={data.stakeholders} /></Section>)}
      {data.risks_and_opportunities && (
        <Section title="⚖️ Riesgos y Oportunidades">
          <div className="grid-2">
            <div>
              <h5 className="sub red">Riesgos</h5>
              <List items={data.risks_and_opportunities.risks || []} />
            </div>
            <div>
              <h5 className="sub green">Oportunidades</h5>
              <List items={data.risks_and_opportunities.opportunities || []} />
            </div>
          </div>
        </Section>
      )}
      {data.recommendations && (<Section title="💡 Recomendaciones" className="sec-orange"><p>{data.recommendations}</p></Section>)}

      {/* Nuevas secciones según el output actualizado del PM */}
      {data.business_case && (
        <Section title="📈 Business Case" className="sec-blue">
          <p>{data.business_case}</p>
        </Section>
      )}
      {data.value_proposition && (
        <Section title="💎 Propuesta de Valor" className="sec-green">
          <p>{data.value_proposition}</p>
        </Section>
      )}

      {data.discovery_alignment && (
        <Section title="🧠 Discovery & Strategic Alignment" className="sec-indigo">
          {data.discovery_alignment.problem_statement && (
            <div className="acta-section">
              <h5><i className="fas fa-exclamation-circle"></i> Problem Statement</h5>
              <p>{data.discovery_alignment.problem_statement}</p>
            </div>
          )}
          {Array.isArray(data.discovery_alignment.success_metrics_detailed) && data.discovery_alignment.success_metrics_detailed.length > 0 && (
            <div className="acta-section">
              <h5>
                <i className="fas fa-chart-bar" aria-hidden="true"></i>
                Métricas SMART
              </h5>
              <ul className="mini-list">
                {data.discovery_alignment.success_metrics_detailed.map((m, idx) => (
                  <li key={idx}>{`${m.metric || 'Métrica'} — Baseline: ${m.baseline || '-'} → Target: ${m.target || '-'} (${m.timeline || '-'})`}</li>
                ))}
              </ul>
            </div>
          )}
          {data.discovery_alignment.business_constraints && (
            <div className="acta-section">
              <h5>
                <i className="fas fa-lock" aria-hidden="true"></i>
                Constraints
              </h5>
              <ul className="mini-list">
                {data.discovery_alignment.business_constraints.budget && (<li>Budget: {data.discovery_alignment.business_constraints.budget}</li>)}
                {data.discovery_alignment.business_constraints.timeline && (<li>Timeline: {data.discovery_alignment.business_constraints.timeline}</li>)}
                {data.discovery_alignment?.business_constraints?.compliance && Array.isArray(data.discovery_alignment.business_constraints.compliance) && data.discovery_alignment.business_constraints.compliance.length > 0 && (
                  <li>Compliance: {data.discovery_alignment.business_constraints.compliance.join(', ')}</li>
                )}
              </ul>
            </div>
          )}
          {data.discovery_alignment?.assumptions && Array.isArray(data.discovery_alignment.assumptions) && data.discovery_alignment.assumptions.length > 0 && (
            <div className="acta-section">
              <h5>
                <i className="fas fa-question-circle" aria-hidden="true"></i>
                Assumptions
              </h5>
              <List items={data.discovery_alignment.assumptions} />
            </div>
          )}
          {data.discovery_alignment?.out_of_scope && Array.isArray(data.discovery_alignment.out_of_scope) && data.discovery_alignment.out_of_scope.length > 0 && (
            <div className="acta-section">
              <h5>
                <i className="fas fa-ban" aria-hidden="true"></i>
                Fuera de Alcance
              </h5>
              <List items={data.discovery_alignment.out_of_scope} />
            </div>
          )}
          {data.discovery_alignment.stakeholder_signoff && (
            <div className="acta-section">
              <h5>
                <i className="fas fa-user-check" aria-hidden="true"></i>
                Stakeholder Signoff
              </h5>
              <p>
                {data.discovery_alignment.stakeholder_signoff.approved ? '✅ Aprobado' : '⏳ Pendiente'}
                {data.discovery_alignment.stakeholder_signoff.notes && (
                  <span className="muted"> — {data.discovery_alignment.stakeholder_signoff.notes}</span>
                )}
              </p>
            </div>
          )}
        </Section>
      )}
    </div>
  );
}

// Product Owner Board Component
const ProductOwnerBoard = ({ data }) => {
  const epicsByPriority = {
    "Must Have": [],
    "Should Have": [],
    "Could Have": [],
    "Backlog": [],
  };

  // Organize epics by priority
  (data.epics || []).forEach(epic => {
    const priority = epic.priority || 'Backlog';
    if (epicsByPriority[priority]) {
      epicsByPriority[priority].push(epic);
    }
  });

  return (
    <div className="product-owner-board">
      <div className="board-header">
        <h3>
          <i className="fas fa-clipboard-list" aria-hidden="true"></i>
          Product Backlog Management
        </h3>
        <div className="board-metadata">
          <span>
            <i className="fas fa-tag" aria-hidden="true"></i>
            <span className="sr-only">Versión: </span>
            {data.document_metadata?.version || '1.0'}
          </span>
          <span>
            <i className="fas fa-calendar-alt" aria-hidden="true"></i>
            <span className="sr-only">Fecha: </span>
            {data.document_metadata?.date || 'N/A'}
          </span>
          <span>
            <i className="fas fa-user-tie" aria-hidden="true"></i>
            Product Owner
          </span>
        </div>
      </div>

      <div className="board-columns">
        {Object.entries(epicsByPriority).map(([priority, epics]) => (
          <div key={priority} className="board-column">
            <div className="column-header">
              <h4>
                <i className="fas fa-list-alt" aria-hidden="true"></i>
                {priority}
              </h4>
              <span className="task-count">{(epics && Array.isArray(epics) ? epics.length : 0)}</span>
            </div>
            <div className="column-content">
              {epics.map(epic => (
                <div key={epic.id || epic.name} className="epic-card">
                  <div className="epic-id">{epic.id || 'EPIC'}</div>
                  <h5 className="epic-title">{epic.name}</h5>
                  <p className="epic-description">{epic.description}</p>
                  
                      {(() => {
                        const stories = epic.user_stories || epic.stories || [];
                        const storiesArray = Array.isArray(stories) ? stories : [];
                        return storiesArray.length > 0;
                      })() && (
                    <div className="epic-stories">
                      <h6>
                        <i className="fas fa-user" aria-hidden="true"></i>
                        User Stories ({(() => {
                          const stories = epic.user_stories || epic.stories || [];
                          return Array.isArray(stories) ? stories.length : 0;
                        })()})
                      </h6>
                      <ul className="story-list">
                            {(() => {
                              const stories = epic.user_stories || epic.stories || [];
                              const storiesArray = Array.isArray(stories) ? stories : [];
                              return storiesArray.slice(0, 3).map((story, idx) => (
                                <li key={idx}>
                                  <i className="fas fa-caret-right" aria-hidden="true"></i>
                                  {typeof story === 'string' ? story : (
                                    story.title ? `${story.id ? `${story.id}: ` : ''}${story.title}` :
                                    story.id ? `Story ${story.id}` :
                                    story.as_a ? `Como ${story.as_a}, quiero ${story.i_want_to}` :
                                    story.name || `Story ${idx + 1}`
                                  )}
                                </li>
                              ));
                            })()}
                            {(() => {
                              const stories = epic.user_stories || epic.stories || [];
                              const storiesArray = Array.isArray(stories) ? stories : [];
                              return storiesArray.length > 3 && (
                                <li className="more-stories">+{storiesArray.length - 3} más...</li>
                              );
                            })()}
                      </ul>
                    </div>
                  )}

                  {(() => {
                    const criteria = epic.acceptance_criteria;
                    const criteriaArray = Array.isArray(criteria) ? criteria : [];
                    return criteriaArray.length > 0;
                  })() && (
                    <div className="epic-criteria">
                      <h6>
                        <i className="fas fa-check-double" aria-hidden="true"></i>
                        Criterios de Aceptación
                      </h6>
                      <ul className="criteria-list">
                        {(() => {
                          const criteria = epic.acceptance_criteria || [];
                          const criteriaArray = Array.isArray(criteria) ? criteria : [];
                          return criteriaArray.slice(0, 2).map((criteria, idx) => (
                            <li key={idx}>
                              <i className="fas fa-check" aria-hidden="true"></i>
                              {typeof criteria === 'string' ? criteria : (
                                criteria.scenario ? criteria.scenario :
                                criteria.given ? `Given: ${criteria.given} When: ${criteria.when || ''} Then: ${criteria.then || ''}` :
                                criteria.description || criteria.text || 'Criterio de aceptación'
                              )}
                            </li>
                          ));
                        })()}
                        {(() => {
                          const criteria = epic.acceptance_criteria || [];
                          const criteriaArray = Array.isArray(criteria) ? criteria : [];
                          return criteriaArray.length > 2 && (
                            <li className="more-criteria">+{criteriaArray.length - 2} más...</li>
                          );
                        })()}
                      </ul>
                    </div>
                  )}

                  {epic.business_value && (
                    <div className="epic-business-value">
                      <i className="fas fa-chart-line"></i> Valor de Negocio: {epic.business_value}
                    </div>
                  )}

                  <div className="epic-meta">
                    <span className="epic-effort">
                      <i className="fas fa-clock"></i> {epic.estimated_effort || 'TBD'}
                    </span>
                    <span className="epic-sprint">
                      <i className="fas fa-calendar"></i> Sprint {epic.target_sprint || 'TBD'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Epic Dependencies Diagram */}
      {data.epics && data.epics.length > 0 && (
        <EpicDependencies epics={data.epics} />
      )}

      {/* Additional Product Owner Sections */}
      {data.customer_journeys && data.customer_journeys.length > 0 && (
        <div className="product-section-card">
          <h3>
            <i className="fas fa-route" aria-hidden="true"></i>
            Customer Journeys
          </h3>
          <div className="journey-grid">
            {data.customer_journeys.map((journey, idx) => (
              <div key={idx} className="journey-card">
                <h4><i className="fas fa-route"></i> {journey.name}</h4>
                <p>{journey.description}</p>
                {journey.steps && (
                  <div className="journey-steps">
                    <h5>Pasos del Journey:</h5>
                    <ol className="steps-list">
                      {(Array.isArray(journey.steps) ? journey.steps : []).map((step, sIdx) => (
                        <li key={sIdx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {data.product_backlog_items && (
        <div className="product-section-card">
          <h3><i className="fas fa-tasks"></i> Product Backlog Items</h3>
          <div className="backlog-grid">
            {data.product_backlog_items.map((item, idx) => (
              <div key={idx} className="backlog-item">
                <i className="fas fa-cube"></i> {item}
              </div>
            ))}
          </div>
        </div>
      )}

      {data.release_plan && (
        <div className="product-section-card">
          <h3><i className="fas fa-rocket"></i> Plan de Releases</h3>
          <p>{data.release_plan}</p>
        </div>
      )}

      {data.key_acceptance_criteria && data.key_acceptance_criteria.length > 0 && (
        <div className="product-section-card">
          <h3><i className="fas fa-check-double"></i> Criterios de Aceptación Clave</h3>
          <ul className="criteria-grid">
            {data.key_acceptance_criteria.map((criteria, idx) => (
              <li key={idx}><i className="fas fa-check"></i> {criteria}</li>
            ))}
          </ul>
        </div>
      )}

      {data.user_stories && data.user_stories.length > 0 && (
        <div className="product-section-card">
          <h3><i className="fas fa-user"></i> User Stories</h3>
          <div className="stories-cards">
            {data.user_stories.map((us, idx) => (
              <div key={us.id || idx} className="story-card">
                <div className="story-header">
                  <span className="story-id">{us.id || `US-${idx+1}`}</span>
                  <span className="story-title">{us.title}</span>
                  {us.wsjf && (
                    <span className="badge badge-wsjf" title={`BV:${us.wsjf.business_value} TC:${us.wsjf.time_criticality} RR/OE:${us.wsjf.risk_reduction_opportunity} JS:${us.wsjf.job_size}`}>
                      WSJF: {us.wsjf.score}
                    </span>
                  )}
                  {us.needs_split && (
                    <span className="badge badge-warning" title="Story > 8 SP, requiere split">Needs Split</span>
                  )}
                </div>
                <div className="story-desc">
                  Como <strong>{us.as_a}</strong>, quiero <strong>{us.i_want_to || us.i_want}</strong>, para que <strong>{us.so_that}</strong>.
                </div>

                {Array.isArray(us.acceptance_criteria) && us.acceptance_criteria.length > 0 && (
                  <div className="story-section">
                    <h4><i className="fas fa-check-double"></i> Criterios de Aceptación</h4>
                    <ul className="mini-list">
                      {us.acceptance_criteria.map((ac, i) => (
                        typeof ac === 'string' ? (
                          <li key={i}>✓ {ac}</li>
                        ) : (
                          <li key={i}>
                            ✓ <strong>{ac.scenario || `Escenario ${i+1}`}</strong> — Given {ac.given}; When {ac.when}; Then {ac.then}
                          </li>
                        )
                      ))}
                    </ul>
                  </div>
                )}

                {Array.isArray(us.business_rules) && us.business_rules.length > 0 && (
                  <div className="story-section">
                    <h4><i className="fas fa-balance-scale"></i> Reglas de Negocio</h4>
                    <List items={us.business_rules} />
                  </div>
                )}

                {Array.isArray(us.edge_cases) && us.edge_cases.length > 0 && (
                  <div className="story-section">
                    <h4><i className="fas fa-exclamation-triangle"></i> Edge Cases</h4>
                    <List items={us.edge_cases} />
                  </div>
                )}

                <div className="story-footer">
                  <span><i className="fas fa-weight-hanging"></i> SP: {us.story_points ?? 'TBD'}</span>
                  <span><i className="fas fa-flag"></i> Prioridad: {us.priority || 'Backlog'}</span>
                  {Array.isArray(us.dependencies) && us.dependencies.length > 0 && (
                    <span><i className="fas fa-link"></i> Deps: {us.dependencies.join(', ')}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

function ProductOwnerView({ data }) {
  return <ProductOwnerBoard data={data} />;
}

// UX/UI Designer Board Component
const UXUIBoard = ({ data }) => {
  const personasByType = {
    "Primary": [],
    "Secondary": [],
    "Edge Cases": [],
  };

  // Organize personas by type
  data.user_personas?.forEach(persona => {
    const type = persona.type || 'Primary';
    personasByType[type]?.push(persona);
  });

  return (
    <div className="ux-ui-board">
      <div className="board-header">
        <h3><i className="fas fa-paint-brush"></i> Design System & User Experience</h3>
        <div className="board-metadata">
          <span><i className="fas fa-palette"></i> {typeof data.design_system === 'string' ? data.design_system : 'Custom Design System'}</span>
          <span><i className="fas fa-calendar-alt"></i> {data.document_metadata?.date || 'N/A'}</span>
          <span><i className="fas fa-user-circle"></i> UX/UI Designer</span>
        </div>
      </div>

      {/* Personas Section con nuevas visualizaciones */}
      {data.user_personas && data.user_personas.length > 0 && (
        <div className="personas-section">
          <h4><i className="fas fa-users"></i> Personas de Usuario</h4>
          <div className="personas-grid-enhanced">
            {data.user_personas.map((persona, idx) => (
              <PersonaCard key={idx} persona={persona} index={idx} />
            ))}
          </div>
          <div className="personas-actions">
            <button className="btn btn-sm btn-secondary"><i className="fas fa-expand"></i> Expandir detalles</button>
            <button className="btn btn-sm btn-secondary"><i className="fas fa-download"></i> Exportar</button>
            <button className="btn btn-sm btn-secondary"><i className="fab fa-figma"></i> Editar en Figma</button>
          </div>
        </div>
      )}

      {/* Journey Map */}
      {(data.user_journey_map || data.user_journey) && (
        <JourneyMap journeyMap={data.user_journey_map || data.user_journey} />
      )}

      {/* Wireframes Gallery */}
      {(data.wireframes || data.wireframe_references) && (
        <WireframesGallery wireframes={data.wireframes || data.wireframe_references} />
      )}

      {/* Design System Guide */}
      {data.design_system && (
        <DesignSystemGuide designSystem={data.design_system} />
      )}

      {/* Personas Legacy Section (mantener para compatibilidad) */}
      {data.user_personas && data.user_personas.length > 0 && Object.keys(personasByType).some(type => personasByType[type].length > 0) && (
        <div className="personas-section-legacy">
          <div className="personas-grid">
            {Object.entries(personasByType).map(([type, personas]) => (
              personas.length > 0 && (
                <div key={type} className="persona-column">
                  <h5>{type} Personas ({personas.length})</h5>
                  {personas.map((persona, idx) => (
                    <div key={idx} className="persona-card">
                      <div className="persona-header">
                        <h6>{persona.name}</h6>
                        <span className="persona-age">{persona.age}</span>
                      </div>
                      <p className="persona-role">{persona.occupation}</p>
                      
                      {persona.needs && (
                        <div className="persona-section">
                          <h7><i className="fas fa-heart"></i> Necesidades</h7>
                          <ul>
                            {persona.needs.slice(0, 3).map((need, nIdx) => (
                              <li key={nIdx}>{need}</li>
                            ))}
                            {persona.needs.length > 3 && (
                              <li className="more-items">+{persona.needs.length - 3} más...</li>
                            )}
                          </ul>
                        </div>
                      )}

                      {persona.goals && (
                        <div className="persona-section">
                          <h7><i className="fas fa-target"></i> Objetivos</h7>
                          <ul>
                            {persona.goals.slice(0, 2).map((goal, gIdx) => (
                              <li key={gIdx}>{goal}</li>
                            ))}
                            {persona.goals.length > 2 && (
                              <li className="more-items">+{persona.goals.length - 2} más...</li>
                            )}
                          </ul>
                        </div>
                      )}

                      {persona.frustrations && (
                        <div className="persona-section">
                          <h7><i className="fas fa-exclamation-triangle"></i> Frustraciones</h7>
                          <ul>
                            {persona.frustrations.slice(0, 2).map((frustration, fIdx) => (
                              <li key={fIdx}>{frustration}</li>
                            ))}
                            {persona.frustrations.length > 2 && (
                              <li className="more-items">+{persona.frustrations.length - 2} más...</li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* User Flows Section */}
      {data.user_flows && data.user_flows.length > 0 && (
        <div className="flows-section">
          <h4><i className="fas fa-route"></i> User Flows</h4>
          <div className="flows-grid">
            {data.user_flows.map((flow, idx) => (
              <div key={idx} className="flow-card">
                <h5><i className="fas fa-arrow-right"></i> {flow}</h5>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Journey Map Section */}
      {data.user_journey_map && (
        <div className="journey-map-section">
          <h4><i className="fas fa-map-signs"></i> User Journey Map</h4>
          <div className="journey-map-grid">
            {Array.isArray(data.user_journey_map.stages) && data.user_journey_map.stages.length > 0 && (
              <div className="journey-block">
                <h5>Stages</h5>
                <List items={data.user_journey_map.stages} />
              </div>
            )}
            {Array.isArray(data.user_journey_map.touchpoints) && data.user_journey_map.touchpoints.length > 0 && (
              <div className="journey-block">
                <h5>Touchpoints</h5>
                <List items={data.user_journey_map.touchpoints} />
              </div>
            )}
            {Array.isArray(data.user_journey_map.emotions) && data.user_journey_map.emotions.length > 0 && (
              <div className="journey-block">
                <h5>Emotions</h5>
                <List items={data.user_journey_map.emotions} />
              </div>
            )}
            {Array.isArray(data.user_journey_map.opportunities) && data.user_journey_map.opportunities.length > 0 && (
              <div className="journey-block">
                <h5>Opportunities (To-Be)</h5>
                <List items={data.user_journey_map.opportunities} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Key Screens Section */}
      {data.key_screens && data.key_screens.length > 0 && (
        <div className="screens-section">
          <h4><i className="fas fa-mobile-alt"></i> Pantallas Clave</h4>
          <div className="screens-grid">
            {data.key_screens.map((screen, idx) => (
              <div key={idx} className="screen-card">
                <h5><i className="fas fa-desktop"></i> {screen.name}</h5>
                <p><strong>Propósito:</strong> {screen.purpose}</p>
                {screen.components && (
                  <div className="screen-components">
                    <h6>Componentes:</h6>
                    <div className="components-tags">
                      {(Array.isArray(screen.components) ? screen.components : []).map((comp, cIdx) => (
                        <span key={cIdx} className="component-tag">{comp}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* UI Components Section */}
      {data.ui_components && data.ui_components.length > 0 && (
        <div className="components-section">
          <h4><i className="fas fa-puzzle-piece"></i> Componentes UI</h4>
          <div className="components-grid">
            {data.ui_components.map((component, idx) => (
              <div key={idx} className="component-card">
                <i className="fas fa-cube"></i> {component}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Wireframes Section */}
      {Array.isArray(data.wireframes) && data.wireframes.length > 0 && (
        <div className="wireframes-section">
          <h4><i className="fas fa-draw-polygon"></i> Wireframes</h4>
          <div className="wireframes-grid">
            {data.wireframes.map((wf, idx) => (
              <div key={idx} className="wireframe-card">
                <h5><i className="fas fa-desktop"></i> {wf.screen || `Screen ${idx+1}`}</h5>
                {wf.url && (
                  <p><a href={wf.url} target="_blank" rel="noreferrer"><i className="fas fa-external-link-alt"></i> Ver en Figma</a></p>
                )}
                {wf.notes && (<p className="muted">{wf.notes}</p>)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Design System, Accessibility & Usability */}
      <div className="design-info-grid">
        {data.design_system && (
          <div className="info-card">
            <h4><i className="fas fa-palette"></i> Design System</h4>
            <p>
              {typeof data.design_system === 'string' ? data.design_system : (
                data.design_system && typeof data.design_system === 'object' ? (
                  data.design_system.name || 
                  (data.design_system.colors ? 'Design System con paleta de colores' : 'Custom Design System')
                ) : 'Custom Design System'
              )}
            </p>
          </div>
        )}
        
        {(data.accessibility_standards || data.accessibility_requirements) && (
          <div className="info-card">
            <h4><i className="fas fa-universal-access"></i> Accesibilidad</h4>
            {Array.isArray(data.accessibility_requirements)
              ? <List items={data.accessibility_requirements} />
              : <p>{data.accessibility_standards || 'WCAG 2.1 AA'}</p>}
          </div>
        )}

        {data.usability_tests && (
          <div className="info-card">
            <h4><i className="fas fa-user-check"></i> Usability Tests</h4>
            <p><strong>Participantes:</strong> {data.usability_tests.participants ?? 'N/A'}</p>
            <p><strong>Success rate:</strong> {data.usability_tests.success_rate ?? 'N/A'}</p>
            {data.usability_tests.notes && <p className="muted">{data.usability_tests.notes}</p>}
          </div>
        )}

        {data.usability_principles && (
          <div className="info-card">
            <h4><i className="fas fa-check-circle"></i> Principios de Usabilidad</h4>
            <ul>
              {data.usability_principles.map((principle, idx) => (
                <li key={idx}>{principle}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

function UXUIView({ data }) {
  return <UXUIBoard data={data} />;
}

// Coordinator View (Backlog Readiness Panel)
function CoordinatorView({ data }) {
  const brief = data.strategic_brief || {};
  const readiness = data.backlog_readiness || {};
  const sprintPlanning = data.sprint_planning_acta || {};
  return (
    <div className="coordinator-synthesis">
      <Section title="🧠 Strategic Brief" className="sec-blue">
        <p><strong>PM:</strong> {brief.pm_summary || 'N/A'}</p>
        <p><strong>SM:</strong> {brief.sm_summary || 'N/A'}</p>
        <p><strong>GO/NO-GO:</strong> {brief.go_no_go || 'pending'}</p>
        {brief.notes && <p className="muted">{brief.notes}</p>}
      </Section>
      <Section title="📋 Backlog Readiness" className="sec-green">
        <h5>Ready Stories</h5>
        <List items={Array.isArray(readiness.ready_stories) ? readiness.ready_stories : []} />
        <h5 className="mt-2">Technical Questions</h5>
        <List items={Array.isArray(readiness.technical_questions) ? readiness.technical_questions : []} />
      </Section>
      {sprintPlanning && Object.keys(sprintPlanning).length > 0 && (
        <Section title="🔄 Checkpoint 4: Sprint Planning Meeting (Official)" className="sec-amber">
          <div className="sprint-planning-acta">
            <div className="acta-status">
              <div className="status-item">
                <span className={`status-badge ${sprintPlanning.committed ? 'status-success' : 'status-pending'}`}>
                  <i className={`fas ${sprintPlanning.committed ? 'fa-check-circle' : 'fa-clock'}`}></i>
                  {sprintPlanning.committed ? 'Committed' : 'Not Committed'}
                </span>
              </div>
              <div className="status-item">
                <span className={`status-badge ${sprintPlanning.clarity_100 ? 'status-success' : 'status-pending'}`}>
                  <i className={`fas ${sprintPlanning.clarity_100 ? 'fa-check-circle' : 'fa-exclamation-circle'}`}></i>
                  {sprintPlanning.clarity_100 ? '100% Clarity' : 'Clarity Issues'}
                </span>
              </div>
              <div className="status-item">
                <span className={`status-badge ${sprintPlanning.jira_updated ? 'status-success' : 'status-pending'}`}>
                  <i className={`fas ${sprintPlanning.jira_updated ? 'fa-check-circle' : 'fa-times-circle'}`}></i>
                  {sprintPlanning.jira_updated ? 'Jira Updated' : 'Jira Pending'}
                </span>
              </div>
            </div>
            {sprintPlanning.sprint_goal && (
              <div className="acta-section">
                <h5><i className="fas fa-bullseye"></i> Sprint Goal</h5>
                <p>{sprintPlanning.sprint_goal}</p>
              </div>
            )}
            {sprintPlanning.team_questions && sprintPlanning.team_questions.length > 0 && (
              <div className="acta-section">
                <h5><i className="fas fa-question-circle"></i> Team Questions</h5>
                <List items={sprintPlanning.team_questions} />
              </div>
            )}
            {sprintPlanning.blockers && sprintPlanning.blockers.length > 0 && (
              <div className="acta-section">
                <h5><i className="fas fa-ban"></i> Blockers</h5>
                <List items={sprintPlanning.blockers} />
              </div>
            )}
            {sprintPlanning.notes && (
              <div className="acta-section">
                <h5><i className="fas fa-sticky-note"></i> Notes</h5>
                <p className="muted">{sprintPlanning.notes}</p>
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  );
}

// Technical Lead Board Component
const TechnicalLeadBoard = ({ data }) => {
  const componentsByLayer = {
    "Frontend": [],
    "Backend": [],
    "Database": [],
    "Infrastructure": [],
    "External": [],
  };

  // Organize components by layer
  data.key_components?.forEach(component => {
    const layer = component.layer || component.technology?.includes('React') ? 'Frontend' : 
                 component.technology?.includes('Node') ? 'Backend' : 
                 component.technology?.includes('PostgreSQL') ? 'Database' : 'Backend';
    componentsByLayer[layer]?.push(component);
  });

  return (
    <div className="technical-board">
      <div className="board-header">
        <h3><i className="fas fa-laptop-code"></i> Technical Architecture & Implementation</h3>
        <div className="board-metadata">
          <span><i className="fas fa-cogs"></i> {data.architecture_overview?.substring(0, 50) || 'Cloud-Native Architecture'}</span>
          <span><i className="fas fa-calendar-alt"></i> {data.document_metadata?.date || 'N/A'}</span>
          <span><i className="fas fa-user-tie"></i> Technical Lead</span>
        </div>
      </div>

      {/* Architecture Overview */}
      {/* Architecture Diagram */}
      {(data.architecture || data.architecture_overview) && (
        <ArchitectureDiagram architecture={data.architecture || { pattern: data.architecture_overview }} />
      )}

      {/* Legacy Architecture Section */}
      {data.architecture_overview && !data.architecture && (
        <div className="architecture-section">
          <h4><i className="fas fa-sitemap"></i> Architecture Overview</h4>
          <div className="architecture-card">
            <p>{data.architecture_overview}</p>
            {data.data_flow && (
              <div className="data-flow">
                <h5><i className="fas fa-arrows-alt"></i> Data Flow</h5>
                <p>{data.data_flow}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* System Components by Layer */}
      {data.key_components && data.key_components.length > 0 && (
        <div className="components-section">
          <h4><i className="fas fa-cubes"></i> System Components</h4>
          <div className="components-layers">
            {Object.entries(componentsByLayer).map(([layer, components]) => (
              components.length > 0 && (
                <div key={layer} className="layer-column">
                  <h5><i className="fas fa-layer-group"></i> {layer} ({components.length})</h5>
                  {components.map((component, idx) => (
                    <div key={idx} className="component-card">
                      <div className="component-header">
                        <h6>{component.name}</h6>
                        <span className="component-tech">{component.technology}</span>
                      </div>
                      <p className="component-desc">{component.description}</p>
                      {component.responsibilities && (
                        <div className="component-responsibilities">
                          <h7>Responsabilidades:</h7>
                          <ul>
                            {(Array.isArray(component.responsibilities) ? component.responsibilities : []).slice(0, 3).map((resp, rIdx) => (
                              <li key={rIdx}>{resp}</li>
                            ))}
                            {(Array.isArray(component.responsibilities) ? component.responsibilities : []).length > 3 && (
                              <li className="more-items">+{(Array.isArray(component.responsibilities) ? component.responsibilities : []).length - 3} más...</li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Tech Stack */}
      {/* Tech Stack Visual */}
      {data.tech_stack && (
        <TechStackVisual techStack={data.tech_stack} />
      )}

      {/* Legacy Tech Stack Section */}
      {data.tech_stack && (
        <div className="tech-stack-section">
          <h4><i className="fas fa-tools"></i> Technology Stack</h4>
          <div className="tech-grid">
            {Object.entries(data.tech_stack).map(([category, technologies]) => {
              const techValue = safeExtractString(technologies);
              const techDisplay = techValue || (typeof technologies === 'string' ? technologies : category);
              
              return (
                <div key={category} className="tech-category">
                  <h5>{category}</h5>
                  <div className="tech-items">
                    {Array.isArray(technologies) ? (
                      technologies.map((tech, idx) => {
                        const techStr = safeExtractString(tech) || (typeof tech === 'string' ? tech : String(tech));
                        return <span key={idx} className="tech-item">{techStr}</span>;
                      })
                    ) : (
                      <span className="tech-item">{techDisplay}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Integrations */}
      {data.integrations && data.integrations.length > 0 && (
        <div className="integrations-section">
          <h4><i className="fas fa-plug"></i> Integrations</h4>
          <div className="integrations-grid">
            {data.integrations.map((integration, idx) => (
              <div key={idx} className="integration-card">
                <h5><i className="fas fa-link"></i> {integration.name}</h5>
                <p><strong>Tipo:</strong> {integration.type}</p>
                {integration.purpose && <p><strong>Propósito:</strong> {integration.purpose}</p>}
                {integration.requirements && (
                  <div className="integration-requirements">
                    <h6>Requisitos:</h6>
                    <ul>
                      {(Array.isArray(integration.requirements) ? integration.requirements : []).slice(0, 2).map((req, rIdx) => (
                        <li key={rIdx}>{req}</li>
                      ))}
                      {(Array.isArray(integration.requirements) ? integration.requirements : []).length > 2 && (
                        <li className="more-items">+{(Array.isArray(integration.requirements) ? integration.requirements : []).length - 2} más...</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Non-Functional Requirements */}
      {/* NFR Checklist */}
      {data.non_functional_requirements && (
        <NFRChecklist nfrs={data.non_functional_requirements} />
      )}

      {/* Legacy NFR Section */}
      {data.non_functional_requirements && (
        <div className="nfr-section">
          <h4><i className="fas fa-cog"></i> Non-Functional Requirements</h4>
          <div className="nfr-grid">
            {Object.entries(data.non_functional_requirements).map(([category, requirement]) => (
              <div key={category} className="nfr-card">
                <h5><i className="fas fa-check-circle"></i> {category}</h5>
                <p>{requirement}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Model */}
      {data.data_model && (
        <div className="data-model-section">
          <h4><i className="fas fa-database"></i> Data Model</h4>
          <div className="data-model-card">
            <p>{data.data_model}</p>
          </div>
        </div>
      )}
    </div>
  );
};

function TechnicalLeadView({ data }) {
  return <TechnicalLeadBoard data={data} />;
}

// Scrum Master Board Component
function ScrumMasterView({ data }) {
  const ceremonies = data.key_ceremonies || data.ceremonies || [];
  const risks = data.risks_and_impediments || data.risks || data.risk_assessment || [];
  const impediments = data.impediments || [];
  const dependencies = data.dependencies_and_blockers || data.dependencies || [];
  const velocity = data.average_velocity || data.velocity || null;
  const capacity = data.team_capacity || null;

  return (
    <div className="scrum-board">
      <div className="board-header">
        <h3><i className="fas fa-users-cog"></i> Procesos Ágiles</h3>
        <div className="board-metadata">
          <span><i className="fas fa-stopwatch"></i> Sprint: {data.sprint_number || 'N/A'}</span>
          <span><i className="fas fa-clock"></i> Duración: {data.sprint_duration || data.sprint_structure?.duration || '2 semanas'}</span>
          {velocity && <span><i className="fas fa-tachometer-alt"></i> Velocidad: {velocity}</span>}
          {capacity && <span><i className="fas fa-users"></i> Capacidad: {capacity}</span>}
        </div>
      </div>

      {/* Sprint Roadmap Visual */}
      {(data.sprint_backlog || data.sprint_structure) && (
        <SprintRoadmap sprintBacklog={data.sprint_backlog} sprintStructure={data.sprint_structure} />
      )}

      {/* Risk Matrix Visual */}
      {risks.length > 0 && (
        <RiskMatrix risks={risks} />
      )}

      {/* Ceremonies Calendar */}
      {(ceremonies.length > 0 || data.sprint_structure) && (
        <CeremoniesCalendar ceremonies={ceremonies} sprintStructure={data.sprint_structure} />
      )}

      {/* Legacy Sections */}
      <div className="scrum-grid">
        <div className="scrum-card">
          <h4><i className="fas fa-calendar-check"></i> Ceremonias</h4>
          <List items={ceremonies} />
        </div>
        <div className="scrum-card">
          <h4><i className="fas fa-exclamation-triangle"></i> Riesgos e Impedimentos</h4>
          <List items={risks} />
          {impediments.length > 0 && (
            <>
              <h5 className="sub">Impedimentos Activos</h5>
              <List items={impediments} />
            </>
          )}
        </div>
        <div className="scrum-card">
          <h4><i className="fas fa-link"></i> Dependencias y Bloqueos</h4>
          <List items={dependencies} />
        </div>
        <div className="scrum-card">
          <h4><i className="fas fa-sync"></i> Mejora de Procesos</h4>
          <p>{data.process_improvements || 'N/A'}</p>
        </div>
      </div>

      {data.sprint_plan && (
        <div className="scrum-section">
          <h4><i className="fas fa-map"></i> Plan de Sprint</h4>
          <p>{data.sprint_plan}</p>
        </div>
      )}
    </div>
  );
}

// QA Specialist Board Component
function QAView({ data }) {
  // Extraer strategy de forma segura
  const strategyRaw = data.testing_strategy_overview || data.test_strategy || null;
  const strategy = typeof strategyRaw === 'string' ? strategyRaw : 
                   (typeof strategyRaw === 'object' && strategyRaw !== null ? 
                     (strategyRaw.overview || strategyRaw.description || safeExtractString(strategyRaw) || JSON.stringify(strategyRaw)) : 
                     null);
  
  const testPhases = data.test_phases || [];
  const planApproach = data.test_plan_approach || data.test_plan || null;
  const keyCases = data.key_test_cases || data.test_cases || [];
  const automationTools = data.automation_tools || data.automation || [];
  const automationCoverage = data.automation_coverage_target || null;
  const qualityMetrics = data.quality_metrics || [];
  const nonFunctional = data.non_functional_requirements || data.non_functional_tests || [];

  return (
    <div className="qa-board">
      <div className="board-header">
        <h3><i className="fas fa-check-circle"></i> Quality Assurance Strategy</h3>
        <div className="board-metadata">
          {automationCoverage && <span><i className="fas fa-robot"></i> Auto: {safeExtractString(automationCoverage) || String(automationCoverage)}</span>}
          {Array.isArray(qualityMetrics) && qualityMetrics.length > 0 && <span><i className="fas fa-chart-bar"></i> KPIs: {qualityMetrics.length}</span>}
        </div>
      </div>

      <div className="qa-grid">
        <div className="qa-card">
          <h4><i className="fas fa-vial"></i> Estrategia de Pruebas</h4>
          <p>{strategy || 'N/A'}</p>
          {testPhases.length > 0 && (
            <>
              <h5 className="sub">Fases</h5>
              <List items={testPhases} />
            </>
          )}
        </div>
        <div className="qa-card">
          <h4><i className="fas fa-clipboard-list"></i> Plan y Casos Clave</h4>
          <p>{planApproach || 'N/A'}</p>
          {keyCases.length > 0 && (
            <>
              <h5 className="sub">Casos Clave</h5>
              <List items={keyCases} />
            </>
          )}
        </div>
        <div className="qa-card">
          <h4><i className="fas fa-cogs"></i> Automatización</h4>
          <List items={automationTools} />
          {automationCoverage && <p className="muted">Cobertura objetivo: {safeExtractString(automationCoverage) || String(automationCoverage)}</p>}
        </div>
        <div className="qa-card">
          <h4><i className="fas fa-tachometer-alt"></i> Métricas de Calidad</h4>
          <List items={qualityMetrics} />
        </div>
      </div>

      {Array.isArray(nonFunctional) && nonFunctional.length > 0 && (
        <div className="qa-section">
          <h4><i className="fas fa-sliders-h"></i> Pruebas No Funcionales</h4>
          {Array.isArray(nonFunctional)
            ? <List items={nonFunctional} />
            : <p>{String(nonFunctional)}</p>}
        </div>
      )}
    </div>
  );
}

// Helper function para extraer valores string de objetos complejos
function safeExtractString(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map(v => safeExtractString(v)).filter(v => v !== null).join(', ') || null;
  if (typeof value === 'object') {
    // Si es un objeto, buscar propiedades comunes que contengan el valor
    return value.framework || value.tech || value.name || value.primary || value.provider || 
           value.title || value.label || value.value || 
           (typeof value.rationale === 'string' ? null : String(value)) || // rationale no es el valor principal
           null;
  }
  return null;
}

function SupervisorBoard({ data }) {
  if (!data || typeof data !== 'object') return null;
  
  // Validar y sanitizar datos antes de renderizar
  const safeGet = (obj, path, defaultValue = null) => {
    if (!obj) return defaultValue;
    const keys = path.split('.');
    let current = obj;
    for (const key of keys) {
      if (current == null || typeof current !== 'object') return defaultValue;
      current = current[key];
      if (current === undefined) return defaultValue;
    }
    return current;
  };

  const projectInfo = data.project_info || {};
  const funcReqs = data.functional_requirements || {};
  const userStories = Array.isArray(funcReqs.user_stories) ? funcReqs.user_stories : [];
  
  // Organizar user stories por prioridad
  const storiesByPriority = {
    'MUST HAVE': userStories.filter(us => (us.priority || '').toUpperCase().includes('MUST')),
    'SHOULD HAVE': userStories.filter(us => (us.priority || '').toUpperCase().includes('SHOULD')),
    'COULD HAVE': userStories.filter(us => (us.priority || '').toUpperCase().includes('COULD')),
    'BACKLOG': userStories.filter(us => !us.priority || !['MUST', 'SHOULD', 'COULD'].some(p => (us.priority || '').toUpperCase().includes(p)))
  };

  const columns = [
    { key: 'MUST HAVE', title: 'Must Have', icon: '🔴' },
    { key: 'SHOULD HAVE', title: 'Should Have', icon: '🟡' },
    { key: 'COULD HAVE', title: 'Could Have', icon: '🟢' },
    { key: 'BACKLOG', title: 'Backlog', icon: '⚪' },
  ];

  const execSummary = data.executive_summary || {};
  const techReqs = data.technical_requirements || {};
  const nfrs = techReqs.nfrs || {};
  const quality = data.quality_assurance || {};
  const risks = data.risk_management || {};
  const roleSignoffs = data.role_signoffs || {};

  // Mapear acceptance criteria por story ID
  const acceptanceCriteriaMap = funcReqs.acceptance_criteria || {};
  const getCriteria = (storyId) => {
    const criteria = acceptanceCriteriaMap[storyId];
    if (Array.isArray(criteria)) return criteria;
    if (typeof criteria === 'string') return [criteria];
    return [];
  };

  return (
    <div className="supervisor-board">
      {/* Header del Proyecto */}
      <div className="supervisor-header">
        <div className="project-info">
          <h2>{projectInfo.name || 'Requerimientos Técnicos Finales'}</h2>
          <div className="project-meta">
            <span className="badge badge-info">ID: {projectInfo.id || 'N/A'}</span>
            <span className="badge badge-info">v{projectInfo.version || '1.0'}</span>
            <span className="badge badge-info">{projectInfo.date || ''}</span>
            <span className={`badge ${projectInfo.status === 'approved' ? 'badge-success' : 'badge-warning'}`}>
              {projectInfo.status === 'approved' ? '✅ Aprobado' : '⚠️ Requiere Refinamiento'}
            </span>
          </div>
        </div>
        
        {execSummary.value_proposition && (
          <div className="value-prop">
            <h4>💎 Propuesta de Valor</h4>
            <p>{execSummary.value_proposition}</p>
          </div>
        )}
      </div>

      {/* Tablero Kanban */}
      <div className="kanban-board">
        <h3 className="kanban-title">📋 Backlog de Desarrollo - User Stories por Prioridad</h3>
        <div className="kanban-columns">
          {columns.map(col => {
            const stories = storiesByPriority[col.key] || [];
            return (
              <div key={col.key} className="kanban-column">
                <div className="kanban-column-header">
                  <span className="column-icon">{col.icon}</span>
                  <span className="column-title">{col.title}</span>
                  <span className="column-count">{stories.length}</span>
                </div>
                <div className="kanban-column-body">
                  {stories.length === 0 ? (
                    <div className="empty-column">No hay stories en esta columna</div>
                  ) : (
                    stories.map((story, idx) => {
                      const criteria = getCriteria(story.id);
                      return (
                        <div key={story.id || idx} className="kanban-card">
                          <div className="card-header">
                            <span className="card-id">{story.id || `US-${idx + 1}`}</span>
                            {story.story_points && (
                              <span className="card-points">{story.story_points} SP</span>
                            )}
                          </div>
                          <h5 className="card-title">{story.title || story.name || 'Sin título'}</h5>
                          {story.description && (
                            <p className="card-description">{story.description}</p>
                          )}
                          {story.as_a && (
                            <div className="card-user-story">
                              <strong>Como:</strong> {story.as_a}<br/>
                              <strong>Quiero:</strong> {story.i_want_to || story.i_want}<br/>
                              <strong>Para:</strong> {story.so_that || story.so_that_value}
                            </div>
                          )}
                          {criteria.length > 0 && (
                            <div className="card-criteria">
                              <strong>✓ Criterios de Aceptación:</strong>
                              <ul className="mini-list">
                                {criteria.map((c, i) => (
                                  <li key={i}>
                                    {typeof c === 'string' ? c : (
                                      c.scenario || 
                                      (c.given ? `Given: ${c.given} When: ${c.when || ''} Then: ${c.then || ''}` : '') ||
                                      c.description || 
                                      c.text ||
                                      `${Object.keys(c).slice(0, 2).join(', ')}...`
                                    )}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {story.dependencies && Array.isArray(story.dependencies) && story.dependencies.length > 0 && (
                            <div className="card-dependencies">
                              <strong>🔗 Dependencias:</strong> {story.dependencies.join(', ')}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Executive Summary Completo */}
      {execSummary.business_need && (
        <Section title="📋 Resumen Ejecutivo" className="sec-blue">
          <div className="exec-summary-grid">
            <div>
              <h5>Necesidad de Negocio</h5>
              <p>{execSummary.business_need}</p>
            </div>
            {execSummary.estimated_effort && (
              <div>
                <h5>Esfuerzo Estimado</h5>
                <p>{execSummary.estimated_effort}</p>
              </div>
            )}
            {execSummary.timeline && (
              <div>
                <h5>Timeline</h5>
                <p>{execSummary.timeline}</p>
              </div>
            )}
          </div>
        </Section>
      )}

      {/* Epics */}
      {Array.isArray(funcReqs.epics) && funcReqs.epics.length > 0 && (
        <Section title="📦 Epics" className="sec-indigo">
          <div className="epics-list">
            {funcReqs.epics.map((epic, idx) => (
              <div key={epic.id || idx} className="epic-item">
                <h5>{epic.id || `EP-${idx + 1}`}: {epic.title || epic.name}</h5>
                {epic.business_value && <p className="epic-value">💼 {epic.business_value}</p>}
                {Array.isArray(epic.stories) && epic.stories.length > 0 && (
                  <p className="epic-stories">Stories: {epic.stories.join(', ')}</p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Definition of Done */}
      {Array.isArray(funcReqs.definition_of_done) && funcReqs.definition_of_done.length > 0 && (
        <Section title="✅ Definition of Done" className="sec-green">
          <List items={funcReqs.definition_of_done} />
        </Section>
      )}

      {/* Edge Cases */}
      {Array.isArray(funcReqs.edge_cases) && funcReqs.edge_cases.length > 0 && (
        <Section title="⚠️ Edge Cases" className="sec-orange">
          <List items={funcReqs.edge_cases} />
        </Section>
      )}

      {/* Secciones de Información */}
      <div className="supervisor-sections">
        {execSummary.success_metrics && execSummary.success_metrics.length > 0 && (
          <Section title="📊 Métricas de Éxito" className="sec-amber">
            <List items={execSummary.success_metrics} />
          </Section>
        )}

        {/* Tech Stack Completo */}
        {techReqs.tech_stack && typeof techReqs.tech_stack === 'object' && (
          <Section title="🛠️ Tech Stack" className="sec-purple">
            <div className="tech-stack-grid">
              {techReqs.tech_stack.frontend && (
                <div>
                  <h5>Frontend</h5>
                  <p>{(() => {
                    const frontend = techReqs.tech_stack?.frontend;
                    if (!frontend) return 'N/A';
                    if (typeof frontend === 'string') return frontend;
                    if (Array.isArray(frontend)) return frontend.map(v => safeExtractString(v) || String(v)).join(', ');
                    const extracted = safeExtractString(frontend);
                    return extracted || Object.keys(frontend).join(', ') || 'N/A';
                  })()}</p>
                </div>
              )}
              {techReqs.tech_stack.backend && (
                <div>
                  <h5>Backend</h5>
                  <p>{(() => {
                    const backend = techReqs.tech_stack?.backend;
                    if (!backend) return 'N/A';
                    if (typeof backend === 'string') return backend;
                    if (Array.isArray(backend)) return backend.map(v => safeExtractString(v) || String(v)).join(', ');
                    const extracted = safeExtractString(backend);
                    return extracted || Object.keys(backend).join(', ') || 'N/A';
                  })()}</p>
                </div>
              )}
              {techReqs.tech_stack.database && (
                <div>
                  <h5>Database</h5>
                  <p>{(() => {
                    const database = techReqs.tech_stack?.database;
                    if (!database) return 'N/A';
                    if (typeof database === 'string') return database;
                    if (Array.isArray(database)) return database.map(v => safeExtractString(v) || String(v)).join(', ');
                    const extracted = safeExtractString(database);
                    return extracted || Object.keys(database).join(', ') || 'N/A';
                  })()}</p>
                </div>
              )}
              {techReqs.tech_stack.infrastructure && (
                <div>
                  <h5>Infrastructure</h5>
                  <p>{(() => {
                    const infra = techReqs.tech_stack?.infrastructure;
                    if (!infra) return 'N/A';
                    if (typeof infra === 'string') return infra;
                    if (Array.isArray(infra?.services)) {
                      return infra.services.map(v => safeExtractString(v) || String(v)).join(', ');
                    }
                    if (typeof infra === 'object') {
                      const extracted = safeExtractString(infra);
                      return extracted || Object.keys(infra).join(', ') || 'N/A';
                    }
                    return 'N/A';
                  })()}</p>
                </div>
              )}
            </div>
          </Section>
        )}

        {nfrs.performance && Array.isArray(nfrs.performance) && nfrs.performance.length > 0 && (
          <Section title="⚡ Requisitos de Rendimiento" className="sec-purple">
            <List items={nfrs.performance} />
          </Section>
        )}

        {nfrs.security && Array.isArray(nfrs.security) && nfrs.security.length > 0 && (
          <Section title="🔒 Requisitos de Seguridad" className="sec-red">
            <List items={nfrs.security} />
          </Section>
        )}

        {nfrs.scalability && (
          <Section title="📈 Escalabilidad" className="sec-blue">
            <List items={Array.isArray(nfrs.scalability) ? nfrs.scalability : [nfrs.scalability]} />
          </Section>
        )}

        {nfrs.maintainability && (
          <Section title="🔧 Mantenibilidad" className="sec-teal">
            <List items={Array.isArray(nfrs.maintainability) ? nfrs.maintainability : [nfrs.maintainability]} />
          </Section>
        )}

        {techReqs.architecture && (
          <Section title="🏗️ Arquitectura Técnica" className="sec-indigo">
            <div className="arch-info">
              {typeof techReqs.architecture === 'object' && (
                <>
                  {techReqs.architecture.pattern && (
                    <p><strong>Patrón:</strong> {techReqs.architecture.pattern}</p>
                  )}
                  {techReqs.architecture.frontend && (
                    <p><strong>Frontend:</strong> {(() => {
                      const frontend = techReqs.architecture.frontend;
                      if (typeof frontend === 'string') return frontend;
                      return safeExtractString(frontend?.framework) ||
                             safeExtractString(frontend?.tech) ||
                             safeExtractString(frontend?.name) ||
                             safeExtractString(frontend) ||
                             (typeof frontend === 'object' ? Object.keys(frontend || {}).join(', ') : 'N/A');
                    })()}</p>
                  )}
                  {techReqs.architecture.backend && (
                    <p><strong>Backend:</strong> {(() => {
                      const backend = techReqs.architecture.backend;
                      if (typeof backend === 'string') return backend;
                      return safeExtractString(backend?.framework) ||
                             safeExtractString(backend?.tech) ||
                             safeExtractString(backend?.name) ||
                             safeExtractString(backend) ||
                             (typeof backend === 'object' ? Object.keys(backend || {}).join(', ') : 'N/A');
                    })()}</p>
                  )}
                  {techReqs.architecture.database && (
                    <p><strong>Base de Datos:</strong> {(() => {
                      const database = techReqs.architecture.database;
                      if (typeof database === 'string') return database;
                      return safeExtractString(database?.primary) ||
                             safeExtractString(database?.tech) ||
                             safeExtractString(database?.name) ||
                             safeExtractString(database) ||
                             (typeof database === 'object' ? Object.keys(database || {}).join(', ') : 'N/A');
                    })()}</p>
                  )}
                  {techReqs.architecture.infrastructure && (
                    <p><strong>Infraestructura:</strong> {typeof techReqs.architecture.infrastructure === 'string' ? techReqs.architecture.infrastructure : (
                      typeof techReqs.architecture.infrastructure === 'object' ? (
                        techReqs.architecture.infrastructure.provider ||
                        techReqs.architecture.infrastructure.services?.join(', ') ||
                        Object.keys(techReqs.architecture.infrastructure).join(', ')
                      ) : 'N/A'
                    )}</p>
                  )}
                </>
              )}
              {typeof techReqs.architecture === 'string' && <p>{techReqs.architecture}</p>}
            </div>
          </Section>
        )}

        {/* API Contracts */}
        {Array.isArray(techReqs.api_contracts) && techReqs.api_contracts.length > 0 && (
          <Section title="🔌 Contratos de API" className="sec-green">
            <div className="api-contracts">
              {techReqs.api_contracts.map((contract, idx) => (
                <div key={idx} className="contract-item">
                  <h5>{contract.endpoint || contract.service || `Endpoint ${idx + 1}`}</h5>
                  {contract.method && <p><strong>Método:</strong> {contract.method}</p>}
                  {contract.input && <p><strong>Input:</strong> {typeof contract.input === 'string' ? contract.input : (
                    contract.input.schema || contract.input.type || contract.input.name || 
                    (typeof contract.input === 'object' ? `${Object.keys(contract.input).join(', ')}` : String(contract.input))
                  )}</p>}
                  {contract.output && <p><strong>Output:</strong> {typeof contract.output === 'string' ? contract.output : (
                    contract.output.schema || contract.output.type || contract.output.name || 
                    (typeof contract.output === 'object' ? `${Object.keys(contract.output).join(', ')}` : String(contract.output))
                  )}</p>}
                  {contract.note && <p className="muted">{contract.note}</p>}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Data Models */}
        {Array.isArray(techReqs.data_models) && techReqs.data_models.length > 0 && (
          <Section title="📊 Modelos de Datos" className="sec-indigo">
            <div className="data-models">
              {techReqs.data_models.map((model, idx) => (
                <div key={idx} className="model-item">
                  <h5>{model.entity || `Entity ${idx + 1}`}</h5>
                  {model.key_constraint && <p><strong>Constraint:</strong> {model.key_constraint}</p>}
                  {Array.isArray(model.fields) && model.fields.length > 0 && (
                    <p><strong>Fields:</strong> {model.fields.map(f => typeof f === 'string' ? f : f.name).join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Security Requirements */}
        {Array.isArray(techReqs.security_requirements) && techReqs.security_requirements.length > 0 && (
          <Section title="🔐 Requisitos de Seguridad Técnicos" className="sec-red">
            <List items={techReqs.security_requirements} />
          </Section>
        )}

        {/* Best Practices */}
        {Array.isArray(techReqs.best_practices_applied) && techReqs.best_practices_applied.length > 0 && (
          <Section title="⭐ Mejores Prácticas Aplicadas" className="sec-amber">
            <List items={techReqs.best_practices_applied} />
          </Section>
        )}

        {/* UX Requirements */}
        {data.ux_requirements && (
          <Section title="🎨 Requisitos UX/UI" className="sec-pink">
            {Array.isArray(data.ux_requirements.user_flows) && data.ux_requirements.user_flows.length > 0 && (
              <div>
                <h5>User Flows</h5>
                <List items={data.ux_requirements.user_flows.map(f => typeof f === 'string' ? f : (
                  f.flow || f.name || f.title || f.description || `${Object.keys(f).slice(0, 2).join(', ')}...`
                ))} />
              </div>
            )}
            {data.ux_requirements.design_system && (
              <div>
                <h5>Design System</h5>
                <p>
                  {typeof data.ux_requirements.design_system === 'string' ? data.ux_requirements.design_system : (
                    data.ux_requirements.design_system && typeof data.ux_requirements.design_system === 'object' ? (
                      data.ux_requirements.design_system.name || 
                      (data.ux_requirements.design_system.colors ? 'Design System con paleta de colores' : 'Custom Design System')
                    ) : 'N/A'
                  )}
                </p>
              </div>
            )}
            {Array.isArray(data.ux_requirements.accessibility) && data.ux_requirements.accessibility.length > 0 && (
              <div>
                <h5>Accesibilidad</h5>
                <List items={data.ux_requirements.accessibility} />
              </div>
            )}
            {data.ux_requirements.responsive_design && (
              <div>
                <h5>Responsive Design</h5>
                <p>
                  {typeof data.ux_requirements.responsive_design === 'string' ? data.ux_requirements.responsive_design : (
                    data.ux_requirements.responsive_design && typeof data.ux_requirements.responsive_design === 'object' ? (
                      data.ux_requirements.responsive_design.breakpoints?.join(', ') ||
                      data.ux_requirements.responsive_design.strategy ||
                      `Responsive: ${Object.keys(data.ux_requirements.responsive_design).join(', ')}`
                    ) : 'N/A'
                  )}
                </p>
              </div>
            )}
          </Section>
        )}

        {quality.test_strategy && (
          <Section title="🧪 Estrategia de Testing" className="sec-green">
            {typeof quality.test_strategy === 'object' && (
              <>
                {quality.test_strategy.automation_ratio && (
                  <p><strong>Automatización:</strong> {(() => {
                    const val = quality.test_strategy.automation_ratio;
                    if (typeof val === 'string' || typeof val === 'number') return String(val);
                    return safeExtractString(val) || 'N/A';
                  })()}</p>
                )}
                {quality.test_strategy.levels && (
                  <p><strong>Niveles:</strong> {(() => {
                    const val = quality.test_strategy.levels;
                    if (Array.isArray(val)) {
                      return val.map(v => safeExtractString(v) || (typeof v === 'string' ? v : String(v))).join(', ');
                    }
                    return safeExtractString(val) || (typeof val === 'string' ? val : 'N/A');
                  })()}</p>
                )}
                {quality.test_strategy.approach && (
                  <p><strong>Enfoque:</strong> {(() => {
                    const val = quality.test_strategy.approach;
                    if (typeof val === 'string') return val;
                    if (typeof val === 'object' && val !== null) {
                      return safeExtractString(val) || JSON.stringify(val);
                    }
                    return safeExtractString(val) || String(val || 'N/A');
                  })()}</p>
                )}
                {quality.test_strategy.pyramid && (
                  <p><strong>Pirámide:</strong> {(() => {
                    const val = quality.test_strategy.pyramid;
                    if (typeof val === 'string') return val;
                    if (typeof val === 'object' && val !== null) {
                      // Si es un objeto, intentar extraer valores string o mostrar estructura
                      const extracted = safeExtractString(val);
                      if (extracted) return extracted;
                      // Si tiene propiedades, mostrar las keys o convertir a string
                      return Object.keys(val).join(', ') || JSON.stringify(val);
                    }
                    return safeExtractString(val) || String(val || 'N/A');
                  })()}</p>
                )}
              </>
            )}
            {quality.coverage_goals && typeof quality.coverage_goals === 'object' && (
              <div>
                <strong>Cobertura Objetivo:</strong>
                <ul>
                  {Object.entries(quality.coverage_goals).map(([key, value]) => (
                    <li key={key}>{key}: {safeExtractString(value) || (typeof value === 'object' ? JSON.stringify(value) : String(value))}</li>
                  ))}
                </ul>
              </div>
            )}
            {Array.isArray(quality.quality_gates) && quality.quality_gates.length > 0 && (
              <div>
                <strong>Quality Gates:</strong>
                <List items={quality.quality_gates} />
              </div>
            )}
          </Section>
        )}

        {/* Test Scenarios */}
        {Array.isArray(quality.test_scenarios) && quality.test_scenarios.length > 0 && (
          <Section title="📝 Escenarios de Prueba" className="sec-green">
            <List items={quality.test_scenarios} />
          </Section>
        )}

        {/* Agile Process */}
        {data.agile_process && (
          <Section title="🔄 Proceso Ágil" className="sec-blue">
            {data.agile_process.sprint_structure && (
              <div>
                <h5>Sprint Structure</h5>
                <p>
                  {typeof data.agile_process.sprint_structure === 'object' ? (
                    data.agile_process.sprint_structure.duration ? `Duración: ${data.agile_process.sprint_structure.duration}` :
                    data.agile_process.sprint_structure.length ? `Sprints de ${data.agile_process.sprint_structure.length} semanas` :
                    `${Object.keys(data.agile_process.sprint_structure).join(', ')}`
                  ) : data.agile_process.sprint_structure}
                </p>
              </div>
            )}
            {Array.isArray(data.agile_process.definition_of_ready) && data.agile_process.definition_of_ready.length > 0 && (
              <div>
                <h5>Definition of Ready</h5>
                <List items={data.agile_process.definition_of_ready} />
              </div>
            )}
            {Array.isArray(data.agile_process.ceremonies) && data.agile_process.ceremonies.length > 0 && (
              <div>
                <h5>Ceremonias</h5>
                <List items={data.agile_process.ceremonies} />
              </div>
            )}
            {data.agile_process.team_composition && (
              <div>
                <h5>Team Composition</h5>
                <p>
                  {typeof data.agile_process.team_composition === 'object' ? (
                    Array.isArray(data.agile_process.team_composition) ? 
                      data.agile_process.team_composition.map(r => r.role || r.name || r).join(', ') :
                      data.agile_process.team_composition.size ? 
                        `Equipo de ${data.agile_process.team_composition.size} miembros` :
                        `${Object.keys(data.agile_process.team_composition).join(', ')}`
                  ) : data.agile_process.team_composition}
                </p>
              </div>
            )}
            {data.agile_process.release_strategy && (
              <div>
                <h5>Release Strategy</h5>
                <p>{data.agile_process.release_strategy}</p>
              </div>
            )}
          </Section>
        )}

        {risks.risks && Array.isArray(risks.risks) && risks.risks.length > 0 && (
          <Section title="⚠️ Riesgos Identificados" className="sec-orange">
            <List items={risks.risks} />
          </Section>
        )}

        {Array.isArray(risks.assumptions) && risks.assumptions.length > 0 && (
          <Section title="💭 Assumptions" className="sec-amber">
            <List items={risks.assumptions} />
          </Section>
        )}

        {Array.isArray(risks.dependencies) && risks.dependencies.length > 0 && (
          <Section title="🔗 Dependencies" className="sec-purple">
            <List items={risks.dependencies} />
          </Section>
        )}

        {Array.isArray(risks.mitigation_strategies) && risks.mitigation_strategies.length > 0 && (
          <Section title="🛡️ Estrategias de Mitigación" className="sec-green">
            <List items={risks.mitigation_strategies} />
          </Section>
        )}

        {data.next_steps && Array.isArray(data.next_steps) && data.next_steps.length > 0 && (
          <Section title="🚀 Próximos Pasos" className="sec-blue">
            <List items={data.next_steps} />
          </Section>
        )}

        {/* Appendices */}
        {data.appendices && (
          <Section title="📎 Apéndices" className="sec-teal">
            {Array.isArray(data.appendices.context7_references) && data.appendices.context7_references.length > 0 && (
              <div>
                <h5>Referencias Context7</h5>
                <List items={data.appendices.context7_references} />
              </div>
            )}
            {Array.isArray(data.appendices.conflict_resolutions) && data.appendices.conflict_resolutions.length > 0 && (
              <div>
                <h5>Resoluciones de Conflictos</h5>
                {data.appendices.conflict_resolutions.map((cr, idx) => (
                  <div key={idx} className="conflict-item">
                    {cr.conflict && <p><strong>Conflicto:</strong> {cr.conflict}</p>}
                    {cr.resolution && <p><strong>Resolución:</strong> {cr.resolution}</p>}
                    {cr.rationale && <p className="muted">{cr.rationale}</p>}
                  </div>
                ))}
              </div>
            )}
            {Array.isArray(data.appendices.tradeoff_analysis) && data.appendices.tradeoff_analysis.length > 0 && (
              <div>
                <h5>Análisis de Trade-offs</h5>
                {data.appendices.tradeoff_analysis.map((to, idx) => (
                  <div key={idx} className="tradeoff-item">
                    {to.decision && <p><strong>Decisión:</strong> {to.decision}</p>}
                    {to.justification && <p className="muted">{to.justification}</p>}
                  </div>
                ))}
              </div>
            )}
          </Section>
        )}

        {Object.keys(roleSignoffs).length > 0 && (
          <Section title="✅ Firmas de Roles" className="sec-teal">
            <div className="signoffs">
              {Object.entries(roleSignoffs).map(([role, signoff]) => (
                <div key={role} className="signoff-item">
                  <strong>{role.replace(/_/g, ' ').replace(/\b\w/g, m => m.toUpperCase())}:</strong>
                  <span className={signoff.approved ? 'badge badge-success' : 'badge badge-warning'}>
                    {signoff.approved ? '✅ Aprobado' : '⏳ Pendiente'}
                  </span>
                  {signoff.notes && <p className="signoff-notes">{signoff.notes}</p>}
                </div>
              ))}
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}

function GenericObjectView({ data }) {
  if (!data || typeof data !== 'object') return null;
  const entries = Object.entries(data);
  return (
    <div className="agent-structured">
      {entries.map(([key, value]) => (
        <Section key={key} title={key.replace(/_/g, ' ').replace(/\b\w/g, m => m.toUpperCase())}>
          {Array.isArray(value) ? <List items={value} /> : (
            <p>
              {typeof value === 'string' ? value : (
                typeof value === 'object' && value !== null ? (
                  <div className="fallback-object-display">
                    {Object.entries(value).slice(0, 5).map(([k, v], idx) => (
                      <div key={idx} className="object-entry">
                        <strong>{k.replace(/_/g, ' ')}:</strong> {
                          typeof v === 'string' ? v :
                          safeRenderValue(v)
                        }
                      </div>
                    ))}
                    {Object.keys(value).length > 5 && (
                      <div className="more-entries">...{Object.keys(value).length - 5} propiedades más</div>
                    )}
                  </div>
                ) : String(value)
              )}
            </p>
          )}
        </Section>
      ))}
    </div>
  );
}

function detectRole(agentName) {
  const s = String(agentName || '').toLowerCase();
  if (s.includes('supervisor')) return 'Supervisor';
  if (s.includes('coordinator')) return 'Coordinator';
  if (s.includes('productowner') || s.includes('product owner') || s.includes('po')) return 'ProductOwner';
  if (s.includes('productmanager') || s.includes('product manager') || s.includes('pm')) return 'ProductManager';
  if (s.includes('uxui') || s.includes('ux/ui') || s.includes('ux') || s.includes('ui')) return 'UXUI_Designer';
  if (s.includes('technical') || s.includes('tech') || s.includes('lead')) return 'TechnicalLead';
  if (s.includes('scrum')) return 'ScrumMaster';
  if (s.includes('qa') || s.includes('quality')) return 'QA_Specialist';
  return agentName;
}

export function AgentContentView({ agentName, content, data: providedData }) {
  // Si se proporciona data directamente (ya parseado), usarlo
  // Si no, intentar parsear desde content
  const data = providedData || parseJson(content);

  if (!data) {
    return (
      <div className="agent-structured">
        <Section title="Contenido">
          <pre className="code-block">
            {typeof content === 'string' ? content : (
              <div className="fallback-content-display">
                <p className="muted">Contenido estructurado disponible. Usa la vista consolidada para ver detalles.</p>
                {providedData && typeof providedData === 'object' && (
                  <div className="data-summary">
                    <strong>Datos disponibles:</strong> {Object.keys(providedData).length} propiedades
                  </div>
                )}
              </div>
            )}
            {!content && providedData && typeof providedData === 'object' && (
              <div className="fallback-content-display">
                <p className="muted">Datos estructurados disponibles ({Object.keys(providedData).length} propiedades)</p>
              </div>
            )}
          </pre>
        </Section>
      </div>
    );
  }

  const role = detectRole(agentName);
  if (role === 'ProductManager') return <ProductManagerView data={data} />;
  if (role === 'ProductOwner') return <ProductOwnerView data={data} />;
  if (role === 'UXUI_Designer') return <UXUIView data={data} />;
  if (role === 'Coordinator') return <CoordinatorView data={data} />;
  if (role === 'TechnicalLead') return <TechnicalLeadView data={data} />;
  if (role === 'ScrumMaster') return <ScrumMasterView data={data} />;
  if (role === 'QA_Specialist') return <QAView data={data} />;
  if (role === 'Supervisor') return <SupervisorBoard data={data} />;

  return <GenericObjectView data={data} />;
}

export default AgentContentView;
