// frontend/src/components/DiagnosisForm.tsx (Com Upload + Gráfico Glaucoma)
import React, { useState, useMemo, type ChangeEvent } from 'react'; // Adiciona ChangeEvent
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';

// --- Interfaces para as Respostas das APIs ---
interface ArbovirusApiResponse {
    friendly_response: string;
    analysis_details: {
        probabilities: { [key: string]: number };
        // Adicione outras chaves se precisar, como structured_symptoms
    };
}

// --- MUDANÇA: Interface para a resposta do Glaucoma ---
interface GlaucomaApiResponse {
    friendly_response: string;
    analysis_details: {
        probabilities: { [key: string]: number }; // Ex: { Normal: 0.37, Glaucomatous: 0.63 }
        predicted_class: string; // Ex: "Glaucomatous"
        confidence: number;      // Ex: 0.627
    };
}
// --- FIM DA MUDANÇA ---

const COLORS: { [key: string]: string } = {
    dengue: '#8884d8',
    chikungunya: '#82ca9d',
    zika: '#ffc658',
    // Cores para Glaucoma (Ajuste se necessário)
    Normal: '#8884d8',
    Glaucomatous: '#e377c2', // Cor diferente
};


export const DiagnosisForm: React.FC = () => {
    // --- Estados para Arbovírus ---
    const [textDescription, setTextDescription] = useState('');
    const [age, setAge] = useState<number | ''>('');
    const [sex, setSex] = useState('M');
    const [arboResult, setArboResult] = useState<ArbovirusApiResponse | null>(null);
    const [isArboLoading, setIsArboLoading] = useState(false);
    const [arboError, setArboError] = useState<string | null>(null);

    // --- MUDANÇA: Estados para Glaucoma ---
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [glaucomaResult, setGlaucomaResult] = useState<GlaucomaApiResponse | null>(null);
    const [isGlaucomaLoading, setIsGlaucomaLoading] = useState(false);
    const [glaucomaError, setGlaucomaError] = useState<string | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null); // Para mostrar a imagem selecionada
    // --- FIM DA MUDANÇA ---

    // Handler para Arbovírus (inalterado)
    const handleArboSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsArboLoading(true);
        setArboError(null);
        setArboResult(null);

        try {
            const response = await fetch('http://localhost:5000/diagnose', { // Rota /diagnose
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_description: textDescription,
                    age: Number(age),
                    sex: sex,
                }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            const data: ArbovirusApiResponse = await response.json();
            setArboResult(data);
        } catch (err: any) {
            setArboError(err.message || 'Ocorreu um erro ao processar a solicitação de arbovírus.');
        } finally {
            setIsArboLoading(false);
        }
    };

    // --- MUDANÇA: Handler para mudança no input de arquivo ---
    const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setImageFile(file);
            // Cria URL de preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreviewUrl(reader.result as string);
            };
            reader.readAsDataURL(file);
             // Limpa resultados anteriores ao selecionar nova imagem
            setGlaucomaResult(null);
            setGlaucomaError(null);
        } else {
            setImageFile(null);
            setPreviewUrl(null);
        }
    };
    // --- FIM DA MUDANÇA ---

    // --- MUDANÇA: Handler para submit do Glaucoma ---
    const handleGlaucomaSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!imageFile) {
            setGlaucomaError("Por favor, selecione um arquivo de imagem.");
            return;
        }

        setIsGlaucomaLoading(true);
        setGlaucomaError(null);
        setGlaucomaResult(null);

        const formData = new FormData();
        formData.append('image', imageFile); // A chave 'image' deve bater com request.files['image'] no backend

        try {
            const response = await fetch('http://localhost:5000/diagnose-glaucoma', { // Nova rota
                method: 'POST',
                // Não definimos Content-Type, o browser faz isso automaticamente para FormData
                body: formData,
            });

            if (!response.ok) {
                 const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const data: GlaucomaApiResponse = await response.json();
            setGlaucomaResult(data);
        } catch (err: any) {
            setGlaucomaError(err.message || 'Ocorreu um erro ao processar a solicitação de glaucoma.');
        } finally {
            setIsGlaucomaLoading(false);
        }
    };
    // --- FIM DA MUDANÇA ---


    // Função de formatação (inalterada)
    const formatResponse = (text: string): string => {
        let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br />');
        return html;
    };

    // Memoização para dados do gráfico de Arbovírus (inalterada)
    const arboChartData = useMemo(() => {
        if (!arboResult) return [];
        return Object.entries(arboResult.analysis_details.probabilities)
            .map(([disease, prob]) => ({
                name: disease.charAt(0).toUpperCase() + disease.slice(1),
                probability: parseFloat((prob * 100).toFixed(1)),
                color: COLORS[disease] || '#cccccc'
            }))
            .sort((a, b) => b.probability - a.probability);
    }, [arboResult]);

    // --- MUDANÇA: Memoização para dados do gráfico de Glaucoma ---
    const glaucomaChartData = useMemo(() => {
        if (!glaucomaResult) return [];
         // Adapta para o formato esperado pelo recharts
        return Object.entries(glaucomaResult.analysis_details.probabilities)
            .map(([className, prob]) => ({
                name: className, // Já vem como 'Normal' ou 'Glaucomatous'
                probability: parseFloat((prob * 100).toFixed(1)),
                color: COLORS[className] || '#cccccc'
            }))
             .sort((a, b) => b.probability - a.probability); // Ordena
    }, [glaucomaResult]);
    // --- FIM DA MUDANÇA ---


    return (
        <div className="container">
            {/* --- Seção Formulário Arbovírus --- */}
            <form onSubmit={handleArboSubmit} className="form-section">
                <h2>1. Análise de Sintomas (Arbovírus)</h2>
                <div className="form-group">
                    <label htmlFor="text_description">Descreva seus sintomas:</label>
                    <textarea id="text_description" value={textDescription} onChange={(e) => setTextDescription(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="age">Idade:</label>
                    <input type="number" id="age" value={age} onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))} min="0" required />
                </div>
                <div className="form-group">
                    <label htmlFor="sex">Sexo:</label>
                    <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}> <option value="M">Masculino</option> <option value="F">Feminino</option> </select>
                </div>
                <button type="submit" disabled={isArboLoading}> {isArboLoading ? 'Analisando Sintomas...' : 'Analisar Sintomas'} </button>
            </form>

            {arboError && <div className="result-box error"><p><strong>Erro (Arbovírus):</strong> {arboError}</p></div>}
            {arboResult && (
                <div className="result-box">
                    <h3>Análise Arbovírus (Assistente Virtual)</h3>
                    <div dangerouslySetInnerHTML={{ __html: formatResponse(arboResult.friendly_response) }} />
                    <h4>Probabilidades Estimadas (Gráfico)</h4>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <BarChart data={arboChartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" /> <XAxis dataKey="name" /> <YAxis unit="%" domain={[0, 100]} />
                                <Tooltip formatter={(value: number) => [`${value}%`, "Prob."]} /> <Legend />
                                <Bar dataKey="probability" name="Probabilidade (%)"> {arboChartData.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))} </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            <hr style={{ margin: '40px 0' }} /> {/* Separador visual */}

            {/* --- MUDANÇA: Seção Formulário Glaucoma --- */}
            <form onSubmit={handleGlaucomaSubmit} className="form-section">
                 <h2>2. Análise de Imagem (Glaucoma)</h2>
                 <div className="form-group">
                     <label htmlFor="imageFile">Selecione a imagem do fundo do olho:</label>
                     <input
                         type="file"
                         id="imageFile"
                         accept="image/png, image/jpeg, image/jpg, image/bmp, image/tiff" // Aceita formatos comuns
                         onChange={handleImageChange}
                         required // Torna a seleção de imagem obrigatória para este form
                     />
                 </div>

                 {/* Preview da Imagem Selecionada */}
                 {previewUrl && (
                    <div className="image-preview">
                        <p>Imagem selecionada:</p>
                        <img src={previewUrl} alt="Preview do exame de fundo de olho" style={{ maxWidth: '200px', maxHeight: '200px', marginTop: '10px' }} />
                    </div>
                 )}

                 <button type="submit" disabled={isGlaucomaLoading || !imageFile}>
                     {isGlaucomaLoading ? 'Analisando Imagem...' : 'Analisar Imagem (Glaucoma)'}
                 </button>
            </form>

            {glaucomaError && <div className="result-box error"><p><strong>Erro (Glaucoma):</strong> {glaucomaError}</p></div>}
            {glaucomaResult && (
                <div className="result-box">
                    <h3>Análise Glaucoma (Assistente Virtual)</h3>
                    <div dangerouslySetInnerHTML={{ __html: formatResponse(glaucomaResult.friendly_response) }} />
                    {/* Gráfico para Glaucoma */}
                    <h4>Probabilidades Estimadas (Gráfico)</h4>
                     <div style={{ width: '100%', height: 250 }}> {/* Altura menor talvez? */}
                        <ResponsiveContainer>
                            <BarChart data={glaucomaChartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}> {/* Gráfico Vertical */}
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" unit="%" domain={[0, 100]} /> {/* Eixo X é a probabilidade */}
                                <YAxis type="category" dataKey="name" width={100} /> {/* Eixo Y são as classes */}
                                <Tooltip formatter={(value: number) => [`${value}%`, "Probabilidade"]} />
                                <Legend />
                                <Bar dataKey="probability" name="Probabilidade (%)" >
                                     {glaucomaChartData.map((entry, index) => (
                                         <Cell key={`cell-${index}`} fill={entry.color} />
                                     ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                     {/* Detalhes adicionais se desejar */}
                    <p style={{marginTop: '15px'}}><strong>Predição do Modelo:</strong> {glaucomaResult.analysis_details.predicted_class} (Confiança: {(glaucomaResult.analysis_details.confidence * 100).toFixed(1)}%)</p>
                </div>
            )}
             {/* --- FIM DA MUDANÇA --- */}

        </div>
    );
};