import React from 'react';
import { useApp } from '../context/AppContext';

const SECTION_LABELS = {
  dashboard: 'Dashboard',
  analyze: 'Analizar',
  history: 'Historial',
  settings: 'Configuración'
};

const SECTION_ICONS = {
  dashboard: 'fas fa-tachometer-alt',
  analyze: 'fas fa-search',
  history: 'fas fa-history',
  settings: 'fas fa-cog'
};

export function Breadcrumbs({ items = [] }) {
  const { state } = useApp();
  
  // Construir breadcrumbs automáticamente desde el estado
  const breadcrumbs = React.useMemo(() => {
    const crumbs = [
      { label: 'Inicio', icon: 'fas fa-home', section: 'dashboard', isRoot: true }
    ];
    
    // Agregar sección actual
    if (state.currentSection && state.currentSection !== 'dashboard') {
      crumbs.push({
        label: SECTION_LABELS[state.currentSection] || state.currentSection,
        icon: SECTION_ICONS[state.currentSection] || 'fas fa-circle',
        section: state.currentSection
      });
    }
    
    // Agregar items personalizados si se proporcionan
    if (items.length > 0) {
      crumbs.push(...items);
    }
    
    // Agregar análisis actual si existe
    if (state.currentAnalysis) {
      crumbs.push({
        label: `Análisis ${state.currentAnalysis.id || 'Actual'}`,
        icon: 'fas fa-file-alt',
        isAnalysis: true
      });
    }
    
    return crumbs;
  }, [state.currentSection, state.currentAnalysis, items]);

  if (breadcrumbs.length <= 1) {
    return null; // No mostrar breadcrumbs si solo hay un nivel
  }

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;
          const isClickable = !isLast && crumb.section;
          
          return (
            <li key={index} className="breadcrumb-item">
              {isClickable ? (
                <a 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    // Aquí se podría navegar si implementamos navegación programática
                  }}
                  className="breadcrumb-link"
                >
                  <i className={crumb.icon}></i>
                  <span>{crumb.label}</span>
                </a>
              ) : (
                <span className="breadcrumb-current">
                  <i className={crumb.icon}></i>
                  <span>{crumb.label}</span>
                </span>
              )}
              {!isLast && (
                <i className="fas fa-chevron-right breadcrumb-separator" aria-hidden="true"></i>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default Breadcrumbs;

