graph TD
    Start([Início]) --> Triage{Triagem / Router}
    
    %% Ramo de Texto (Arbovirose)
    Triage -->|Texto Clínico| Anamnese[Agente de Anamnese]
    Anamnese -->|Faltam Dados?| AskUser[Pergunta ao Usuário]
    AskUser --> Anamnese
    Anamnese -->|Dados Completos| ToolArbo[Ferramenta: XGBoost]
    ToolArbo --> Critic{Crítico Médico}
    
    %% Ramo de Imagem (Glaucoma)
    Triage -->|Imagem| ToolGlaucoma[Ferramenta: CNN + VLM]
    ToolGlaucoma --> Critic
    
    %% Ramo Administrativo (Laboratório)
    Triage -->|Comando Admin| ManagerAgent[Gerente de Laboratório]
    ManagerAgent --> ToolGA[Ferramenta: Genetic Optimizer]
    ToolGA --> Critic
    
    %% Validação Final
    Critic -->|Inconclusivo| AskUser
    Critic -->|Conclusivo| FinalAnswer[Resposta Final + Blockchain]