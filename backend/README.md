# Backend - Instagram Creator Intelligence API

FastAPI-powered backend that provides AI-driven creator insights, content generation, and trend analysis for Instagram creators.

## 🎯 Overview

This backend service analyzes Instagram creator data using AI (OpenAI GPT) to provide:
- **Trend-based content generation** - AI-generated posts optimized for engagement
- **Style matching** - Generate content in any creator's style
- **Creator insights** - Categorized analysis of 25+ Instagram creators
- **Engagement metrics** - Real follower data and engagement rate calculations

**Tech Stack:**
- **Framework:** FastAPI (Python 3.12+)
- **Database:** MongoDB
- **AI:** OpenAI GPT-4o-mini
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2

---

## 📁 Architecture

```
backend/
├── api/
│   ├── server.py              # FastAPI app entry point
│   ├── routers/               # API endpoints
│   │   ├── creator_router.py  # /api/creators/* (list, network, details)
│   │   ├── instagram_router.py # /api/instagram/* (fetch, health)
│   │   ├── style_router.py    # /api/style/* (content in creator style)
│   │   └── trend_router.py    # /api/trend/* (trend-based content)
│   └── services/              # Business logic
│       ├── style_service.py   # Content generation in creator style
│       └── trend_service.py   # Trend-based content generation
└── database/
    ├── connection.py          # MongoDB connection
    ├── models.py              # Data models
    └── repositories.py        # Database operations (Repository Pattern)
```

**Note:** Data collection, embedding generation, and analysis happen in the `collectors/instagram/` folder (outside backend). This backend is a pure API layer that serves pre-processed data from MongoDB.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (local or cloud)
- OpenAI API key

### Local Development

```bash
# 1. Navigate to backend folder
cd backend

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (.env file)
cp .env.example .env
# Edit .env with your credentials:
#   MONGO_URI=mongodb+srv://...
#   OPENAI_API_KEY=sk-...
#   DATABASE_NAME=ig_raw

# 5. Start server
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

**Server runs at:** http://localhost:8000  
**API docs:** http://localhost:8000/docs

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
cd backend

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker CLI

```bash
cd backend

# Build image
docker build -t instagram-backend:latest .

# Run container
docker run -d \
  --name instagram-backend \
  -p 8000:8000 \
  --env-file .env \
  instagram-backend:latest

# View logs
docker logs -f instagram-backend
```

**Health Check:** Built-in healthcheck monitors `/api/creators/list` endpoint

---

## ☁️ Cloud Deployment

### Railway

1. Create `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn api.server:app --host 0.0.0.0 --port $PORT"
  }
}
```

2. Set environment variables:
   - `MONGO_URI`
   - `OPENAI_API_KEY`
   - `DATABASE_NAME`

### Render

1. Connect GitHub repository
2. Select **Docker** deployment
3. Set Docker context: `backend`
4. Add environment variables

### Heroku

```bash
# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set MONGO_URI="..."
heroku config:set OPENAI_API_KEY="..."

# Deploy with Heroku Container Registry
heroku container:login
cd backend
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

---

## 📊 MongoDB Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| **user_profiles** | Creator profiles with AI analysis | `username`, `primary_category`, `profile_data` |
| **user_snapshots** | Raw Instagram user + posts data | `user_id`, `user_info`, `posts[]` |
| **post_embeddings** | Individual post embeddings (384-dim) | `post_id`, `user_id`, `caption`, `embedding` |
| **user_embeddings** | User style embeddings (384-dim) | `user_id`, `embedding`, `model` |
| **raw_api_responses** | Raw API responses from Instagram | `username`, `endpoint`, `raw` |

---

## 🎨 API Endpoints

### Creator APIs

- `GET /api/creators/list?platform=instagram` - Get all creators
- `GET /api/creators/{username}?platform=instagram` - Get creator details

### Content Generation APIs

- `POST /api/trend/generate` - Generate trend-based content
  ```json
  {
    "category": "Finance",
    "topic": "passive income",
    "tone": "casual",
    "length": "medium",
    "format": "post",
    "follower_count": 10000
  }
  ```

- `POST /api/style/generate` - Generate content in creator's style
  ```json
  {
    "creator_name": "herfirst100k",
    "user_topic": "investing for beginners"
  }
  ```

**Full API Documentation:** http://localhost:8000/docs

---

## 🔧 Environment Variables

Required variables in `.env`:

```bash
# MongoDB connection string
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Database name
DATABASE_NAME=ig_raw

# OpenAI API key for content generation
OPENAI_API_KEY=sk-proj-...

# Server port (optional, default: 8000)
PORT=8000
```

---

## 🏗️ Development

### Adding New Categories

Edit `backend/api/services/trend_service.py`:

```python
CATEGORY_KEYWORDS = {
    'YourCategory': ['keyword1', 'keyword2', ...],
    # ...
}
```

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Style

- Format: `black .`
- Lint: `flake8 .`
- Type check: `mypy .`

---

## 📝 Data Flow

```
MongoDB (user_profiles, post_embeddings)
    ↓
Repositories (repositories.py)
    ↓
Services (trend_service.py, style_service.py)
    ↓
    ├→ Extract evidence (keywords, hooks, hashtags)
    ├→ GPT-4o-mini generates content
    └→ Calculate engagement projections
    ↓
API Response (FastAPI routers)
```

---

## 🐛 Troubleshooting

**Issue:** `ModuleNotFoundError: database`  
**Fix:** Ensure you're in the backend directory and virtual environment is activated

**Issue:** `MongoDB connection failed`  
**Fix:** Check `MONGO_URI` in `.env` and verify MongoDB is accessible

**Issue:** `OpenAI API error`  
**Fix:** Verify `OPENAI_API_KEY` is valid and has credits

**Issue:** `Port 8000 already in use`  
**Fix:** `lsof -ti:8000 | xargs kill` or use different port

---

## 📚 Related Documentation

- **Collectors:** See `../collectors/instagram/README.md` for data collection pipeline
- **Frontend:** See `../xhs-analyser-frontend/README.md` for UI setup
- **Deployment:** See `DEPLOYMENT.md` for detailed cloud deployment guides (deprecated - content merged here)
