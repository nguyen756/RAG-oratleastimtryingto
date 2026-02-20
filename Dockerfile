FROM python:3.10-slim 

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --default-timeout=1000 -r requirements.txt



RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer( 'all-MiniLM-L6-v2');"

COPY . .

CMD ["python","app/main.py"]
