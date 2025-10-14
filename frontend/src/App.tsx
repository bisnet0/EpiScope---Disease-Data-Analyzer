// frontend/src/App.tsx
import { DiagnosisForm } from './components/DiagnosisForm';
import './App.css';

function App() {
  return (
    <>
      <header>
        <h1>EpiScope - Analisador de Doenças</h1>
      </header>
      <main>
        <DiagnosisForm />
      </main>
    </>
  );
}

export default App;