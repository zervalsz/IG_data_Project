# Instagram Data Analysis Pipeline

A robust data pipeline for analyzing Instagram user profiles using ChatGPT or Gemini, with automatic retry logic for API rate limits, smart batch processing, and duplicate prevention. Designed to work with your raw MongoDB data without requiring data collection.

## 🎯 Overview

This pipeline is designed to:
1. **Adapt** raw Instagram API responses into user snapshots (via `adapter.py`)
2. **Analyze** user profiles using ChatGPT or Gemini API with automatic retries on rate limits
3. **Store** analysis results back to MongoDB with duplicate prevention
4. **Batch process** multiple users with intelligent detection of existing profiles
5. **(Optional)** Display results in the frontend

**Key Features:**
- ✅ **Skip data collection** - Use your own raw Instagram data (filename pattern: `xxx(username)_... .json`)
- ✅ **Rate limit resilience** - 5 retries with exponential backoff (1s, 2s, 4s, 8s, 16s) for OpenAI 429 errors
- ✅ **Flexible AI provider** - Choose between OpenAI ChatGPT or Google Gemini
- ✅ **Smart batch processing** - `batch_processor.py` auto-detects and skips users with existing profiles
- ✅ **Duplicate prevention** - Profiles are updated, not duplicated on re-runs (upsert with platform-specific checks)
- ✅ **Adapter pattern** - Transforms raw API responses into pipeline-compatible snapshots
- ✅ **Compatible with frontend** - Same MongoDB structure as original pipeline

---

## 📋 Prerequisites

- Python 3.10+
- MongoDB instance with `ig_raw` database
- Raw Instagram data in `raw_api_responses` collection
- One of:
  - **OpenAI API key** (for ChatGPT - gpt-4o-mini recommended)
  - **Google Gemini API key** (for Gemini - gemini-2.0-flash)
