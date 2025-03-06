"""
Main entry point for the FastAPI application.
"""

import os
import uvicorn
from app.core.app import create_app
from dotenv import load_dotenv
import logfire

load_dotenv()

app = create_app()

logfire.configure()
logfire.instrument_fastapi(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
