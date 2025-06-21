#!/usr/bin/env python3
"""
Production Memory Orchestration Server
FastAPI server with Mem0 Platform API integration for advanced memory management
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import logging

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

# Security and validation
from pydantic import BaseModel, Field
import jwt
from passlib.context import CryptContext

# HTTP clients for Mem0 Platform API
import httpx
import requests

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums
class MemoryType(str, Enum):
    GOAL = "goal"
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    CONTEXT = "context"
    INSIGHT = "insight"
    REFERENCE = "reference"
    CODE_SNIPPET = "code_snippet"
    MEETING_NOTE = "meeting_note"

class MemoryPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SourceType(str, Enum):
    CHATGPT = "chatgpt"
    CURSOR = "cursor"
    VOICE = "voice"
    SLACK = "slack"
    NOTION = "notion"
    EMAIL = "email"
    MANUAL = "manual"

# Configuration
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    MEM0_BASE_URL = "https://api.mem0.ai/v1"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

config = Config()

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for demo (replace with database in production)
users_db = {}
rate_limits = {}

# Mem0 Platform API Client
class Mem0Client:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = config.MEM0_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def add_memory(self, messages: List[Dict], user_id: str, metadata: Dict = None):
        """Add memory using Mem0 Platform API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories",
                    headers=self.headers,
                    json={
                        "messages": messages,
                        "user_id": user_id,
                        "metadata": metadata or {}
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            return {"error": str(e)}
    
    async def search_memories(self, query: str, user_id: str, limit: int = 10):
        """Search memories using Mem0 Platform API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "user_id": user_id,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            return {"results": [], "error": str(e)}

# Initialize Mem0 client
mem0_client = None
if config.MEM0_API_KEY:
    mem0_client = Mem0Client(config.MEM0_API_KEY)
    logger.info("Mem0 Platform API client initialized successfully")
else:
    logger.warning("MEM0_API_KEY not found - memory features will be limited")

# Pydantic models
class UserCreate(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    memory_type: MemoryType = MemoryType.CONTEXT
    priority: MemoryPriority = MemoryPriority.MEDIUM
    source: SourceType = SourceType.MANUAL
    project_id: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MemorySearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    memory_types: Optional[List[MemoryType]] = None
    sources: Optional[List[SourceType]] = None
    project_id: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)

class MemoryResponse(BaseModel):
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    source: SourceType
    project_id: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    importance_score: int

# Security functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Rate limiting
def check_rate_limit(user_id: str) -> bool:
    now = datetime.now(datetime.timezone.utc)
    if user_id not in rate_limits:
        rate_limits[user_id] = []
    
    # Clean old requests
    rate_limits[user_id] = [
        req_time for req_time in rate_limits[user_id]
        if (now - req_time).total_seconds() < config.RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limits[user_id]) >= config.RATE_LIMIT_REQUESTS:
        return False
    
    rate_limits[user_id].append(now)
    return True

# Memory processing
def calculate_importance_score(content: str, memory_type: MemoryType, metadata: Dict) -> int:
    """Calculate importance score based on content, type, and metadata"""
    base_score = 50
    
    type_scores = {
        MemoryType.GOAL: 80,
        MemoryType.DECISION: 70,
        MemoryType.ACTION_ITEM: 75,
        MemoryType.INSIGHT: 65,
        MemoryType.CONTEXT: 50,
        MemoryType.REFERENCE: 40,
        MemoryType.CODE_SNIPPET: 60,
        MemoryType.MEETING_NOTE: 55
    }
    
    score = type_scores.get(memory_type, base_score)
    
    # Content length bonus
    if len(content) > 200:
        score += 10
    elif len(content) < 50:
        score -= 10
    
    # Metadata-based adjustments
    if metadata.get("urgent", False):
        score += 20
    if metadata.get("project_critical", False):
        score += 15
    
    return min(max(score, 0), 100)

def detect_memory_type(content: str) -> MemoryType:
    """Simple heuristic to detect memory type from content"""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["goal", "objective", "aim", "target"]):
        return MemoryType.GOAL
    elif any(word in content_lower for word in ["todo", "task", "action", "need to"]):
        return MemoryType.ACTION_ITEM
    elif any(word in content_lower for word in ["decided", "decision", "choose", "selected"]):
        return MemoryType.DECISION
    elif any(word in content_lower for word in ["insight", "learned", "realized", "discovered"]):
        return MemoryType.INSIGHT
    elif any(word in content_lower for word in ["def ", "class ", "function", "import"]):
        return MemoryType.CODE_SNIPPET
    elif any(word in content_lower for word in ["meeting", "discussed", "agenda"]):
        return MemoryType.MEETING_NOTE
    elif any(word in content_lower for word in ["reference", "documentation", "link", "url"]):
        return MemoryType.REFERENCE
    else:
        return MemoryType.CONTEXT

# Initialize FastAPI app
app = FastAPI(
    title="Memory Orchestration Platform",
    description="Advanced memory management system with Mem0 Platform integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Memory Orchestration Platform starting up...")
    logger.info(f"📊 Mem0 API integration: {'✅ enabled' if mem0_client else '⚠️ disabled (no API key)'}")
    logger.info(f"🔐 Secret key: {'✅ configured' if config.SECRET_KEY != 'your-secret-key-change-in-production' else '⚠️ using default'}")
    logger.info(f"🌍 Environment variables loaded:")
    logger.info(f"   - PORT: {os.getenv('PORT', 'not set')}")
    logger.info(f"   - MEM0_API_KEY: {'✅ set' if config.MEM0_API_KEY else '❌ not set'}")
    logger.info(f"   - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
    logger.info("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Memory Orchestration Platform shutting down...")
    logger.info("✅ Application shutdown complete")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "Memory Orchestration Platform API",
        "version": "1.0.0",
        "status": "operational",
        "mem0_integration": "enabled" if mem0_client else "disabled",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "endpoints": {
            "health": "/health",
            "auth": "/auth/login",
            "memories": "/memories",
            "search": "/memories/search"
        }
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint for Railway debugging"""
    return {
        "status": "ok", 
        "message": "Memory Orchestration Platform is running",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check():
    """Simple health check that always returns healthy for Railway"""
    return {
        "status": "healthy",
        "service": "Memory Orchestration Platform",
        "version": "1.0.0",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "mem0_configured": bool(mem0_client)
    }

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user exists
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password and store user
    hashed_password = hash_password(user_data.password)
    user_id = str(uuid.uuid4())
    
    users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "created_at": datetime.now(datetime.timezone.utc),
    }
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    }

