# Use a stable Python base
FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

# Install system build dependencies required to compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install python deps
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# (optional) ensure spaCy model if wheel not installed
RUN python -c "import importlib,sys; \
    (importlib.import_module('spacy') and print('spacy ready')) if 'spacy' in globals() else None" || true

EXPOSE 8501
CMD ["streamlit", "run", "resumescreeningapp.py", "--server.port", "8501", "--server.headless", "true"]
