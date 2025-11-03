import React, { useState, useEffect } from 'react';

export function Sidebar({ navigationItems, currentSection, onSectionChange }) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    // Recuperar estado desde localStorage
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved === 'true';
  });

  useEffect(() => {
    // Guardar estado en localStorage
    localStorage.setItem('sidebarCollapsed', String(isCollapsed));
  }, [isCollapsed]);

  const handleToggle = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!isCollapsed && (
          <div className="sidebar-logo">
            <i className="fas fa-brain"></i>
            <span>HiveMind</span>
          </div>
        )}
        <button 
          className="sidebar-toggle" 
          onClick={handleToggle}
          title={isCollapsed ? 'Expandir' : 'Colapsar'}
          aria-label={isCollapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
        >
          <i className={`fas fa-chevron-${isCollapsed ? 'right' : 'left'}`}></i>
        </button>
      </div>
      
      <nav className="nav">
        <ul className="nav-list">
          {navigationItems.map(item => (
            <li 
              key={item.id}
              className={`nav-item ${currentSection === item.id ? 'active' : ''}`}
              onClick={() => onSectionChange(item.id)}
              title={isCollapsed ? item.label : undefined}
            >
              <i className={item.icon}></i>
              {!isCollapsed && <span>{item.label}</span>}
            </li>
          ))}
        </ul>
      </nav>
      
      {!isCollapsed && (
        <div className="sidebar-footer">
          <div className="sidebar-info">
            <i className="fas fa-info-circle"></i>
            <small>Versión 1.0.0</small>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;

