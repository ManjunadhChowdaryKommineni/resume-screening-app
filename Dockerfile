# Dockerfile — Python 3.11 base for compatibility with spaCy/blis
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copy project files
COPY . /app

# Install system packages required to build some Python wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install python deps
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Expose default Streamlit port
EXPOSE 8501

# at the end of Dockerfile, replace any existing CMD with this:
CMD ["bash", "-lc", "streamlit run resumescreeningapp.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false"]


