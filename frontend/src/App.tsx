import { useState } from "react";
import { DiagnosisArbovirusForm } from "./components/DiagnosisArbovirusForm";
import { DiagnosisGlaucomaForm } from "./components/DiagnosisGlaucomaForm";
import { DiagnosisDAppForm } from "./components/DiagnosisDAppForm";
import { LoginForm } from "./components/LoginForm";
import { Dashboard } from "./components/Dashboard"; // <--- Importado!
import ThemeToggle from './components/ThemeToggle';
import { AuthProvider, useAuth } from "./context/AuthContext";
import {
  Linkedin,
  Github,
  Globe,
  PersonCircle,
  Wallet2,
  Activity,
} from "react-bootstrap-icons";
import { FaMosquito, FaRegEye } from "react-icons/fa6";
import { VscSignOut } from "react-icons/vsc";

import "./App.css";
import { BrowserRouter } from "react-router-dom";
import { PiSignatureLight } from "react-icons/pi";
import AgentChat from "./components/AgentChat";

// 1. Adicionamos 'dashboard' aqui
type Mode = "dashboard" | "web2" | "web3" | "image";

const MainLayout = () => {
  // 2. Dashboard agora é a Home
  const [mode, setMode] = useState<Mode>("dashboard");

  const {
    user,
    isAuthenticated,
    loadingAuth,
    signOut,
    walletAddress,
    connectWallet,
  } = useAuth();

  if (loadingAuth) {
    return (
      <div
        style={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#242424",
          color: "#fff",
        }}
      >
        <h3>Carregando Sessão...</h3>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <header style={{ justifyContent: "center", padding: "2rem" }}>
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
          <img
            src="/EpiScope.png"
            alt="Logo"
            style={{ width: "40px", marginRight: "15px" }}
          />
          <h1>EpiScope AI</h1>
        </div>

        <div className="mode-selector" style={{ marginRight: "10px" }}>
          {/* 3. Botão do Dashboard */}
          <button
            onClick={() => setMode("dashboard")}
            className={mode === "dashboard" ? "active" : ""}
          >
            <Activity style={{ marginRight: 5 }} /> Dashboard
          </button>

          <button
            onClick={() => setMode("web2")}
            className={mode === "web2" ? "active" : ""}
          >
            <FaMosquito style={{ marginRight: 5 }} />
            Arboviroses
          </button>
          <button
            onClick={() => setMode("image")}
            className={mode === "image" ? "active" : ""}
          >
            <FaRegEye style={{ marginRight: 5 }} />
            Glaucoma
          </button>
          <button
            onClick={() => setMode("web3")}
            className={mode === "web3" ? "active" : ""}
          >
            <PiSignatureLight style={{ marginRight: 5 }} />
            Assinatura
          </button>
        </div>

        <div className="user-profile">
          <ThemeToggle />
          {walletAddress ? (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                background: "rgba(46, 204, 113, 0.2)",
                color: "#2ecc71",
                padding: "5px 10px",
                borderRadius: "20px",
                fontSize: "0.8rem",
                marginRight: "10px",
              }}
            >
              <Wallet2 />
              <span>
                {walletAddress.substring(0, 6)}...{walletAddress.substring(38)}
              </span>
            </div>
          ) : (
            <button
              onClick={connectWallet}
              style={{
                background: "transparent",
                border: "1px solid #f39c12",
                color: "#f39c12",
                padding: "5px 10px",
                borderRadius: "20px",
                fontSize: "0.8rem",
                marginRight: "10px",
                cursor: "pointer",
              }}
            >
              Conectar Wallet
            </button>
          )}

          <div className="user-info">
            <PersonCircle size={20} style={{ marginRight: "8px" }} />
            <span>{user?.username}</span>
          </div>
          <button onClick={signOut} className="logout-btn" title="Sair">
            <VscSignOut />
          </button>
        </div>
      </header>

      <main>
        {/* 4. Renderiza o Dashboard */}
        {mode === "dashboard" && <Dashboard />}
        {mode === "web2" && <DiagnosisArbovirusForm />}
        {mode === "web3" && <DiagnosisDAppForm />}
        {mode === "image" && <DiagnosisGlaucomaForm />}
       
      </main>

      <footer className="footer">
        <p className="footer-note">
          Desenvolvido por <span className="author">Henrique Bisneto</span>
        </p>
        <div className="social-links">
          <a href="https://linkedin.com/in/bisnet0/" target="_blank">
            <Linkedin size={22} />
          </a>
          <a href="https://github.com/bisnet0" target="_blank">
            <Github size={22} />
          </a>
          <a href="https://www.henriquebisneto.com.br/" target="_blank">
            <Globe size={22} />
          </a>
        </div>
      </footer>
       <AgentChat />
    </>
  );
};

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