@app.post("/auth/login")
async def login_user(user_data: UserLogin):
    user = users_db.get(user_data.email)
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["id"]
    }

# Memory endpoints
@app.post("/memories", response_model=MemoryResponse)
async def create_memory(
    memory_data: MemoryCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_token)
):
    # Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Auto-detect memory type if not specified
    if memory_data.memory_type == MemoryType.CONTEXT:
        detected_type = detect_memory_type(memory_data.content)
        memory_data.memory_type = detected_type
    
    # Calculate importance score
    importance_score = calculate_importance_score(
        memory_data.content, 
        memory_data.memory_type, 
        memory_data.metadata
    )
    
    # Create memory record
    memory_id = str(uuid.uuid4())
    
    # Enhanced metadata
    enhanced_metadata = {
        **memory_data.metadata,
        "memory_type": memory_data.memory_type.value,
        "priority": memory_data.priority.value,
        "source": memory_data.source.value,
        "project_id": memory_data.project_id,
        "tags": memory_data.tags,
        "importance_score": importance_score,
        "user_id": user_id
    }
    
    # Store in Mem0 Platform if available
    if mem0_client:
        messages = [
            {"role": "user", "content": memory_data.content}
        ]
        background_tasks.add_task(
            store_in_mem0_platform, 
            user_id,
            messages, 
            enhanced_metadata, 
            memory_id
        )
    
    return MemoryResponse(
        id=memory_id,
        content=memory_data.content,
        memory_type=memory_data.memory_type,
        priority=memory_data.priority,
        source=memory_data.source,
        project_id=memory_data.project_id,
        tags=memory_data.tags,
        metadata=enhanced_metadata,
        created_at=datetime.now(datetime.timezone.utc),
        importance_score=importance_score
    )

