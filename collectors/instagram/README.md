# Instagram Data Analysis Pipeline

A complete end-to-end data pipeline for Instagram user analysis powered by AI. Fetches raw data from TikHub, generates user profiles with ChatGPT/Gemini, creates multimodal embeddings (user + post level), and stores everything in MongoDB.

## 🎯 Overview

This pipeline provides a full solution for Instagram user analysis:

1. **Fetch** - Raw Instagram data via TikHub API (`fetcher.py`)
2. **Adapt** - Transform raw API responses into snapshots (`adapter.py`)
3. **Analyze** - Generate user profiles with ChatGPT/Gemini (`analyzer.py`) 
4. **Embed (User)** - Create 512-dim user style embeddings with FlagEmbedding (`pipeline.py`)
5. **Embed (Posts)** - Extract 384-dim multimodal post embeddings with YOLO + OCR + text (`extract_post_multimodal.py`)
6. **Store** - Save all data to MongoDB with duplicate prevention
7. **(Optional)** Display results in Next.js frontend

**Key Features:**
- ✅ **Complete Pipeline** - From TikHub API to MongoDB to Frontend
- ✅ **Multimodal Embeddings** - User-level (text) + Post-level (vision + text + engagement)
- ✅ **AI Profile Analysis** - GPT-4o-mini or Gemini with automatic retry on rate limits
- ✅ **Smart Visual Processing** - YOLO object detection + EasyOCR text extraction
- ✅ **Production Ready** - Upsert logic, retry mechanisms, graceful error handling
- ✅ **Local-First Mode** - Option to save fetched data locally before MongoDB upload
- ✅ **Flexible Providers** - OpenAI or Google Gemini for analysis

---

## 📋 Prerequisites

