FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    mupdf-tools \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p tmp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