- If you want to fetch raw data via TikHub:
  - **TIKHUB_API_TOKEN** environment variable (required)
  - **TIKHUB_BASE_URL** (optional, defaults to https://api.tikhub.io)
- Raw data filenames should follow pattern: `xxx(username)_... .json` for automatic username extraction

---

## 📁 Architecture

### Components

| File | Purpose | Status |
|------|---------|--------|
| `adapter.py` | Converts raw_api_responses → user_snapshots, extracts username from filenames | ✅ Fixed (no more duplicate posts) |
| `analyzer.py` | Analyzes profiles with ChatGPT/Gemini, includes retry logic for 429 errors | ✅ Enhanced (5 retries + exponential backoff) |
| `pipeline.py` | Orchestrator: reads snapshots → calls analyzer → saves with upsert | ✅ Enhanced (platform-specific upsert, duplicate prevention) |
| `batch_processor.py` | **NEW** - Processes multiple users, auto-detects existing profiles | ✅ Fully tested |
| `requirements.txt` | Dependencies | ✅ Complete |

### Data Flow

```
raw_api_responses (MongoDB)
    ↓ [adapter.py extracts username from filenames]
user_snapshots (MongoDB)
    ↓ [pipeline.py reads + calls analyzer.py]
ChatGPT/Gemini API
    ↓ [analysis with retry logic on 429 errors]
user_profiles (MongoDB) - Upserted with platform='instagram' check
user_embeddings (MongoDB) - Optional; generated using `FlagEmbedding` when available, otherwise a local `sentence-transformers` fallback will be used if installed (see `EMBEDDING_MODEL` env var)
    ↓ [FastAPI backend + Frontend]
Display in Frontend (Optional)
```

---

## 📋 Prerequisites

- Python 3.8+
- MongoDB instance with your Instagram data
- One of:
  - OpenAI API key (for ChatGPT)
  - Google Gemini API key
- ~2GB disk space for embedding model

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd collectors/instagram
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env` file in `collectors/instagram/`:

**For ChatGPT (OpenAI):**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=ig_raw
RAW_COLLECTION=raw_api_responses
OPENAI_API_KEY=sk-your-openai-api-key
CHAT_MODEL=gpt-4o-mini
AI_PROVIDER=openai
```

**For Gemini (Google):**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=ig_raw
RAW_COLLECTION=raw_api_responses
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash
AI_PROVIDER=gemini
```

### 3. Verify Your MongoDB Data

Your data should be in `raw_api_responses` collection:

```bash
# Check collection exists and count documents
python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DATABASE_NAME', 'ig_raw')]
count = db['raw_api_responses'].count_documents({})
print(f'Documents in raw_api_responses: {count}')

# Show sample document structure
sample = db['raw_api_responses'].find_one()
print(f'Sample doc keys: {list(sample.keys()) if sample else \"Empty\"}')
"
```

---

## 🔧 Usage

### Option 1: Process All Users (Smart Batch Processing - Recommended)

The `batch_processor.py` script automatically:
- Detects all users with raw data in `raw_api_responses`
- Skips users who already have profiles in `user_profiles`
- Only processes new users

```bash
# Default: process only new users (skips existing)
python3 batch_processor.py

# Reprocess all users (overwrite existing profiles)
python3 batch_processor.py --force-all

# Process specific users
python3 batch_processor.py --force username1 username2 username3
```

**Output:**
```
🔍 Scanning for Instagram users with raw data...
✅ Found 6 users with raw data
📊 Checking existing profiles...
   - doobydobap: ✅ Already has profile (skip)
   - herfirst100k: ✅ Already has profile (skip)
   - jackinvestment: ❌ No profile (will process)
   - madfitig: ❌ No profile (will process)
   - rainn: ❌ No profile (will process)
   - theholisticpsychologist: ❌ No profile (will process)

🚀 Processing 4 new users...
[1/4] Processing jackinvestment...
✅ Created user_profiles
✅ Created user_embeddings (0 dimensions - FlagEmbedding unavailable)

... [progress for each user]

✅ All users processed successfully!
Processing summary:
  - New profiles: 4
  - Updated profiles: 0
  - Skipped (existing): 2
  - Failed: 0
```

### Option 2: Process Single User

```bash
python3 pipeline.py --user_id username_or_user_id
```

Example with detailed output:
```
============================================================
🎯 Processing Instagram user: herfirst100k
============================================================

📥 Step 1: Reading data from MongoDB...
✅ Found user: herfirst100k
   - Posts: 49
   - Profile created: 2024-01-15

🤖 Step 2: Analyzing user profile...
✅ Analysis complete
   - Topics identified: 5
   - Embedding: 0 dimensions (FlagEmbedding unavailable - gracefully skipped)

💾 Step 3: Saving to MongoDB...
✅ Updated user_profiles (duplicate prevention active)

✨ User herfirst100k analysis complete!
```

### Option: Fetch + Process a Username

If you have valid TikHub credentials in your environment, you can fetch raw data and process it in one command:

```bash
# Fetch raw data for `doobydobap`, upsert snapshot, then run analysis & save profile
python3 pipeline.py --fetch_username doobydobap
```

This runs:
1. `fetch_user_info` (and `fetch_user_posts`/`fetch_user_reels` if available)
2. Upserts a `user_snapshots` document for that username
3. Runs the analyzer and saves `user_profiles` / `user_embeddings`


📥 Step 1: Reading data from MongoDB...
✅ Found user: herfirst100k
   - Posts: 49
   - Profile created: 2024-01-15

🤖 Step 2: Analyzing user profile...
✅ Analysis complete
   - Topics identified: 5
   - Embedding: 0 dimensions (FlagEmbedding unavailable - gracefully skipped)

💾 Step 3: Saving to MongoDB...
✅ Updated user_profiles (duplicate prevention active)

✨ User herfirst100k analysis complete!
```

### Option 3: Process Multiple Users

```bash
# Reprocess all users (overwrite)
python3 pipeline.py --all

# Process first 10 users
python3 pipeline.py --all --limit 10
```

---

## ✨ Verified System Status

**Currently Processed Users (6 total):**

| Username | Posts | Topics | Status |
|----------|-------|--------|--------|
| doobydobap | 49 | Korean food, cooking, lifestyle | ✅ Profile created |
| herfirst100k | 49 | Financial empowerment, women's finance, investing, career, business | ✅ Profile created |
| jackinvestment | 25 | Investment, personal growth, financial tips | ✅ Profile created |
| madfitig | 49 | Fitness, health, training, wellness, lifestyle | ✅ Profile created |
| rainn | 37 | Sexual assault awareness, prevention, support, community, empowerment | ✅ Profile created |
| theholisticpsychologist | 49 | Mental health, psychology, wellness, personal development, spirituality | ✅ Profile created |

**Key Improvements Made:**
- ✅ Fixed duplicate post extraction (was extracting 97, now correctly shows 49)
- ✅ Implemented 5-retry exponential backoff for OpenAI rate limits
- ✅ Implemented platform-specific upsert to prevent duplicate profiles
- ✅ Created batch processor for intelligent multi-user processing
- ✅ All 6 users analyzed without duplicates on re-runs

---

## � Recent changes (what I implemented)
These are the recent reliability and usability improvements made to the TikHub-based Instagram collector and how to use them.

### ✅ Reliability & error handling
- **Retry + backoff for HTTP calls**: Added an internal `_http_get(...)` helper that retries transient errors (network failures, 429, and 5xx) with exponential backoff to reduce flaky failures. 🚀
- **Clearer error persistence**: When API calls fail (client or server errors), the raw error body and status are now saved into the DB with endpoints like `posts_list_error` and `reels_list_error` so you can triage failures later. 🧾
- **Improved error messages**: Fetch functions raise clearer `RuntimeError` that include HTTP status and response body for faster debugging. 🔎

### 📁 Local-first & reproducibility
- **Local-first mode for paged fetches**: `fetch_and_store_paged(..., store_local_first=True)` (or CLI flag `--store_local_first`) writes all fetched pages (user_info, posts pages, reels pages) to `outputs/raw/instagram/<username>/...` first, then uploads them to MongoDB in a second step.
  - Use `--local_file_limit <n>` (default 5) to stop after collecting n files if you only want a small sample.
  - This ensures you always have reproducible local copies before any DB activity. 💾
- **Single-fetch local copies**: Single-page fetch calls (e.g., `fetch_user_posts` / `fetch_user_reels`) now also write a local JSON file even if `save=False`, so you get a local snapshot for every fetch. 📂

### 🔒 Pagination safety
- **Repeated cursor detection**: Pagination stops if the next cursor repeats (prevents infinite loops when the API returns the same cursor). ⚠️
- **Candidate cursor heuristics**: When no explicit next cursor is present, heuristics try to find a candidate `max_id` or `end_cursor` from last items so you can still fetch more pages in many cases. 🧠

### 🧰 CLI & diagnostics
- **New CLI flags:**
  - `--store_local_first` (paired with `--local_file_limit`) for `--fetch_username_paged`
  - `--diagnose` to run environment connectivity and credential checks (checks `MONGO_URI`, `TIKHUB_API_TOKEN`, DB connectivity, and FlagEmbedding availability)
- **Usage example (collect locally then upload):**

```bash
cd collectors/instagram
python3 pipeline.py --fetch_username_paged adventuresofnik --post_pages 3 --reel_pages 2 --page_count 12 --store_local_first --local_file_limit 5
```

This will:
1. Fetch user_info and up to the requested pages, writing each page to `outputs/raw/instagram/adventuresofnik/`.
2. After collection completes, upload local files to `raw_api_responses` and upsert snapshot.

### ✅ Tests & dev ergonomics
- **Tests added**: Added `tests/test_fetcher_local_and_retry.py` and `tests/test_store_local_first.py` covering local writes, retry behavior, repeated-cursor stop, and the local-first upload flow.
- **Tests support in minimal envs**: tests include a `conftest.py` that ensures the project root is importable and core imports (`dotenv`, `pymongo`) are handled gracefully in test environments.

---

## �📊 Output Data Structure

### 1. `user_profiles` Collection

```json
{
  "_id": ObjectId("..."),
  "platform": "instagram",
  "user_id": "123456789",
  "username": "example_user",
  "profile_data": {
    "user_style": {
      "persona": "Finance-focused educator empowering women to take control of their financial future through accessible, actionable advice",
      "tone": "Motivational, educational, empowering, relatable, authentic",
      "interests": ["financial literacy", "women's empowerment", "investing", "career growth"]
    },
    "content_topics": ["financial education", "women's investing", "career development", "wealth building", "financial independence"],
    "posting_pattern": {
      "frequency": "Daily to every other day",
      "best_time_to_post": "Morning (7-10 AM) or evening (6-9 PM)",
      "content_mix": ["educational posts", "personal stories", "financial tips", "carousel posts"]
    },
    "audience_type": ["Young women", "Career professionals", "Aspiring investors", "Financial learners"],
    "engagement_style": "Interactive and educational - responds to comments, asks questions, provides actionable advice",
    "brand_fit": ["Financial services", "Career development platforms", "Investment apps", "Educational tech"],
    "user_style_embedding": []  // 0 dimensions if FlagEmbedding unavailable
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 2. `user_embeddings` Collection (Optional)

```json
{
  "_id": ObjectId("..."),
  "platform": "instagram",
  "user_id": "example_user",
  "user_style_embedding": [],
  "model": "BAAI/bge-small-zh-v1.5",
  "dimension": 0,
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

## 🎨 Analysis Output Fields

The analyzer provides comprehensive user profile data:

| Field | Description |
|-------|-------------|
| `user_style.persona` | 2-3 sentence description of the user's identity |
| `user_style.tone` | Words describing their posting/writing style |
| `user_style.interests` | Key interest areas and topics |
| `content_topics` | Main content categories |
| `posting_pattern` | Frequency, best times, content mix |
| `audience_type` | Demographics of followers |
| `engagement_style` | How they interact with audience |
| `brand_fit` | Suitable brand partnerships |
| `user_style_embedding` | 384-dim vector for similarity search |

---

## 🔄 Key Implementation Details

### Adapter Pattern (adapter.py)

**Transforms raw Instagram API responses into snapshots:**

```python
# Input: raw_api_responses documents
# Process:
# 1. Extract username from filename pattern: xxx(username)_... .json
# 2. Group all raw documents by user_id
# 3. Extract posts from raw.data.items (fixed: no longer duplicates)

# Output: user_snapshots collection with structure:
{
  "platform": "instagram",
  "user_id": "123456789",
  "username": "extracted_from_filename",
  "user_info": {...},
  "posts": [...49 posts per user...]
}
```

### Analyzer with Retry Logic (analyzer.py)

**Analyzes profiles with automatic 429 handling:**

```python
# When ChatGPT/Gemini responds with 429 Too Many Requests:
# Attempt 1: Sleep 1s, retry
# Attempt 2: Sleep 2s, retry
# Attempt 3: Sleep 4s, retry
# Attempt 4: Sleep 8s, retry
# Attempt 5: Sleep 16s, retry
# If still failing, raise exception

# This prevents: "OPENAI_API_KEY... quota exceeded" crashes
# Successfully processed 6 users through retry logic
```

### Duplicate Prevention (pipeline.py)

**Prevents duplicate profiles on re-runs:**

```python
# Old approach (broken):
profile = get_by_user_id(user_id)  # Didn't check platform, missed instagram profiles
if not profile:
    create_profile()  # Created duplicates for same user

# New approach (fixed):
profile = get_by_user_id(user_id, platform='instagram')  # Platform-specific check
if profile:
    collection.update_one(
        {"_id": profile['_id']},
        {"$set": {...new_data...}}
    )  # Upsert existing record
else:
    create_profile()  # Only create if truly new
```

### Smart Batch Processing (batch_processor.py)

**Intelligently processes multiple users:**

```python
# Flow:
users_with_raw = get_users_with_raw_data()  # Query raw_api_responses
users_with_profiles = get_users_with_profiles()  # Query user_profiles

for user in users_with_raw:
    if user in users_with_profiles:
        skip(user)  # Already processed
    else:
        process_user(user)  # Process new user

# Modes:
# --all (default): Skip existing, process new
# --force-all: Reprocess all users
# --force [users]: Force reprocess specific users
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

### Issue: FlagEmbedding Import Error

**Error:** `AttributeError: module 'transformers' has no attribute 'is_torch_fx_available'`

**Status:** ✅ **Gracefully Handled** - Embedding generation is optional

**Solution:** 
- The analyzer catches this error and continues without embeddings
- `user_style_embedding` will be empty array `[]` with dimension 0
- Profile analysis still completes successfully
- Embeddings can be generated later with different model if needed

**Workaround (if you need embeddings):**
```bash
# Try using a different embedding model
pip install sentence-transformers
# Then modify analyzer.py to use SentenceTransformer instead of FlagEmbedding
```

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

**Last Updated:** January 15, 2024  
**System Status:** ✅ All 6 users processed, no duplicates, retry logic active  
**Tested with:** 6 Instagram creators across various niches

