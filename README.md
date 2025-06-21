# Memory Orchestration Platform

Advanced memory management system with Mem0 Platform integration, designed for seamless integration with Custom GPTs and other AI tools.

## 🚀 Features

- **Memory Management**: Store, search, and retrieve memories with semantic search
- **Mem0 Integration**: Leverages Mem0 Platform for advanced memory capabilities
- **Custom GPT Ready**: Simplified authentication and endpoints for ChatGPT Custom GPTs
- **Multi-source Support**: Handle memories from various sources (ChatGPT, Cursor, Voice, etc.)
- **JWT Authentication**: Secure authentication with token-based access
- **Rate Limiting**: Built-in rate limiting for API protection

## 🔧 Quick Setup for Custom GPT

### 1. Custom GPT Configuration

When creating your Custom GPT, use these settings:

**Authentication:**
- Type: API Key
- Auth Type: Custom
- Custom Header Name: `Authorization`
- API Key: `memory-gpt-2025-key`

**OpenAPI Schema:** Use the provided `custom-gpt-openapi.yaml`

### 2. Available Endpoints for Custom GPT

- `POST /gpt/memories` - Add a new memory
- `POST /gpt/search` - Search existing memories
- `GET /health` - Health check (no auth required)

### 3. Example Usage

**Add Memory:**
```json
{
  "content": "User prefers dark mode for all applications"
}
```

**Search Memories:**
```json
{
  "query": "user preferences"
}
```

## 🌐 Deployment

Currently deployed on Render at: https://memory-orchestration-platform.onrender.com

## 🔐 Authentication Options

### For Custom GPT (Simplified)
- Use API Key: `memory-gpt-2025-key`
- Endpoints: `/gpt/memories`, `/gpt/search`

### For Full API Access (JWT)
1. Register: `POST /auth/register`
2. Login: `POST /auth/login`
3. Use returned JWT token for all authenticated endpoints

## 📝 API Documentation

### Health Check
```bash
curl https://memory-orchestration-platform.onrender.com/health
```

### Add Memory (Custom GPT)
```bash
curl -X POST https://memory-orchestration-platform.onrender.com/gpt/memories \
  -H "Authorization: memory-gpt-2025-key" \
  -H "Content-Type: application/json" \
  -d '{"content": "Remember user prefers concise responses"}'
```

### Search Memories (Custom GPT)
```bash
curl -X POST https://memory-orchestration-platform.onrender.com/gpt/search \
  -H "Authorization: memory-gpt-2025-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "user preferences"}'
```

## 🛠 Development

### Local Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (see `.env.example`)
4. Run: `python production_mem0_server.py`

### Environment Variables
- `MEM0_API_KEY`: Your Mem0 Platform API key
- `SECRET_KEY`: JWT secret key
- `PORT`: Server port (default: 8090)

## 🔄 Troubleshooting Custom GPT

If you're experiencing authentication issues:

1. **Check API Key**: Ensure you're using `memory-gpt-2025-key`
2. **Test Endpoints**: Try the `/health` endpoint first (no auth required)
3. **Use Simplified Endpoints**: Use `/gpt/memories` and `/gpt/search` instead of the full API
4. **Check Logs**: Monitor server logs for specific error messages

### Test Without Authentication
```bash
curl https://memory-orchestration-platform.onrender.com/test-auth
```

## 📊 Memory Types

- `GOAL`: Goals and objectives
- `ACTION_ITEM`: Tasks and todos  
- `DECISION`: Decisions made
- `CONTEXT`: General context information
- `INSIGHT`: Insights and learnings
- `REFERENCE`: Reference materials
- `CODE_SNIPPET`: Code snippets
- `MEETING_NOTE`: Meeting notes

## 🎯 Use Cases

- **Personal AI Assistant**: Remember user preferences and context
- **Project Management**: Track decisions, goals, and action items
- **Learning**: Store insights and knowledge for retrieval
- **Code Documentation**: Remember code patterns and snippets
- **Meeting Management**: Store and search meeting notes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- [Mem0 Documentation](https://docs.mem0.ai)
- [Mem0 Discord Community](https://discord.gg/mem0)
- [GitHub Issues](https://github.com/your-repo/issues)

---

**Built with ❤️ using Mem0 Platform API** 