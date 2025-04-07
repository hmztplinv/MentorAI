FROM python:3.10

WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# Uygulama dosyalarını kopyala
COPY app ./app
COPY init_db.py .
COPY requirements.txt .
COPY run.py .
COPY setup.py .

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir -r requirements.txt

# ChromaDB dizinini oluştur
RUN mkdir -p ./chromadb

# Uygulamayı çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]