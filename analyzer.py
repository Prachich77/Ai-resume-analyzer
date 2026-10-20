"""Core logic: PDF text extraction + Gemini analysis."""
import json
import re
from typing import Optional

from google import genai
from pypdf import PdfReader

MODEL_NAME = "gemini-3.5-flash-lite"

PROMPT_TEMPLATE = """You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
Analyze the resume below{jd_clause}.

Return ONLY valid JSON (no markdown, no commentary) with exactly this schema:
{{
  "ats_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<point>", ...],
  "weaknesses": ["<point>", ...],
  "missing_skills": ["<skill>", ...],
  "suggestions": ["<specific, actionable improvement>", ...]
}}

Scoring guide: formatting & structure, keyword relevance, quantified achievements,
clarity, and {jd_score_note}.

{jd_block}RESUME:
\"\"\"
{resume_text}
\"\"\"
"""


def extract_text_from_pdf(file) -> str:
    """Extract text from an uploaded PDF (file path or file-like object)."""
    reader = PdfReader(file)
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages).strip()


def _parse_json(raw: str) -> dict:
    """Parse model output into a dict, tolerating stray code fences."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def analyze_resume(
    resume_text: str, api_key: str, job_description: Optional[str] = None
) -> dict:
    """Send the resume to Gemini and return the structured analysis."""
    if not resume_text:
        raise ValueError("No text could be extracted from the PDF (it may be a scanned image).")

    jd = (job_description or "").strip()
    prompt = PROMPT_TEMPLATE.format(
        jd_clause=" against the job description provided" if jd else "",
        jd_score_note="match with the job description" if jd else "general industry relevance",
        jd_block=f'JOB DESCRIPTION:\n"""\n{jd}\n"""\n\n' if jd else "",
        resume_text=resume_text[:15000],
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    data = _parse_json(response.text)

    # Normalise so the UI never breaks on missing keys
    data["ats_score"] = max(0, min(100, int(data.get("ats_score", 0))))
    for key in ("strengths", "weaknesses", "missing_skills", "suggestions"):
        data[key] = data.get(key) or []
    data["summary"] = data.get("summary", "")
    return data
