# Instagram Data Collector & Analyzer

Complete data pipeline for fetching Instagram creator data, generating AI-powered profile analysis, and creating embeddings for content intelligence.

## 🎯 Overview

This collector provides end-to-end Instagram data processing:

1. **Fetch** - Raw Instagram data via TikHub API (user info, posts, reels)
2. **Store** - Save raw responses to MongoDB
3. **Analyze** - Generate creator profiles using OpenAI/Gemini
4. **Embed** - Create 384-dim embeddings for users and posts
5. **Categorize** - Auto-assign creators to categories (Finance, Food, Fitness, etc.)

**Key Features:**
- ✅ TikHub API integration with pagination support
- ✅ AI profile analysis (OpenAI GPT-4o-mini or Google Gemini)
- ✅ Multimodal post embeddings (all-MiniLM-L6-v2)
- ✅ Real engagement metrics (follower counts, like/comment ratio)
- ✅ Automatic retry logic for rate limits
- ✅ Batch processing support

---

## 📋 Prerequisites

- Python 3.10+
- MongoDB (local or cloud)
- **TikHub API Token** - Get from [tikhub.io](https://tikhub.io)
- **OpenAI API Key** (for GPT-4o-mini) OR **Google Gemini API Key**

---

## 🚀 Quick Start

### Setup

```bash
# 1. Navigate to collector folder
cd collectors/instagram

# 2. Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials:
#   TIKHUB_TOKEN=your_token_here
#   OPENAI_API_KEY=sk-...
#   MONGO_URI=mongodb+srv://...
```

### Collect Data for a Single User

```bash
# Fetch user data (user info + posts + reels)
python3 test_single_user.py --username herfirst100k
```

**This will:**
1. Fetch user info from TikHub
2. Fetch 2 pages of posts (up to 50 posts each)
3. Fetch 2 pages of reels (up to 50 reels each)
4. Save raw responses to MongoDB (`raw_api_responses`)
5. Create normalized snapshot (`user_snapshots`)

### Analyze User & Generate Embeddings

```bash
# Run full analysis pipeline
python3 pipeline.py --user herfirst100k
```

**This will:**
1. Read snapshot from MongoDB
2. Generate AI profile analysis (topics, style, interests)
3. Create 384-dim user embedding
4. Process all posts and generate post embeddings
5. Calculate engagement rates
6. Save to `user_profiles` and `post_embeddings`

### Batch Process Multiple Users

```bash
# Process all users in user_snapshots
python3 pipeline.py --all

# Or use batch processor
python3 batch_processor.py --platform instagram
```

---

## 📦 Components

### Core Scripts

| File | Purpose | Command |
|------|---------|---------|
| **test_single_user.py** | Fetch data for one Instagram user | `python3 test_single_user.py --username <user>` |
| **pipeline.py** | Analyze user & generate embeddings | `python3 pipeline.py --user <user_id>` |
| **generate_embeddings.py** | Generate embeddings only | `python3 generate_embeddings.py --username <user>` |
| **batch_processor.py** | Batch process multiple users | `python3 batch_processor.py --platform instagram` |
| **update_follower_counts.py** | Extract follower counts from raw data | `python3 update_follower_counts.py` |
| **fix_engagement_data.py** | Update post engagement metrics | `python3 fix_engagement_data.py` |

### Helper Scripts

- **fetcher.py** - TikHub API client
- **adapter.py** - Converts raw API responses to snapshots
- **analyzer.py** - AI profile generation

---

## 📊 Data Schema

### MongoDB Collections

#### 1. raw_api_responses (TikHub raw data)

```json
{
  "username": "herfirst100k",
  "endpoint": "user_info",
  "raw": {
    "code": 200,
    "data": {
      "data": {
        "user": {
          "username": "herfirst100k",
          "edge_followed_by": { "count": 2220917 },
          "edge_owner_to_timeline_media": { "count": 45 }
        }
      }
    }
  },
  "filename": "herfirst100k_user_info_20260221.json",
  "timestamp": "2026-02-21T10:30:00Z"
}
```

#### 2. user_snapshots (Normalized data)

```json
{
  "user_id": "herfirst100k",
  "platform": "instagram",
  "user_info": {
    "username": "herfirst100k",
    "biography": "Financial literacy for women...",
    "follower_count": 2220917
  },
  "posts": [
    {
      "id": "3847291938471",
      "caption": "3 ways to build passive income...",
      "like_count": 12450,
      "comment_count": 342,
      "taken_at": 1739283600
    }
  ]
}
```

#### 3. user_profiles (AI analysis)

```json
{
  "user_id": "herfirst100k",
  "username": "herfirst100k",
  "platform": "instagram",
  "profile_data": {
    "primary_category": "Finance",
    "categories": ["Finance"],
    "content_topics": [
      "financial literacy",
      "investing for women",
      "debt payoff",
      "wealth building"
    ],
    "user_style": {
      "persona": "Financial educator empowering women...",
      "tone": "motivational, educational, empowering",
      "interests": ["finance", "investing", "entrepreneurship"]
    },
    "follower_count": 2220917
  }
}
```

#### 4. post_embeddings (Post-level embeddings)

```json
{
  "post_id": "3847291938471",
  "user_id": "herfirst100k",
  "username": "herfirst100k",
  "platform": "instagram",
  "caption": "3 ways to build passive income...",
  "like_count": 12450,
  "comment_count": 342,
  "engagement_rate": 0.58,
  "categories": ["Finance"],
  "embedding": [0.123, -0.456, ...]
}
```

#### 5. user_embeddings (User-level embeddings)

```json
{
  "user_id": "herfirst100k",
  "platform": "instagram",
  "embedding": [0.234, -0.567, ...],
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "dimension": 384
}
```

---

## 🔧 Advanced Usage

### Custom Categories

Update categories for a creator:

```bash
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, str(Path('../../backend')))
from database.connection import get_database

db = get_database()
db.user_profiles.update_one(
    {'username': 'creator_name'},
    {'\$set': {'profile_data.primary_category': 'Lifestyle'}}
)
"
```

### Extract Follower Counts

If follower counts are missing:

```bash
python3 update_follower_counts.py
```

### Regenerate Embeddings

```bash
# For one user
python3 generate_embeddings.py --username herfirst100k

# For all users
python3 generate_embeddings.py --all
```

### Fix Engagement Data

```bash
python3 fix_engagement_data.py
```

---

## 🎨 AI Profile Analysis

The analyzer uses GPT-4o-mini (or Gemini) to extract:

**User Style:**
- Persona description (50-100 words)
- Tone (friendly, professional, etc.)
- Interests (5-10 keywords)

**Content Topics:**
- 5-7 main content themes

**Categories:**
- Primary category (Finance, Food, Fitness, Fashion, Tech, Wellness, Lifestyle)

---

## 📈 Engagement Metrics

**Calculation:**
```python
engagement_rate = ((like_count + comment_count) / follower_count) * 100
```

**Typical Ranges:**
- < 1%: Low engagement
- 1-3%: Average
- 3-6%: Good
- > 6%: Excellent

---

## 🐛 Troubleshooting

**Issue:** `This account is a restricted profile`  
**Fix:** Account is private. Use a different public account.

**Issue:** `ImportError: cannot import name 'get_database'`  
**Fix:** Add backend to Python path (scripts have this built-in)

**Issue:** `FlagEmbedding import failed`  
**Fix:** Install: `pip install --upgrade transformers FlagEmbedding`

**Issue:** `OpenAI rate limit exceeded`  
**Fix:** Analyzer has built-in retry. Wait or switch to Gemini.

---

## 📚 Complete Workflow Example

```bash
# 1. Collect data
python3 test_single_user.py --username kayla_itsines

# 2. Analyze and embed
python3 pipeline.py --user kayla_itsines

# 3. Verify
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, str(Path('../../backend')))
from database.connection import get_database

db = get_database()
profile = db.user_profiles.find_one({'username': 'kayla_itsines'})
print(f\"Category: {profile['profile_data']['primary_category']}\")
print(f\"Posts: {db.post_embeddings.count_documents({'username': 'kayla_itsines'})}\")
"
```

---

## 🔗 Integration with Backend

The backend API reads data from MongoDB collections populated by this collector:

- Backend reads: `user_profiles`, `post_embeddings`, `user_embeddings`
- Frontend fetches from backend API
- To update: Run collector → Restart backend if needed

---

## 📝 Environment Variables

```bash
# TikHub API
TIKHUB_TOKEN=your_token

# MongoDB
MONGO_URI=mongodb+srv://...
DATABASE_NAME=ig_raw

# AI (choose one)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
```

---

## � Celebrity Accounts Added

The following celebrity Instagram accounts have been added to the database for demo purposes to showcase the AI's ability to capture distinct, recognizable voices.

| Username | Name | Followers | Category | Added | Topics |
|----------|------|-----------|----------|-------|--------|
| **@therock** | Dwayne "The Rock" Johnson | 396M+ | Celebrity | 2026-02-23 | Film/acting, fitness, product endorsements |
| **@kimkardashian** | Kim Kardashian | 363M+ | Celebrity | 2026-02-23 | Brand launches, fashion, family |
| **@realdonaldtrump** | Donald Trump | 26M+ | Celebrity | 2026-02-23 | Political updates, national events, movie promotion |
| **@taylorswift** | Taylor Swift | 283M+ | Celebrity | 2026-02-23 | Music releases, videos, tours, merchandise, storytelling |
| **@leomessi** | Lionel Messi | 504M+ | Celebrity | 2026-02-23 | Football, achievements, brand partnerships, fan engagement |

**Total: 5 Celebrity Accounts**

These high-profile accounts demonstrate the platform's capability to analyze and mimic distinctive content styles from world-famous personalities with massive followings.

---

## �🎯 Next Steps

1. **Start Backend:** `cd ../../backend && uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload`
2. **Start Frontend:** `cd ../../xhs-analyser-frontend && pnpm dev`
3. **Access UI:** http://localhost:3000

