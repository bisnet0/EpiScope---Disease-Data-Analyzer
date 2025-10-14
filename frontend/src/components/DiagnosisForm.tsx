// frontend/src/components/DiagnosisForm.tsx
import React, { useState } from 'react';

// Definindo a estrutura da resposta da API para o TypeScript
interface ApiResponse {
    friendly_response: string;
    analysis_details: {
        probabilities: {
            [key: string]: number;
        };
    };
}

export const DiagnosisForm: React.FC = () => {
    // Estados para controlar os campos do formulário
    const [textDescription, setTextDescription] = useState('');
    const [age, setAge] = useState<number | ''>('');
    const [sex, setSex] = useState('M');
    const [criteriaCode, setCriteriaCode] = useState(2);

    // Estados para controlar o resultado da API
    const [result, setResult] = useState<ApiResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('http://localhost:5000/diagnose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_description: textDescription,
                    age: Number(age),
                    sex: sex,
                    criteria_code: criteriaCode,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data: ApiResponse = await response.json();
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Ocorreu um erro ao processar a solicitação.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container">
            <form onSubmit={handleSubmit}>
                <h2>Relatar Sintomas</h2>
                <div className="form-group">
                    <label htmlFor="text_description">Descreva seus sintomas:</label>
                    <textarea
                        id="text_description"
                        value={textDescription}
                        onChange={(e) => setTextDescription(e.target.value)}
                        placeholder="Ex: Estou com febre alta e dor de cabeça há 3 dias..."
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="age">Idade:</label>
                    <input
                        type="number"
                        id="age"
                        value={age}
                        onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="sex">Sexo:</label>
                    <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                        <option value="M">Masculino</option>
                        <option value="F">Feminino</option>
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="criteria_code">Critério de Suspeita:</label>
                    <select id="criteria_code" value={criteriaCode} onChange={(e) => setCriteriaCode(Number(e.target.value))}>
                        <option value={1}>Laboratorial</option>
                        <option value={2}>Clínico-Epidemiológico</option>
                    </select>
                </div>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Analisando...' : 'Analisar Sintomas'}
                </button>
            </form>

            {error && <div className="result-box error"><p>{error}</p></div>}

            {result && (
                <div className="result-box">
                    <h3>Análise do Assistente Virtual</h3>
                    <p style={{ whiteSpace: 'pre-wrap' }}>{result.friendly_response}</p>
                    <h4>Probabilidades:</h4>
                    <ul>
                        {Object.entries(result.analysis_details.probabilities).map(([disease, prob]) => (
                            <li key={disease}>{`${disease.charAt(0).toUpperCase() + disease.slice(1)}: ${(prob * 100).toFixed(0)}%`}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};