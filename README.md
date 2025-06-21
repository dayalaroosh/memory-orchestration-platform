# Memory Orchestration Platform

A production-ready memory management system built with FastAPI and integrated with Mem0 Platform API for intelligent memory processing.

## 🧠 Features

- **Intelligent Memory Management**: Powered by Mem0 Platform API for advanced memory processing
- **Multi-Level Memory Types**: Goals, decisions, insights, code snippets, and more
- **Semantic Search**: Find memories by meaning, not just keywords
- **User Authentication**: JWT-based secure authentication
- **Rate Limiting**: Built-in API rate limiting for production use
- **RESTful API**: Clean, documented endpoints for all operations
- **Background Processing**: Async memory storage for optimal performance

## 🚀 Quick Start

### Environment Setup

Create a `.env` file with the following variables:

```bash
# Required: Mem0 Platform API Key
MEM0_API_KEY=your_mem0_api_key_here

# Optional: Custom configuration
SECRET_KEY=your_secret_key_here
PORT=8090
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Get Your Mem0 API Key

1. Sign up at [Mem0 Platform](https://mem0.ai)
2. Create a new API key in your dashboard
3. Add it to your `.env` file as `MEM0_API_KEY`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python production_mem0_server.py
```

The server will start at `http://localhost:8090`

## 📚 API Documentation

### Authentication

#### Register User
```bash
POST /auth/register
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Login
```bash
POST /auth/login
{
  "email": "user@example.com", 
  "password": "secure_password"
}
```

### Memory Operations

#### Create Memory
```bash
POST /memories
Authorization: Bearer <token>
{
  "content": "I need to implement user authentication",
  "memory_type": "action_item",
  "priority": "high",
  "source": "manual",
  "project_id": "web-app-v2",
  "tags": ["auth", "security"],
  "metadata": {"urgent": true}
}
```

#### Search Memories
```bash
POST /memories/search
Authorization: Bearer <token>
{
  "query": "authentication tasks",
  "limit": 10
}
```

#### Get All Memories
```bash
GET /memories
Authorization: Bearer <token>
```

### Memory Types

- `goal` - Long-term objectives
- `action_item` - Tasks to complete
- `decision` - Important decisions made
- `context` - General context information
- `insight` - Key insights learned
- `reference` - Reference materials
- `code_snippet` - Code examples
- `meeting_note` - Meeting summaries

### Priority Levels

- `low` - Nice to have
- `medium` - Standard priority
- `high` - Important
- `critical` - Urgent/critical

## 🏗️ Architecture

### Mem0 Platform Integration

This platform uses Mem0's hosted API service for:
- **Intelligent Fact Extraction**: Automatically extracts key information
- **Semantic Search**: Meaning-based memory retrieval
- **Memory Consolidation**: Resolves conflicts and updates existing memories
- **Performance Optimization**: 91% faster than full-context approaches

### Components

- **FastAPI Server**: High-performance async API server
- **JWT Authentication**: Secure user authentication
- **Mem0 Platform API**: Advanced memory processing
- **Background Tasks**: Async memory storage
- **Rate Limiting**: Production-ready request limiting

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM0_API_KEY` | Mem0 Platform API key | Required |
| `SECRET_KEY` | JWT signing key | Auto-generated |
| `PORT` | Server port | 8090 |
| `RATE_LIMIT_REQUESTS` | Requests per window | 100 |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | 60 |

## 🚀 Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on push to main

### Vercel

1. Connect repository to Vercel
2. Add environment variables
3. Deploy serverless functions

### Docker

```bash
# Build image
docker build -t memory-platform .

# Run container
docker run -p 8090:8090 -e MEM0_API_KEY=your_key memory-platform
```

## 📊 Performance

With Mem0 Platform integration:
- **26% higher accuracy** than basic memory systems
- **91% lower latency** than full-context approaches  
- **90% token cost savings** through intelligent extraction
- **Sub-second response times** for memory operations

## 🔒 Security

- JWT-based authentication
- Rate limiting protection
- Input validation and sanitization
- Secure password hashing
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- [Mem0 Documentation](https://docs.mem0.ai)
- [Mem0 Discord Community](https://discord.gg/mem0)
- [GitHub Issues](https://github.com/your-repo/issues)

---

**Built with ❤️ using Mem0 Platform API** 