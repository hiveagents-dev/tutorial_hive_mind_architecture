import React from 'react';

// Componente para mostrar contenido estructurado (JSON parseado)
export function StructuredContent({ content, title = "Contenido" }) {
  if (!content) return null;

  // Intentar parsear como JSON
  let parsedContent;
  try {
    parsedContent = typeof content === 'string' ? JSON.parse(content) : content;
  } catch (error) {
    // Si no es JSON válido, mostrar como texto plano
    return (
      <div className="structured-content">
        <h4>{title}</h4>
        <div className="content-text">
          <pre>{content}</pre>
        </div>
      </div>
    );
  }

  // Función recursiva para renderizar objetos JSON
  const renderValue = (value, key = null, level = 0) => {
    const indent = level * 20;
    
    if (value === null) {
      return <span className="json-null">null</span>;
    }
    
    if (typeof value === 'boolean') {
      return <span className="json-boolean">{value.toString()}</span>;
    }
    
    if (typeof value === 'number') {
      return <span className="json-number">{value}</span>;
    }
    
    if (typeof value === 'string') {
      return <span className="json-string">"{value}"</span>;
    }
    
    if (Array.isArray(value)) {
      return (
        <div className="json-array" style={{ marginLeft: `${indent}px` }}>
          <span className="json-bracket">[</span>
          {value.map((item, index) => (
            <div key={index} className="json-array-item">
              <span className="json-index">{index}:</span>
              {renderValue(item, index, level + 1)}
            </div>
          ))}
          <span className="json-bracket">]</span>
        </div>
      );
    }
    
    if (typeof value === 'object') {
      return (
        <div className="json-object" style={{ marginLeft: `${indent}px` }}>
          <span className="json-bracket">{'{'}</span>
          {Object.entries(value).map(([objKey, objValue]) => (
            <div key={objKey} className="json-property">
              <span className="json-key">"{objKey}":</span>
              {renderValue(objValue, objKey, level + 1)}
            </div>
          ))}
          <span className="json-bracket">{'}'}</span>
        </div>
      );
    }
    
    return <span className="json-unknown">{String(value)}</span>;
  };

  return (
    <div className="structured-content">
      <h4>{title}</h4>
      <div className="json-content">
        {renderValue(parsedContent)}
      </div>
    </div>
  );
}

// Componente para mostrar preview del contenido (sin JSON crudo)
export function ContentPreview({ content, maxLength = 200 }) {
  if (!content) return null;

  // Intentar parsear como JSON para preview humanizado
  let preview = null;
  let summaryItems = [];
  
  try {
    const parsed = typeof content === 'string' ? JSON.parse(content) : content;
    
    if (typeof parsed === 'object' && parsed !== null) {
      // Crear preview humanizado sin mostrar JSON crudo
      if (Array.isArray(parsed)) {
        summaryItems = parsed.slice(0, 3).map((item, idx) => {
          if (typeof item === 'string') return item;
          if (typeof item === 'object' && item !== null) {
            // Extraer campos descriptivos
            return item.title || item.name || item.description || item.id || `Elemento ${idx + 1}`;
          }
          return String(item);
        });
        if (parsed.length > 3) {
          summaryItems.push(`${parsed.length - 3} elementos más`);
        }
      } else {
        // Es un objeto, extraer valores descriptivos
        const entries = Object.entries(parsed).slice(0, 3);
        summaryItems = entries.map(([key, value]) => {
          const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
          if (typeof value === 'string' && value.length < 50) {
            return `${label}: ${value}`;
          } else if (typeof value === 'number' || typeof value === 'boolean') {
            return `${label}: ${String(value)}`;
          } else if (Array.isArray(value)) {
            return `${label}: ${value.length} elementos`;
          } else if (typeof value === 'object' && value !== null) {
            return `${label}: ${Object.keys(value).length} propiedades`;
          }
          return label;
        });
        if (Object.keys(parsed).length > 3) {
          summaryItems.push(`${Object.keys(parsed).length - 3} propiedades más`);
        }
      }
    } else {
      // Valor simple
      preview = String(parsed);
    }
  } catch (error) {
    // No es JSON válido, usar preview de texto truncado
    const text = String(content);
    preview = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }

  return (
    <div className="content-preview">
      {summaryItems.length > 0 ? (
        <div className="preview-summary">
          {summaryItems.map((item, idx) => (
            <div key={idx} className="preview-item">
              <i className="fas fa-circle"></i>
              <span>{item}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="preview-text">
          {preview || 'Contenido disponible'}
        </div>
      )}
    </div>
  );
}
