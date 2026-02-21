import React, { ChangeEvent } from "react";

interface Props {
  previewUrl: string | null;
  loading: boolean;
  onImageChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: React.FormEvent) => void;
}

export const GlaucomaInputForm: React.FC<Props> = ({ previewUrl, loading, onImageChange, onSubmit }) => (
  <form onSubmit={onSubmit} className="form-section">
    <h2>2. Análise de Imagem (Glaucoma CNN)</h2>
    <div className="form-group">
      <label>Imagem do fundo do olho:</label>
      <input type="file" accept="image/*" onChange={onImageChange} />
    </div>
    
    {previewUrl && (
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <img 
          src={previewUrl} 
          alt="Preview" 
          style={{ maxWidth: "200px", borderRadius: "8px", border: "1px solid #444" }} 
        />
      </div>
    )}
    
    <button type="submit" disabled={loading}>
      {loading ? "Analisando..." : "Enviar Imagem"}
    </button>
  </form>
);