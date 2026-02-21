import React from "react";
import { useGlaucoma } from "./hooks/useGlaucoma";
import { GlaucomaInputForm } from "./components/GlaucomaInputForm";
import { GlaucomaResultChart } from "./components/GlaucomaResultChart";
import { GlaucomaExperimentsPanel } from "../GlaucomaExperimentsPanel"; // Ajuste o caminho

export const DiagnosisGlaucomaForm: React.FC = () => {
  const { state, actions, charts } = useGlaucoma();

  return (
    <div className="container">
      
      <GlaucomaInputForm
        previewUrl={state.previewUrl}
        loading={state.loading}
        onImageChange={actions.handleImageChange}
        onSubmit={actions.submitDiagnosis}
      />

      <div className="results-wrapper">
        {state.error && <div className="result-box error"><p>{state.error}</p></div>}
        
        {state.result && (
          <GlaucomaResultChart 
            result={state.result} 
            chartData={charts.chartData} 
          />
        )}
      </div>

      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => state.setShowLab(!state.showLab)}
          style={{ 
            background: 'transparent', 
            border: '1px solid #e91e63', 
            color: '#e91e63', 
            padding: '8px 16px', 
            borderRadius: '4px', 
            cursor: 'pointer' 
          }}
        >
          {state.showLab ? 'Fechar Lab' : '👁️ Abrir Lab de Visão Computacional (AG)'}
        </button>
      </div>

      {state.showLab && <GlaucomaExperimentsPanel />}
    </div>
  );
};