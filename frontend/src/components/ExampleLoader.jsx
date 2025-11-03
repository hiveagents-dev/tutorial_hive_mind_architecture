import React, { useState } from 'react';
import { ActionButton } from './ActionButton';

const EXAMPLES = [
  {
    id: 'ecommerce',
    title: 'E-commerce B2B',
    description: 'Plataforma de comercio electrónico para empresas',
    businessNeed: 'Necesitamos una plataforma de e-commerce B2B que permita a las empresas gestionar catálogos de productos, procesar pedidos a gran escala, integrar con sistemas ERP existentes y ofrecer descuentos por volumen. La plataforma debe soportar múltiples monedas, diferentes métodos de pago y tener un sistema de aprobación de pedidos por niveles.',
    methodology: 'scrum',
    consensus: 'weighted_voting'
  },
  {
    id: 'fintech',
    title: 'Fintech Wallet',
    description: 'Wallet digital para pagos internacionales',
    businessNeed: 'Desarrollar una wallet digital que permita a usuarios realizar pagos internacionales en tiempo real, con soporte para múltiples criptomonedas y monedas fiat. Debe incluir KYC/AML, conversión automática de divisas, y integración con bancos tradicionales para depósitos y retiros.',
    methodology: 'scrum',
    consensus: 'weighted_voting'
  },
  {
    id: 'healthcare',
    title: 'Sistema de Salud',
    description: 'Plataforma de gestión hospitalaria',
    businessNeed: 'Crear un sistema integral de gestión hospitalaria que incluya gestión de pacientes, historiales médicos digitales, programación de citas, gestión de inventario médico, facturación y reportes. Debe cumplir con regulaciones HIPAA y permitir integración con equipos médicos.',
    methodology: 'safe',
    consensus: 'majority'
  },
  {
    id: 'logistics',
    title: 'Logística Inteligente',
    description: 'Sistema de optimización de rutas',
    businessNeed: 'Desarrollar un sistema de optimización de rutas de entrega que use IA para calcular las rutas más eficientes, considere tráfico en tiempo real, restricciones de vehículos, horarios de entrega y costos de combustible. Debe integrar con GPS y sistemas de gestión de flotas.',
    methodology: 'kanban',
    consensus: 'confidence_threshold'
  }
];

export function ExampleLoader({ onLoadExample, disabled = false }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedExample, setSelectedExample] = useState(null);

  const handleLoadExample = (example) => {
    setSelectedExample(example);
    onLoadExample(example);
    setIsOpen(false);
  };

  return (
    <div className="example-loader">
      <ActionButton
        type="secondary"
        size="medium"
        icon="fas fa-magic"
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className="example-trigger"
      >
        Cargar Ejemplo
      </ActionButton>
      
      {isOpen && (
        <div className="example-dropdown">
          <div className="example-header">
            <h4>Selecciona un ejemplo</h4>
            <button 
              className="close-btn"
              onClick={() => setIsOpen(false)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          <div className="example-list">
            {EXAMPLES.map((example) => (
              <div 
                key={example.id}
                className={`example-item ${selectedExample?.id === example.id ? 'selected' : ''}`}
                onClick={() => handleLoadExample(example)}
              >
                <div className="example-title">
                  <i className="fas fa-lightbulb"></i>
                  {example.title}
                </div>
                <div className="example-description">
                  {example.description}
                </div>
                <div className="example-meta">
                  <span className="methodology">
                    <i className="fas fa-project-diagram"></i>
                    {example.methodology.toUpperCase()}
                  </span>
                  <span className="consensus">
                    <i className="fas fa-handshake"></i>
                    {example.consensus.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
