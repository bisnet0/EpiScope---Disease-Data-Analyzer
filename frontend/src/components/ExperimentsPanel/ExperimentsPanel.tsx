import React from 'react';
import { useExperiments } from './hooks/useExperiments';
import { ControlsColumn } from './components/ControlsColumn';
import { ChartsColumn } from './components/ChartsColumn';
import Toast from '../Toast/Toast';

export const ExperimentsPanel: React.FC = () => {
  const { state, setters, actions } = useExperiments();

  return (
    <div style={{ marginTop: '30px', borderTop: '1px solid #444', paddingTop: '20px' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        🧪 Laboratório de Hiperparâmetros 
        <span style={{ fontSize: '0.8rem', background: '#646cff', padding: '2px 8px', borderRadius: '4px' }}>
          MODO AVANÇADO
        </span>
      </h3>

      <p style={{ color: '#888', fontSize: '0.9rem', marginBottom: '20px' }}>
        Utilize Algoritmos Genéticos para encontrar a configuração perfeita ou teste manualmente.
      </p>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <ControlsColumn state={state} setters={setters} actions={actions} />
        <ChartsColumn 
          viewMode={state.viewMode} 
          setViewMode={setters.setViewMode}
          manualHistory={state.manualHistory}
          evolutionHistory={state.evolutionHistory}
        />
      </div>

      {state.toast && (
        <Toast 
          type={state.toast.type} 
          message={state.toast.message} 
          onClose={setters.closeToast} 
          title={state.toast.title} 
        />
      )}
    </div>
  );
};