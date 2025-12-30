from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Header
from .config import Config


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = Config.JWT_SECRET
ALGO = "HS256"
ACCESS_EXPIRE_MINUTES = 60*24*7

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(subject: int) -> str:
    payload = {"sub": str(subject), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)

def decode_token(token: str) -> int:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
        return int(data.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split(" ")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    user_id = decode_token(token)
    return user_id
