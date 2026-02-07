# Instagram Creator Analysis & Style Generator

A full-stack application for analyzing Instagram creators, visualizing their relationship networks, and generating AI-powered content in their unique styles.

## 🌟 Features

### 1. **Creator Network Visualization**
- Interactive force-directed graph showing 11 Instagram creators
- Relationship edges based on content similarity (cosine similarity ≥ 0.7)
- Semantic embeddings using BAAI/bge-small-en-v1.5 (384-dimensional)
- Click nodes to view detailed creator profiles

### 2. **AI Style Generator**
- Generate Instagram captions in any creator's unique style
- Powered by OpenAI GPT-4o-mini
- Platform-specific prompts (English for Instagram, Chinese for XiaohongShu)
- Analyzes creator's tone, topics, and writing patterns

### 3. **Creator Profiles**
- 11 Instagram creators across niches: finance, wellness, comedy, fitness, food
- Topics, style analysis, and content themes
- Persona extraction from profile data

## 🏗️ Architecture

```
├── backend/                  # FastAPI backend (Python)
│   ├── api/                 # REST API endpoints
│   │   ├── routers/        # Creator & style generation routes
│   │   └── services/       # Business logic layer
│   ├── database/           # MongoDB repositories & models
│   ├── generators/         # Embedding & network generators
│   └── processors/         # Data processing pipelines
│
├── xhs-analyser-frontend/  # Next.js 16 frontend (React/TypeScript)
│   ├── app/                # App router pages
│   ├── src/components/     # React components
│   └── messages/           # i18n translations (zh/en)
│
└── collectors/             # Data collection tools
    ├── instagram/          # Instagram profile scraper
    └── xiaohongshu/       # XHS scraper (legacy)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm (for frontend)
- MongoDB Atlas account
- OpenAI API key

### Backend Setup

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Create backend/.env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

3. **Start the server**
   ```bash
   uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload
   ```

   API will be available at `http://localhost:5001`

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd xhs-analyser-frontend
   pnpm install
   ```

2. **Start development server**
   ```bash
   pnpm dev
   ```

   App will be available at `http://localhost:3000`

## 📊 Data Pipeline

### 1. Profile Collection
```bash
cd collectors/instagram
python collector.py --username <instagram_username>
```

### 2. Generate Embeddings
```bash
cd backend/generators
python generate_embeddings.py
```
- Uses BAAI/bge-small-en-v1.5 model
- Creates 384-dimensional vectors
- Stores in MongoDB `user_embeddings` collection

### 3. Build Creator Network
```bash
python instagram_network.py
```
- Computes cosine similarity between embeddings
- Creates edges where similarity ≥ 0.7
- Stores network in MongoDB `creator_networks` collection

## 🗄️ Database Schema

### MongoDB Collections

**user_profiles**
```javascript
{
  user_id: "username",
  nickname: "Display Name",
  platform: "instagram",
  profile_data: {
    user_style: {
      persona: "...",
      tone: "motivational, supportive, educational",
      interests: ["finance", "investing"]
    },
    content_topics: ["topic1", "topic2"],
    engagement_style: "..."
  }
}
```

**user_embeddings**
```javascript
{
  user_id: "username",
  platform: "instagram",
  embedding: [0.123, -0.456, ...], // 384 dimensions
  created_at: ISODate("...")
}
```

**creator_networks**
```javascript
{
  platform: "instagram",
  creators: [...],  // Node data
  edges: [          // Relationship edges
    {source: "user1", target: "user2", weight: 0.758}
  ]
}
```

## 🎨 API Endpoints

### Creator Network
- `GET /api/creators/network?platform=instagram` - Get network graph
- `GET /api/creators/list?platform=instagram` - List all creators
- `GET /api/creators/{username}?platform=instagram` - Get creator profile

### Style Generation
- `GET /api/style/creators?platform=instagram` - Get creators for style generation
- `POST /api/style/generate` - Generate content in creator's style
  ```json
  {
    "creator_name": "theholisticpsychologist",
    "user_input": "how to deal with anxiety",
    "platform": "instagram"
  }
  ```

### Health Check
- `GET /api/health` - API health status

## 🌐 Deployment

### GitHub Codespaces
The app automatically detects Codespaces and adjusts URLs:
- Backend: `https://*-5001.app.github.dev`
- Frontend: `https://*-3000.app.github.dev`

### Environment Variables
**Backend** (`backend/.env`):
```bash
OPENAI_API_KEY=sk-proj-...
```

**Frontend** (`xhs-analyser-frontend/.env`):
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5001
```

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB Atlas
- **Embeddings**: sentence-transformers (BAAI/bge-small-en-v1.5)
- **LLM**: OpenAI GPT-4o-mini
- **Data Processing**: pandas, numpy

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Visualization**: D3.js (force-directed graph)
- **i18n**: next-intl

## 🎯 Creator Network

### Current Creators (11)
1. **herfirst100k** - Finance/investing for women
2. **jackinvestment** - Personal finance & investment
3. **ramit** - Debt reduction & money mindset
4. **theholisticpsychologist** - Mental health & trauma healing
5. **adventuresofnik** - Solo backpacking & self-defense
6. **nabela** - Wellness & personal transformation
7. **tinx** - Dating advice & lifestyle
8. **mondaypunday** - Standup comedy
9. **doobydobap** - Korean recipes & cooking
10. **madfitig** - Fitness & workout challenges
11. **rainn** - Sexual assault awareness

### Network Clusters
- **Finance**: herfirst100k ↔ jackinvestment ↔ ramit (similarity: 0.70-0.74)
- **Wellness**: theholisticpsychologist ↔ nabela (similarity: 0.73)
- Individual creators with unique content positioning

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Embedding model: [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- LLM: OpenAI GPT-4o-mini
- UI inspiration: Modern data visualization practices

---

**Built with ❤️ for creator analysis and AI-powered content generation**
