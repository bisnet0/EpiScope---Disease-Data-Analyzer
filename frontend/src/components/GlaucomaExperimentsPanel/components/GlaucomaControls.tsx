import React from 'react';

interface Props {
  state: any;
  setters: any;
  actions: any;
}

export const GlaucomaControls: React.FC<Props> = ({ state, setters, actions }) => {
  return (
    <div style={{ flex: '1 1 300px', background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
      <div className="form-group">
        <label>Classificador Final (Head):</label>
        <select value={state.modelType} onChange={e => setters.setModelType(e.target.value)}>
          <option value="xgboost">XGBoost (Gradient Boosting)</option>
          <option value="random_forest">Random Forest</option>
          <option value="decision_tree">Decision Tree</option>
        </select>
      </div>

      <div style={{ marginTop: '15px', borderTop: '1px solid #333', paddingTop: '10px', marginBottom: '15px' }}>
        <button
          onClick={() => setters.setShowAdvancedGA(!state.showAdvancedGA)}
          style={{ background: 'none', border: 'none', color: '#e91e63', fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', padding: 0 }}
        >
          {state.showAdvancedGA ? '▼ Ocultar Config Genética' : '▶ Configurar Algoritmo Genético'}
        </button>

        {state.showAdvancedGA && (
          <div style={{ marginTop: '10px', background: '#252525', padding: '10px', borderRadius: '6px' }}>
            <div className="form-group">
              <label style={{ fontSize: '0.8rem' }}>Gerações: {state.generations}</label>
              <input type="range" min="3" max="20" value={state.generations} onChange={e => setters.setGenerations(Number(e.target.value))} style={{ height: '4px' }} />
            </div>
            <div className="form-group">
              <label style={{ fontSize: '0.8rem' }}>População: {state.popSize}</label>
              <input type="range" min="5" max="50" value={state.popSize} onChange={e => setters.setPopSize(Number(e.target.value))} style={{ height: '4px' }} />
            </div>
            <div className="form-group">
              <label style={{ fontSize: '0.8rem' }}>Taxa de Mutação: {Math.round(state.mutationRate * 100)}%</label>
              <input type="range" min="0.01" max="0.5" step="0.01" value={state.mutationRate} onChange={e => setters.setMutationRate(Number(e.target.value))} style={{ height: '4px' }} />
            </div>
          </div>
        )}
      </div>

      {/* Resultados em ReadOnly */}
      <div style={{ opacity: 0.6, pointerEvents: 'none' }}>
        <div className="form-group">
          <label>Profundidade Resultante: {state.maxDepth}</label>
          <input type="range" value={state.maxDepth} readOnly />
        </div>
        {state.modelType !== 'decision_tree' && (
          <div className="form-group">
            <label>Estimadores Resultantes: {state.nEstimators}</label>
            <input type="range" value={state.nEstimators} readOnly />
          </div>
        )}
      </div>

      <button
        onClick={actions.handleRunEvolution}
        disabled={state.loading}
        style={{
          width: '100%', marginTop: '20px',
          background: state.loading ? '#555' : 'linear-gradient(45deg, #e91e63, #9b59b6)',
          color: '#fff', fontWeight: 'bold', padding: '12px', border: 'none', borderRadius: '6px', cursor: 'pointer'
        }}
      >
        {state.loading ? '🧬 Evoluindo Rede...' : '🧬 Iniciar Algoritmo Genético'}
      </button>
    </div>
  );
};