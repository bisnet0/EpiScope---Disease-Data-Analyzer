FROM python:3.11
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt . 
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
COPY . ./backend
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py

EXPOSE 5000
CMD ["python", "backend/app.py"]