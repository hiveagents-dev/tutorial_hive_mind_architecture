import React from 'react';

function parseJson(s) {
  try { return typeof s === 'string' ? JSON.parse(s) : s; } catch { return null; }
}

function firstLine(text) {
  if (!text) return null;
  const t = String(text).trim();
  const m = t.split(/\n|\.|;|\r/).map(x => x.trim()).filter(Boolean);
  return m[0] || t.slice(0, 180);
}

const ROLE_SHORT = {
  ProductManager: { code: 'PM', cls: 'chip-pm' },
  ProductOwner: { code: 'PO', cls: 'chip-po' },
  UXUI_Designer: { code: 'UX', cls: 'chip-ux' },
  TechnicalLead: { code: 'TL', cls: 'chip-tl' },
  ScrumMaster: { code: 'SM', cls: 'chip-sm' },
  QA_Specialist: { code: 'QA', cls: 'chip-qa' },
};

function guessSourcesForBullet(bullet, workers){
  if(!bullet) return [];
  const text = String(bullet).toLowerCase();
  const hits = [];
  for(const w of workers){
    const body = (w?.content || '').toLowerCase();
    if(!body) continue;
    // Heurística simple: coincidencia parcial del bullet o palabras clave por rol
    const role = w?.agent_name;
    const roleMeta = ROLE_SHORT[role];
    if(!roleMeta) continue;
    const keywordsByRole = {
      ProductManager: ['valor', 'mercado', 'compet', 'viabilidad', 'kpi', 'métrica'],
      ProductOwner: ['story', 'epic', 'criterio', 'backlog', 'journey'],
      UXUI_Designer: ['persona', 'flujo', 'pantalla', 'ux', 'ui', 'accesib'],
      TechnicalLead: ['arquitect', 'integr', 'nfr', 'rendim', 'segur', 'datos', 'modelo'],
      ScrumMaster: ['ceremon', 'riesg', 'imped', 'depend', 'mejora', 'velocity', 'sprint'],
      QA_Specialist: ['prueba', 'test', 'automat', 'calidad', 'cobertura', 'criterio'],
    };
    const kws = keywordsByRole[role] || [];
    const kwHit = kws.some(k => text.includes(k) || body.includes(k));
    const bodyHit = body.includes(text.slice(0, Math.min(40, text.length))); // trozo corto
    if (kwHit || bodyHit) hits.push({ code: roleMeta.code, cls: roleMeta.cls });
  }
  // limitar a 3 fuentes para no saturar
  return hits.slice(0,3);
}

export function CoordinatorSynthesis({ coordinator, workers = [], onShowFull }) {
  const data = parseJson(coordinator?.content) || {};
  const bullets = [];

  const bExec = data.executive_summary ? firstLine(data.executive_summary) : null;
  const bVision = data.business_vision ? firstLine(data.business_vision) : null;
  const bProd = data.product_definition ? firstLine(data.product_definition) : null;
  if (bExec) bullets.push(bExec);
  if (bVision) bullets.push(bVision);
  if (bProd) bullets.push(bProd);
  if (bullets.length < 3 && data.key_points && Array.isArray(data.key_points)) {
    for (const kp of data.key_points) {
      if (bullets.length >= 3) break;
      bullets.push(firstLine(kp));
    }
  }
  if (!bullets.length) bullets.push(firstLine(coordinator?.content));

  const connections = workers.map(w => ({ name: w.agent_name, ok: !!w.content && w.content.length > 0 }));

  // Precisión de procedencia basada en campo origen
  function fieldSourcesForBullet(b) {
    if (!b) return [];
    if (b === bExec) return [{ code: 'PM', cls: 'chip-pm' }, { code: 'PO', cls: 'chip-po' }];
    if (b === bVision) return [{ code: 'PM', cls: 'chip-pm' }];
    if (b === bProd) return [{ code: 'PO', cls: 'chip-po' }];
    return [];
  }

  return (
    <div className="coord-center">
      <div className="coord-header">
        <div className="title">
          <span className="icon">🧠</span>
          <div>
            <h4>Síntesis Coordinada</h4>
            <p>Documento integrador que conecta análisis de todos los agentes</p>
          </div>
        </div>
        <div className="meta">
          <span className={`confidence ${coordinator?.confidence >= 0.8 ? 'high' : coordinator?.confidence >= 0.6 ? 'medium' : 'low'}`}>
            {Math.round((coordinator?.confidence || 0) * 100)}%
          </span>
        </div>
      </div>

      <div className="coord-body">
        <div className="key-points">
          <div className="kp-title">📌 Puntos Clave</div>
          <ul>
            {bullets.filter(Boolean).slice(0,3).map((b, i) => {
              const explicit = fieldSourcesForBullet(b);
              const sources = explicit.length ? explicit : guessSourcesForBullet(b, workers);
              return (
                <li key={i} className="kp-item">
                  <span className="dot-bullet">•</span>
                  <span className="kp-text">{b}</span>
                  {sources.length > 0 && (
                    <span className="source-chips">
                      {sources.map((s, idx) => (
                        <span key={idx} className={`source-chip ${s.cls}`}>{s.code}</span>
                      ))}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
        <div className="connections">
          <div className="conn-title">Conexiones de Agentes</div>
          <div className="conn-graph">
            {connections.map((c, i) => (
              <div key={i} className={`conn-line ${c.ok ? 'ok' : 'dim'}`}>
                <span className="dot"></span>
                <span className="label">{c.name}</span>
                <span className="line"></span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="coord-actions">
        <button className="btn btn-secondary" onClick={() => onShowFull && onShowFull(coordinator)}>
          <i className="fas fa-expand"></i>
          Ver Análisis Completo
        </button>
      </div>
    </div>
  );
}

export default CoordinatorSynthesis;
