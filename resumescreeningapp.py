import streamlit as st
import pandas as pd
import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- PAGE CONFIG ---
st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="centered")

# --- CUSTOM CSS FOR STYLING (less brittle selectors) ---
st.markdown(
    """
    <style>
    /* apply to the main container */
    .stApp {
        background: linear-gradient(to right, #f9f9f9, #f0f0f0);
    }
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold;
        padding: 0.45em 1.6em;
        border-radius: 10px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
        transform: scale(1.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER ---
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>📄 AI-Powered Resume Screening</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Smart filtering of resumes using Natural Language Processing and Machine Learning</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- LOAD SPACY MODEL ---
@st.cache_resource
def load_model():
    # keep model load in a single place; using the small model for demo
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # user might not have model installed; give friendly error
        st.error(
            "spaCy model 'en_core_web_sm' not found. Install it or add to requirements. "
            "Example: python -m spacy download en_core_web_sm"
        )
        raise

nlp = load_model()

# --- TEXT PROCESSING FUNCTIONS ---
def extract_text_from_pdf(file) -> str:
    """Return extracted text for a file-like object (PDF)."""
    try:
        reader = PyPDF2.PdfReader(file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        # don't crash whole app if a PDF can't be read
        st.warning(f"Could not extract text from {getattr(file, 'name', 'file')}: {e}")
        return ""

def preprocess(text: str) -> str:
    if not text:
        return ""
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

# --- INPUT FORM ---
with st.form(key="resume_form"):
    st.subheader("📌 Step 1: Enter Job Description")
    job_description = st.text_area(
        "Paste the job description below",
        height=180,
        placeholder="E.g., We are looking for a software engineer with Python, Django, and REST API experience...",
    )

    st.subheader("📎 Step 2: Upload Resume PDFs")
    uploaded_files = st.file_uploader("Upload one or more resumes", type="pdf", accept_multiple_files=True)

    submitted = st.form_submit_button("🚀 Submit and Analyze")

# --- MAIN LOGIC ---
if submitted:
    if not job_description:
        st.warning("⚠️ Please enter a job description.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        with st.spinner("🔍 Analyzing resumes..."):
            jd_processed = preprocess(job_description)
            resumes_processed = []
            names = []

            for file in uploaded_files:
                # Ensure file pointer is at start
                try:
                    file.seek(0)
                except Exception:
                    pass

                text = extract_text_from_pdf(file)
                if not text.strip():
                    st.warning(f"No text extracted from {file.name}. Skipping.")
                    continue

                processed = preprocess(text)
                resumes_processed.append(processed)
                names.append(file.name)

            if not resumes_processed:
                st.error("No valid resumes to analyze after extraction. Please upload plaintext PDFs.")
            else:
                # build TF-IDF on job description + all resumes
                tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
                vectors = tfidf.fit_transform([jd_processed] + resumes_processed)

                cosine_scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

                ranked = sorted(zip(names, cosine_scores), key=lambda x: x[1], reverse=True)

                df = pd.DataFrame(ranked, columns=["Resume", "Match Score"])
                df["Match Percentage"] = (df["Match Score"] * 100).round(2)

                st.success("✅ Analysis Complete!")
                st.subheader("🏆 Ranked Candidates")

                for index, row in df.iterrows():
                    percentage = float(row["Match Percentage"])
                    rank = index + 1
                    resume_name = f"Rank {rank} – {row['Resume']}"

                    if percentage >= 80:
                        bar_color = "#4CAF50"  # Green
                    elif percentage >= 50:
                        bar_color = "#FFC107"  # Yellow
                    else:
                        bar_color = "#F44336"  # Red

                    st.markdown(
                        f"""
                    <div style='
                        padding: 12px;
                        margin-bottom: 12px;
                        border: 1px solid #e0e0e0;
                        border-radius: 10px;
                        background-color: #ffffff;
                    '>
                        <strong style='font-size:15px; color: black;'>{resume_name}</strong><br><br>
                        <span style='color: #555;'>Match Score:</span>
                        <div style="background-color: #eee; border-radius: 10px; height: 22px; width: 100%;">
                            <div style="
                                width: {percentage}% ;
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
                    """,
                        unsafe_allow_html=True,
                    )

                csv = df.to_csv(index=False).encode()
                st.download_button("📥 Download Results as CSV", csv, "ranked_resumes.csv", "text/csv")


