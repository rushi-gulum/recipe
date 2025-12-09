# Request logging middleware
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        body = await request.body()
        try:
            req_text = body.decode("utf-8") if body else ""
        except Exception:
            req_text = str(body)
        logger.info(f"[API-IN] {request.method} {request.url} body={req_text}")
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        logger.info(f"[API-OUT] {request.method} {request.url} status={response.status_code} time_ms={elapsed:.1f}")
        return response

# Legacy function for backward compatibility
async def log_requests(request: Request, call_next):
    """Log incoming requests and response times"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response