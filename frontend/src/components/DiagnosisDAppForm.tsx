// frontend/src/components/DiagnosisDAppForm.tsx
import React, { useState } from 'react';

// Extend the Window interface to include the ethereum property
declare global {
    interface Window {
        ethereum?: any;
    }
}
import { ethers } from 'ethers';

// CONSTANTES DA REDE LOCAL CARTESI
const INPUTBOX_ADDRESS = "0x59b22D57D4f067708AB0c00552767405926dc768";
const DAPP_ADDRESS = "0x70ac08179605AF2D9e75782b8DEcDD3c22aA4D0C";
const INPUTBOX_ABI = ["function addInput(address _dapp, bytes memory _input) returns (bytes32)"];
const GRAPHQL_URL = "http://localhost:8080/graphql";
const FLASK_API_URL = "http://localhost:5000";

// Função para buscar o resultado (notice) da blockchain
const fetchNotices = async (inputIndex: number) => {
    const query = `
        query GetNotice {
            input(index: ${inputIndex}) {
                notices {
                    edges {
                        node {
                            payload
                        }
                    }
                }
            }
        }
    `;
    const response = await fetch(GRAPHQL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    });
    const data = await response.json();
    const noticePayload = data.data.input.notices.edges[0]?.node?.payload;
    if (noticePayload) {
        // O payload vem em hexadecimal, precisamos decodificar
        return JSON.parse(ethers.toUtf8String(noticePayload));
    }
    return null;
};


export const DiagnosisDAppForm: React.FC = () => {
    const [signer, setSigner] = useState<ethers.Signer | null>(null);
    const [account, setAccount] = useState<string | null>(null);
    const [textDescription, setTextDescription] = useState('');
    const [age, setAge] = useState<number | ''>(30);
    const [sex, setSex] = useState('M');
    const [criteriaCode, setCriteriaCode] = useState(2)

    const [status, setStatus] = useState('');
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const connectWallet = async () => {
        if (!window.ethereum) return setError("MetaMask não detectada.");
        try {
            const provider = new ethers.BrowserProvider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = await provider.getSigner();
            setSigner(signer);
            setAccount(await signer.getAddress());
        } catch (e) { setError("Falha ao conectar a carteira."); }
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!signer) return setError("Conecte sua carteira primeiro.");

        setStatus('Enviando transação...');
        setError(null);
        setResult(null);

        try {
            // --- PASSO NOVO: Chamar a API Flask para estruturar os dados ---
            const structureResponse = await fetch(`${FLASK_API_URL}/structure-symptoms`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text_description: textDescription }),
            });
            if (!structureResponse.ok) throw new Error("Falha ao se comunicar com o serviço de IA.");

            const structuredSymptoms = await structureResponse.json();

            // --- FIM DO PASSO NOVO ---

            // Combina os dados estruturados pela IA com os outros dados do formulário
            const payloadForDApp = {
                ...structuredSymptoms, // Sintomas vêm da IA
                idade: Number(age),
                sexo_encoded: sex === 'F' ? 1 : 0,
                // Adiciona as colunas de critério, assumindo 0 para as não selecionadas
                criterio_0: 0,
                criterio_1: criteriaCode === 1 ? 1 : 0,
                criterio_2: criteriaCode === 2 ? 1 : 0,
                criterio_3: 0
            };

            setStatus('Passo 2/4: Enviando transação para a blockchain...');
            const inputBox = new ethers.Contract(INPUTBOX_ADDRESS, INPUTBOX_ABI, signer);
            const inputBytes = ethers.toUtf8Bytes(JSON.stringify(payloadForDApp));

            const tx = await inputBox.addInput(DAPP_ADDRESS, inputBytes);
            setStatus('Passo 3/4: Aguardando confirmação da transação...');
            const receipt = await tx.wait();

            const inputIndex = parseInt(receipt.logs[0].topics[2], 16);
            setStatus(`Passo 4/4: Buscando diagnóstico verificável (Input #${inputIndex})...`);

            // Polling para buscar o resultado
            const interval = setInterval(async () => {
                const notice = await fetchNotices(inputIndex);
                if (notice) {
                    clearInterval(interval);
                    setResult(notice);
                    setStatus('Diagnóstico recebido!');
                }
            }, 3000); // Tenta a cada 3 segundos

        } catch (e: any) {
            console.error(e);
            setError(e.message);
            setStatus('');
        }
    };

    return (
        <div className="dapp-container">
            {/* Coluna 1: Formulário e Conexão */}
            <div className="form-wrapper">
                {!account ? (
                    <button onClick={connectWallet}>Conectar MetaMask</button>
                ) : (
                    <div className="wallet-connected">Conectado com: {account.substring(0, 6)}...{account.substring(account.length - 4)}</div>
                )}
                <form onSubmit={handleSubmit} style={{ opacity: !signer ? 0.5 : 1 }}>
                    <div className="form-group">
                        <label>Descreva seus sintomas:</label>
                        <textarea value={textDescription} onChange={(e) => setTextDescription(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label>Idade:</label>
                        <input type="number" value={age} onChange={(e) => setAge(Number(e.target.value))} required />
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
                    <button type="submit" disabled={!signer || status.includes('Passo')}>
                        {status ? 'Processando...' : 'Analisar (Web3 com IA)'}
                    </button>
                </form>
                <p className="footer-note">Para esta função, certifique-se que sua MetaMask está conectada à rede 'Localhost 8545'.</p>
            </div>
            <div className="results-wrapper">
                {status && <div className="result-box status"><p><strong>Status:</strong> {status}</p></div>}
                {error && <div className="result-box error"><p>{error}</p></div>}
                {result && (
                    <div className="result-box">
                        <h3>Diagnóstico Verificado na Blockchain</h3>
                        <p><strong>Resultado Provável:</strong> {result.diagnostico_provavel.toUpperCase()}</p>
                    </div>
                )}
            </div>


        </div>
    );
};