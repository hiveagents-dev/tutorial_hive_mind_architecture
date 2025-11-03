import React, { useState } from 'react';

/**
 * Componente para mostrar texto con truncado inteligente y opción de expandir/contraer
 */
export function TruncatedText({ 
  text, 
  maxLength = 200, 
  className = '',
  showExpandButton = true,
  expandLabel = 'Ver más',
  collapseLabel = 'Ver menos'
}) {
  if (!text || typeof text !== 'string') return null;

  const [isExpanded, setIsExpanded] = useState(false);
  const shouldTruncate = text.length > maxLength;
  const displayText = isExpanded || !shouldTruncate ? text : `${text.substring(0, maxLength)}...`;

  if (!shouldTruncate && !showExpandButton) {
    return <span className={className}>{text}</span>;
  }

  return (
    <div className={`truncated-text ${className}`}>
      <span className="truncated-content">
        {displayText}
      </span>
      {shouldTruncate && showExpandButton && (
        <button 
          className="btn-text-link"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={isExpanded ? collapseLabel : expandLabel}
        >
          {isExpanded ? (
            <>
              <i className="fas fa-chevron-up"></i> {collapseLabel}
            </>
          ) : (
            <>
              <i className="fas fa-chevron-down"></i> {expandLabel}
            </>
          )}
        </button>
      )}
    </div>
  );
}

/**
 * Componente para mostrar texto con tooltip explicativo
 */
export function TooltipText({ 
  text, 
  tooltip, 
  className = '',
  position = 'top'
}) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <span 
      className={`tooltip-wrapper ${className}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className="tooltip-trigger">
        {text}
        <i className="fas fa-info-circle tooltip-icon"></i>
      </span>
      {showTooltip && tooltip && (
        <div className={`tooltip tooltip-${position}`}>
          <div className="tooltip-content">
            {tooltip}
          </div>
          <div className="tooltip-arrow"></div>
        </div>
      )}
    </span>
  );
}

/**
 * Componente para mostrar contenido JSON de forma humanizada (sin mostrar JSON crudo)
 */
export function HumanizedContent({ content, className = '' }) {
  if (!content) return null;

  // Intentar parsear como JSON
  let parsed;
  try {
    parsed = typeof content === 'string' ? JSON.parse(content) : content;
  } catch {
    // No es JSON, mostrar como texto truncado
    return <TruncatedText text={content} className={className} />;
  }

  // Si es objeto o array, mostrar de forma estructurada
  if (typeof parsed === 'object') {
    if (Array.isArray(parsed)) {
      return (
        <div className={`humanized-content ${className}`}>
          <ul className="humanized-list">
            {parsed.slice(0, 5).map((item, idx) => (
              <li key={idx}>
                {typeof item === 'string' ? item : (
                  typeof item === 'object' && item !== null ? (
                    item.title || item.name || item.description || item.label || 
                    `${Object.keys(item).slice(0, 2).join(', ')}...`
                  ) : String(item)
                )}
              </li>
            ))}
            {parsed.length > 5 && (
              <li className="more-items-indicator">
                <i className="fas fa-ellipsis-h"></i> {parsed.length - 5} elementos más
              </li>
            )}
          </ul>
        </div>
      );
    }

    // Es un objeto, mostrar propiedades importantes
    const entries = Object.entries(parsed);
    return (
      <div className={`humanized-content ${className}`}>
        <dl className="humanized-definition-list">
          {entries.slice(0, 10).map(([key, value]) => (
            <React.Fragment key={key}>
              <dt>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</dt>
              <dd>
                {typeof value === 'string' ? (
                  <TruncatedText text={value} maxLength={150} />
                ) : Array.isArray(value) ? (
                  `${value.length} elementos`
                ) : typeof value === 'object' ? (
                  `${Object.keys(value).length} propiedades`
                ) : (
                  String(value)
                )}
              </dd>
            </React.Fragment>
          ))}
          {entries.length > 10 && (
            <div className="more-items-indicator">
              <i className="fas fa-ellipsis-h"></i> {entries.length - 10} propiedades más
            </div>
          )}
        </dl>
      </div>
    );
  }

  // Valor simple
  return <TruncatedText text={String(parsed)} className={className} />;
}

