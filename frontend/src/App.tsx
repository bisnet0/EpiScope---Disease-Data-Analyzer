// src/App.tsx
import { useState } from 'react';
import { DiagnosisForm } from './components/DiagnosisForm';
import { DiagnosisDAppForm } from './components/DiagnosisDAppForm';
import { ImageDiagnosisForm } from './components/ImageDiagnosisForm';
import { LoginForm } from './components/LoginForm'; // Importar
import { AuthProvider, useAuth } from './context/AuthContext'; // Importar
import { Linkedin, Github, Globe, BoxArrowRight, PersonCircle } from 'react-bootstrap-icons';
import './App.css';

type Mode = 'web2' | 'web3' | 'image';

// Componente interno para acessar o hook useAuth
const MainLayout = () => {
  const [mode, setMode] = useState<Mode>('web2');
  const { user, isAuthenticated, signOut } = useAuth();

  // Se não estiver autenticado, mostra Login
  if (!isAuthenticated) {
    return (
      <>
        <header style={{ justifyContent: 'center' }}>
          <img src="/EpiScope.png" alt="EpiScope Logo" className="logo" style={{ width: "150px" }} />
        </header>
        <LoginForm />
      </>
    );
  }

  // Se estiver autenticado, mostra o Dashboard
  return (
    <>
      <header className="dashboard-header">
        <div className="header-left">
          <img src="/EpiScope.png" alt="Logo" className="logo-small" style={{ width: '80px', marginRight: '15px' }} />
          <h1>EpiScope - Analisador de Doenças</h1>
        </div>

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

        <div className="user-profile">
          <div className="user-info">
            <PersonCircle size={20} style={{ marginRight: '8px' }} />
            <span>Olá, {user?.username}</span>
          </div>
          <button onClick={signOut} className="logout-btn" title="Sair">
            <BoxArrowRight size={20} />
          </button>
        </div>
      </header>

      <main className="app-main">
        {mode === 'web2' && <DiagnosisForm />}
        {mode === 'web3' && <DiagnosisDAppForm />}
        {mode === 'image' && <ImageDiagnosisForm />}
      </main>

      <footer className="footer">
        <p className="footer-note">Desenvolvido por <span className="author">Henrique Bisneto</span></p>
        <div className="social-links">
          <a href="https://linkedin.com/in/bisnet0/" target="_blank"><Linkedin size={22} /></a>
          <a href="https://github.com/bisnet0" target="_blank"><Github size={22} /></a>
          <a href="https://www.henriquebisneto.com.br/" target="_blank"><Globe size={22} /></a>
        </div>
      </footer>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;