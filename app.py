"""Streamlit front end for the AI Resume Analyzer."""
import json
import os

import streamlit as st
from dotenv import load_dotenv

from analyzer import analyze_resume, extract_text_from_pdf

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}
    .hero {background: linear-gradient(135deg,#4f46e5,#7c3aed); padding: 28px 32px;
           border-radius: 16px; color: white; margin-bottom: 24px;}
    .hero h1 {margin: 0; font-size: 2rem;}
    .hero p {margin: 6px 0 0; opacity: .9;}
    .card {border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 18px 20px; height: 100%;}
    .chip {display:inline-block; background:#fee2e2; color:#991b1b; padding:4px 12px;
           border-radius:999px; margin:4px 6px 4px 0; font-size:.85rem; font-weight:500;}
    </style>
    <div class="hero">
        <h1>📄 AI Resume Analyzer</h1>
        <p>Upload your PDF resume and get an ATS score, strengths, weaknesses and missing skills — powered by Google Gemini.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Free key from https://aistudio.google.com/apikey",
    )
    st.caption("Model: gemini-3.5-flash-lite (free tier)")
    st.divider()
    st.markdown("**How it works**\n1. Upload PDF\n2. (Optional) paste a job description\n3. Click Analyze")

# ---------- Inputs ----------
left, right = st.columns([1, 1])
with left:
    uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with right:
    jd = st.text_area(
        "Job description (optional)",
        height=140,
        placeholder="Paste a job description to get a role-specific match score...",
    )

if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not uploaded:
        st.error("Please upload a PDF resume first.")
    else:
        try:
            with st.spinner("Reading your resume and analyzing with Gemini..."):
                text = extract_text_from_pdf(uploaded)
                st.session_state["result"] = analyze_resume(text, api_key, jd)
        except Exception as e:  # show friendly error
            st.error(f"Something went wrong: {e}")

# ---------- Results ----------
result = st.session_state.get("result")
if result:
    score = result["ats_score"]
    color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"

    st.divider()
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("ATS Score", f"{score}/100")
        st.progress(score / 100)
        st.write(f"{color} " + ("Strong" if score >= 75 else "Fair" if score >= 50 else "Needs work"))
    with c2:
        st.subheader("Summary")
        st.write(result["summary"])

    a, b = st.columns(2)
    with a:
        st.markdown("### ✅ Strengths")
        for s in result["strengths"]:
            st.success(s)
    with b:
        st.markdown("### ⚠️ Weaknesses")
        for w in result["weaknesses"]:
            st.warning(w)

    st.markdown("### 🧩 Missing Skills")
    if result["missing_skills"]:
        st.markdown(
            "".join(f'<span class="chip">{s}</span>' for s in result["missing_skills"]),
            unsafe_allow_html=True,
        )
    else:
        st.write("No major gaps found.")

    st.markdown("### 💡 Suggestions")
    for i, s in enumerate(result["suggestions"], 1):
        st.info(f"{i}. {s}")

    with st.expander("View raw JSON"):
        st.json(result)
    st.download_button(
        "⬇️ Download report (JSON)",
        data=json.dumps(result, indent=2),
        file_name="resume_analysis.json",
        mime="application/json",
    )
