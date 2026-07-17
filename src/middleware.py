from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger('uvicorn.acess')
logger.disabled=True

def register_middleware(app:FastAPI):
    
    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        
        
        response = await call_next(request)
    
        message=f"{request.method}-{request.url.path} "
        logger.info(message)
        return response
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_methods = ["*"],
        allow_headers = ["*"],
        allow_credentials = True,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )