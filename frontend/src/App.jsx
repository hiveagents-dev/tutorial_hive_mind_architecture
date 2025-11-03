import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Sidebar } from './components/Sidebar';
import { Breadcrumbs } from './components/Breadcrumbs';

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

function AppContent() {
  const { state, actions } = useApp();

  const navigationItems = [
    { id: 'dashboard', icon: 'fas fa-tachometer-alt', label: 'Dashboard' },
    { id: 'analyze', icon: 'fas fa-search', label: 'Analizar' },
    { id: 'history', icon: 'fas fa-history', label: 'Historial' },
    { id: 'settings', icon: 'fas fa-cog', label: 'Configuración' },
  ];

  const renderCurrentSection = () => {
    switch (state.currentSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'analyze':
        return <Analyze />;
      case 'history':
        return <History />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <i className="fas fa-brain"></i>
            <h1>HiveMind Architecture</h1>
          </div>
          <div className="header-actions">
            <div className={`api-status ${state.apiStatus}`}>
              <i className="fas fa-circle"></i>
              <span>
                {state.apiStatus === 'connected' ? 'Conectado' : 
                 state.apiStatus === 'error' ? 'Desconectado' : 'Conectando...'}
              </span>
            </div>
            <button 
              className="btn btn-secondary" 
              onClick={actions.refreshApiStatus}
              disabled={state.loading}
            >
              <i className="fas fa-sync-alt"></i>
              Actualizar
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        <Sidebar 
          navigationItems={navigationItems}
          currentSection={state.currentSection}
          onSectionChange={actions.setCurrentSection}
        />

        <div className="content">
          <Breadcrumbs />
          {renderCurrentSection()}
        </div>
      </main>

      {/* Loading Overlay */}
      {state.loading && (
        <div className="loading-overlay" data-testid="loading-overlay" style={{ display: 'block', position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999 }}>
          <div className="loading-spinner" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', color: 'white' }}>
            <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', marginBottom: '1rem' }}></i>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Procesando...</div>
          </div>
        </div>
      )}

      {/* Error Toast */}
      {state.error && (
        <div className="error-toast">
          <i className="fas fa-exclamation-circle"></i>
          <span>{state.error}</span>
          <button 
            className="toast-close"
            onClick={() => actions.setError(null)}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}
    </div>
  );
}

export default App;