async def store_in_mem0_platform(user_id: str, messages: List[Dict], metadata: Dict, memory_id: str):
    """Background task to store memory in Mem0 Platform"""
    try:
        if mem0_client:
            result = await mem0_client.add_memory(messages, user_id, metadata)
            logger.info(f"Stored memory {memory_id} in Mem0 Platform: {result}")
    except Exception as e:
        logger.error(f"Failed to store memory {memory_id} in Mem0 Platform: {str(e)}")

@app.post("/memories/search")
async def search_memories(
    search_data: MemorySearch,
    user_id: str = Depends(verify_token)
):
    # Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    results = []
    
    if mem0_client:
        # Use Mem0 Platform API for search
        mem0_results = await mem0_client.search_memories(
            search_data.query, 
            user_id, 
            search_data.limit
        )
        
        if "results" in mem0_results:
            results = mem0_results["results"]
    else:
        # Fallback: basic search simulation
        results = [{
            "id": str(uuid.uuid4()),
            "memory": f"Mock result for: {search_data.query}",
            "score": 0.8,
            "metadata": {"source": "fallback"}
        }]
    
    return {
        "query": search_data.query,
        "results": results,
        "total": len(results),
        "timestamp": datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/memories")
async def get_all_memories(user_id: str = Depends(verify_token)):
    """Get all memories for a user"""
    if mem0_client:
        # This would need to be implemented in Mem0 Platform API
        return {
            "message": "Feature requires Mem0 Platform API extension",
            "user_id": user_id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat()
        }
    else:
        return {
            "memories": [],
            "user_id": user_id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat()
        }

@app.get("/memories/projects")
async def get_user_projects(user_id: str = Depends(verify_token)):
    """Get all projects for a user"""
    return {
        "projects": [],
        "user_id": user_id,
        "timestamp": datetime.now(datetime.timezone.utc).isoformat()
    }

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Depends(verify_token)):
    """Delete a specific memory"""
    return {
        "message": f"Memory {memory_id} deletion requested",
        "user_id": user_id,
        "timestamp": datetime.now(datetime.timezone.utc).isoformat()
    }

@app.post("/memories/add")
async def add_memory_legacy(request: dict, user_id: str = Depends(verify_token)):
    """Legacy endpoint for backward compatibility"""
    content = request.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    memory_data = MemoryCreate(content=content)
    return await create_memory(memory_data, BackgroundTasks(), user_id)

if __name__ == "__main__":
    # Railway sets PORT automatically, fallback to 8090 for local development
    port = int(os.getenv("PORT", 8090))
    # Always bind to 0.0.0.0 for Railway compatibility
    host = "0.0.0.0"
    
    # Use single worker for Railway (auto-scaling platform)
    workers = 1
    
    logger.info(f"🚀 Starting Memory Orchestration Platform on {host}:{port}")
    logger.info(f"👥 Workers: {workers} (Railway optimized)")
    logger.info(f"📊 Mem0 API integration: {'enabled' if mem0_client else 'disabled'}")
    logger.info(f"🔐 Environment: {'production' if os.getenv('RAILWAY_ENVIRONMENT') else 'development'}")
    
    try:
        uvicorn.run(
            "production_mem0_server:app",  # Use string import path for Railway
            host=host,
            port=port,
            workers=workers,  # Single worker for Railway
            reload=False,
            log_level="info",
            access_log=True,
            # Railway-specific optimizations
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise 