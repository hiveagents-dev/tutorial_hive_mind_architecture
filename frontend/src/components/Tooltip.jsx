import React, { useState, useEffect, useRef } from 'react';

/**
 * Componente de tooltip mejorado con posicionamiento inteligente
 */
export function Tooltip({ 
  children, 
  content, 
  position = 'top',
  delay = 200,
  className = ''
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState(position);
  const tooltipRef = useRef(null);
  const triggerRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      // Calcular posición para evitar overflow
      if (triggerRef.current && tooltipRef.current) {
        const triggerRect = triggerRef.current.getBoundingClientRect();
        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        let newPosition = position;

        // Ajustar horizontalmente
        if (position === 'right' && triggerRect.right + tooltipRect.width > viewportWidth) {
          newPosition = 'left';
        } else if (position === 'left' && triggerRect.left - tooltipRect.width < 0) {
          newPosition = 'right';
        }

        // Ajustar verticalmente
        if (position === 'top' && triggerRect.top - tooltipRect.height < 0) {
          newPosition = 'bottom';
        } else if (position === 'bottom' && triggerRect.bottom + tooltipRect.height > viewportHeight) {
          newPosition = 'top';
        }

        setTooltipPosition(newPosition);
      }
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  if (!content) return children;

  return (
    <span 
      className={`tooltip-container ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      ref={triggerRef}
    >
      {children}
      {isVisible && (
        <div 
          ref={tooltipRef}
          className={`tooltip tooltip-${tooltipPosition}`}
          role="tooltip"
        >
          <div className="tooltip-content">
            {content}
          </div>
          <div className="tooltip-arrow"></div>
        </div>
      )}
    </span>
  );
}

/**
 * Diccionario de tooltips para términos técnicos comunes
 */
export const TOOLTIP_DEFINITIONS = {
  'Votación Ponderada': 'Cada agente tiene un peso diferente según su especialidad. Por ejemplo, en decisiones técnicas, el Technical Lead tiene más peso que otros agentes.',
  'Consenso Probable': 'Indica que hay una alta probabilidad (>80%) de que los agentes especializados estén de acuerdo en el análisis.',
  'Consenso': 'Acuerdo entre los 6 agentes especializados del sistema. Un consenso alto indica mayor confiabilidad en los resultados.',
  'Weighted Voting': 'Mecanismo de decisión donde cada agente vota con un peso diferente según su dominio de expertise.',
  'Confidence': 'Nivel de confianza que tiene cada agente en su análisis, expresado como un porcentaje del 0 al 100%.',
  'Story Points': 'Unidad de estimación ágil que representa el esfuerzo relativo de completar una tarea, considerando complejidad, riesgo e incertidumbre.',
  'Definition of Done': 'Lista de criterios que deben cumplirse para que un ítem de trabajo se considere completo.',
  'Sprint': 'Período de tiempo fijo (típicamente 1-4 semanas) durante el cual un equipo trabaja en un conjunto de tareas.',
  'Epic': 'Grupo grande de trabajo que puede dividirse en múltiples User Stories. Representa una funcionalidad completa.',
  'User Story': 'Descripción simple de una funcionalidad desde la perspectiva del usuario, siguiendo el formato "Como [rol], quiero [acción] para [beneficio]".',
  'MoSCoW': 'Método de priorización que clasifica requisitos en: Must have (debe tener), Should have (debería tener), Could have (podría tener), Won\'t have (no tendrá).',
  'INVEST': 'Criterios para buenas User Stories: Independent (Independiente), Negotiable (Negociable), Valuable (Valiosa), Estimable (Estimable), Small (Pequeña), Testable (Testeable).',
  'NFR': 'Non-Functional Requirements: Requisitos que definen la calidad del sistema (rendimiento, seguridad, escalabilidad) en lugar de funcionalidades específicas.',
  'C4 Model': 'Modelo de arquitectura con 4 niveles: Context (contexto), Container (contenedores), Component (componentes), Code (código).',
  'WSJF': 'Weighted Shortest Job First: Método de priorización que divide el valor por el tiempo de entrega.',
};

/**
 * Componente helper para mostrar texto con tooltip automático
 */
export function SmartText({ text, className = '' }) {
  // Verificar si el texto coincide con alguna definición de tooltip
  const tooltip = TOOLTIP_DEFINITIONS[text];
  
  if (tooltip) {
    return (
      <Tooltip content={tooltip}>
        <span className={`smart-text ${className}`}>
          {text}
          <i className="fas fa-info-circle tooltip-icon-small"></i>
        </span>
      </Tooltip>
    );
  }

  return <span className={className}>{text}</span>;
}

