import React, { useMemo } from "react";
import { Tooltip } from './Tooltip';

// Wrapper simple para tooltip
function TooltipWrapper({ children, content }) {
  if (!content) return children;
  return (
    <Tooltip content={content} position="top" delay={300}>
      {children}
    </Tooltip>
  );
}

const ROLE_THEMES = {
  ProductManager: { color: 'agent-blue', icon: 'fas fa-chart-bar', title: 'Valor de Negocio', desc: 'Análisis de valor, mercado objetivo y competencia' },
  ProductOwner: { color: 'agent-green', icon: 'fas fa-clipboard-list', title: 'Especificaciones', desc: 'Epics, user stories y customer journeys' },
  UXUI_Designer: { color: 'agent-purple', icon: 'fas fa-palette', title: 'Diseño UX/UI', desc: 'Personas, flujos y pantallas clave' },
  TechnicalLead: { color: 'agent-orange', icon: 'fas fa-microchip', title: 'Arquitectura Técnica', desc: 'Arquitectura, integraciones y no funcionales' },
  ScrumMaster: { color: 'agent-teal', icon: 'fas fa-stream', title: 'Procesos Ágiles', desc: 'Flujo, ceremonias, riesgos y dependencias' },
  QA_Specialist: { color: 'agent-red', icon: 'fas fa-vial', title: 'Calidad y Testing', desc: 'Estrategia de pruebas, métricas y cobertura' }
};

function tryParseJson(text) {
  try {
    const cleaned = typeof text === 'string' ? text.trim() : '';
    if (!cleaned) return null;
    return JSON.parse(cleaned);
  } catch {
    return null;
  }
}

function extractPreviewItems(content) {
  const json = tryParseJson(content);
  if (json && typeof json === 'object') {
    const entries = Object.entries(json)
      .filter(([k, v]) => v != null && String(v).trim().length > 0)
      .slice(0, 3)
      .map(([k, v]) => ({ 
        label: k.replace(/_/g, ' '), 
        value: typeof v === 'string' ? v.slice(0, 160) : (
          Array.isArray(v) ? `${v.length} elementos` :
          typeof v === 'object' && v !== null ? (
            v.title || v.name || v.description || v.id || `${Object.keys(v).length} propiedades`
          ).slice(0, 160) :
          String(v).slice(0, 160)
        )
      }));
    const remaining = Math.max(Object.keys(json).length - entries.length, 0);
    return { items: entries, remaining };
  }

  const lines = String(content || '')
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l);
  const bullets = lines.filter(l => /^[-*•]/.test(l)).map(l => l.replace(/^[-*•]\s?/, ''));
  const items = (bullets.length ? bullets : lines).slice(0, 3).map((v, i) => ({ label: `Punto ${i + 1}`, value: v.slice(0, 160) }));
  const remaining = Math.max((bullets.length || lines.length) - items.length, 0);
  return { items, remaining };
}

function QualityIndicators({ agent, content }) {
  const indicators = useMemo(() => {
    const flags = [];
    const conf = agent?.confidence ?? 0;
    if (conf >= 0.8) flags.push({ 
      icon: 'fas fa-check-circle', 
      label: 'Consenso probable', 
      className: 'ok',
      tooltip: 'Indica que hay una alta probabilidad (>80%) de que los agentes especializados estén de acuerdo en el análisis.'
    });
    if (/risk|riesgo|issue|bloqueo|bloqueador/i.test(content || '')) flags.push({ 
      icon: 'fas fa-exclamation-triangle', 
      label: 'Puntos de atención', 
      className: 'warn',
      tooltip: 'El análisis identifica posibles riesgos o puntos que requieren atención especial.'
    });
    if (/dependenc/i.test(content || '')) flags.push({ 
      icon: 'fas fa-link', 
      label: 'Dependencias', 
      className: 'info',
      tooltip: 'El análisis identifica dependencias entre tareas o componentes que deben considerarse.'
    });
    return flags;
  }, [agent, content]);

  if (!indicators.length) return null;
  return (
    <div className="agent-indicators">
      {indicators.map((it, idx) => (
        <TooltipWrapper key={idx} content={it.tooltip}>
          <span 
            className={`indicator ${it.className}`}
            role="status"
            aria-label={it.tooltip || it.label}
          >
            <i className={it.icon} aria-hidden="true"></i>
            {it.label}
          </span>
        </TooltipWrapper>
      ))}
    </div>
  );
}

