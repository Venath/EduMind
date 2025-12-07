"""
API Dependencies - Database sessions, authentication, etc.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Optional: Add authentication dependency
# Uncomment and customize when you add authentication

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# 
# security = HTTPBearer()
# 
# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
#     """
#     Verify JWT token
#     """
#     token = credentials.credentials
#     
#     # TODO: Implement JWT verification
#     # For now, just return token
#     # In production, verify token with secret key
#     
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     
#     return token

