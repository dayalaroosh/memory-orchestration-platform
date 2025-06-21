#!/usr/bin/env python3
"""
Production Memory Orchestration Server
FastAPI server with Mem0 Platform API integration for advanced memory management
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import logging
import re

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

# Security and validation
from pydantic import BaseModel, Field
import jwt  # PyJWT - Modern JWT library
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
    except jwt.InvalidTokenError:  # Updated exception for PyJWT
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Rate limiting
def check_rate_limit(user_id: str) -> bool:
    now = datetime.now(timezone.utc)
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

# Simple API key for Custom GPT
CUSTOM_GPT_API_KEY = "memory-gpt-2025-key"

def verify_simple_auth(authorization: str = Header(None)):
    """Simple API key authentication for Custom GPT"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Handle both "Bearer token" and "token" formats
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    # For Custom GPT, accept the simple API key
    if token == CUSTOM_GPT_API_KEY:
        return "custom-gpt-user"
    
    # Also try JWT token verification
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check():
    """Simple health check that always returns healthy for Railway"""
    return {
        "status": "healthy",
        "service": "Memory Orchestration Platform",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mem0_configured": bool(mem0_client)
    }

@app.get("/test-auth")
async def test_auth_endpoint():
    """Test endpoint that doesn't require authentication"""
    return {
        "status": "ok",
        "message": "This endpoint works without authentication",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "auth_required": False
    }

