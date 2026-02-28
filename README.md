# Instagram Creator Analysis & Content Generator

A full-stack application for analyzing Instagram creators and generating AI-powered, data-driven content using engagement metrics and style analysis.

## 🌟 Features

### 1. **Dual-Path Content Generation**

#### Style-Based Generator
- Generate content in any creator's unique style
- AI analyzes creator's tone, persona, and writing patterns
- **Style consistency scoring** with evidence breakdown (length, emojis, hashtags, voice)
- Custom topic input with creator-specific adaptation
- Powered by OpenAI GPT-4o-mini with enhanced anti-templating guards

#### Trend-Based Generator
- **Real engagement rate analysis** using actual follower counts
- Category-based content optimization (Finance, Wellness, Food, Fitness, Tech, Fashion, Lifestyle)
- **Category-specific content templates** (e.g., Food: 60% recipe narrative, Tech: 50% hot takes)
- **Data-driven insights with transparency**:
  - Displays calculation formulas (Expected Engagement = Engagement Rate × Baseline Followers)
  - References actual top-performing posts with engagement metrics
  - Evidence breakdown (keywords, hooks with explanations, hashtags)
- **Structured strategy output**:
  - Key Strategy (3-bullet summary) - collapsible
  - Why This Works (detailed evidence-based explanation) - collapsible
- Projected metrics for any account size (normalized to 10K followers)
- Calculates: engagement rate, like:comment ratio, expected performance

### 2. **Creator Discovery & Categories**
- Browse **29 Instagram creators** organized by 8 categories (including Celebrity category)
- Auto-categorization by content type
- One-click access to creator profiles
- Direct style generation from explore creators page

### 3. **Smart Engagement Analytics**
- **29.33% average engagement rate** (calculated from real follower data)
- Follower count extraction from raw API data
- Per-post engagement rate: `(likes + comments) / followers × 100`
- Platform-specific normalization for realistic expectations

### 4. **Interactive Landing Page**
- Clear two-path navigation (Style vs. Trend)
- "How It Works" side-by-side comparison showing both tracks
- Explore creators intermediate page for browsing
- Modern gradient-based UI design (no top navigation bar)

### 5. **Creator Network Visualization** (Legacy Feature)
- Interactive force-directed graph
- Relationship edges based on content similarity (cosine similarity ≥ 0.7)
- Semantic embeddings using BAAI/bge-small-en-v1.5 (384-dimensional)

## 🏗️ Architecture

```
├── backend/                  # FastAPI backend (Python)
│   ├── api/                 # REST API endpoints
│   │   ├── routers/        # Modular route handlers
│   │   │   ├── creator_router.py    # Creator profiles & network
│   │   │   ├── style_router.py      # Style-based generation
│   │   │   └── trend_router.py      # Trend-based generation (NEW)
│   │   └── services/       # Business logic layer
│   │       ├── style_service.py     # Style generation service
│   │       └── trend_service.py     # Engagement analysis service (NEW)
│   ├── database/           # MongoDB repositories & models
│   │   ├── repositories.py # Data access layer with follower count extraction
│   │   └── models.py       # Pydantic models
│   ├── generators/         # Embedding & network generators
│   └── processors/         # Data processing pipelines
│
├── frontend/               # Next.js 16 frontend (React/TypeScript)
│   ├── app/                # App router pages
│   │   ├── page.tsx                     # Landing page (NEW)
│   │   ├── style-generator/page.tsx     # Style-based generator (NEW)
│   │   ├── trend-generator/page.tsx     # Trend-based generator (NEW)
│   │   ├── creator/[id]/page.tsx        # Creator profile pages (NEW)
│   │   └── api/proxy/                   # Proxy layer for Codespaces (NEW)
│   │       ├── creators/route.ts        # Creator list proxy
│   │       ├── creator/[id]/route.ts    # Individual creator proxy
│   │       ├── style/generate/route.ts  # Style generation proxy
│   │       └── trend/generate/route.ts  # Trend generation proxy
│   ├── src/components/     # React components
│   │   ├── LandingPage.tsx             # Main landing page (NEW)
│   │   ├── AccountCategories.tsx       # Category browser (NEW)
│   │   ├── CreatorNetworkGraph.tsx     # D3 network visualization
│   │   └── StyleChatbot.tsx            # Legacy style generator
│   └── messages/           # i18n translations (zh/en)
│
└── collectors/             # Data collection tools
    └── instagram/          # Instagram profile scraper
```

