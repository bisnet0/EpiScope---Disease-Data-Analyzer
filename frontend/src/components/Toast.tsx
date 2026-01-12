import React, { useEffect, useState, type CSSProperties } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface ToastProps {
    title?: string;
    message: string;
    type?: ToastType;
    onClose: () => void;
    duration?: number;
}

interface ToastStyleConfig {
    iconBg: string; // Fundo do ícone
    iconColor: string; // Cor do ícone
    icon: React.ReactNode;
}

const Toast: React.FC<ToastProps> = ({ title, message, type = 'info', onClose, duration = 4000 }) => {
    const [isVisible, setIsVisible] = useState(false);

    // Configurações para o modo Dark (cores mais vibrantes para contrastar com o fundo preto)
    const types: Record<ToastType, ToastStyleConfig> = {
        success: {
            iconBg: 'rgba(34, 197, 94, 0.15)', // Verde escuro transparente
            iconColor: '#4ade80', // Verde Neon
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            )
        },
        error: {
            iconBg: 'rgba(239, 68, 68, 0.15)', // Vermelho escuro transparente
            iconColor: '#f87171', // Vermelho Neon
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            )
        },
        info: {
            iconBg: 'rgba(59, 130, 246, 0.15)', // Azul escuro transparente
            iconColor: '#60a5fa', // Azul Neon
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
            )
        }
    };

    const styleConfig = types[type] || types.info;

    useEffect(() => {
        const enterTimer = setTimeout(() => setIsVisible(true), 10);
        const exitTimer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 400);
        }, duration);

        return () => {
            clearTimeout(enterTimer);
            clearTimeout(exitTimer);
        };
    }, [duration, onClose]);

    const styles: Record<string, CSSProperties> = {
        overlay: {
            position: 'fixed',
            top: '24px',
            right: '24px',
            zIndex: 9999,
            pointerEvents: isVisible ? 'auto' : 'none',
        },
        glassCard: {
            display: 'flex',
            alignItems: 'flex-start',
            gap: '16px',
            minWidth: '340px',
            maxWidth: '400px',
            padding: '20px', // Mais espaçamento interno
            borderRadius: '12px', // Bordas levemente menos redondas (estilo card dashboard)
            
            // --- DARK LIQUID GLASS ---
            // Fundo Escuro Profundo (quase preto/azul navy) com transparência
            backgroundColor: 'rgba(22, 28, 36, 0.85)', 
            
            // Blur forte para desfocar o fundo
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            
            // Borda muito sutil (branca com 8% de opacidade) para definir o shape no escuro
            border: '1px solid rgba(255, 255, 255, 0.08)',
            
            // Sombra preta forte para dar profundidade
            boxShadow: '0 20px 40px -4px rgba(0, 0, 0, 0.4)',
            // -----------------------------

            transform: isVisible 
                ? 'translateY(0) scale(1)' 
                : 'translateY(-20px) scale(0.95)',
            opacity: isVisible ? 1 : 0,
            transition: 'all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)',
        },
        iconBox: {
            background: styleConfig.iconBg,
            color: styleConfig.iconColor,
            minWidth: '40px',
            height: '40px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            // Brilho sutil ao redor do ícone
            boxShadow: `0 0 15px ${styleConfig.iconBg}`, 
        },
        content: {
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            paddingTop: '2px'
        },
        title: {
            margin: '0 0 6px 0',
            fontSize: '15px',
            fontWeight: '600',
            color: '#FFFFFF', // Título Branco Puro
            letterSpacing: '0.02em'
        },
        message: {
            margin: 0,
            fontSize: '14px',
            color: '#919EAB', // Cinza claro (Slate 400) para leitura no escuro
            lineHeight: '1.5',
            fontWeight: '400'
        },
        closeBtn: {
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            color: '#637381', // Icone de fechar mais discreto
            padding: '4px',
            marginTop: '-4px',
            marginRight: '-4px',
            borderRadius: '50%',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }
    };

    return (
        <div style={styles.overlay}>
            <div style={styles.glassCard}>
                <div style={styles.iconBox}>
                    {styleConfig.icon}
                </div>
                
                <div style={styles.content}>
                    {title && <h4 style={styles.title}>{title}</h4>}
                    <p style={styles.message}>{message}</p>
                </div>

                <button 
                    onClick={() => { setIsVisible(false); setTimeout(onClose, 400); }}
                    style={styles.closeBtn}
                    aria-label="Close"
                    onMouseEnter={(e) => {
                        e.currentTarget.style.color = '#fff';
                        e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.color = '#637381';
                        e.currentTarget.style.background = 'transparent';
                    }}
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        </div>
    );
};

export default Toast;