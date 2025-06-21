# 🧠 Memory Orchestration Platform

> The "Postman for AI Memory" - Seamless memory sharing across ChatGPT, Cursor, voice interfaces, and other AI tools.

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/aroosh-dayal/memory-orchestration-platform.git
cd memory-orchestration-platform

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
python production_mem0_server.py
```

### Railway Deployment
```bash
# Deploy to Railway
railway login
railway create memory-orchestration-platform
railway up
```

### Vercel Deployment (Alternative)
```bash
# Deploy to Vercel
vercel login
vercel --prod
```

## 🏗️ Architecture

The Memory Orchestration Platform provides:

- **🔗 Universal Memory API** - Single API for all AI tools
- **🤖 Multi-Tool Integration** - ChatGPT, Cursor, Voice, Web Dashboard
- **🔒 Enterprise Security** - JWT auth, encryption, audit logs
- **📊 Smart Analytics** - Usage insights and memory intelligence
- **⚡ High Performance** - Sub-200ms response times, 99.9% uptime

## 🛠️ Features

### Core Memory Operations
- **Create**: Store memories with rich metadata
- **Search**: Semantic search with AI-powered relevance
- **Update**: Version-controlled memory updates
- **Delete**: Secure memory deletion with audit trails

### AI Tool Integrations
- **ChatGPT Custom GPT**: Proactive memory suggestions
- **Cursor IDE**: Inline memory management
- **Voice Interface**: "Remember this" commands
- **Web Dashboard**: Visual memory management

### Enterprise Features
- **Multi-tenant Architecture**: Isolated user/team workspaces
- **SSO Integration**: SAML, OAuth, Active Directory
- **Audit Logging**: Complete activity tracking
- **Data Governance**: Retention policies, compliance

## 📚 API Documentation

### Authentication
```bash
# Register new user
curl -X POST "https://your-domain.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "password"}'

# Login
curl -X POST "https://your-domain.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

### Memory Operations
```bash
# Create memory
curl -X POST "https://your-domain.com/memories" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Important decision", "memory_type": "decision"}'

# Search memories
curl -X POST "https://your-domain.com/memories/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "project goals", "limit": 10}'
```

## 🔧 Configuration

### Environment Variables
```env
# Core Settings
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./memory_platform.db

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Performance
REDIS_URL=redis://localhost:6379
MAX_WORKERS=4
```

## 🚀 Deployment Options

### 1. Railway (Recommended)
- Automatic deployments from GitHub
- Built-in database and Redis
- Environment variable management
- Easy scaling

### 2. Vercel + Supabase
- Serverless deployment
- PostgreSQL database
- Edge functions
- Global CDN

### 3. Docker
```bash
docker build -t memory-platform .
docker run -p 8090:8090 memory-platform
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Load testing
locust -f tests/load/locustfile.py
```

## 📊 Monitoring

- **Health Check**: `/health`
- **Metrics**: `/metrics`
- **Status**: `/status`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [memory-platform.vercel.app](https://memory-platform.vercel.app)
- **API Docs**: [api-docs.memory-platform.com](https://api-docs.memory-platform.com)
- **Status**: [status.memory-platform.com](https://status.memory-platform.com)

---

**Built with ❤️ for the AI community** 