@app.post("/test-memory")
async def test_memory_endpoint(data: dict):
    """Test memory endpoint without authentication for debugging"""
    return {
        "status": "success",
        "message": "Memory test endpoint working",
        "received_data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
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
        "created_at": datetime.now(timezone.utc),
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
        created_at=datetime.now(timezone.utc),
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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/memories")
async def get_all_memories(user_id: str = Depends(verify_token)):
    """Get all memories for a user"""
    if mem0_client:
        # This would need to be implemented in Mem0 Platform API
        return {
            "message": "Feature requires Mem0 Platform API extension",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        return {
            "memories": [],
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/memories/projects")
async def get_user_projects(user_id: str = Depends(verify_token)):
    """Get all projects for a user"""
    return {
        "projects": [],
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Depends(verify_token)):
    """Delete a specific memory"""
    return {
        "message": f"Memory {memory_id} deletion requested",
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/memories/add")
async def add_memory_legacy(request: dict, user_id: str = Depends(verify_token)):
    """Legacy endpoint for backward compatibility"""
    content = request.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    memory_data = MemoryCreate(content=content)
    return await create_memory(memory_data, BackgroundTasks(), user_id)

# Simplified endpoints for Custom GPT
@app.post("/gpt/memories")
async def add_memory_for_gpt(
    data: dict,
    user_id: str = Depends(verify_simple_auth)
):
    """Simplified memory addition for Custom GPT"""
    try:
        memory_content = data.get("memory", data.get("content", ""))
        if not memory_content:
            raise HTTPException(status_code=400, detail="Memory content is required")
        
        # Create a simple memory entry
        memory_id = str(uuid.uuid4())
        memory_entry = {
            "id": memory_id,
            "content": memory_content,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "metadata": data.get("metadata", {})
        }
        
        # Store in local storage (simple dict for now)
        if not hasattr(app.state, "memories"):
            app.state.memories = {}
        
        if user_id not in app.state.memories:
            app.state.memories[user_id] = []
        
        app.state.memories[user_id].append(memory_entry)
        
        # Also try to store in Mem0 if available
        if mem0_client:
            try:
                messages = [{"role": "user", "content": memory_content}]
                await mem0_client.add_memory(messages, user_id, data.get("metadata", {}))
            except Exception as e:
                logger.warning(f"Failed to store in Mem0: {e}")
        
        return {
            "message": "Memory added successfully",
            "memory_id": memory_id,
            "content": memory_content
        }
        
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")

@app.post("/gpt/search")
async def search_memories_for_gpt(
    data: dict,
    user_id: str = Depends(verify_simple_auth)
):
    """Simplified memory search for Custom GPT"""
    try:
        query = data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        results = []
        
        # Search in local storage
        if hasattr(app.state, "memories") and user_id in app.state.memories:
            for memory in app.state.memories[user_id]:
                if query.lower() in memory["content"].lower():
                    results.append({
                        "memory": memory["content"],
                        "score": 0.8,  # Simple scoring
                        "created_at": memory["created_at"].isoformat()
                    })
        
        # Also search in Mem0 if available
        if mem0_client:
            try:
                mem0_results = await mem0_client.search_memories(query, user_id, limit=5)
                if mem0_results and "memories" in mem0_results:
                    for mem in mem0_results["memories"]:
                        results.append({
                            "memory": mem.get("memory", mem.get("content", "")),
                            "score": mem.get("score", 0.5),
                            "source": "mem0"
                        })
            except Exception as e:
                logger.warning(f"Failed to search Mem0: {e}")
        
        return {
            "results": results[:10],  # Limit to 10 results
            "total_results": len(results),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")

def parse_memory_command(text: str) -> Tuple[str, str, Dict]:
    """Parse natural language memory commands"""
    text = text.strip().lower()
    
    # Command patterns
    patterns = {
        'remember': [
            r'^/?remember\s+(.+)',
            r'^/?save\s+(.+)',
            r'remember that (.+)',
            r'save this:?\s*(.+)'
        ],
        'recall': [
            r'^/?recall\s+(.+)',
            r'^/?search\s+(.+)', 
            r'what did i say about (.+)',
            r'find (.+)',
            r'search for (.+)'
        ]
    }
    
    for command, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                return command, content, {}
    
    return None, text, {}

def detect_memory_worthy_content(text: str) -> List[Dict]:
    """Detect content that should be automatically remembered"""
    memory_patterns = [
        (r'i prefer (.+)', 'preference'),
        (r'my goal is (.+)', 'goal'),
        (r'i work at (.+)', 'personal_info'),
        (r'i\'m working on (.+)', 'project'),
        (r'i decided to (.+)', 'decision'),
        (r'i learned (.+)', 'insight'),
        (r'important:?\s*(.+)', 'important'),
        (r'note:?\s*(.+)', 'note')
    ]
    
    suggestions = []
    for pattern, memory_type in memory_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            content = match.group(1).strip()
            suggestions.append({
                'content': content,
                'type': memory_type,
                'confidence': 0.8,
                'full_match': match.group(0)
            })
    
    return suggestions

# New endpoints for ChatGPT Actions
@app.post("/gpt/trigger-memory")
async def trigger_memory_action(
    data: dict,
    user_id: str = Depends(verify_simple_auth)
):
    """Process memory trigger commands from regular ChatGPT"""
    try:
        command = data.get("command", "").lower()
        content = data.get("content", "")
        user_context = data.get("user_context", "")
        metadata = data.get("metadata", {})
        
        if not content:
            # Try to parse command from content
            parsed_command, parsed_content, parsed_metadata = parse_memory_command(content or user_context)
            if parsed_command:
                command = parsed_command
                content = parsed_content
                metadata.update(parsed_metadata)
        
        if command == "remember" or command == "save":
            # Add memory
            memory_id = str(uuid.uuid4())
            memory_entry = {
                "id": memory_id,
                "content": content,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "metadata": {
                    **metadata,
                    "source": "chatgpt_trigger",
                    "command": command
                }
            }
            
            # Store locally
            if not hasattr(app.state, "memories"):
                app.state.memories = {}
            if user_id not in app.state.memories:
                app.state.memories[user_id] = []
            app.state.memories[user_id].append(memory_entry)
            
            # Try Mem0 if available
            if mem0_client:
                try:
                    messages = [{"role": "user", "content": content}]
                    await mem0_client.add_memory(messages, user_id, metadata)
                except Exception as e:
                    logger.warning(f"Mem0 storage failed: {e}")
            
            return {
                "success": True,
                "action": "remembered",
                "result": f"✅ Saved: {content[:50]}{'...' if len(content) > 50 else ''}",
                "memory_id": memory_id
            }
            
        elif command == "recall" or command == "search":
            # Search memories
            results = []
            
            # Search local storage
            if hasattr(app.state, "memories") and user_id in app.state.memories:
                for memory in app.state.memories[user_id]:
                    if content.lower() in memory["content"].lower():
                        results.append({
                            "content": memory["content"],
                            "score": 0.8,
                            "created_at": memory["created_at"].isoformat()
                        })
            
            # Search Mem0 if available
            if mem0_client:
                try:
                    mem0_results = await mem0_client.search_memories(content, user_id, limit=5)
                    if mem0_results and "memories" in mem0_results:
                        for mem in mem0_results["memories"]:
                            results.append({
                                "content": mem.get("memory", mem.get("content", "")),
                                "score": mem.get("score", 0.5),
                                "source": "mem0"
                            })
                except Exception as e:
                    logger.warning(f"Mem0 search failed: {e}")
            
            return {
                "success": True,
                "action": "recalled",
                "result": f"🔍 Found {len(results)} memories about '{content}'",
                "memories": results[:5]  # Limit to 5 results
            }
        
        else:
            return {
                "success": False,
                "action": "unknown",
                "result": f"❌ Unknown command: {command}. Use 'remember' or 'recall'."
            }
            
    except Exception as e:
        logger.error(f"Error in trigger_memory_action: {e}")
        return {
            "success": False,
            "action": "error",
            "result": f"❌ Error: {str(e)}"
        }

@app.post("/gpt/smart-detect")
async def smart_detect_memory(
    data: dict,
    user_id: str = Depends(verify_simple_auth)
):
    """Automatically detect memory-worthy content"""
    try:
        conversation_text = data.get("conversation_text", "")
        
        suggestions = detect_memory_worthy_content(conversation_text)
        should_remember = len(suggestions) > 0
        
        # Auto-save high-confidence suggestions
        auto_saved = False
        if should_remember:
            for suggestion in suggestions:
                if suggestion["confidence"] > 0.7:
                    # Auto-save this memory
                    memory_id = str(uuid.uuid4())
                    memory_entry = {
                        "id": memory_id,
                        "content": suggestion["content"],
                        "user_id": user_id,
                        "created_at": datetime.now(timezone.utc),
                        "metadata": {
                            "type": suggestion["type"],
                            "auto_detected": True,
                            "confidence": suggestion["confidence"],
                            "source": "smart_detection"
                        }
                    }
                    
                    # Store locally
                    if not hasattr(app.state, "memories"):
                        app.state.memories = {}
                    if user_id not in app.state.memories:
                        app.state.memories[user_id] = []
                    app.state.memories[user_id].append(memory_entry)
                    auto_saved = True
        
        return {
            "should_remember": should_remember,
            "suggested_memories": suggestions,
            "auto_saved": auto_saved,
            "message": f"🤖 Detected {len(suggestions)} memory-worthy items" if should_remember else "No memories detected"
        }
        
    except Exception as e:
        logger.error(f"Error in smart_detect_memory: {e}")
        return {
            "should_remember": False,
            "suggested_memories": [],
            "auto_saved": False,
            "error": str(e)
        }

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