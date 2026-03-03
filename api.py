from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from dotenv import load_dotenv

# Load env variables since agent relies on them
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Import the core modules from our agent
from generators.content_generator import ContentGenerator, POST_TYPES
from agent import _get_publisher, _enabled_platforms

app = FastAPI(title="RunesCard Social Agent API")

# Setup CORS to allow Next.js local frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    platform: str
    post_type: str = "random"
    extra_hint: str = ""

class GenerateResponse(BaseModel):
    text: str

class PublishRequest(BaseModel):
    platform: str
    text: str

class PublishResponse(BaseModel):
    success: bool
    result: str

@app.get("/api/config")
def get_config():
    """Returns available options for the frontend."""
    return {
        "platforms": _enabled_platforms(),
        "post_types": POST_TYPES + ["random"]
    }

@app.post("/api/generate", response_model=GenerateResponse)
def generate_post(req: GenerateRequest):
    """Generates a post and returns the text without publishing."""
    try:
        generator = ContentGenerator()
        
        # If random, pass None to the generator
        ptype = None if req.post_type == "random" else req.post_type
        
        text = generator.generate(req.platform, ptype, req.extra_hint)
        return GenerateResponse(text=text)
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Generation failed: {err_msg}")
        if "429 RESOURCE_EXHAUSTED" in err_msg or "limit: 0" in err_msg:
            clean_msg = "Gemini API Quota Exceeded (Limit: 0). Your API key does not have access to the Free Tier in your region, or you need to enable billing in Google AI Studio. Alternatively, switch to OpenAI in your .env file."
            raise HTTPException(status_code=429, detail=clean_msg)
        raise HTTPException(status_code=500, detail=err_msg)

@app.post("/api/publish", response_model=PublishResponse)
def publish_post(req: PublishRequest):
    """Actually publishes the given text to the platform."""
    try:
        publisher = _get_publisher(req.platform)
        if not publisher:
            raise HTTPException(status_code=400, detail=f"Publisher for {req.platform} could not be initialized. Check keys.")
        
        result = publisher.post(req.text)
        return PublishResponse(success=True, result=str(result))
    except Exception as e:
        logger.error(f"Publishing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
