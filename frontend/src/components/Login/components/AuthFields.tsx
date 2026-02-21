import React from 'react';

interface Props {
  state: any;
  setters: any;
  actions: any;
}

export const AuthFields: React.FC<Props> = ({ state, setters, actions }) => {
  return (
    <form onSubmit={actions.handleSubmit}>
      {!state.isLogin && (
        <div className="form-group">
          <label>Usuário</label>
          <input 
            type="text" 
            value={state.username} 
            onChange={e => setters.setUsername(e.target.value)} 
            required 
          />
        </div>
      )}

      <div className="form-group">
        <label>E-mail</label>
        <input 
          type="email" 
          value={state.email} 
          onChange={e => setters.setEmail(e.target.value)} 
          required 
        />
      </div>

      <div className="form-group">
        <label>Senha</label>
        <input 
          type="password" 
          value={state.password} 
          onChange={e => setters.setPassword(e.target.value)} 
          required 
        />
      </div>

      <button type="submit" disabled={state.loading} className="btn-primary">
        {state.loading ? 'Processando...' : (state.isLogin ? 'Entrar' : 'Cadastrar')}
      </button>
    </form>
  );
};