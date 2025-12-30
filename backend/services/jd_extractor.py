import json
from .ollama_client import call_ollama
from .ats_scoring import simple_keyword_extract

def extract_keywords_llm(jd_text: str):
    prompt = (
        "Extract ATS-relevant keywords from the Job Description. "
        "Group into skills (technical), tools/frameworks, and soft_skills. "
        "Return ONLY strict JSON: {\"skills\":[], \"tools\":[], \"soft_skills\":[]}.\n\n"
        f"Job Description:\n{jd_text}\n"
    )
    resp = call_ollama(prompt)
    try:
        return json.loads(resp)
    except Exception:
        # fallback to basic extraction
        tokens = simple_keyword_extract(jd_text)
        return {"skills": tokens[:50], "tools": [], "soft_skills": []}
