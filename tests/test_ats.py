import pytest
from backend.services.ats_scoring import semantic_score

def test_semantic_score_similarity():
    resume = "Experienced Python developer with experience in Django, REST APIs, Docker"
    jd = "Looking for Python developer with Docker and REST API experience"
    score = semantic_score(resume, jd)
    assert score > 20
