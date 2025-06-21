# Cursor MCP Setup - Memory Orchestration Platform

## ✅ Status Check
- **Node.js**: v22.16.0 ✅
- **Render Service**: https://memory-orchestration-platform.onrender.com ✅ (Healthy)
- **MCP Server**: memory-mcp-server.js ✅
- **API Key**: memory-gpt-2025-key ✅

## 🔧 Add to Cursor Settings

1. **Open Cursor Settings**: Press `Ctrl+,`
2. **Search for**: "MCP" or "Model Context Protocol"
3. **Add this configuration**:

```json
{
  "mcpServers": {
    "memory-orchestration": {
      "command": "node",
      "args": ["memory-mcp-server.js"],
      "cwd": "C:\\Users\\Aroosh Dayal\\Documents\\Cursor\\memory-platform-clean",
      "env": {
        "MEMORY_API_URL": "https://memory-orchestration-platform.onrender.com",
        "MEMORY_API_KEY": "memory-gpt-2025-key"
      }
    }
  }
}
```

4. **Save settings** and **restart Cursor**

## 🧪 Test Commands

Once configured, try these commands in Cursor:

```
@memory remember I prefer clean, modular code
@memory remember I'm working on a memory orchestration platform
@memory recall my coding preferences
@memory get_context programming style
```

## 🛠️ Available Tools

Your MCP server provides these tools:
- **remember**: Store new memories
- **recall**: Search existing memories  
- **get_context**: Get relevant context for topics
- **sync_from_tool**: Sync memories from other tools

## 🎉 You're Ready!

Your Memory Orchestration Platform is fully configured and ready to use with Cursor!

**Service URL**: https://memory-orchestration-platform.onrender.com
**Status**: Operational
**Integration**: MCP Protocol Ready 