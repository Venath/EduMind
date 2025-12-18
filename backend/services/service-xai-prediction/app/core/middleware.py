from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException as StarletteHTTPException
import logging
import time 
from typing import Callable

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next: callable):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc) if logger.level == logging.DEBUG else "An error occured"
            }
        )
        
async def logging_middleware(request: Request, call_next: Callable):
    """Request/response logging middleware"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request) 
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} -"
        f"Duration: {process_time:.3f}s"
    )
    
    return response

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )
    
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail}
    )