### Key Features

**Proxy Architecture**
- Next.js API routes act as proxy layer for GitHub Codespaces
- Server-to-server communication via `localhost`
- Solves port visibility issues in cloud environments

**Engagement Analysis Pipeline**
1. Extract follower counts from `raw_api_responses.raw.data.data.user.edge_followed_by.count`
2. Calculate per-post engagement rate: `(likes + comments) / follower_count × 100`
3. Average across all creators in category
4. Project to target account size (10K followers default)
5. Split engagement using actual like:comment ratio

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
   uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload
   ```

   API will be available at `http://localhost:5000`

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
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

**raw_api_responses** (NEW - follower data source)
```javascript
{
  platform: "instagram",
  username: "herfirst100k",
  endpoint: "user_info",
  raw: {
    data: {
      data: {
        user: {
          edge_followed_by: {
            count: 2185756  // Used for engagement rate calculation
          },
          full_name: "Tori Dunlap — Money Expert",
          biography: "...",
          // ... other user fields
        }
      }
    }
  }
}
```

**post_embeddings** (with engagement metrics)
```javascript
{
  user_id: "username",
  platform: "instagram",
  like_count: 104137,
  comment_count: 378,
  caption: "Post text...",
  embedding: [0.123, -0.456, ...], // 384 dimensions
  created_at: ISODate("...")
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

### Creator Management
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

### Trend Generation (NEW)
- `GET /api/trend/categories` - List available categories
- `POST /api/trend/generate` - Generate engagement-optimized content
  ```json
  {
    "category": "lifestyle",
    "platform": "instagram"
  }
  ```
  
  **Response:**
  ```json
  {
    "success": true,
    "content": "Generated Instagram caption...",
    "category": "lifestyle",
    "creators_analyzed": 4,
    "posts_analyzed": 127,
    "insights": {
      "engagement_rate": 29.33,        // Percentage of followers
      "avg_likes": 2922,                // Expected for 10K followers
      "avg_comments": 10,               // Expected for 10K followers
      "avg_engagement": 2932,           // Total expected engagement
      "raw_avg_likes": 103759,          // From established creators
      "raw_avg_comments": 378,          // From established creators
      "engagement_ratio": 274.5         // Likes:comments ratio
    }
  }
  ```

### Frontend Proxy Endpoints (for Codespaces)
- `GET /api/proxy/creators` - Proxies to backend creator list
- `GET /api/proxy/creator/[id]` - Proxies to backend creator profile
- `POST /api/proxy/style/generate` - Proxies to backend style generation
- `POST /api/proxy/trend/generate` - Proxies to backend trend generation

### Health Check
- `GET /api/health` - API health status

## 🌐 Deployment

### GitHub Codespaces
The app automatically detects Codespaces and adjusts URLs:
- Backend: `https://*-5000.app.github.dev`
- Frontend: `https://*-3000.app.github.dev`

### Environment Variables
**Backend** (`backend/.env`):
```bash
OPENAI_API_KEY=sk-proj-...
```

**Frontend** (`frontend/.env`):
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB Atlas (ig_raw database)
- **Embeddings**: sentence-transformers (BAAI/bge-small-en-v1.5)
- **LLM**: OpenAI GPT-4o-mini
- **Data Processing**: pandas, numpy
- **Analytics**: Real-time engagement rate calculation

### Frontend
- **Framework**: Next.js 16 (App Router with Turbopack)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Visualization**: D3.js (force-directed graph)
- **i18n**: next-intl
- **Proxy Layer**: Next.js API routes for Codespaces compatibility

## ✨ What's New (v2.0)

