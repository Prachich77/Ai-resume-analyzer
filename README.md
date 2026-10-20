# 📄 AI Resume Analyzer

An LLM-powered web app that reads a PDF resume and returns an **ATS score, strengths,
weaknesses, missing skills and improvement suggestions** as structured JSON, displayed
in a clean Streamlit interface. Optionally paste a job description for a role-specific match.

## Tech stack
- Python 3.10+
- Google Gemini 3.5 Flash Lite (free tier) via `google-genai`
- pypdf (PDF text extraction)
- Streamlit (front end)

## How it works
1. **Extract** – `pypdf` pulls the text out of the uploaded PDF.
2. **Prompt** – the text (plus optional job description) is wrapped in a prompt that forces a fixed JSON schema.
3. **Analyze** – Gemini returns the JSON (`response_mime_type="application/json"`).
4. **Display** – Streamlit renders the score, cards, skill chips and a downloadable report.

## Project structure
```
ai-resume-analyzer/
├── app.py            # Streamlit UI
├── analyzer.py       # PDF extraction + Gemini call
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup
```bash
git clone https://github.com/<your-username>/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then paste your key into .env
streamlit run app.py
```
Get a free API key at https://aistudio.google.com/apikey

## Limitations
- Scanned/image-only PDFs have no extractable text (OCR not included).
- The ATS score is an AI estimate, not the output of a real ATS.

## Roadmap
- OCR support, DOCX upload, multi-resume comparison, rewrite suggestions.