export function AgentCard({ agent, onShow, compact = false }) {
  const role = agent?.agent_name || 'Agent';
  const theme = ROLE_THEMES[role] || { color: 'agent-default', icon: 'fas fa-user-gear', title: role, desc: 'Análisis especializado' };
  const confidencePct = Math.round((agent?.confidence || 0) * 100);

  // Extraer resumen inteligente (sin JSON raw)
  const getSmartSummary = () => {
    const json = tryParseJson(agent?.content);
    if (!json || typeof json !== 'object') {
      // Si no es JSON, devolver primeras líneas limpias
      const text = String(agent?.content || '');
      const lines = text.split('\n').filter(l => l.trim() && !l.trim().startsWith('{') && !l.trim().startsWith('}'));
      return lines.slice(0, 2).join(' ').slice(0, 120);
    }

    // Para JSON, extraer valores clave y significativos
    const summaryFields = [];
    Object.entries(json).forEach(([key, value]) => {
      if (value && typeof value === 'string' && value.length > 20 && value.length < 200) {
        summaryFields.push({ key: key.replace(/_/g, ' '), value: value.slice(0, 100) });
      } else if (Array.isArray(value) && value.length > 0) {
        summaryFields.push({ key: key.replace(/_/g, ' '), value: `${value.length} elementos` });
      } else if (value && typeof value === 'object') {
        summaryFields.push({ key: key.replace(/_/g, ' '), value: `${Object.keys(value).length} sub-elementos` });
      }
      if (summaryFields.length >= 3) return;
    });
    return summaryFields;
  };

  const smartSummary = getSmartSummary();
  const remaining = Array.isArray(smartSummary) 
    ? Math.max(Object.keys(tryParseJson(agent?.content) || {}).length - smartSummary.length, 0)
    : 0;

  return (
    <div className={`agent-card redesigned ${theme.color} ${compact ? 'compact' : ''}`}>
      <div className="agent-header">
        <div className="agent-title">
          <div className="agent-icon-wrapper">
            <i className={theme.icon} aria-hidden="true" aria-label={`Ícono de ${role}`}></i>
          </div>
          <div className="agent-title-content">
            <h5>{role}</h5>
            <div className="agent-subtitle">{theme.title}</div>
          </div>
        </div>
        <div className="agent-meta">
          <span 
            className={`confidence-badge ${confidencePct >= 80 ? 'high' : confidencePct >= 60 ? 'medium' : 'low'}`}
            aria-label={`Nivel de confianza: ${confidencePct}%`}
            role="status"
          >
            {confidencePct}%
          </span>
        </div>
      </div>

      <div className="agent-progress-compact">
        <div className="progress-bar-mini">
          <div className="progress-fill-mini" style={{ width: `${confidencePct}%` }}></div>
        </div>
      </div>

      <QualityIndicators agent={agent} content={agent?.content} />

      <div className="agent-preview-smart">
        {Array.isArray(smartSummary) ? (
          <div className="smart-summary">
            {smartSummary.map((item, idx) => (
              <div key={idx} className="summary-item">
                <span className="summary-key">{item.key}:</span>
                <span className="summary-value">{item.value}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="smart-summary-text">{smartSummary || 'Análisis completado'}</div>
        )}
        {remaining > 0 && (
          <div className="more-indicator">
            <i className="fas fa-ellipsis-h"></i> {remaining} elementos más
          </div>
        )}
      </div>

      <div className="agent-actions-compact">
        <button 
          className="btn btn-primary btn-sm btn-expand" 
          onClick={() => onShow && onShow(agent)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onShow && onShow(agent);
            }
          }}
          aria-label={`Ver análisis completo de ${role}`}
          title="Ver análisis completo"
        >
          <i className="fas fa-eye" aria-hidden="true"></i>
          <span>Ver Completo</span>
        </button>
        <div className="quick-actions" role="group" aria-label="Acciones rápidas">
          <button 
            className="btn-icon-sm" 
            title="Copiar análisis"
            aria-label={`Copiar análisis de ${role} al portapapeles`}
            onClick={(e) => {
              e.stopPropagation();
              if (agent?.content) {
                navigator.clipboard.writeText(agent.content);
              }
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.currentTarget.click();
              }
            }}
          >
            <i className="fas fa-copy" aria-hidden="true"></i>
            <span className="sr-only">Copiar</span>
          </button>
          <button 
            className="btn-icon-sm" 
            title="Exportar PDF"
            aria-label={`Exportar análisis de ${role} como PDF`}
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Implementar exportación PDF
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.currentTarget.click();
              }
            }}
          >
            <i className="fas fa-file-pdf" aria-hidden="true"></i>
            <span className="sr-only">Exportar PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default AgentCard;
