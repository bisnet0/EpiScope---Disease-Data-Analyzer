import { useState } from 'react';
import { DiagnosisForm } from './components/DiagnosisForm';
import { DiagnosisDAppForm } from './components/DiagnosisDAppForm';
import { ImageDiagnosisForm } from './components/ImageDiagnosisForm';
import { Linkedin, Github, Globe } from 'react-bootstrap-icons';
import './App.css';

type Mode = 'web2' | 'web3' | 'image';

function App() {
  const [mode, setMode] = useState<Mode>('web2');

  return (
    <>
      <header>
        <h1>EpiScope - Analisador de Doenças</h1>
        <div className="mode-selector">
          <button onClick={() => setMode('web2')} className={mode === 'web2' ? 'active' : ''}>
            Análise Rápida (ML + IA)
          </button>
          <button onClick={() => setMode('web3')} className={mode === 'web3' ? 'active' : ''}>
            Análise Verificável (ML + DApp)
          </button>
          <button onClick={() => setMode('image')} className={mode === 'image' ? 'active' : ''}>
            Análise de Imagem (CNN + IA)
          </button>
        </div>
      </header>

      <main>
        {mode === 'web2' && <DiagnosisForm />}
        {mode === 'web3' && <DiagnosisDAppForm />}
        {mode === 'image' && <ImageDiagnosisForm />}
      </main>

      <footer className="footer">
        <p className="footer-note">
          Desenvolvido por <span className="author">Henrique Bisneto</span>
        </p>
        <div className="social-links">
          <a href="https://linkedin.com/in/bisnet0/" target="_blank" rel="noopener noreferrer">
            <Linkedin size={22} />
          </a>
          <a href="https://github.com/bisnet0" target="_blank" rel="noopener noreferrer">
            <Github size={22} />
          </a>
          <a href="https://www.henriquebisneto.com.br/" target="_blank" rel="noopener noreferrer">
            <Globe size={22} />
          </a>
        </div>
        <p className="footer-handle">@bisnet0</p>
      </footer>
    </>
  );
}

export default App;
