import streamlit as st
from utils.analyzer import (
    extract_text_from_pdf, semantic_similarity,
    extract_keywords, compare_keywords, generate_suggestions
)
import pandas as pd

st.set_page_config(page_title="AI Resume Analyzer", page_icon="�", layout="centered")

# --- Load Custom CSS ---
def load_css(file_name):
    """Loads a CSS file and applies it to the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: Could not find {file_name}. Please ensure it's in the same directory as app.py.")

# Make sure style.css is in the same directory as app.py
load_css("style.css")

# --- Header Section ---
# Using a container for the header to apply consistent styling
with st.container():
    # Adjusted columns to place logo on the left and title on the right
    col_logo, col_title_text = st.columns([0.5, 3]) # Smaller column for logo, larger for text
    with col_logo:
        # Using the uploaded logo image. Ensure this path is correct relative to app.py
        st.image("assets/hi.png", width=80) # Adjusted width for side placement
    with col_title_text:
        st.markdown("<h1 style='text-align: left; border-bottom: none; padding-bottom: 0;'>GotIT - An AI-Powered Resume Analyzer</h1>", unsafe_allow_html=True)
        st.markdown("Compare your resume with a job description and get intelligent feedback!")

st.markdown("---") # Separator

# --- Input Section ---
with st.container():
    st.markdown("<div class='input-section-container'>", unsafe_allow_html=True)
    st.subheader("Upload Resume & Job Description")
    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], help="Please upload your resume in PDF format.")
    jd_text = st.text_area("Paste the job description here:", height=200, help="Copy and paste the full job description text.")
    
    # Add an "Analyze" button to explicitly trigger analysis
    analyze_button = st.button("Analyze Resume", help="Click to analyze your resume against the job description.")
    st.markdown("</div>", unsafe_allow_html=True)


def export_analysis_to_csv(results, filename="resume_analysis.csv"):
    """Exports the analysis results to a CSV file."""
    df = pd.DataFrame([results])
    # Convert lists to comma-separated strings for CSV
    df["Matched Keywords"] = df["Matched Keywords"].apply(lambda x: ", ".join(x))
    df["Missing Keywords"] = df["Missing Keywords"].apply(lambda x: ", ".join(x))
    df["Suggestions"] = df["Suggestions"].apply(lambda x: " | ".join(x))
    
    st.download_button(
        label="Download Analysis as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=filename,
        mime="text/csv",
    )
    st.success("Analysis ready for download!")


if analyze_button and resume_file and jd_text:
    # Display a spinner while processing
    with st.spinner("Analyzing your resume... This might take a moment."):
        resume_text = extract_text_from_pdf(resume_file)
        sim_score = semantic_similarity(resume_text, jd_text)
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(jd_text)
        matched, missing = compare_keywords(resume_keywords, jd_keywords)
        suggestions = generate_suggestions(missing)

    st.success("Analysis complete! See the results below.")
    st.markdown("---") # Separator

    # --- Overall Score Section ---
    with st.container():
        st.subheader("📊 Overall Analysis")
        
        # Determine color based on similarity score
        score_percentage = round(sim_score * 100, 2)
        score_color = "#28a745" if score_percentage >= 75 else "#dc3545" # Green for >=75, Red otherwise
        unfilled_color = "#e9ecef" # Light gray for the unfilled part of the circle

        # Use columns for better layout of the score
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Circular progress bar using HTML/CSS classes
            st.markdown(
                f"""
                <div class="score-container">
                    <div class="circular-progress" style="background: conic-gradient({score_color} { score_percentage}%, {unfilled_color} {score_percentage}%);">
                        <div class="inner-circle">
                            <h2 class="score-value" style="color: {score_color};">{int(score_percentage)}</h2>
                            <p class="score-label">out of 100</p>
                        </div>
                    </div>
                    <h3 style='text-align: center; color: #333; margin-top: 20px;'>Overall Score: {score_percentage}%</h3>
                    <p style='text-align: center; color: #555;'>This score reflects your resume's effectiveness based on our AI analysis.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---") # Separator

    # --- Strengths (Matched Keywords) ---
    with st.container():
        with st.expander("View Strengths ", expanded=True):
            if matched:
                #st.markdown("<div class='stBlock'>", unsafe_allow_html=True)
                st.markdown("#### ✅ Matched Keywords")
                for keyword in matched:
                    st.markdown(f"- <span class='matched-keyword'>{keyword}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No direct keyword matches found. Consider reviewing the job description for key terms.")

    st.markdown("---") # Separator

    # --- Weaknesses / Improvement Suggestions ---
    with st.container():
        with st.expander(" View Areas for Improvement", expanded=True):
            if missing or suggestions:
               # st.markdown("<div class='stBlock'>", unsafe_allow_html=True)
                if missing:
                    st.markdown("#### ❌ Missing Keywords")
                    for keyword in missing:
                        st.markdown(f"- <span class='missing-keyword'>{keyword}</span>", unsafe_allow_html=True)
                
                if suggestions:
                    st.markdown("#### 📝 Suggestions to Enhance Your Resume")
                    for s in suggestions:
                        st.markdown(f"- {s}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.success("Your resume seems to cover all key aspects of the job description! Great job!")

    st.markdown("---") # Separator

    with st.container():
        # Prepare results dict for export
        results = {
            "Similarity": sim_score,
            "Matched Keywords": matched, # Keep as list for internal processing, convert for CSV export
            "Missing Keywords": missing,
            "Suggestions": suggestions
        }

        st.subheader("Export Analysis")
        export_analysis_to_csv(results)

