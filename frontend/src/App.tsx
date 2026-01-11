import { useState } from 'react';
import { DiagnosisArbovirusForm } from './components/DiagnosisArbovirusForm'; // Novo
import { DiagnosisGlaucomaForm } from './components/DiagnosisGlaucomaForm';   // Novo
import { DiagnosisDAppForm } from './components/DiagnosisDAppForm';
import { LoginForm } from './components/LoginForm';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Linkedin, Github, Globe, BoxArrowRight, PersonCircle } from 'react-bootstrap-icons';
import './App.css';

type Mode = 'web2' | 'web3' | 'image';

const MainLayout = () => {
  const [mode, setMode] = useState<Mode>('web2');
  const { user, isAuthenticated, signOut } = useAuth();

  if (!isAuthenticated) {
    return (
      <>
        <header style={{justifyContent: 'center', padding: '2rem'}}>
           <img src="/EpiScope.png" alt="Logo" style={{width:"150px"}}/>
        </header>
        <LoginForm />
      </>
    );
  }

  return (
    <>
      <header className="dashboard-header">
        <div className="header-left">
            <img src="/EpiScope.png" alt="Logo" style={{width: '40px', marginRight: '15px'}}/>
            <h1>EpiScope AI</h1>
        </div>
        <div className="user-profile">
            <div className="user-info">
                <PersonCircle size={20} style={{marginRight: '8px'}}/>
                <span>{user?.username}</span>
            </div>
            <button onClick={signOut} className="logout-btn" title="Sair">
                <BoxArrowRight size={20} />
            </button>
        </div>
        <div className="mode-selector">
          <button onClick={() => setMode('web2')} className={mode === 'web2' ? 'active' : ''}>
            Arboviroses (Multi-Model)
          </button>
          <button onClick={() => setMode('web3')} className={mode === 'web3' ? 'active' : ''}>
            Web3 (Cartesi)
          </button>
          <button onClick={() => setMode('image')} className={mode === 'image' ? 'active' : ''}>
            Glaucoma (CNN)
          </button>
        </div>
      </header>

      <main>
        {mode === 'web2' && <DiagnosisArbovirusForm />}
        {mode === 'web3' && <DiagnosisDAppForm />}
        {mode === 'image' && <DiagnosisGlaucomaForm />}
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