- Python 3.10+
- MongoDB instance (local or cloud)
- **TikHub API Token** (for data fetching) - Get from [TikHub.io](https://tikhub.io)
- One of:
  - **OpenAI API key** (recommended: gpt-4o-mini)
  - **Google Gemini API key** (gemini-2.0-flash)
- ~3GB disk space (2.3GB for venv + models, rest for temp files)

---

## 📁 Architecture

### Components Overview

| File | Purpose | Status |
|------|---------|--------|
| **fetcher.py** | Fetches raw data from TikHub API (user bio, posts, reels) | ✅ Production |
| **adapter.py** | Converts raw_api_responses → user_snapshots | ✅ Fixed |
| **analyzer.py** | AI profile analysis with ChatGPT/Gemini + retry logic | ✅ Enhanced |
| **pipeline.py** | Main orchestrator: fetch → analyze → embed → store | ✅ Complete |
| **extract_post_multimodal.py** | Extract post embeddings (YOLO + OCR + text) | ✅ New |
| **batch_processor.py** | Batch process multiple users with skip logic | ✅ Tested |

### MongoDB Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| **raw_api_responses** | Raw TikHub API responses | `user_id`, `endpoint`, `data`, `filename` |
| **user_snapshots** | Normalized user + posts structure | `user_id`, `username`, `user_info`, `posts[]` |
| **user_profiles** | AI-generated profile analysis | `user_id`, `username`, `profile_data.user_style`, `topics` |
| **user_embeddings** | 512-dim user style embeddings | `user_id`, `user_style_embedding`, `model`, `dimension` |
| **post_embeddings** | 384-dim multimodal post embeddings | `post_id`, `user_id`, `embedding`, `caption`, `objects`, `ocr_text` |

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DATA FETCHING (fetcher.py)                              │
│    TikHub API → raw_api_responses (MongoDB)                │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DATA ADAPTATION (adapter.py)                            │
│    raw_api_responses → user_snapshots (MongoDB)            │
│    • Extracts username from filenames                      │
│    • Normalizes post structure                             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PROFILE ANALYSIS (pipeline.py → analyzer.py)            │
│    user_snapshots → ChatGPT/Gemini → user_profiles         │
│    • 5 content topics                                      │
│    • User style analysis                                   │
│    • Retry logic for rate limits                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. USER EMBEDDING (pipeline.py + FlagEmbedding)            │
│    profile_data → BAAI/bge-small-zh-v1.5 → user_embeddings │
│    • 512 dimensions                                        │
│    • Text-based embedding from user style                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. POST EMBEDDINGS (extract_post_multimodal.py)            │
│    posts → YOLO + OCR + Transformer → post_embeddings     │
│    • 384 dimensions (all-MiniLM-L6-v2)                     │
│    • Object detection (YOLO)                               │
│    • Text extraction (EasyOCR)                             │
│    • Caption embedding                                     │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. FRONTEND (Optional - Next.js + FastAPI)                 │
│    MongoDB → API → React UI                                │
│    • Search by style                                       │
│    • Vector similarity                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd collectors/instagram
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**Note:** The system will automatically install compatible versions:
- `transformers<5.0.0` (for FlagEmbedding compatibility)
- `FlagEmbedding==1.3.5` (for user embeddings)
- `sentence-transformers` (for post embeddings)
- `ultralytics` (YOLO for object detection)
- `easyocr` (for text extraction)

### 2. Configure Environment Variables

Create `.env` file in `collectors/instagram/`:

```env
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=ig_raw

# TikHub API (for data fetching)
TIKHUB_API_TOKEN=your-tikhub-token
TIKHUB_BASE_URL=https://api.tikhub.io  # Optional, this is default

# AI Provider (choose one)
# Option 1: OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
CHAT_MODEL=gpt-4o-mini
AI_PROVIDER=openai

# Option 2: Google Gemini
# GEMINI_API_KEY=your-gemini-api-key
# GEMINI_MODEL=gemini-2.0-flash
# AI_PROVIDER=gemini

# Embedding Models (optional - uses defaults if not specified)
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5  # For user embeddings (512-dim)
# POST_EMBEDDING_MODEL=all-MiniLM-L6-v2  # For post embeddings (384-dim)
```

### 3. Download Required Models

The pipeline will auto-download models on first run:
- **BAAI/bge-small-zh-v1.5** (96MB) - User embeddings
- **all-MiniLM-L6-v2** (88MB) - Post embeddings  
- **yolov8n.pt** (6MB) - Object detection

---

## 🔧 Usage

### Complete Pipeline (Recommended)

Process a user from TikHub API → MongoDB → Embeddings:

```bash
# Full pipeline: fetch + analyze + user embedding + post embeddings
python3 pipeline.py --fetch_username mondaypunday

# This automatically:
# 1. Fetches raw data from TikHub
# 2. Creates snapshot
# 3. Analyzes profile with ChatGPT/Gemini
# 4. Generates 512-dim user embedding
# 5. Stores everything in MongoDB
```

Then extract post embeddings:

```bash
# Extract multimodal embeddings for 10 posts
python3 extract_post_multimodal.py --username mondaypunday --count 10
```

**Expected Output:**
```
📦 Loading embedding model: BAAI/bge-small-zh-v1.5
✅ Embedding model loaded

🎯 Processing Instagram user: mondaypunday
✅ Found user: mondaypunday (25 posts)

🤖 Analyzing user profile...
✅ Generated embedding (dimension: 512)
✅ Analysis complete
   - Topics: 5
   - Embedding: 512 dimensions

💾 Step 3: Saving to MongoDB...
✅ Updated user_profiles
✅ Created user_embeddings

🎬 Extracting multimodal embeddings for: mondaypunday
✅ Found 10 posts with media
📦 Loading models...
✅ Models loaded

📸 Processing post 1/10
   - YOLO detected: 1 person
   - Caption: "Dallas 12/22-23..."
   - Embedding: 384 dimensions
✅ Saved to MongoDB: post_embeddings

... [9 more posts]

✅ Processing complete! (10/10 posts, 100% success)
```

### Batch Processing

Process multiple users efficiently:

```bash
# Process only new users (skip existing)
python3 batch_processor.py

# Force reprocess all users
python3 batch_processor.py --force-all

# Force reprocess specific users
python3 batch_processor.py --force user1 user2 user3
```

### Paged Fetching with Local Storage

For large accounts or reproducibility, fetch data locally first:

```bash
# Fetch 3 pages of posts, 2 pages of reels, store locally first
python3 pipeline.py --fetch_username_paged mondaypunday \
  --post_pages 3 \
  --reel_pages 2 \
  --page_count 12 \
  --store_local_first \
  --local_file_limit 5

# Files saved to: outputs/raw/instagram/mondaypunday/
# Then uploaded to MongoDB after all pages fetched
```

### Diagnostics

Check your environment configuration:

```bash
python3 pipeline.py --diagnose
```

**Output:**
```
🔍 Running diagnostics...
 - MONGO_URI: True
 - TIKHUB_BASE: True
 - TIKHUB_TOKEN: True
 - MONGO_CONNECT: True
 - FLAG_EMBEDDING_AVAILABLE: True
```

---

## 📊 MongoDB Data Structures

### 1. user_profiles Collection

```json
{
  "_id": "ObjectId(...)",
  "platform": "instagram",
  "user_id": "mondaypunday",
  "username": "mondaypunday",
  "profile_data": {
    "user_style": {
      "persona": "Stand-up comedian sharing observational humor about daily life...",
      "tone": "Humorous, relatable, conversational, authentic",
      "interests": ["comedy", "stand-up", "social commentary", "storytelling"]
    },
    "content_topics": [
      {"topic": "Stand-up Comedy", "percentage": 40},
      {"topic": "Humor and Satire", "percentage": 25},
      {"topic": "Social Commentary", "percentage": 20},
      {"topic": "Cultural Observations", "percentage": 10},
      {"topic": "Life Experiences", "percentage": 5}
    ],
    "posting_pattern": {
      "frequency": "Weekly to bi-weekly",
      "best_time_to_post": "Evening (7-10 PM)",
      "content_mix": ["video clips", "tour dates", "promotional content"]
    },
    "audience_type": ["Comedy fans", "Young adults", "Social observers"],
    "engagement_style": "Interactive - responds to comments, promotional",
    "brand_fit": ["Comedy clubs", "Entertainment platforms", "Lifestyle brands"]
  },
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:35:00Z"
}
```

### 2. user_embeddings Collection

```json
{
  "_id": "ObjectId(...)",
  "platform": "instagram",
  "user_id": "mondaypunday",
  "user_style_embedding": [0.0234, -0.1245, 0.0567, ...],  // 512 floats
  "model": "BAAI/bge-small-zh-v1.5",
  "dimension": 512,
  "created_at": "2026-02-06T10:35:00Z",
  "updated_at": "2026-02-06T10:35:00Z"
}
```

### 3. post_embeddings Collection

```json
{
  "_id": "ObjectId(...)",
  "platform": "instagram",
  "post_id": "2982334644151768448",
  "user_id": "mondaypunday",
  "username": "mondaypunday",
  "embedding": [-0.0591, -0.0529, -0.0117, ...],  // 384 floats
  "caption": "Dallas 12/22-23\nDetroit 12/29-31...",
  "objects": ["person"],  // YOLO detections
  "ocr_text": [],  // EasyOCR extractions
  "like_count": 216879,
  "comment_count": 599,
  "play_count": 2485055,
  "media_urls": ["https://instagram.fmil1-1.fna.fbcdn.net/..."],
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "dimension": 384,
  "created_at": "2026-02-06T11:00:00Z"
}
```

### 4. user_snapshots Collection

```json
{
  "_id": "ObjectId(...)",
  "platform": "instagram",
  "user_id": "mondaypunday",
  "username": "mondaypunday",
  "user_info": {
    "username": "mondaypunday",
    "full_name": "Monday Punday",
    "bio": "Comedian | Tour dates below",
    "follower_count": 150000,
    "following_count": 500,
    "posts_count": 25
  },
  "posts": [
    {
      "id": "2982334644151768448",
      "caption": "Dallas 12/22-23...",
      "likes": 216879,
      "comments": 599,
      "timestamp": 1735167600,
      "media_type": "video",
      "media_url": "https://..."
    }
    // ... 24 more posts
  ],
  "snapshot_date": "2026-02-06T09:00:00Z"
}
```

### 5. raw_api_responses Collection

```json
{
  "_id": "ObjectId(...)",
  "user_id": "mondaypunday",
  "endpoint": "user_posts",
  "filename": "instagram(mondaypunday)_posts_001.json",
  "data": {
    "items": [ /* raw API response */ ],
    "next_cursor": "..."
  },
  "created_at": "2026-02-06T08:00:00Z"
}
```

---

## 🔗 Frontend Integration (Optional)

To display results in the frontend:

1. **API is already set up** - The FastAPI backend at `/api/creators/*` already works with these MongoDB collections

2. **Your data will be available at:**
   - `GET /api/creators/list` - All Instagram creators
   - `GET /api/creators/{username}` - Specific creator details
   - `GET /api/style/creators` - Filter by style/interests

3. **Frontend Access:**
   ```bash
   cd xhs-analyser-frontend
   pnpm dev
   # Visit http://localhost:3000
   ```

The frontend automatically displays data from the `user_profiles` and `user_embeddings` collections.

---

## 📊 Performance & Costs

### Estimated Costs (per user analysis)

| Provider | Model | Est. Cost |
|----------|-------|-----------|
| OpenAI | gpt-4o-mini | ~$0.01-0.03 per user |
| Google Gemini | gemini-2.0-flash | ~$0.005-0.02 per user |

### Processing Time

- **Per user:** 5-15 seconds (API call + data processing)
- **100 users:** ~10-25 minutes
- **1000 users:** ~2-4 hours
- **Batch processing:** Smart skipping of existing users reduces time on re-runs

### Optimization Tips

```bash
# Process in small batches for reliability
python3 batch_processor.py  # Process new users (fast)

# If reprocessing large batches:
python3 batch_processor.py --force-all --limit 50  # First 50
# Wait for completion, check results
python3 batch_processor.py --force-all --limit 100  # Next batch
```

---

## 🐛 Known Issues & Solutions

### ~~Issue: FlagEmbedding Import Error~~ ✅ FIXED

**Error:** `AttributeError: module 'transformers' has no attribute 'is_torch_fx_available'`

**Status:** ✅ **RESOLVED** - Fixed by downgrading transformers

**Root Cause:** FlagEmbedding 1.3.5 is incompatible with transformers 5.0.0 (removed `is_torch_fx_available`)

**Solution:**
```bash
pip install 'transformers<5.0.0'  # Will install 4.57.6
pip install FlagEmbedding==1.3.5
```

**Verification:**
```bash
python3 pipeline.py --diagnose
# Should show: FLAG_EMBEDDING_AVAILABLE: True ✅
```

**Result:** User embeddings now generate successfully with **512 dimensions** using BAAI/bge-small-zh-v1.5 model.

---

### Issue: OpenAI Rate Limit (429 Error)

**Error:** `HTTPError: 429 Too Many Requests`

**Status:** ✅ **Automatically Handled** - Retry logic implemented

**Solution:**
- Pipeline automatically retries 5 times with exponential backoff
- First retry after 1 second, final retry after 16 seconds
- If you still get 429 after 5 retries: Your account is rate-limited
- **Action:** Wait 1-2 hours or upgrade your OpenAI account tier

### Issue: MongoDB Connection Failed

```bash
# Test connection
python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('YOUR_MONGO_URI', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✅ Connected successfully')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Issue: No Users Found

```bash
# Check if raw_api_responses collection has data
python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DATABASE_NAME', 'ig_raw')]
docs = db['raw_api_responses'].find()
for doc in docs[:3]:
    print('Keys:', list(doc.keys())[:10])
    break
"
```

---

## 📝 Example: Direct Python Usage

```python
from pipeline import process_instagram_user
import os
from dotenv import load_dotenv

load_dotenv()

# Process single user
process_instagram_user("herfirst100k")

# Check results in MongoDB
from pymongo import MongoClient
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DATABASE_NAME', 'ig_raw')]
profile = db['user_profiles'].find_one({'username': 'herfirst100k'})
print("User style:", profile['profile_data']['user_style'])
print("Topics:", profile['profile_data']['content_topics'])
```

---

## 📚 File Reference

### adapter.py Key Functions

```python
extract_username(filename: str) -> str
    # Extract username from filename like "xxx(username)_... .json"

extract_posts(data: dict) -> list
    # Extract posts from raw API response structure

normalize_snapshot(raw_docs: list) -> dict
    # Convert raw API responses to pipeline-compatible snapshot
```

### analyzer.py Key Functions

```python
analyze_user_profile(user_info, posts, ai_provider) -> dict
    # Analyzes profile, returns user_style, topics, patterns, etc.
    # Includes 5-retry logic for 429 rate limit errors

call_openai(prompt, system_message) -> str
    # Calls ChatGPT with exponential backoff retry

call_gemini(prompt, system_message) -> str
    # Calls Gemini with exponential backoff retry
```

### pipeline.py Key Functions

```python
process_instagram_user(user_id: str) -> None
    # Main function: reads snapshot → analyzes → saves with upsert
    # Platform-specific duplicate prevention active

get_by_user_id(user_id: str, platform: str = "instagram") -> dict
    # Retrieves existing profile with platform check
```

### batch_processor.py Key Functions

```python
get_users_with_raw_data() -> list
    # Returns list of usernames with raw data in collection

get_users_with_profiles() -> list
    # Returns list of usernames with existing profiles

process_users(users: list, force: bool = False) -> dict
    # Batch processes users, skips existing unless force=True
```

---

## 🔄 Data Flow Diagram

```
Your MongoDB (Raw Instagram Data)
    ↓
collectors/instagram/adapter.py
    ↓
collectors/instagram/pipeline.py
    ↓
analyzer.py (ChatGPT/Gemini with retry logic)
    ↓
MongoDB Storage (user_profiles, user_embeddings)
    ↓
FastAPI Backend (/api/creators/*)
    ↓
Frontend Display (Optional)
```

---

## 🔗 Frontend Integration (Optional)

The backend is already configured to use these MongoDB collections:

```bash
# API endpoints already available:
GET /api/creators/list              # All Instagram creators
GET /api/creators/{username}        # Specific creator details
GET /api/style/creators             # Filter by style/interests

# To run frontend:
cd xhs-analyser-frontend
pnpm dev
# Visit http://localhost:3000
```

The frontend automatically reads from `user_profiles` and `user_embeddings` collections.

---

## 🚀 Quick Start (TL;DR)

```bash
# Setup
cd collectors/instagram
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp ../../.env .env
# Edit .env with your MongoDB URI and OpenAI key

# Run
python3 batch_processor.py

# Done! Check MongoDB user_profiles collection
```

---

**Last Updated:** February 06, 2025  
**System Status:** ✅ Complete pipeline with multimodal embeddings - User profiles (512-dim) + Post embeddings (384-dim) working  
**Tested with:** Instagram user mondaypunday - Full pipeline: fetch → analyze → user embedding (512-dim) → post embeddings (10 posts, 384-dim each)  
**Known Issues:** FlagEmbedding compatibility FIXED (transformers<5.0.0)

