# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
# Exponha a porta que o Flask está usando
EXPOSE 5000
# Comando para rodar a aplicação
CMD ["python", "app.py"]