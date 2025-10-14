// frontend/src/App.tsx
import { useState } from 'react';
import { DiagnosisForm } from './components/DiagnosisForm';
import { DiagnosisDAppForm } from './components/DiagnosisDAppForm';
import './App.css';

type Mode = 'web2' | 'web3';

function App() {
  const [mode, setMode] = useState<Mode>('web2');

  return (
    <>
      <header>
        <h1>EpiScope - Analisador de Doenças</h1>
        <div className="mode-selector">
          <button onClick={() => setMode('web2')} className={mode === 'web2' ? 'active' : ''}>Análise Rápida (Web2)</button>
          <button onClick={() => setMode('web3')} className={mode === 'web3' ? 'active' : ''}>Análise Verificável (Web3)</button>
        </div>
      </header>
      <main>
        {mode === 'web2' ? <DiagnosisForm /> : <DiagnosisDAppForm />}
      </main>
    </>
  );
}

export default App;