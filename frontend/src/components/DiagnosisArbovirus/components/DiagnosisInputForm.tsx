import React from 'react';

interface FormProps {
  textDescription: string;
  setTextDescription: (val: string) => void;
  age: number | '';
  setAge: (val: number | '') => void;
  sex: string;
  setSex: (val: string) => void;
  loading: boolean;
  onSubmit: (e: React.FormEvent) => void;
}

export const DiagnosisInputForm: React.FC<FormProps> = ({
  textDescription, setTextDescription, age, setAge, sex, setSex, loading, onSubmit
}) => (
  <form onSubmit={onSubmit} className="form-section">
    <h2>1. Análise Clínica (Arboviroses)</h2>
    <div className="form-group">
      <label>Descreva seus sintomas:</label>
      <textarea
        value={textDescription}
        onChange={(e) => setTextDescription(e.target.value)}
        required
        placeholder="Ex: Febre alta, dor atrás dos olhos..."
      />
    </div>
    <div className="form-group">
      <label>Idade:</label>
      <input
        type="number"
        value={age}
        onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))}
        min="0"
        required
      />
    </div>
    <div className="form-group">
      <label>Sexo:</label>
      <select value={sex} onChange={(e) => setSex(e.target.value)}>
        <option value="M">Masculino</option>
        <option value="F">Feminino</option>
      </select>
    </div>
    <button type="submit" disabled={loading}>
      {loading ? 'Analisando...' : 'Rodar Diagnóstico'}
    </button>
  </form>
);