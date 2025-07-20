##writefile app.py
import streamlit as st
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import subprocess
import importlib.util
# --- PAGE CONFIG ---
st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="centered")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .reportview-container {
        background: linear-gradient(to right, #f9f9f9, #f0f0f0);
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5em 2em;
        border-radius: 10px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📄 AI-Powered Resume Screening</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Smart filtering of resumes using Natural Language Processing and Machine Learning</p>", unsafe_allow_html=True)
st.markdown("---")
def ensure_spacy_model():
    model_name = "en_core_web_sm"
    if not importlib.util.find_spec(model_name):
        subprocess.run(["python", "-m", "spacy", "download", model_name])
    return spacy.load(model_name)

nlp = ensure_spacy_model()
# --- LOAD SPACY MODEL ---
@st.cache_resource
def load_model():
    return spacy.load("en_core_web_sm")

nlp = load_model()

# --- TEXT PROCESSING FUNCTIONS ---
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def preprocess(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

# --- INPUT FORM ---
with st.form(key="resume_form"):
    st.subheader("📌 Step 1: Enter Job Description")
    job_description = st.text_area("Paste the job description below", height=180, placeholder="E.g., We are looking for a software engineer with Python, Django, and REST API experience...")

    st.subheader("📎 Step 2: Upload Resume PDFs")
    uploaded_files = st.file_uploader("Upload one or more resumes", type="pdf", accept_multiple_files=True)

    submitted = st.form_submit_button("🚀 Submit and Analyze")

# --- MAIN LOGIC ---
if submitted:
    if uploaded_files and job_description:
        with st.spinner("🔍 Analyzing resumes..."):
            jd_processed = preprocess(job_description)
            resumes = []
            names = []

            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                processed = preprocess(text)
                resumes.append(processed)
                names.append(file.name)

            tfidf = TfidfVectorizer()
            vectors = tfidf.fit_transform([jd_processed] + resumes)
            cosine_scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

            ranked = sorted(zip(names, cosine_scores), key=lambda x: x[1], reverse=True)

            df = pd.DataFrame(ranked, columns=["Resume", "Match Score"])
            df["Match Percentage"] = (df["Match Score"] * 100).round(2)

            st.success("✅ Analysis Complete!")
            st.subheader("🏆 Ranked Candidates")

            for index, row in df.iterrows():
                percentage = row["Match Percentage"]
                rank = index + 1
                resume_name = f"Rank {rank} – {row['Resume']}"

                # Color coding
                if percentage >= 80:
                    bar_color = "#4CAF50"   # Green
                elif percentage >= 50:
                    bar_color = "#FFC107"   # Yellow
                else:
                    bar_color = "#F44336"   # Red

                st.markdown(f"""
                <div style='
                    padding: 15px;
                    margin-bottom: 15px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    background-color: #f4f4f4;
                '>
                    <strong style='font-size:16px; color: black;'>{resume_name}</strong><br><br>
                    <span style='color: #555;'>Match Score:</span>
                    <div style="background-color: #ddd; border-radius: 10px; height: 22px;">
                        <div style="
                            width: {percentage}%;
                            background-color: {bar_color};
                            height: 100%;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                            font-weight: bold;
                            line-height: 22px;
                        ">
                            {percentage}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # CSV Download
            csv = df.to_csv(index=False).encode()
            st.download_button("📥 Download Results as CSV", csv, "ranked_resumes.csv", "text/csv")

    else:
        st.warning("⚠️ Please upload at least one resume and enter a job description.")
