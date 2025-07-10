import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

tech_keywords = [
    "python", "sql", "excel", "tableau", "pandas", "numpy",
    "machine learning", "data analysis", "power bi", "r", "statistics"
]

def extract_text_from_pdf(uploaded_file):
    pdf = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

def semantic_similarity(text1, text2):
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    score = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return float(score[0][0])

def extract_keywords(text):
    return [kw for kw in tech_keywords if kw.lower() in text.lower()]

def compare_keywords(resume_kws, jd_kws):
    matched = list(set(resume_kws) & set(jd_kws))
    missing = list(set(jd_kws) - set(resume_kws))
    return matched, missing

def generate_suggestions(missing_kws):
    return [f"Consider adding a project or experience with: **{kw}**" for kw in missing_kws]

import pandas as pd

def export_analysis_to_csv(results, filename="resume_analysis.csv"):
    if not isinstance(results, pd.DataFrame):
        df = pd.DataFrame(results)
    else:
        df = results
    df.to_csv(filename, index=False)
    print(f"Analysis results exported to {filename}")