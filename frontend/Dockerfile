# ==========================================
# ESTÁGIO 1: BUILD (Ambiente Node)
# ==========================================
FROM node:18-alpine as builder

WORKDIR /app

# Copia os arquivos de dependência primeiro (aproveita cache do Docker)
COPY package*.json ./

# 👇 CORREÇÃO AQUI: Força o NPM a ignorar conflitos de dependências antigas
RUN npm install --legacy-peer-deps

# Copia o resto do código e gera os estáticos
COPY . .
RUN npm run build

# ==========================================
# ESTÁGIO 2: PRODUÇÃO (Ambiente Nginx)
# ==========================================
FROM nginx:alpine

# Remove a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia a nossa configuração customizada pro Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os arquivos gerados no Estágio 1 para a pasta pública do Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# O Cloud Run espera que o container escute na porta 8080
EXPOSE 8080

# Inicia o Nginx
CMD ["nginx", "-g", "daemon off;"]