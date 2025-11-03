import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiClient } from '../api/client';

// Estado inicial
const initialState = {
  // Estado de la aplicación
  loading: false,
  error: null,
  apiStatus: 'connecting',
  
  // Configuración
  methodologies: [],
  selectedMethodology: 'scrum',
  selectedConsensusStrategy: 'weighted_voting',
  
  // Resultados
  currentAnalysis: null,
  analysisHistory: [],
  historyFromDb: [], // Historial desde la BD
  historyLoading: false,
  historyFilters: {
    limit: 50,
    offset: 0,
    methodology: null,
    success_only: false
  },
  selectedHistoryItem: null,
  
  // UI
  currentSection: 'dashboard',
  showFullContentModal: false,
  fullContentData: null,
};

// Tipos de acciones
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_API_STATUS: 'SET_API_STATUS',
  SET_METHODOLOGIES: 'SET_METHODOLOGIES',
  SET_SELECTED_METHODOLOGY: 'SET_SELECTED_METHODOLOGY',
  SET_SELECTED_CONSENSUS_STRATEGY: 'SET_SELECTED_CONSENSUS_STRATEGY',
  SET_CURRENT_ANALYSIS: 'SET_CURRENT_ANALYSIS',
  ADD_ANALYSIS_TO_HISTORY: 'ADD_ANALYSIS_TO_HISTORY',
  SET_CURRENT_SECTION: 'SET_CURRENT_SECTION',
  SHOW_FULL_CONTENT_MODAL: 'SHOW_FULL_CONTENT_MODAL',
  HIDE_FULL_CONTENT_MODAL: 'HIDE_FULL_CONTENT_MODAL',
  SET_HISTORY_LOADING: 'SET_HISTORY_LOADING',
  SET_HISTORY_FROM_DB: 'SET_HISTORY_FROM_DB',
  SET_HISTORY_FILTERS: 'SET_HISTORY_FILTERS',
  SET_SELECTED_HISTORY_ITEM: 'SET_SELECTED_HISTORY_ITEM',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ActionTypes.SET_API_STATUS:
      return { ...state, apiStatus: action.payload };
    
    case ActionTypes.SET_METHODOLOGIES:
      return { ...state, methodologies: action.payload };
    
    case ActionTypes.SET_SELECTED_METHODOLOGY:
      return { ...state, selectedMethodology: action.payload };
    
    case ActionTypes.SET_SELECTED_CONSENSUS_STRATEGY:
      return { ...state, selectedConsensusStrategy: action.payload };
    
    case ActionTypes.SET_CURRENT_ANALYSIS:
      return { ...state, currentAnalysis: action.payload };
    
    case ActionTypes.ADD_ANALYSIS_TO_HISTORY:
      return { 
        ...state, 
        analysisHistory: [action.payload, ...state.analysisHistory].slice(0, 10) // Mantener solo los últimos 10
      };

    case ActionTypes.UPDATE_CURRENT_ANALYSIS_INCREMENTAL:
      const { agent_name, content, message_type, timestamp, methodology, metadata } = action.payload;
      const newWorkerResponses = state.currentAnalysis?.worker_responses ? [...state.currentAnalysis.worker_responses] : [];
      
      // Find or create agent response
      let existingAgentIndex = newWorkerResponses.findIndex(resp => resp.agent_name === agent_name);
      if (existingAgentIndex !== -1) {
        // Update existing agent's content
        newWorkerResponses[existingAgentIndex] = {
          ...newWorkerResponses[existingAgentIndex],
          content: newWorkerResponses[existingAgentIndex].content + content, // Append content
          timestamp: timestamp,
          methodology: methodology,
          metadata: metadata,
          content_length: (newWorkerResponses[existingAgentIndex].content?.length || 0) + (content?.length || 0)
        };
      } else {
        // Add new agent response
        newWorkerResponses.push({
          agent_name: agent_name,
          confidence: 0, // Confidence will be updated with final result
          timestamp: timestamp,
          methodology: methodology,
          content: content,
          content_length: content?.length || 0,
          message_type: message_type
        });
      }

      return {
        ...state,
        currentAnalysis: {
          ...state.currentAnalysis,
          worker_responses: newWorkerResponses,
          // Initialize other fields if not present
          methodology: state.currentAnalysis?.methodology || methodology,
          timestamp: state.currentAnalysis?.timestamp || timestamp,
          execution_time: 0, // Will be updated with final result
          consensus_result: state.currentAnalysis?.consensus_result || { achieved: false, consensus_level: 0, strategy_used: '', justification: '', metadata: {} },
          coordinator_response: state.currentAnalysis?.coordinator_response || { agent_name: 'Coordinator', content: '', confidence: 0, timestamp: '', methodology: '', content_length: 0 },
          supervisor_response: state.currentAnalysis?.supervisor_response || { agent_name: 'Supervisor', content: '', confidence: 0, timestamp: '', methodology: '', content_length: 0 },
          metadata: state.currentAnalysis?.metadata || {}
        }
      };
    
    case ActionTypes.SET_CURRENT_SECTION:
      return { ...state, currentSection: action.payload };
    
    case ActionTypes.SHOW_FULL_CONTENT_MODAL:
      return { 
        ...state, 
        showFullContentModal: true, 
        fullContentData: action.payload 
      };
    
    case ActionTypes.HIDE_FULL_CONTENT_MODAL:
      return { 
        ...state, 
        showFullContentModal: false, 
        fullContentData: null 
      };
    
    case ActionTypes.SET_HISTORY_LOADING:
      return { ...state, historyLoading: action.payload };
    
    case ActionTypes.SET_HISTORY_FROM_DB:
      return { ...state, historyFromDb: action.payload, historyLoading: false };
    
    case ActionTypes.SET_HISTORY_FILTERS:
      return { ...state, historyFilters: { ...state.historyFilters, ...action.payload } };
    
    case ActionTypes.SET_SELECTED_HISTORY_ITEM:
      return { ...state, selectedHistoryItem: action.payload };
    
    default:
      return state;
  }
}

