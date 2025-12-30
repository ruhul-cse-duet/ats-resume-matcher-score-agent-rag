# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
# Check Python version (need 3.11+)
python --version

# Check Docker
docker --version
docker compose version

# Check Ollama
ollama --version
```

---

## Step 1: Install Ollama (2 minutes)

### Windows/Mac
1. Download from https://ollama.ai
2. Install and run the application
3. Ollama will start automatically in the background

### Pull a Model
```bash
# Recommended: Fast and accurate
ollama pull qwen3:4b

# Alternative: Lighter/faster
ollama pull qwen2.5:3b

# Verify installation
ollama list
```

---

## Step 2: Configure Environment (1 minute)

Create `.env` file in project root:

```env
# Database (change password in production!)
DATABASE_URL=postgresql://atsuser:atspass@db:5432/atsdb

# Security (MUST change in production!)
JWT_SECRET=your-super-secret-jwt-key-here

# Ollama Configuration
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=300

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Linux Users**: Change `OLLAMA_URL` to:
```env
OLLAMA_URL=http://172.17.0.1:11434/api/generate
```

---

## Step 3: Start Services (2 minutes)

```bash
# Navigate to project directory
cd "ATS Resume Matcher RAG Langchain Agent"

# Start all services
docker compose up --build
```

**Wait for logs showing**:
```
api_1  | INFO:     Application startup complete.
db_1   | database system is ready to accept connections
```

---

## Step 4: Initialize Database (30 seconds)

In a new terminal:
```bash
# Run migrations
docker compose exec api alembic upgrade head
```

You should see:
```
INFO  [alembic.runtime.migration] Running upgrade -> 0001_create_tables
```

---

## Step 5: Access Application (10 seconds)

Open your browser:
```
http://localhost:8000
```

You should see the ATS Resume Matcher interface!

---

## 🎯 First Use

### Create Account
1. Click **Sign Up** tab
2. Enter email: `test@example.com`
3. Enter password (min 6 characters)
4. Click **Create Account**

### Analyze Resume
1. Paste a job description in the text area
2. Click **Choose file** or drag & drop a resume (PDF/DOCX/TXT)
3. Click **Analyze Resume**
4. Wait 5-30 seconds for results
5. View score, matched keywords, and analysis

### Rewrite Resume
1. Ensure job description is filled
2. Paste your resume text in the **Resume Text** field
3. Click **Rewrite & Optimize**
4. Copy optimized resume with **Copy** button

---

## 🔧 Troubleshooting

### "Cannot connect to LLM service"

**Check Ollama is running:**
```bash
# Should show running process
ollama list

# If not running, start it
ollama serve
```

**Verify model is pulled:**
```bash
ollama list
# Should show qwen2.5:7b (or your model)
```

**Test Ollama directly:**
```bash
ollama run qwen2.5:7b "Hello"
# Should respond with text
```

### "Database error"

**Check containers are running:**
```bash
docker compose ps
# All should show "Up"
```

**Restart services:**
```bash
docker compose restart
```

**Re-run migrations:**
```bash
docker compose exec api alembic upgrade head
```

### Frontend shows blank page

**Check logs:**
```bash
docker compose logs api
```

**Clear browser cache:**
- Press `Ctrl+Shift+R` (Windows/Linux)
- Press `Cmd+Shift+R` (Mac)

**Check JavaScript console:**
- Press `F12` → Console tab
- Look for errors

### File upload fails

**Check file:**
- Size < 10MB
- Format: PDF, DOCX, or TXT
- Not corrupted

**Check logs:**
```bash
docker compose logs api | grep -i error
```

---

## ⚡ Tips for Best Performance

### Use Appropriate Model
```bash
# For speed (3-5 seconds per analysis)
ollama pull qwen2.5:3b

# For balance (5-10 seconds)
ollama pull qwen2.5:7b

# For accuracy (10-30 seconds)
ollama pull qwen2.5:14b
```

### Enable GPU (if available)
Ollama automatically uses GPU if available. Check:
```bash
nvidia-smi  # For NVIDIA GPUs
```

### Optimize for Your Use Case

**Job Seeker** (frequent use, speed matters):
- Use `qwen2.5:3b` model
- Reduce `OLLAMA_TIMEOUT` to 60
- Keep resume concise (1-2 pages)

**HR Professional** (accuracy matters):
- Use `qwen2.5:14b` model
- Keep default timeout (300)
- Detailed job descriptions

---

## 📱 Mobile Access

### Access from Phone/Tablet

1. Find your computer's IP:
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

2. On mobile browser, visit:
```
http://YOUR_IP_ADDRESS:8000
```

Example: `http://192.168.1.100:8000`

---

## 🛑 Stop Services

```bash
# Stop containers
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

---

## 🔄 Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose up --build

# Run any new migrations
docker compose exec api alembic upgrade head
```

---

## 📊 Check System Status

### View Logs
```bash
# All services
docker compose logs -f

# Just API
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Health Check
```bash
# API health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"ATS Resume Matcher"}
```

---

## 🎓 Next Steps

1. **Read Full Documentation**
   - `README.md` - Complete guide
   - `ERROR_HANDLING.md` - Error reference
   - `UPDATE_SUMMARY.md` - Latest changes

2. **Explore Features**
   - Try different file formats
   - Test with various job descriptions
   - Compare resume versions

3. **Customize**
   - Try different Ollama models
   - Adjust timeout settings
   - Customize prompts in service files

4. **Deploy to Production**
   - Follow security checklist in README
   - Set strong JWT_SECRET
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS

---

## 💬 Need Help?

1. **Check Documentation**
   - README.md (comprehensive guide)
   - ERROR_HANDLING.md (all error scenarios)

2. **Common Issues**
   - See Troubleshooting section above
   - Check GitHub issues

3. **Logs**
   - Always check logs first
   - Most errors are clearly logged

---

## ✅ Success Checklist

- [ ] Ollama installed and model pulled
- [ ] `.env` file configured
- [ ] Docker containers running
- [ ] Database migrations completed
- [ ] Can access http://localhost:8000
- [ ] Created test account successfully
- [ ] Analyzed a sample resume
- [ ] Received score and analysis

---

**Time Investment**: ~5 minutes setup, lifetime of better resumes! 🎉

**Status**: Production Ready ✅  
**Version**: 1.1.0
