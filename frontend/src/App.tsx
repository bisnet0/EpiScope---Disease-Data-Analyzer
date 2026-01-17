import { useState } from 'react';
import { DiagnosisArbovirusForm } from './components/DiagnosisArbovirusForm';
import { DiagnosisGlaucomaForm } from './components/DiagnosisGlaucomaForm';
import { DiagnosisDAppForm } from './components/DiagnosisDAppForm';
import { LoginForm } from './components/LoginForm';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Linkedin, Github, Globe, BoxArrowRight, PersonCircle, Wallet2 } from 'react-bootstrap-icons';
import './App.css';
import { BrowserRouter } from 'react-router-dom';

type Mode = 'web2' | 'web3' | 'image';

const MainLayout = () => {
  const [mode, setMode] = useState<Mode>('web2');

  const { user, isAuthenticated, loadingAuth, signOut, walletAddress, connectWallet } = useAuth();


  if (loadingAuth) {
    return (
      <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#242424', color: '#fff' }}>
        <h3>Carregando Sessão...</h3>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <header style={{ justifyContent: 'center', padding: '2rem' }}>
          <img src="/EpiScope.png" alt="Logo" style={{ width: "150px" }} />
        </header>
        <LoginForm />
      </>
    );
  }

  return (
    <>
      <header className="dashboard-header">
        <div className="header-left">
          <img src="/EpiScope.png" alt="Logo" style={{ width: '40px', marginRight: '15px' }} />
          <h1>EpiScope AI</h1>
        </div>

        <div className="user-profile">
          {/* --- LÓGICA DA WALLET ADICIONADA AQUI --- */}
          {walletAddress ? (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '5px',
              background: 'rgba(46, 204, 113, 0.2)', color: '#2ecc71',
              padding: '5px 10px', borderRadius: '20px', fontSize: '0.8rem', marginRight: '10px'
            }}>
              <Wallet2 />
              {/* Mostra começo...fim do endereço */}
              <span>{walletAddress.substring(0, 6)}...{walletAddress.substring(38)}</span>
            </div>
          ) : (
            <button
              onClick={connectWallet}
              style={{
                background: 'transparent', border: '1px solid #f39c12', color: '#f39c12',
                padding: '5px 10px', borderRadius: '20px', fontSize: '0.8rem', marginRight: '10px', cursor: 'pointer'
              }}
            >
              Conectar Wallet
            </button>
          )}
          {/* --------------------------------------- */}

          <div className="user-info">
            <PersonCircle size={20} style={{ marginRight: '8px' }} />
            <span>{user?.username}</span>
          </div>
          <button onClick={signOut} className="logout-btn" title="Sair">
            <BoxArrowRight size={20} />
          </button>
        </div>

        <div className="mode-selector">
          <button onClick={() => setMode('web2')} className={mode === 'web2' ? 'active' : ''}>
            Arboviroses
          </button>
          <button onClick={() => setMode('web3')} className={mode === 'web3' ? 'active' : ''}>
           Assinatura DApp
          </button>
          <button onClick={() => setMode('image')} className={mode === 'image' ? 'active' : ''}>
            Glaucoma
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
    <BrowserRouter>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;