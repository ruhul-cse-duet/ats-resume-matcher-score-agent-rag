from backend.services.jd_extractor import extract_keywords_llm

def test_jd_extractor_basic():
    jd = "We need a backend engineer: Python, FastAPI, Docker, AWS"
    out = extract_keywords_llm(jd)
    assert isinstance(out, dict)
    assert "skills" in out
