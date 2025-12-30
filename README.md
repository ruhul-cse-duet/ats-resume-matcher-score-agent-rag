# ATS Resume Matcher - AI-Powered Resume Analysis System

> Intelligent ATS (Applicant Tracking System) resume analysis using RAG, Ollama LLM, FastAPI, PostgreSQL, and modern web technologies.

## 🚀 Features

- **AI-Powered Analysis**: Uses Ollama LLM for intelligent resume evaluation
- **RAG Architecture**: Retrieval-Augmented Generation for context-aware analysis
- **Semantic Matching**: FAISS-based vector similarity search
- **Resume Rewriting**: AI-optimized resume rewriting for ATS compatibility
- **User Authentication**: Secure JWT-based authentication system
- **Modern UI**: Responsive, gradient-based design with smooth animations
- **Multi-Format Support**: PDF, DOCX, and TXT file uploads
- **Real-time Feedback**: Live progress indicators and error handling

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Ollama (running locally or remotely)
- PostgreSQL (via Docker)

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd "ATS Resume Matcher RAG Langchain Agent"
```

### 2. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

Pull a model (e.g., qwen2.5):
```bash
ollama pull qwen3:4b
# Or use a lighter model:
ollama pull llama2:7b
```

### 3. Configure Environment

Create `.env` file:
```env
DATABASE_URL=postgresql://atsuser:atspass@db:5432/atsdb
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=300
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Note**: On Linux, use `http://172.17.0.1:11434/api/generate` instead of `host.docker.internal`

### 4. Start Services

```bash
docker compose up --build
```

### 5. Run Database Migrations

```bash
docker compose exec api alembic upgrade head
```

### 6. Access Application

Open browser: http://127.0.0.1:8000

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── api.py           # API endpoints
│   │   ├── auth.py          # Authentication logic
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   ├── database.py      # Database configuration
│   │   └── config.py        # Application settings
│   └── services/
│       ├── parser.py        # Resume parsing (PDF/DOCX/TXT)
│       ├── ollama_client.py # Ollama API client
│       ├── jd_extractor.py  # Job description keyword extraction
│       ├── ats_scoring.py    # Semantic similarity scoring
│       ├── resume_rewriter.py # AI resume rewriting
│       └── embeddings_index.py # FAISS vector index
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── style.css            # Responsive CSS styles
│   └── script.js            # Frontend JavaScript logic
├── alembic/                 # Database migrations
├── tests/                   # Unit tests
├── docker-compose.yml       # Docker services configuration
├── Dockerfile              # API container definition
├── requirements.txt        # Python dependencies
└── README.md

```

## 🔧 API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - User login

### Resume Analysis
- `POST /analyze` - Analyze resume against job description
- `POST /rewrite` - Rewrite resume for ATS optimization

### Health Check
- `GET /health` - Service health status

## 🎯 Usage Guide

### 1. Sign Up / Login
- Create an account or login with existing credentials
- All data is stored securely with JWT authentication

### 2. Analyze Resume
- Paste job description in the text area
- Upload resume (PDF, DOCX, or TXT format, max 10MB)
- Click "Analyze Resume"
- View ATS compatibility score, matched keywords, and detailed analysis

### 3. Rewrite Resume
- Paste your current resume text
- Ensure job description is filled in Analyze section
- Click "Rewrite & Optimize"
- Copy optimized resume with improved ATS compatibility

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./ats.db` |
| `JWT_SECRET` | Secret key for JWT tokens | `replace-with-secret` |
| `OLLAMA_URL` | Ollama API endpoint | `http://localhost:11434/api/generate` |
| `OLLAMA_MODEL` | LLM model to use | `qwen2.5:7b` |
| `OLLAMA_TIMEOUT` | Request timeout in seconds | `300` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |


### Supported File Formats
- **PDF**: Automatic text extraction
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

## 🐛 Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
**Error**: `Cannot connect to LLM service`

