#!/usr/bin/env bash
set -e

# Upgrade pip and install requirements (allow partial failures)
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt || true

# If blis failed to build, try installing a prebuilt wheel (best-effort; ignore errors)
pip install blis==0.9.1 || true

# Ensure spaCy model is installed (download at runtime if not present)
python - <<'PY'
import sys, subprocess, importlib
try:
    import en_core_web_sm
    print("spaCy model en_core_web_sm already installed.")
except Exception:
    print("Installing spaCy model en_core_web_sm via spacy.cli.download()...")
    try:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        print("Model installed.")
    except Exception as e:
        print("Warning: automatic spaCy model download failed:", e, file=sys.stderr)
        # As fallback, try pip installing the wheel (best-effort)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"])
        except Exception as e2:
            print("Warning: fallback wheel install also failed:", e2, file=sys.stderr)
PY

# Start Streamlit. Use $PORT if the host provides it (Render does).
if [ -n "$PORT" ]; then
  streamlit run resumescreeningapp.py --server.port $PORT --server.headless true
else
  streamlit run resumescreeningapp.py --server.headless true
fi
