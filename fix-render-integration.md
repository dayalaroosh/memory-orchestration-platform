# Fix Render Integration - Step-by-Step Guide

## Problem Summary
Moving the Memory Orchestration Platform service to a new Render project has caused configuration mismatches:
- Port conflicts (local 8090 vs Render 10000)
- URL changes (new .onrender.com subdomain)
- Environment variable resets
- MCP server pointing to wrong endpoint

## Step 1: Identify Your New Render Service Details

### 1.1 Log into Render Dashboard
1. Go to https://render.com/dashboard
2. Navigate to your new project
3. Find your Memory Orchestration Platform service

### 1.2 Get Service Information
Record these details:
- **Service Name**: `_____________________`
- **Service URL**: `https://______________.onrender.com`
- **Last Deploy Status**: `_____________________`
- **Current Branch**: `_____________________`

### 1.3 Check Environment Variables
In your Render service settings, verify these environment variables exist:
- [ ] `MEM0_API_KEY` = `your-mem0-api-key`
- [ ] `PORT` = `10000` (or let Render set automatically)
- [ ] `SECRET_KEY` = `your-secret-key`

## Step 2: Update Production Server for Render Compatibility

### 2.1 Update Port Configuration
The current production server needs to use Render's port:

```python
# In production_mem0_server.py, around line 915
# Change this:
port = int(os.getenv("PORT", 8090))

# To this:
port = int(os.getenv("PORT", 10000))  # Render default
```

### 2.2 Add Render Environment Detection
Add this to help debug:

```python
# Add after line 330 in startup_event()
logger.info(f"🌐 Render Environment:")
logger.info(f"   - RENDER_EXTERNAL_URL: {os.getenv('RENDER_EXTERNAL_URL', 'not set')}")
logger.info(f"   - RENDER_SERVICE_NAME: {os.getenv('RENDER_SERVICE_NAME', 'not set')}")
logger.info(f"   - PORT: {os.getenv('PORT', 'not set')}")
```

### 2.3 Update Health Endpoint
Enhance the health endpoint to return Render info:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Memory Orchestration Platform",
        "version": "1.0.0", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mem0_configured": bool(mem0_client),
        "render_url": os.getenv("RENDER_EXTERNAL_URL", ""),
        "port": os.getenv("PORT", "10000")
    }
```

## Step 3: Update MCP Server Configuration

### 3.1 Create Environment File
Create `.env` file in `memory-platform-clean/`:

```bash
# .env
MEMORY_API_URL=https://YOUR_RENDER_SERVICE_URL.onrender.com
MEMORY_API_KEY=memory-gpt-2025-key
NODE_ENV=development
```

### 3.2 Update MCP Server to Use Environment
Modify `memory-mcp-server.js`:

```javascript
// Add at the top after imports
import dotenv from 'dotenv';
dotenv.config();

// Update CONFIG object
const CONFIG = {
  MEMORY_API_URL: process.env.MEMORY_API_URL || 'http://localhost:8090',
  MEMORY_API_KEY: process.env.MEMORY_API_KEY || 'memory-gpt-2025-key',
  MCP_SERVER_NAME: 'memory-orchestration',
  MCP_SERVER_VERSION: '1.0.0'
};

// Add debug logging
console.error(`🔧 MCP Server Config: ${CONFIG.MEMORY_API_URL}`);
```

### 3.3 Update Package.json
Add dotenv dependency:

```json
{
  "dependencies": {
    "@fastify/cors": "^11.0.1",
    "@modelcontextprotocol/sdk": "^1.13.0", 
    "axios": "^1.10.0",
    "dotenv": "^16.5.0",
    "fastify": "^5.4.0"
  }
}
```

### 3.4 Update Cursor MCP Configuration
Update `mcp-config.json`:

```json
{
  "mcpServers": {
    "memory-orchestration": {
      "command": "node",
      "args": ["memory-mcp-server.js"],
      "cwd": ".",
      "env": {
        "MEMORY_API_URL": "https://YOUR_RENDER_SERVICE_URL.onrender.com",
        "MEMORY_API_KEY": "memory-gpt-2025-key"
      }
    }
  }
}
```

## Step 4: Deploy and Test

### 4.1 Commit and Push Changes
```bash
git add .
git commit -m "Fix Render integration - update port and API URL"
git push origin main
```

### 4.2 Monitor Render Deploy
1. Watch deploy logs in Render Dashboard
2. Look for successful startup messages
3. Check for any error messages

### 4.3 Test Render Service
```bash
# Test health endpoint
curl https://YOUR_RENDER_SERVICE_URL.onrender.com/health

# Test memory endpoint
curl -X POST "https://YOUR_RENDER_SERVICE_URL.onrender.com/gpt/memories" \
  -H "Authorization: Bearer memory-gpt-2025-key" \
  -H "Content-Type: application/json" \
  -d '{"memory":"Test from fixed configuration","metadata":{"source":"test"}}'

# Test search endpoint  
curl -X POST "https://YOUR_RENDER_SERVICE_URL.onrender.com/gpt/search" \
  -H "Authorization: Bearer memory-gpt-2025-key" \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
```

### 4.4 Test MCP Server Locally
```bash
# Install dependencies
npm install

# Test MCP server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | node memory-mcp-server.js

# Test remember function
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"remember","arguments":{"content":"MCP test memory","type":"test","source":"cursor"}}}' | node memory-mcp-server.js
```

## Step 5: Verify Cursor Integration

### 5.1 Restart Cursor
1. Close Cursor completely
2. Reopen Cursor in the memory-platform-clean directory
3. Check if MCP server is detected

### 5.2 Test Memory Tools
1. Try using the "remember" tool in Cursor
2. Try using the "recall" tool in Cursor  
3. Check for any error messages

## Troubleshooting Common Issues

### Issue: Render Service Won't Start
**Symptoms**: Deploy fails, service shows as "Build Failed"
**Solutions**:
- Check Render logs for Python errors
- Verify requirements.txt includes all dependencies
- Ensure production_mem0_server.py has correct port binding

### Issue: MCP Server Can't Connect
**Symptoms**: "Memory API unavailable" errors
**Solutions**:
- Verify .env file has correct Render URL
- Test Render service manually with curl
- Check API key is correct

### Issue: 404 Errors on Endpoints
**Symptoms**: "/gpt/memories" returns 404
**Solutions**:
- Verify correct version of production server is deployed
- Check that endpoints exist in deployed code
- Test with different HTTP client

### Issue: CORS Errors
**Symptoms**: Browser blocks requests
**Solutions**:
- Verify CORS middleware is enabled
- Check allowed origins include your domain
- Test with curl instead of browser

## Success Checklist

### ✅ Render Service
- [ ] Service deploys successfully
- [ ] Health endpoint returns 200 OK
- [ ] Service URL is accessible
- [ ] Environment variables are set

### ✅ API Endpoints
- [ ] `/gpt/memories` accepts POST requests
- [ ] `/gpt/search` returns results
- [ ] API key authentication works
- [ ] Response format is correct

### ✅ MCP Integration
- [ ] MCP server connects to Render
- [ ] No connection timeouts
- [ ] Memory tools work correctly
- [ ] Error handling works

### ✅ Cursor Integration  
- [ ] Cursor detects MCP server
- [ ] Memory tools appear in Cursor
- [ ] End-to-end workflow works
- [ ] No configuration errors

---

**Next Steps After Fix**:
1. Document the new Render URL in all configs
2. Update any external integrations
3. Test with real-world usage scenarios
4. Set up monitoring for the Render service 