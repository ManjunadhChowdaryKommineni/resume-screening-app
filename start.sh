#!/usr/bin/env bash
set -e

# Upgrade pip and install requirements
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Ensure spaCy model is installed (download at runtime if not present)
python - <<'PY'
import sys, subprocess

try:
    import en_core_web_sm
    print("spaCy model en_core_web_sm already installed.")
except ImportError:
    print("Downloading spaCy model en_core_web_sm...")
    try:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
    except Exception as e:
        print("Error downloading model:", e, file=sys.stderr)
PY

# Start Streamlit
streamlit run resumescreeningapp.py --server.port ${PORT:-8501} --server.headless true