**Solutions**:
- Ensure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`
- Verify OLLAMA_URL in `.env` file
- On Windows/Mac: Use `host.docker.internal`
- On Linux: Use `172.17.0.1`

#### 2. Database Connection Error
**Error**: `Database error occurred`

**Solutions**:
- Check if PostgreSQL container is running: `docker compose ps`
- Verify DATABASE_URL in `.env`
- Restart services: `docker compose restart`
- Run migrations: `docker compose exec api alembic upgrade head`

#### 3. File Upload Fails
**Error**: `Failed to parse resume file`

**Solutions**:
- Check file size (must be < 10MB)
- Ensure file format is PDF, DOCX, or TXT
- Verify file is not corrupted
- Check file permissions

#### 4. Authentication Issues
**Error**: `Invalid credentials` or `Token expired`

**Solutions**:
- Clear browser localStorage and login again
- Verify JWT_SECRET is consistent across restarts
- Check password length (minimum 6 characters)

#### 5. Slow Analysis
**Issue**: Analysis takes too long

**Solutions**:
- Use a lighter Ollama model (e.g., `qwen2.5:3b`)
- Reduce OLLAMA_TIMEOUT if acceptable
- Ensure Ollama has sufficient system resources
- Check CPU/GPU usage

#### 6. Frontend Not Loading
**Issue**: Blank page or 404 errors

**Solutions**:
- Check frontend directory path in `main.py`
- Verify static files are present
- Clear browser cache
- Check console for JavaScript errors

## 🧪 Running Tests

```bash

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=backend tests/
```

## 📊 Performance Optimization

### For Better Speed:
1. Use lighter Ollama models (`qwen2.5:3b` instead of `7b`)
2. Reduce context window in prompts
3. Enable GPU acceleration for Ollama
4. Use Redis for caching (future enhancement)
5. Optimize embedding model batch size

### For Better Accuracy:
1. Use larger Ollama models (`qwen2.5:14b` or `32b`)
2. Increase OLLAMA_TIMEOUT
3. Fine-tune prompts in service files
4. Use domain-specific embedding models


## 🔐 Security Considerations

### Production Deployment:
1. **Change JWT_SECRET**: Use a strong, random secret key
2. **Use HTTPS**: Enable SSL/TLS encryption
3. **Restrict CORS**: Update `allow_origins` in `main.py`
4. **Enable Rate Limiting**: Add rate limiting middleware
5. **Use Strong Passwords**: Enforce password complexity
6. **Environment Variables**: Never commit `.env` to version control
7. **Database Security**: Use strong database passwords
8. **Input Validation**: Always validate and sanitize user input

## 🚀 Deployment

### Docker Production Build

```bash
# Build optimized images
docker compose -f docker-compose.prod.yml up --build -d

# Check logs
docker compose logs -f api

# Stop services
docker compose down
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export JWT_SECRET="..."

# Run migrations
alembic upgrade head

# Start application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## 📝 Development

### Adding New Features

1. **Backend Changes**:
   - Add endpoints in `backend/app/api.py`
   - Create services in `backend/services/`
   - Update models in `backend/app/models.py`
   - Add migrations: `alembic revision --autogenerate -m "description"`

2. **Frontend Changes**:
   - Update UI in `frontend/index.html`
   - Add styles in `frontend/style.css`
   - Implement logic in `frontend/script.js`

### Code Style

```bash
# Format Python code
black backend/

# Lint JavaScript
eslint frontend/script.js

# Type checking (if using TypeScript)
tsc --noEmit
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **Sentence Transformers** - Embedding models
- **FAISS** - Vector similarity search
- **FastAPI** - Modern web framework
- **PostgreSQL** - Reliable database

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

## 🔄 Changelog

### Version 1.1.0 (Current)
- ✅ Comprehensive error handling
- ✅ Retry logic for API calls
- ✅ Improved file upload with drag-and-drop
- ✅ Enhanced UI responsiveness
- ✅ Better input validation
- ✅ Fixed configuration inconsistencies
- ✅ Added detailed logging
- ✅ Improved security measures

### Version 1.0.0
- Initial release with core features

---

Made with ❤️ for better job applications