### Complete Frontend Redesign
- **Landing Page**: Clear two-path navigation with side-by-side "How It Works" comparison
- **Explore Creators**: Intermediate page for browsing creators by category
- **Dedicated Generator Pages**: Separate UIs for style-based and trend-based generation
- **No Top Navigation**: Clean interface focused on content generation
- **Style Consistency Scoring**: Evidence-based metrics showing how well generated content matches creator patterns

### Engagement Analytics Engine
- **Real follower data integration**: Extracts actual follower counts from raw API responses
- **Engagement rate calculation**: Per-post analysis across all creators
- **Smart normalization**: Projects metrics to any account size (default: 10K followers)
- **Data-driven prompts**: Uses top-performing content patterns for generation

### Enhanced Style Generation
- **Iteration 4**: Creator-specific pattern matching (length, emoji, hashtag behavior)
- **Anti-Templating Guards**: Stops generic "THANK YOU" openings and influencer clichés
- **Bilingual Support**: Detects and matches Spanish+English mixing ratios
- **Consistency Scoring**: 4-metric scoring system (length, emoji, hashtag, voice)
- **Evidence Display**: Transparent breakdown showing what was measured (perfect/close/mismatch)

### Developer Experience
- **Proxy architecture**: Solves GitHub Codespaces port visibility issues
- **Modular services**: TrendService for engagement analysis, StyleService for content generation
- **Repository pattern**: Clean data access layer with follower count extraction
- **Type-safe APIs**: Full TypeScript support with proper error handling

## 🎯 Creator Categories & Analytics

### Creator Breakdown by Category

**Total Creators: 29** (5 celebrities, 24 regular creators)

#### Celebrity ⭐ (5 creators)
- **@leomessi** - 504M followers - Football legend, world's most-followed athlete
- **@therock** - 396M followers - Film/acting, fitness, product endorsements
- **@kimkardashian** - 363M followers - Fashion, brand launches, family
- **@taylorswift** - 283M followers - Music releases, tours, storytelling
- **@realdonaldtrump** - 26M followers - Political updates, national events

#### Finance & Money (3+ creators)
- **@herfirst100k** - 2.2M followers - Finance/investing for women
- **@jackinvestment** - 17.7K followers - Personal finance & investment tips
- **@ramit** - 941K followers - Debt reduction & money mindset

#### Mental Health & Wellness (2 creators)
- **theholisticpsychologist** - 9.1M followers - Mental health & trauma healing
- **nabela** - 2.9M followers - Wellness & personal transformation

#### Food & Cooking (1 creator)
- **doobydobap** - 1.1M followers - Korean recipes & cooking tutorials

#### Fitness & Sports (1 creator)
- **madfitig** - 2.3M followers - Fitness & workout challenges

#### Lifestyle & Entertainment (4 creators)
- **tinx** - 642K followers - Dating advice & lifestyle
- **mondaypunday** - 355K followers - Standup comedy
- **adventuresofnik** - 19K followers - Solo backpacking & self-defense
- **rainn** - 80K followers - Sexual assault awareness

### Engagement Analytics

**Overall Platform Metrics:**
- Average engagement rate: **29.33%** (calculated from actual follower data)
- Average like:comment ratio: **274.5:1**
- Total creators analyzed: **29** (including 5 celebrities)
- Total follower count: **20B+** (with celebrity accounts)

**Category Performance:**
Categories are optimized based on engagement patterns from established creators, then normalized for smaller accounts (~10K followers) to provide realistic expectations.

### Network Clusters (Legacy Feature)
- **Finance**: herfirst100k ↔ jackinvestment ↔ ramit (similarity: 0.70-0.74)
- **Wellness**: theholisticpsychologist ↔ nabela (similarity: 0.73)
- Individual creators with unique content positioning

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Embedding model: [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- LLM: OpenAI GPT-4o-mini
- UI inspiration: Modern data visualization and content generation platforms
- Data source: Instagram creator profiles and engagement metrics

---

**Built with ❤️ for data-driven content generation and creator analysis**

**v2.0 - February 2026** - Complete redesign with engagement analytics and dual-path generation
