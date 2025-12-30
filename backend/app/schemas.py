from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    user_id: int


class AnalyzeResponse(BaseModel):
    resume_id: int
    score: float
    matched_keywords: List[str]
    analysis: str
