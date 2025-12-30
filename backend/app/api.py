from fastapi import UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .database import engine, Base, SessionLocal
from . import models, crud, schemas
from .auth import create_access_token, verify_password, get_current_user, hash_password
from backend.services.parser import parse_upload
from backend.services.ollama_client import call_ollama
from backend.services.jd_extractor import extract_keywords_llm
from backend.services.ats_scoring import semantic_score
from backend.services.resume_rewriter import rewrite_resume_ats
from backend.services.embeddings_index import EmbeddingsIndex
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/signup", response_model=schemas.TokenResponse)
def signup(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Register a new user with comprehensive error handling"""
    try:
        # Validate email format
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid email format"
            )
        
        # Validate password strength
        if not password or len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Password must be at least 6 characters"
            )
        
        # Check if user exists
        existing_user = crud.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        
        # Create user
        user = crud.create_user(db, email, password)
        token = create_access_token(user.id)
        
        logger.info(f"User created successfully: {email}")
        return {"access_token": token, "user_id": user.id}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during signup: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during signup"
        )
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/auth/login", response_model=schemas.TokenResponse)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Authenticate user with comprehensive error handling"""
    try:
        # Validate input
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Get user
        user = crud.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create token
        token = create_access_token(user.id)
        logger.info(f"User logged in: {email}")
        return {"access_token": token, "user_id": user.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.post("/analyze")
def analyze(
    resume: UploadFile = File(...), 
    jd: str = Form(...), 
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
):
    """Analyze resume against job description with comprehensive error handling"""
    try:
        # Validate inputs
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file is required"
            )
        
        if not jd or len(jd.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description must be at least 10 characters"
            )
        
        # Validate file size (10MB limit)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        resume.file.seek(0, 2)  # Seek to end
        file_size = resume.file.tell()
        resume.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(resume.filename.lower())[1]
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Parse resume
        try:
            parsed = parse_upload(resume)
            if not parsed or len(parsed.strip()) < 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to extract meaningful text from resume"
                )
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse resume file"
            )
        
        # Save resume to database
        try:
            r = crud.save_resume(db, user_id, resume.filename, parsed)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving resume: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume"
            )
        
        # Extract keywords with fallback
        try:
            jd_keywords = extract_keywords_llm(jd)
            matched = [k for k in jd_keywords.get("skills", []) if k.lower() in parsed.lower()]
        except Exception as e:
            logger.warning(f"Error extracting keywords: {str(e)}")
            matched = []
            jd_keywords = {"skills": [], "tools": [], "soft_skills": []}
        
        # Calculate semantic score
        try:
            score = semantic_score(parsed, jd)
        except Exception as e:
            logger.warning(f"Error calculating semantic score: {str(e)}")
            score = 0.0
        
        # RAG: fetch top context from resume paragraphs
        try:
            paras = [p for p in parsed.split("\n\n") if p.strip()]
            emb = EmbeddingsIndex(model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
            
            if paras:
                emb.build(paras[:128])
                top = emb.query(jd, k=3)
                context_text = "\n\n".join(t for t, sc in top)
            else:
                context_text = parsed[:1000]
        except Exception as e:
            logger.warning(f"Error building embeddings index: {str(e)}")
            context_text = parsed[:1000]
        
        # Generate analysis with LLM
        try:
            prompt = (
                "You are an ATS resume evaluator. Using the context and job description, provide concise analysis.\n\n"
                f"Context:\n{context_text}\n\nJob Description:\n{jd}\n"
            )
            analysis = call_ollama(prompt)
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            analysis = "LLM service unavailable. Basic analysis: Score calculated based on semantic similarity."
        
        # Save analysis
        try:
            a = crud.save_analysis(db, r.id, jd, score, matched, analysis)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving analysis: {str(e)}")
            db.rollback()
            # Continue even if save fails
        
        logger.info(f"Analysis completed for resume {r.id}, score: {score}")
        return {
            "resume_id": r.id, 
            "score": score, 
            "matched_keywords": matched, 
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
        )

@router.post("/rewrite")
def rewrite(
    resume_text: str = Form(...), 
    jd: str = Form(...), 
    user_id: int = Depends(get_current_user)
):
    """Rewrite resume to be ATS-optimized with error handling"""
    try:
        # Validate inputs
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume text must be at least 50 characters"
            )
        
        if not jd or len(jd.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description must be at least 10 characters"
            )
        
        # Rewrite resume
        try:
            out = rewrite_resume_ats(resume_text, jd)
            logger.info(f"Resume rewritten successfully for user {user_id}")
            return out
        except Exception as e:
            logger.error(f"Error rewriting resume: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rewrite resume. LLM service may be unavailable."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during rewrite: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during rewrite"
        )
