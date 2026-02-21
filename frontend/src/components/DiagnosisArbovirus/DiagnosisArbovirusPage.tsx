import React from 'react';
import { useDiagnosis } from './hooks/useDiagnosis';
import { formatResponseHtml } from './utils/formatters';
import { DiagnosisInputForm } from './components/DiagnosisInputForm';
import { ProbabilityChart } from './components/Charts/ProbabilityChart';
import { AlgorithmsChart } from './components/Charts/AlgorithmsChart';
import { ExperimentsPanel } from '../ExperimentsPanel/ExperimentsPanel';

export const DiagnosisArbovirusForm: React.FC = () => {
  const { form, state, actions, charts } = useDiagnosis();

  return (
    <div className="container">
      <DiagnosisInputForm
        textDescription={form.textDescription}
        setTextDescription={form.setTextDescription}
        age={form.age}
        setAge={form.setAge}
        sex={form.sex}
        setSex={form.setSex}
        loading={state.loading}
        onSubmit={actions.submitDiagnosis}
      />

      <div className="results-wrapper">
        {state.error && <div className="result-box error"><p>{state.error}</p></div>}

        {state.result && (
          <div className="result-box">
            <h3>🤖 Resultado da Análise</h3>
            <div
              dangerouslySetInnerHTML={{ __html: formatResponseHtml(state.result.friendly_response) }}
              style={{ marginBottom: '2rem' }}
            />

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
              <ProbabilityChart data={charts.diseaseChartData} />
              <AlgorithmsChart
                data={charts.modelsChartData}
                winnerModel={state.result.analysis_details.winner_model}
              />
            </div>
          </div>
        )}

        <div style={{ marginTop: '40px', textAlign: 'center' }}>
          <button
            type="button"
            onClick={() => state.setShowLab(!state.showLab)}
            style={{ background: 'transparent', border: '1px solid rgb(27, 132, 69)', color: '#aaa' }}
          >
            {state.showLab ? 'Fechar Laboratório' : '🔬 Abrir Laboratório de IA (Modo Avançado)'}
          </button>
        </div>

        {state.showLab && <ExperimentsPanel />}
      </div>
    </div>
  );
};