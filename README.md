# 📄 AI Resume Screening App

An intelligent Resume Screening System that uses **Machine Learning and Natural Language Processing (NLP)** to analyze, filter, and rank resumes based on job descriptions. This project helps automate the recruitment process by identifying the most relevant candidates efficiently.

---

## 🚀 Features

- 📄 Resume parsing and text extraction  
- 🧠 NLP-based analysis using TF-IDF / similarity techniques  
- 📊 Candidate ranking based on job description match  
- ⚡ Fast and automated screening process  
- 🎯 Improves hiring efficiency and reduces manual effort  

---

## 🧠 Tech Stack

- **Programming Language:** Python  
- **Libraries:** Scikit-learn, Pandas, NumPy  
- **NLP Techniques:** TF-IDF, Cosine Similarity  
- **Framework (if used):** Flask / Streamlit  
- **Others:** Regex, Text Preprocessing  

---

## ⚙️ How It Works

1. Upload resumes (PDF/Text format)  
2. Extract text content from resumes  
3. Preprocess text (cleaning, tokenization)  
4. Convert text into numerical features using TF-IDF  
5. Compare resumes with job description  
6. Rank candidates based on similarity score  

## 📂 Project Structure

```
resume-screening-app/
├── data/
├── model/
├── app.py
├── preprocessing.py
├── requirements.txt
└── README.md
```

## ▶️ Installation

```bash
git clone https://github.com/ManjunadhChowdaryKommineni/resume-screening-app
cd resume-screening-app
pip install -r requirements.txt
