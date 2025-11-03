import React, { useState } from 'react';

export function ResultActions({ 
  onExportPDF, 
  onCopyLink, 
  onGenerateNew,
  onShareResults,
  onSaveTemplate 
}) {
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopyLink && onCopyLink();
    } catch (error) {
      console.error('Error copying link:', error);
    }
  };

  const handleExportPDF = () => {
    onExportPDF && onExportPDF();
    // Aquí se implementaría la lógica de exportación a PDF
    console.log('Exporting to PDF...');
  };

  const handleGenerateNew = () => {
    onGenerateNew && onGenerateNew();
  };

  const handleShareResults = () => {
    onShareResults && onShareResults();
  };

  const handleSaveTemplate = () => {
    onSaveTemplate && onSaveTemplate();
  };

  return (
    <div className="result-actions">
      <div className="actions-primary">
        <button 
          className="btn btn-primary"
          onClick={handleExportPDF}
        >
          <i className="fas fa-file-pdf"></i>
          Exportar PDF
        </button>
        
        <button 
          className="btn btn-secondary"
          onClick={handleCopyLink}
        >
          <i className={`fas ${copied ? 'fa-check' : 'fa-link'}`}></i>
          {copied ? 'Copiado!' : 'Copiar Enlace'}
        </button>
        
        <button 
          className="btn btn-secondary"
          onClick={handleGenerateNew}
        >
          <i className="fas fa-plus"></i>
          Nuevo Análisis
        </button>
      </div>

      <div className="actions-secondary">
        <button 
          className="btn btn-outline"
          onClick={() => setShowActions(!showActions)}
          aria-expanded={showActions}
          aria-label="Mostrar más acciones"
          aria-haspopup="true"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setShowActions(!showActions);
            }
            if (e.key === 'Escape' && showActions) {
              setShowActions(false);
            }
          }}
        >
          <i className="fas fa-ellipsis-h" aria-hidden="true"></i>
          Más Acciones
        </button>
        
        {showActions && (
          <div 
            className="actions-dropdown" 
            role="menu"
            aria-label="Menú de acciones adicionales"
          >
            <button 
              className="action-item"
              onClick={handleShareResults}
              role="menuitem"
              aria-label="Compartir resultados del análisis"
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleShareResults();
                }
              }}
            >
              <i className="fas fa-share-alt" aria-hidden="true"></i>
              Compartir Resultados
            </button>
            <button 
              className="action-item"
              onClick={handleSaveTemplate}
              role="menuitem"
              aria-label="Guardar análisis como plantilla"
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleSaveTemplate();
                }
              }}
            >
              <i className="fas fa-save" aria-hidden="true"></i>
              Guardar como Plantilla
            </button>
            <button 
              className="action-item"
              onClick={() => window.print()}
              role="menuitem"
              aria-label="Imprimir resultados del análisis"
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  window.print();
                }
              }}
            >
              <i className="fas fa-print" aria-hidden="true"></i>
              Imprimir
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
