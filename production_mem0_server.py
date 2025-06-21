#!/usr/bin/env python3
"""
Production Memory Orchestration Server
Enhanced FastAPI server with security, scalability, and advanced memory management
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

# Memory and AI
from mem0 import Memory
import asyncio

# Load environment
from dotenv import load_dotenv
load_dotenv("mem0.env")

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
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

config = Config()

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for demo (replace with database in production)
users_db = {}
memories_db = {}
rate_limits = {}

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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
    now = datetime.utcnow()
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
    
    return max(10, min(100, score))

def detect_memory_type(content: str) -> MemoryType:
    """Auto-detect memory type from content"""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["goal", "objective", "target", "aim"]):
        return MemoryType.GOAL
    elif any(word in content_lower for word in ["todo", "task", "action", "need to"]):
        return MemoryType.ACTION_ITEM
    elif any(word in content_lower for word in ["decided", "decision", "concluded"]):
        return MemoryType.DECISION
    elif any(word in content_lower for word in ["insight", "learned", "discovered"]):
        return MemoryType.INSIGHT
    elif any(word in content_lower for word in ["code", "function", "class", "def"]):
        return MemoryType.CODE_SNIPPET
    elif any(word in content_lower for word in ["meeting", "discussed", "agenda"]):
        return MemoryType.MEETING_NOTE
    
    return MemoryType.CONTEXT

# Initialize Memory service
memory_service = None
try:
    if config.OPENAI_API_KEY:
        memory_service = Memory()
        logger.info("Mem0 service initialized successfully")
    else:
        logger.warning("OpenAI API key not set")
except Exception as e:
    logger.error(f"Failed to initialize Mem0: {e}")

# FastAPI app
app = FastAPI(
    title="Memory Orchestration Platform",
    description="Production-ready memory management for AI workflows",
    version="2.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/")
async def root():
    return {
        "service": "Memory Orchestration Platform",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if memory_service else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "memory": memory_service is not None,
            "openai_configured": bool(config.OPENAI_API_KEY)
        }
    }

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user exists
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "api_key": str(uuid.uuid4())
    }
    
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "api_key": users_db[user_data.email]["api_key"]
    }

@app.post("/auth/login")
async def login_user(user_data: UserLogin):
    user = users_db.get(user_data.email)
    
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account disabled")
    
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
    
    # Auto-detect memory type if needed
    if memory_data.memory_type == MemoryType.CONTEXT:
        detected_type = detect_memory_type(memory_data.content)
        memory_data.memory_type = detected_type
    
    # Calculate importance score
    importance_score = calculate_importance_score(
        memory_data.content, memory_data.memory_type, memory_data.metadata
    )
    
    # Create memory record
    memory_id = str(uuid.uuid4())
    memory_record = {
        "id": memory_id,
        "user_id": user_id,
        "content": memory_data.content,
        "memory_type": memory_data.memory_type,
        "priority": memory_data.priority,
        "source": memory_data.source,
        "project_id": memory_data.project_id,
        "tags": memory_data.tags,
        "metadata": memory_data.metadata,
        "created_at": datetime.utcnow(),
        "importance_score": importance_score
    }
    
    # Store in memory database
    if user_id not in memories_db:
        memories_db[user_id] = {}
    memories_db[user_id][memory_id] = memory_record
    
    # Store in Mem0 (background task)
    if memory_service:
        background_tasks.add_task(
            store_in_mem0,
            user_id,
            memory_data.content,
            memory_data.metadata,
            memory_id
        )
    
    return MemoryResponse(**memory_record)

async def store_in_mem0(user_id: str, content: str, metadata: Dict, memory_id: str):
    """Background task to store in Mem0"""
    try:
        if memory_service:
            messages = [{"role": "user", "content": content}]
            result = memory_service.add(
                messages=messages,
                user_id=user_id,
                metadata={**metadata, "memory_id": memory_id}
            )
            logger.info(f"Memory {memory_id} stored in Mem0: {result}")
    except Exception as e:
        logger.error(f"Failed to store in Mem0: {e}")

@app.post("/memories/search")
async def search_memories(
    search_data: MemorySearch,
    user_id: str = Depends(verify_token)
):
    # Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    user_memories = memories_db.get(user_id, {})
    results = []
    
    # Filter memories
    for memory in user_memories.values():
        # Text search
        if search_data.query.lower() not in memory["content"].lower():
            continue
        
        # Type filter
        if search_data.memory_types and memory["memory_type"] not in search_data.memory_types:
            continue
        
        # Source filter
        if search_data.sources and memory["source"] not in search_data.sources:
            continue
        
        # Project filter
        if search_data.project_id and memory["project_id"] != search_data.project_id:
            continue
        
        results.append(MemoryResponse(**memory))
    
    # Sort by importance and limit
    results.sort(key=lambda x: x.importance_score, reverse=True)
    results = results[:search_data.limit]
    
    # Also search in Mem0 if available
    mem0_results = []
    if memory_service:
        try:
            mem0_search = memory_service.search(
                query=search_data.query,
                user_id=user_id,
                limit=search_data.limit
            )
            if mem0_search:
                mem0_results = mem0_search
        except Exception as e:
            logger.error(f"Mem0 search failed: {e}")
    
    return {
        "query": search_data.query,
        "results": results,
        "mem0_results": mem0_results,
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/memories")
async def get_all_memories(user_id: str = Depends(verify_token)):
    """Get all memories for a user"""
    user_memories = memories_db.get(user_id, {})
    results = [MemoryResponse(**memory) for memory in user_memories.values()]
    
    # Sort by creation date
    results.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "memories": results,
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/memories/projects")
async def get_user_projects(user_id: str = Depends(verify_token)):
    """Get all projects for a user"""
    user_memories = memories_db.get(user_id, {})
    projects = set()
    
    for memory in user_memories.values():
        if memory["project_id"]:
            projects.add(memory["project_id"])
    
    return {
        "projects": list(projects),
        "total": len(projects)
    }

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Depends(verify_token)):
    """Delete a specific memory"""
    user_memories = memories_db.get(user_id, {})
    
    if memory_id not in user_memories:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    del user_memories[memory_id]
    
    return {"message": "Memory deleted successfully", "memory_id": memory_id}

# Legacy endpoints for backward compatibility
@app.post("/memories/add")
async def add_memory_legacy(request: dict, user_id: str = Depends(verify_token)):
    """Legacy endpoint for backward compatibility"""
    messages = request.get("messages", [])
    metadata = request.get("metadata", {})
    
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    content = messages[0].get("content", "")
    
    memory_data = MemoryCreate(
        content=content,
        metadata=metadata,
        source=SourceType.CHATGPT
    )
    
    background_tasks = BackgroundTasks()
    return await create_memory(memory_data, background_tasks, user_id)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8090))
    logger.info(f"Starting Memory Orchestration Server on port {port}")
    uvicorn.run(
        "production_mem0_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    ) 