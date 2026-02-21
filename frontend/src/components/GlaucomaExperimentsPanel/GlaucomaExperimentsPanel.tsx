import React from 'react';
import { useGlaucomaExperiments } from './hooks/useGlaucomaExperiments';
import { GlaucomaControls } from './components/GlaucomaControls';
import { GlaucomaEvolutionChart } from './components/GlaucomaEvolutionChart';
import Toast from '../Toast'; // Ajuste o caminho

export const GlaucomaExperimentsPanel: React.FC = () => {
  const { state, setters, actions } = useGlaucomaExperiments();

  return (
    <div style={{ marginTop: '30px', borderTop: '1px solid #444', paddingTop: '20px' }}>
      
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#e91e63' }}>
        👁️ Laboratório de Visão Computacional 
        <span style={{ fontSize: '0.8rem', background: '#333', padding: '2px 8px', borderRadius: '4px', color: '#fff' }}>
          HÍBRIDO
        </span>
      </h3>

      <p style={{ color: '#aaa', fontSize: '0.9rem', marginBottom: '20px' }}>
        Otimize o classificador final (Top-Layer) que processa as características extraídas pela CNN.
      </p>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <GlaucomaControls state={state} setters={setters} actions={actions} />
        <GlaucomaEvolutionChart history={state.evolutionHistory} modelType={state.modelType} />
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