import React from 'react';

interface Props {
  state: any;
  setters: any;
  actions: any;
}

export const ControlsColumn: React.FC<Props> = ({ state, setters, actions }) => {
  return (
    <div style={{ flex: '1 1 300px', background: '#1e1e1e', padding: '20px', borderRadius: '8px' }}>
      
      {/* Botões de IA */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          onClick={actions.handleSuggestParams}
          disabled={state.loading}
          title="Buscar melhor histórico"
          style={{ flex: 1, background: 'linear-gradient(-45deg, #101bec80, #1db731e5)', border: '1px solid #555', color: '#fff', padding: '10px', cursor: 'pointer', borderRadius: '6px' }}
        >
          🔮 Oráculo
        </button>
        <button
          onClick={actions.handleRunEvolution}
          disabled={state.loading}
          title="Rodar Algoritmo Genético"
          style={{ flex: 1, background: 'linear-gradient(45deg, #8e44ad, #c0392b)', border: 'none', color: '#fff', padding: '10px', cursor: 'pointer', borderRadius: '6px', fontWeight: 'bold' }}
        >
          🧬 Evoluir
        </button>
      </div>

      <div style={{ marginTop: '15px', borderTop: '1px solid #333', paddingTop: '10px' }}>
        <button
          onClick={() => setters.setShowAdvancedGA(!state.showAdvancedGA)}
          style={{ background: 'none', border: 'none', color: '#8e44ad', fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', padding: 0 }}
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
            <small style={{ color: '#666', fontSize: '0.7rem' }}>Atenção: Aumentar População/Gerações aumenta o tempo de processamento.</small>
          </div>
        )}
      </div>

      {/* Form Manual */}
      <div className="form-group">
        <label>Algoritmo:</label>
        <select value={state.modelType} onChange={e => setters.setModelType(e.target.value)}>
          <option value="xgboost">XGBoost</option>
          <option value="random_forest">Random Forest</option>
          <option value="decision_tree">Decision Tree</option>
        </select>
      </div>

      <div className="form-group">
        <label>Profundidade Máxima (Max Depth): {state.maxDepth}</label>
        <input type="range" min="1" max="50" value={state.maxDepth} onChange={e => setters.setMaxDepth(Number(e.target.value))} />
      </div>

      {state.modelType !== 'decision_tree' && (
        <div className="form-group">
          <label>Nº Estimadores (Árvores): {state.nEstimators}</label>
          <input type="range" min="10" max="1000" step="10" value={state.nEstimators} onChange={e => setters.setNEstimators(Number(e.target.value))} />
        </div>
      )}

      {state.modelType === 'xgboost' && (
        <div className="form-group">
          <label>Taxa de Aprendizado (LR): {state.learningRate}</label>
          <input type="range" min="0.001" max="1.0" step="0.001" value={state.learningRate} onChange={e => setters.setLearningRate(Number(e.target.value))} />
        </div>
      )}

      <button
        onClick={actions.handleRunExperiment}
        disabled={state.loading}
        style={{ width: '100%', marginTop: '15px', background: state.loading ? '#555' : '#2ecc71', color: '#000', fontWeight: 'bold', padding: '12px', border: 'none', borderRadius: '6px', cursor: state.loading ? 'wait' : 'pointer' }}
      >
        {state.loading ? state.loadingMessage || 'Processando...' : '🧪 Rodar Teste Único'}
      </button>
    </div>
  );
};