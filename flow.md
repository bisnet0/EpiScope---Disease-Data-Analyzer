+----------------+      +-------------------------+      +---------------------------+
|   Frontend     |      |      Backend API        |      |     Serviços Externos     |
| (React + Vite) |      |      (Flask/Docker)     |      |---------------------------|
+----------------+      +-------------------------+      | [x] API Pública de Saúde  |
       |                         |                       | [x] API do Gemini/GPT-4   |
       | 1. Envia Sintomas       |                       +---------------------------+
       | (Texto livre)           |
       |------------------------>| POST /diagnose          |
       |                         |   |                     |
       |                         |   | 2. Chama a IA       |
       |                         |   | (Gemini) para       |
       |                         |   | estruturar dados    |
       |                         |   |-------------------->|
       |                         |   |                     |
       |                         |   | 3. Recebe JSON      |
       |                         |   |   com sintomas      |
       |                         |   |   estruturados      |
       |                         |   |<--------------------|
       |                         |   |                     |
       |                         |   | 4. Carrega o modelo |
       |                         |   |   de Árvore de      |      +----------------------+
       |                         |   |   Decisão treinado  |      |   Banco de Dados     |
       |                         |   |   e executa a       |      | (PostgreSQL/Docker)  |
       |                         |   |   previsão          |      +----------------------+
       |                         |   |                     |                ^
       |                         |   | 5. Chama a IA       |                |
       |                         |   | (Gemini) para       |                |
       |                         |   |   gerar a resposta  |                | (Processo Offline)
       |                         |   |   amigável          |                | Script de Ingestão
       |                         |   |-------------------->|                | de Dados
       |                         |   |                     |                |
       |                         |   | 6. Recebe o texto   |
       |                         |   |   final             |
       |                         |   |<--------------------|
       |                         |                         |
       | 7. Retorna JSON com     |                         |
       |    previsões e texto    |                         |
       |<------------------------|                         |
       |                         |                         |
+----------------+      +-------------------------+      +---------------------------+