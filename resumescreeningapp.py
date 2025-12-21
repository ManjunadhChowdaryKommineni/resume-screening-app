import streamlit as st
import pandas as pd
import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="📄",
    layout="centered"
)

# ---------------- MODERN CSS ----------------
st.markdown("""
<style>

/* Animated gradient background */
.stApp {
    background: linear-gradient(120deg, #1e3c72, #2a5298, #6a11cb);
    background-size: 300% 300%;
    animation: gradientBG 12s ease infinite;
    font-family: 'Segoe UI', sans-serif;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glass card */
.glass {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    margin-bottom: 18px;
}

/* Headings */
h1, h2, h3 {
    color: white !important;
}

/* Labels & text */
p, label, span {
    color: #eaeaea !important;
}

/* Inputs */
textarea, input {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.95) !important;
}

/* Mirror Effect Button */
.stButton>button {
    position: relative;
    background: linear-gradient(135deg, #00f2fe, #4facfe);
    color: white;
    font-weight: 600;
    padding: 12px 36px;
    border-radius: 30px;
    border: none;
    transition: all 0.3s ease;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

/* Mirror shine */
.stButton>button::after {
    content: "";
    position: absolute;
    top: 0;
    left: -80%;
    width: 60%;
    height: 100%;
    background: rgba(255,255,255,0.35);
    transform: skewX(-25deg);
}

/* Hover animation */
.stButton>button:hover::after {
    left: 130%;
    transition: left 0.6s ease;
}

.stButton>button:hover {
    transform: translateY(-2px) scale(1.04);
    box-shadow: 0 18px 40px rgba(0,0,0,0.45);
}

/* Download button */
.stDownloadButton>button {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    border-radius: 30px;
    font-weight: bold;
}

/* Progress bar background */
.progress-bg {
    background-color: rgba(255,255,255,0.25);
    border-radius: 12px;
    height: 22px;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style="text-align:center;
background: linear-gradient(90deg,#00f2fe,#4facfe,#43e97b);
-webkit-background-clip:text;
color:transparent;
font-size:42px;
font-weight:800;">
📄 AI Resume Matcher
</h1>

<p style="text-align:center; font-size:18px;">
Smart Resume Screening using NLP & Machine Learning
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- LOAD SPACY ----------------
@st.cache_resource
def load_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        raise

nlp = load_model()

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception:
        return ""

def preprocess(text):
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and token.is_alpha
    ]
    return " ".join(tokens)

# ---------------- FORM ----------------
with st.form("resume_form"):
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.subheader("📌 Step 1: Job Description")
    job_description = st.text_area(
        "Paste Job Description",
        height=180,
        placeholder="Looking for a Python developer with ML and REST API experience..."
    )

    st.subheader("📎 Step 2: Upload Resumes (PDF)")
    uploaded_files = st.file_uploader(
        "Upload resumes",
        type="pdf",
        accept_multiple_files=True
    )

    submitted = st.form_submit_button("🚀 Analyze Resumes")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PROCESSING ----------------
if submitted:
    if not job_description:
        st.warning("⚠️ Please enter a job description.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        with st.spinner("🔍 Matching resumes..."):
            jd_processed = preprocess(job_description)
            resumes = []
            names = []

            for file in uploaded_files:
                file.seek(0)
                text = extract_text_from_pdf(file)
                if text.strip():
                    resumes.append(preprocess(text))
                    names.append(file.name)

            tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            vectors = tfidf.fit_transform([jd_processed] + resumes)

            scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
            ranked = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)

            df = pd.DataFrame(ranked, columns=["Resume", "Score"])
            df["Match %"] = (df["Score"] * 100).round(2)

        st.success("✅ Analysis Complete")

        st.subheader("🏆 Ranked Candidates")

        for i, row in df.iterrows():
            percent = row["Match %"]

            if percent >= 80:
                color = "#43e97b"
            elif percent >= 50:
                color = "#fbc531"
            else:
                color = "#ff6b6b"

            st.markdown(f"""
            <div class="glass">
                <strong>Rank {i+1} – {row['Resume']}</strong><br><br>
                <div class="progress-bg">
                    <div style="
                        width:{percent}%;
                        background:{color};
                        height:100%;
                        border-radius:12px;
                        text-align:center;
                        color:black;
                        font-weight:bold;
                        line-height:22px;">
                        {percent}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        csv = df.to_csv(index=False).encode()
        st.download_button(
            "📥 Download Results CSV",
            csv,
            "resume_results.csv",
            "text/csv"
        )



