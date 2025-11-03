import React, { useEffect } from 'react';
import { StructuredContent } from './StructuredContent';
import { AgentContentView } from './AgentContentView';

export function Modal({ isOpen, onClose, title, children, size = 'large' }) {
  // Debug logs
  console.log('🔍 Modal render - isOpen:', isOpen, 'title:', title);
  
  // Cerrar modal con Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      console.log('🔍 Modal abriendo - agregando listeners');
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevenir scroll del body
    }

    return () => {
      console.log('🔍 Modal cerrando - removiendo listeners');
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    console.log('🔍 Modal no renderizado - isOpen es false');
    return null;
  }

  const sizeClass = {
    small: 'modal-small',
    medium: 'modal-medium',
    large: 'modal-large',
    xlarge: 'modal-xlarge'
  }[size] || 'modal-large';

  return (
    <div className="modal active" onClick={onClose}>
      <div 
        className={`modal-content ${sizeClass}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>{title}</h3>
          <button 
            className="modal-close" 
            onClick={onClose}
            aria-label="Cerrar modal"
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
}

// Modal específico para contenido completo de agentes
export function FullContentModal({ isOpen, onClose, agentData }) {
  console.log('🔍 FullContentModal render - isOpen:', isOpen, 'agentData:', agentData);
  
  if (!agentData) {
    console.log('🔍 FullContentModal no renderizado - no hay agentData');
    return null;
  }

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title={`${agentData.agent_name} - Contenido Completo`}
      size="xlarge"
    >
      <div className="full-content-modal">
        <div className="agent-meta">
          <div className="meta-item">
            <strong>Agente:</strong> {agentData.agent_name}
          </div>
          <div className="meta-item">
            <strong>Confianza:</strong> 
            <span className={`confidence ${agentData.confidence > 0.8 ? 'high' : agentData.confidence > 0.6 ? 'medium' : 'low'}`}>
              {(agentData.confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="meta-item">
            <strong>Metodología:</strong> {agentData.methodology || 'N/A'}
          </div>
          <div className="meta-item">
            <strong>Timestamp:</strong> {new Date(agentData.timestamp).toLocaleString()}
          </div>
        </div>
        
        <div className="agent-content-full">
          <AgentContentView 
            agentName={agentData.agent_name} 
            content={agentData.content || agentData.output_content}
            data={agentData.output_json || agentData.supervisor_response_content || agentData.data}
          />
        </div>
        
        <div className="modal-actions">
          <button 
            className="btn btn-secondary" 
            onClick={() => {
              const contentToCopy = agentData.content || agentData.output_content || 
                                   JSON.stringify(agentData.output_json || agentData.data || agentData.supervisor_response_content, null, 2);
              copyToClipboard(contentToCopy);
            }}
          >
            <i className="fas fa-copy"></i>
            Copiar
          </button>
          <button 
            className="btn btn-primary" 
            onClick={() => downloadContent(agentData)}
          >
            <i className="fas fa-download"></i>
            Descargar
          </button>
        </div>
      </div>
    </Modal>
  );
}

// Funciones auxiliares
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    // Mostrar toast de éxito (implementar si es necesario)
    console.log('Contenido copiado al portapapeles');
  }).catch(err => {
    console.error('Error al copiar:', err);
  });
}

function downloadContent(agentData) {
  const content = {
    agent_name: agentData.agent_name,
    confidence: agentData.confidence,
    methodology: agentData.methodology,
    timestamp: agentData.timestamp,
    content: agentData.content || agentData.output_content,
    output_json: agentData.output_json || agentData.data || agentData.supervisor_response_content
  };
  
  const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `hivemind-${agentData.agent_name}-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
