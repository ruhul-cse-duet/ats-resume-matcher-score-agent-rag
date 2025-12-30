from sqlalchemy.orm import Session
from . import models
from .auth import hash_password

def create_user(db: Session, email: str, password: str):
    user = models.User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def save_resume(db: Session, user_id: int, filename: str, text: str):
    r = models.Resume(user_id=user_id, filename=filename, text=text)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def save_analysis(db: Session, resume_id: int, jd: str, score: float, matched_keywords: list, analysis_text: str):
    a = models.Analysis(resume_id=resume_id, jd=jd, score=score, matched_keywords=",".join(matched_keywords), analysis_text=analysis_text)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
