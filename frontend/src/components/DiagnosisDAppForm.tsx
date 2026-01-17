import React, { useEffect, useState } from 'react';
import { ethers } from 'ethers';
import { useAuth } from '../context/AuthContext';
import api from '../services/api'; 
import { ShieldCheck, CloudUpload, ClockHistory, FileEarmarkText, CheckCircle } from 'react-bootstrap-icons';


interface HistoryItem {
    id: number;
    type: 'Arbovirose' | 'Glaucoma';
    date: string;
    details: string;
    result: any;
    signature?: string; 
}


const INPUT_BOX_ADDRESS = "0x59b22D57D4f067708AB0c00552767405926dc768";
const DAPP_ADDRESS = "0xab7528bb862fB57E8A2BCd567a2e929a0Be56a5e";
const INPUTBOX_ABI = ["function addInput(address _dapp, bytes memory _input) returns (bytes32)"];

export const DiagnosisDAppForm: React.FC = () => {
    const { walletAddress, connectWallet, signer } = useAuth();
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [sendingId, setSendingId] = useState<number | null>(null);

    
    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            
            const response = await api.get('/diagnose/history');
            setHistory(response.data);
        } catch (error) {
            console.error("Erro ao buscar histórico:", error);
        } finally {
            setLoading(false);
        }
    };

        const formatDateBR = (iso: string) => {
        const date = new Date(iso);

        const day = date.toLocaleString("pt-BR", {
            day: "2-digit",
            timeZone: "America/Sao_Paulo"
        });

        const month = date.toLocaleString("pt-BR", {
            month: "2-digit",
            timeZone: "America/Sao_Paulo"
        });

        const hour = date.toLocaleString("pt-BR", {
            hour: "2-digit",
            hour12: false,
            timeZone: "America/Sao_Paulo"
        });

        const minute = date.toLocaleString("pt-BR", {
            minute: "2-digit",
            timeZone: "America/Sao_Paulo"
        });

        return `${hour}h${minute}m`;
    };

    const handleRegisterOnChain = async (item: HistoryItem) => {
        if (!signer || !walletAddress) {
            alert("Por favor, conecte sua carteira primeiro.");
            connectWallet();
            return;
        }

        setSendingId(item.id);

        try {
            
            const payload = JSON.stringify({
                action: "register_diagnosis",
                diagnosis_id: item.id,
                type: item.type,
                timestamp: item.date,
                data_hash: ethers.id(JSON.stringify(item.result)), 
                submitter: walletAddress
            });

            
            const inputBytes = ethers.toUtf8Bytes(payload);

            
            
            const inputBox = new ethers.Contract(INPUT_BOX_ADDRESS, INPUTBOX_ABI, signer);
            
            console.log(`Enviando Input para DApp ${DAPP_ADDRESS}...`);
            const tx = await inputBox.addInput(DAPP_ADDRESS, inputBytes);
            
            console.log("Transação enviada:", tx.hash);
            alert(`✅ Transação enviada para Blockchain!\nHash: ${tx.hash.substring(0, 15)}...`);
            
            
            

        } catch (error: any) {
            console.error("Erro Blockchain:", error);
            alert("Erro ao registrar: " + (error.reason || error.message));
        } finally {
            setSendingId(null);
        }
    };

    return (
        <div className="container">
            <div className="form-section" style={{ maxWidth: '1000px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                    <h2 style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
                        <ShieldCheck style={{ marginRight: '10px', color: '#646cff' }}/> 
                        Cartesi DApp Ledger
                    </h2>
                    
                    {!walletAddress ? (
                        <button onClick={connectWallet} className="btn-primary" style={{ background: '#f39c12', padding: '8px 16px' }}>
                            🦊 Conectar MetaMask
                        </button>
                    ) : (
                        <div style={{ color: '#2ecc71', border: '1px solid #2ecc71', padding: '5px 15px', borderRadius: '20px', fontSize: '0.9rem' }}>
                            🟢 Wallet Conectada
                        </div>
                    )}
                </div>

                <p style={{ color: '#aaa', marginBottom: '30px', lineHeight: '1.5' }}>
                    Selecione um diagnóstico do seu histórico Web2 para enviar para a camada de execução verificável (Cartesi Machine).
                    Isso cria uma prova criptográfica imutável do resultado.
                </p>

                {loading ? (
                    <p style={{textAlign: 'center', color: '#666'}}>Carregando histórico...</p>
                ) : (
                    <div className="history-list" style={{ overflowX: 'auto' }}>
                        {history.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '40px', background: '#1e1e1e', borderRadius: '8px' }}>
                                <p>Nenhum diagnóstico encontrado.</p>
                                <small style={{color: '#666'}}>Realize um diagnóstico nas outras abas primeiro.</small>
                            </div>
                        ) : (
                            <table style={{ width: '100%', borderCollapse: 'collapse', color: '#eee', minWidth: '600px' }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid #444', textAlign: 'left', color: '#888' }}>
                                        <th style={{ padding: '15px' }}>Data</th>
                                        <th style={{ padding: '15px' }}>Tipo</th>
                                        <th style={{ padding: '15px' }}>Resumo</th>
                                        <th style={{ padding: '15px', textAlign: 'right' }}>Ação Blockchain</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history.map((item) => (
                                        <tr key={`${item.type}-${item.id}`} style={{ borderBottom: '1px solid #333', transition: 'background 0.2s' }}>
                                            <td style={{ padding: '15px' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <ClockHistory size={14}/> 
                                                    {new Date(item.date).toLocaleDateString("pt-BR")}
                                                    <small style={{color: '#666'}}> {formatDateBR(item.date)}</small>
                                                </div>
                                            </td>
                                            <td style={{ padding: '15px' }}>
                                                <span style={{ 
                                                    background: item.type === 'Arbovirose' ? 'rgba(52, 152, 219, 0.2)' : 'rgba(233, 30, 99, 0.2)',
                                                    color: item.type === 'Arbovirose' ? '#3498db' : '#e91e63',
                                                    padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: '500'
                                                }}>
                                                    {item.type}
                                                </span>
                                            </td>
                                            <td style={{ padding: '15px', color: '#ccc', fontSize: '0.9rem', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {item.details}
                                            </td>
                                            <td style={{ padding: '15px', textAlign: 'right' }}>
                                                {item.signature ? (
                                                    <span title="Registrado na Blockchain" style={{ color: '#2ecc71', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '5px' }}>
                                                        <CheckCircle /> Registrado
                                                    </span>
                                                ) : (
                                                    <button 
                                                        onClick={() => handleRegisterOnChain(item)}
                                                        disabled={sendingId === item.id || !walletAddress}
                                                        style={{ 
                                                            background: 'transparent', 
                                                            border: walletAddress ? '1px solid #646cff' : '1px solid #444', 
                                                            color: walletAddress ? '#646cff' : '#666', 
                                                            padding: '6px 12px', fontSize: '0.8rem', borderRadius: '6px',
                                                            cursor: walletAddress ? 'pointer' : 'not-allowed',
                                                            display: 'inline-flex', alignItems: 'center', gap: '6px',
                                                            transition: 'all 0.2s'
                                                        }}
                                                    >
                                                        {sendingId === item.id ? 'Assinando...' : <><CloudUpload /> Registrar</>}
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};