// Context
const AppContext = createContext();

// Provider
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Cargar información inicial
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      
      // Verificar estado de la API
      await apiClient.checkHealth();
      dispatch({ type: ActionTypes.SET_API_STATUS, payload: 'connected' });
      
      // Cargar metodologías
      const info = await apiClient.getInfo();
      dispatch({ type: ActionTypes.SET_METHODOLOGIES, payload: info.methodologies });
      
    } catch (error) {
      console.error('Error loading initial data:', error);
      dispatch({ type: ActionTypes.SET_API_STATUS, payload: 'error' });
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
    } finally {
      dispatch({ type: ActionTypes.SET_LOADING, payload: false });
    }
  };

  // Acciones
  const actions = {
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    
    setApiStatus: (status) => dispatch({ type: ActionTypes.SET_API_STATUS, payload: status }),
    
    setSelectedMethodology: (methodology) => 
      dispatch({ type: ActionTypes.SET_SELECTED_METHODOLOGY, payload: methodology }),
    
    setSelectedConsensusStrategy: (strategy) => 
      dispatch({ type: ActionTypes.SET_SELECTED_CONSENSUS_STRATEGY, payload: strategy }),
    
    setCurrentSection: (section) => 
      dispatch({ type: ActionTypes.SET_CURRENT_SECTION, payload: section }),
    
    showFullContentModal: (data) => 
      dispatch({ type: ActionTypes.SHOW_FULL_CONTENT_MODAL, payload: data }),
    
    hideFullContentModal: () => 
      dispatch({ type: ActionTypes.HIDE_FULL_CONTENT_MODAL }),
    
    analyzeBusinessNeed: async (businessNeed) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        dispatch({ type: ActionTypes.SET_ERROR, payload: null });
        
        const result = await apiClient.analyzeBusinessNeed({
          business_need: businessNeed,
          methodology: state.selectedMethodology,
          consensus_strategy: state.selectedConsensusStrategy,
          verbose: true,
        });
        
        dispatch({ type: ActionTypes.SET_CURRENT_ANALYSIS, payload: result });
        dispatch({ type: ActionTypes.ADD_ANALYSIS_TO_HISTORY, payload: result });
        
        return result;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    },
    
    analyzeBusinessNeedWS: (businessNeed) => {
      console.log('🔌 Iniciando analyzeBusinessNeedWS con:', businessNeed);
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      dispatch({ type: ActionTypes.SET_ERROR, payload: null });
      
      // Inicializar análisis vacío para mostrar progreso incremental
      const initial = {
        business_need: businessNeed,
        methodology: state.selectedMethodology,
        consensus_strategy: state.selectedConsensusStrategy,
        execution_time: 0,
        worker_responses: [],
        coordinator_response: null,
        supervisor_response: null,
        consensus_result: { achieved: false, consensus_level: 0, strategy_used: '', justification: '', metadata: {} },
        metadata: {},
        timestamp: new Date().toISOString(),
      };
      dispatch({ type: ActionTypes.SET_CURRENT_ANALYSIS, payload: initial });

      console.log('🔌 Conectando WebSocket...');
      const ws = apiClient.connectAnalysisWS({
        business_need: businessNeed,
        methodology: state.selectedMethodology,
        consensus_strategy: state.selectedConsensusStrategy,
        verbose: true,
        onOpen: () => {
          console.log('🔌 WebSocket conectado para análisis');
        },
        onAgentUpdate: (msg) => {
          console.log('📨 Mensaje de agente recibido:', msg);
          try {
            if (!msg) return;
            
            // Actualizar análisis incremental usando el reducer existente
            dispatch({ type: ActionTypes.UPDATE_CURRENT_ANALYSIS_INCREMENTAL, payload: msg });
          } catch (e) {
            console.error('Error procesando mensaje de agente:', e);
          }
        },
        onFinal: (finalData) => {
          console.log('✅ Análisis completado:', finalData);
          dispatch({ type: ActionTypes.SET_CURRENT_ANALYSIS, payload: finalData });
          dispatch({ type: ActionTypes.ADD_ANALYSIS_TO_HISTORY, payload: finalData });
          dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        },
        onError: (message) => {
          console.error('❌ Error en WebSocket:', message);
          
          // Solo usar REST como último recurso si WebSocket falla completamente
          console.log('🔄 WebSocket falló, intentando REST como último recurso...');
          
          apiClient.analyzeBusinessNeed({
            business_need: businessNeed,
            methodology: state.selectedMethodology,
            consensus_strategy: state.selectedConsensusStrategy,
            verbose: true,
          })
          .then(result => {
            console.log('✅ Fallback REST exitoso');
            dispatch({ type: ActionTypes.SET_CURRENT_ANALYSIS, payload: result });
            dispatch({ type: ActionTypes.ADD_ANALYSIS_TO_HISTORY, payload: result });
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
          })
          .catch(error => {
            console.error('❌ Fallback REST también falló:', error);
            dispatch({ type: ActionTypes.SET_ERROR, payload: `Error en análisis: ${error.message}` });
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
          });
        },
        onClose: () => {
          console.log('🔌 WebSocket cerrado');
          dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        }
      });
      
      console.log('🔌 WebSocket creado:', ws);
      return ws; // Retornar instancia para control externo
    },
    
    runExampleAnalysis: async () => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        dispatch({ type: ActionTypes.SET_ERROR, payload: null });
        
        const result = await apiClient.runExampleAnalysis();
        
        dispatch({ type: ActionTypes.SET_CURRENT_ANALYSIS, payload: result });
        dispatch({ type: ActionTypes.ADD_ANALYSIS_TO_HISTORY, payload: result });
        
        return result;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    },
    
    refreshApiStatus: async () => {
      try {
        await apiClient.checkHealth();
        dispatch({ type: ActionTypes.SET_API_STATUS, payload: 'connected' });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_API_STATUS, payload: 'error' });
      }
    },
    
    loadHistoryFromDb: async (filters = {}) => {
      try {
        dispatch({ type: ActionTypes.SET_HISTORY_LOADING, payload: true });
        const updatedFilters = { ...state.historyFilters, ...filters };
        dispatch({ type: ActionTypes.SET_HISTORY_FILTERS, payload: updatedFilters });
        
        const result = await apiClient.getAnalysisHistory(updatedFilters);
        dispatch({ type: ActionTypes.SET_HISTORY_FROM_DB, payload: result.analyses || [] });
        
        return result;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: `Error cargando historial: ${error.message}` });
        dispatch({ type: ActionTypes.SET_HISTORY_LOADING, payload: false });
        throw error;
      }
    },
    
    loadAnalysisById: async (analysisId) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        const result = await apiClient.getAnalysisById(analysisId);
        
        if (result.analysis) {
          dispatch({ type: ActionTypes.SET_SELECTED_HISTORY_ITEM, payload: result.analysis });
          return result.analysis;
        }
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: `Error cargando análisis: ${error.message}` });
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    },
  };

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook para usar el contexto
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
