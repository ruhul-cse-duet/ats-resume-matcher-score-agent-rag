from .ollama_client import call_ollama

def rewrite_resume_ats(resume_text: str, jd_text: str):
    prompt = (
        "You are an expert resume writer. Rewrite the resume content to be ATS-optimized for the given Job Description. "
        "Do NOT invent any new experience or skills. Use bullet points and metrics when possible. "
        "Return JSON: {\"summary\": \"...\", \"experience\": [...], \"skills\": [...]}.\n\n"
        f"JOB DESCRIPTION:\n{jd_text}\n\nRESUME:\n{resume_text}\n"
    )
    resp = call_ollama(prompt)
    # try parse; if not JSON, return as text
    import json
    try:
        return json.loads(resp)
    except Exception:
        return {"rewritten": resp}
