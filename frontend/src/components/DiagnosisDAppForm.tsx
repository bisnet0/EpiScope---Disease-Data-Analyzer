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
    const [formData, setFormData] = useState({
        febre: 1, cefaleia: 1, idade: 40, sexo_encoded: 0, criterio_2: 1
    });
    
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
            const inputBox = new ethers.Contract(INPUTBOX_ADDRESS, INPUTBOX_ABI, signer);
            const inputBytes = ethers.toUtf8Bytes(JSON.stringify(formData));
            
            const tx = await inputBox.addInput(DAPP_ADDRESS, inputBytes);
            setStatus('Transação enviada. Aguardando confirmação...');
            
            const receipt = await tx.wait();
            // Pegar o index do input a partir dos logs da transação
            const inputIndex = parseInt(receipt.logs[0].topics[2], 16);
            setStatus(`Transação confirmada! Buscando resultado para o Input #${inputIndex}...`);

            // Polling para buscar o resultado
            const interval = setInterval(async () => {
                const notice = await fetchNotices(inputIndex);
                if (notice) {
                    clearInterval(interval);
                    setResult(notice);
                    setStatus('Diagnóstico recebido!');
                }
            }, 2000); // Tenta a cada 2 segundos

        } catch (e: any) {
            console.error(e);
            setError(e.message);
            setStatus('');
        }
    };

    // (O resto do JSX é similar ao formulário anterior)
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: Number(value) }));
    };

    return (
         <div className="dapp-container">
            {!account ? (
                <button onClick={connectWallet}>Conectar MetaMask</button>
            ) : (
                <div className="wallet-connected">Conectado com: {account.substring(0, 6)}...{account.substring(account.length - 4)}</div>
            )}
             <form onSubmit={handleSubmit} style={{ opacity: !signer ? 0.5 : 1 }}>
                <div className="form-group">
                    <label>Febre?</label>
                    <select name="febre" value={formData.febre} onChange={handleInputChange} disabled={!signer}><option value={1}>Sim</option><option value={0}>Não</option></select>
                </div>
                <div className="form-group">
                    <label>Dor de Cabeça?</label>
                    <select name="cefaleia" value={formData.cefaleia} onChange={handleInputChange} disabled={!signer}><option value={1}>Sim</option><option value={0}>Não</option></select>
                </div>
                <div className="form-group">
                    <label>Idade:</label>
                    <input type="number" name="idade" value={formData.idade} onChange={handleInputChange} disabled={!signer}/>
                </div>
                {/* Adicione outros inputs conforme necessário */}
                 <button type="submit" disabled={!signer || status.includes('Enviando')}>
                    {status.includes('Enviando') ? 'Processando na Blockchain...' : 'Analisar (Web3)'}
                </button>
            </form>
            
            {status && <div className="result-box status"><p><strong>Status:</strong> {status}</p></div>}
            {error && <div className="result-box error"><p>{error}</p></div>}
            {result && (
                <div className="result-box">
                    <h3>Diagnóstico Verificado na Blockchain</h3>
                    <p><strong>Resultado Provável:</strong> {result.diagnostico_provavel.toUpperCase()}</p>
                </div>
            )}
            <p className="footer-note">Para esta função, certifique-se que sua MetaMask está conectada à rede 'Localhost 8545'.</p>
         </div>
    );
};