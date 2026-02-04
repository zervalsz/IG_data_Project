# Instagram Data Schema & Configuration Examples

## 📦 MongoDB Collections Schema

### 1. Raw Data Collection: `user_snapshots`

This is where your existing Instagram data is stored (the input):

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "platform": "instagram",
  "user_id": "123456789",
  "user_info": {
    "username": "travel_blogger",
    "bio": "Exploring the world one photo at a time 🌍",
    "followers": 15000,
    "following": 500,
    "posts_count": 250,
    "profile_pic": "https://...",
    "verified": true,
    "engagement_rate": 4.5
  },
  "posts": [
    {
      "id": "post_123456",
      "caption": "Sunset at Santorini 🌅 The blue domes and white buildings are absolutely stunning!",
      "likes": 3500,
      "comments": 245,
      "shares": 89,
      "hashtags": ["#santorini", "#greece", "#travel", "#sunset"],
      "image_url": "https://...",
      "video_url": null,
      "timestamp": "2024-01-15T18:30:00Z",
      "location": "Oia, Santorini"
    },
    {
      "id": "post_123457",
      "caption": "Street food adventure in Bangkok! 🍜 Best pad thai I've ever had!",
      "likes": 2800,
      "comments": 156,
      "shares": 45,
      "hashtags": ["#bangkok", "#thailand", "#foodie", "#streetfood"],
      "image_url": "https://...",
      "video_url": null,
      "timestamp": "2024-01-14T12:15:00Z",
      "location": "Bangkok, Thailand"
    }
    // ... more posts
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T18:30:00Z"
}
```

**Key Points:**
- Platform must be "instagram"
- user_id should be unique identifier (can be string or number)
- posts is an array with at least caption, likes, comments
- hashtags should be array of strings
- Timestamps in ISO 8601 format

---

### 2. Processed Data Collection: `user_profiles`

This is created by the pipeline (the output):

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "platform": "instagram",
  "user_id": "123456789",
  "username": "travel_blogger",
  "profile_data": {
    "user_style": {
      "persona": "An adventurous and passionate travel enthusiast who documents their journeys with stunning photography and authentic storytelling.",
      "tone": "inspirational, authentic, relatable, educational",
      "interests": [
        "travel",
        "photography",
        "culture",
        "food",
        "adventure",
        "sustainability"
      ]
    },
    "content_topics": [
      "travel destinations",
      "food culture",
      "photography tips",
      "travel guides",
      "sustainable tourism"
    ],
    "posting_pattern": {
      "frequency": "daily",
      "best_time_to_post": "7-9 PM EST",
      "content_mix": [
        "destination photos (40%)",
        "food photography (30%)",
        "travel tips (20%)",
        "personal stories (10%)"
      ]
    },
    "audience_type": [
      "travel enthusiasts (25-45 years)",
      "photography hobbyists",
      "adventure seekers",
      "aspiring travelers",
      "sustainability-conscious consumers"
    ],
    "engagement_style": "Highly interactive with followers. Responds to comments with personal anecdotes and travel advice. Encourages audience to share their own travel experiences.",
    "brand_fit": [
      "travel insurance companies",
      "tourism boards",
      "premium luggage brands",
      "travel apps",
      "eco-friendly products",
      "luxury hotels",
      "photography equipment"
    ],
    "user_style_embedding": [
      0.123, 0.456, 0.789, -0.234, 0.567, ...
      // 384-dimensional vector
    ]
  },
  "created_at": "2024-01-15T18:35:00Z",
  "updated_at": "2024-01-15T18:35:00Z"
}
```

---

### 3. Embedding Collection: `user_embeddings`

Separate collection for embeddings (useful for similarity searches):

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "platform": "instagram",
  "user_id": "travel_blogger",
  "user_style_embedding": [
    0.123, 0.456, 0.789, -0.234, 0.567, 0.891, -0.345, 0.678, ...
    // 384 dimensions total
  ],
  "model": "BAAI/bge-small-zh-v1.5",
  "dimension": 384,
  "created_at": "2024-01-15T18:35:00Z"
}
```

---

## 🔧 Configuration Examples

### Example 1: Using ChatGPT (OpenAI)

**.env file:**
```env
# MongoDB
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=instagram_data

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz
CHAT_MODEL=gpt-4o-mini
AI_PROVIDER=openai

# Embedding
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

**Usage:**
```bash
python3 pipeline.py --user_id 123456789
```

---

### Example 2: Using Google Gemini

**.env file:**
```env
# MongoDB
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=instagram_data

# Google Gemini Configuration
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.0-flash
AI_PROVIDER=gemini

# Embedding
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

**Usage:**
```bash
python3 pipeline.py --user_id 123456789
```

---

### Example 3: Local MongoDB

**.env file:**
```env
# Local MongoDB
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=instagram_data

# OpenAI
OPENAI_API_KEY=sk-...
AI_PROVIDER=openai
```

**Start MongoDB locally:**
```bash
# Using Docker
docker run -d -p 27017:27017 mongo

# Or with mongodb server
mongod
```

---

## 📝 Data Validation Checklist

Before running the pipeline, verify your MongoDB data:

```javascript
// MongoDB shell commands to check your data

// 1. Check collection exists
db.user_snapshots.countDocuments()

// 2. Check platform field
db.user_snapshots.find({platform: "instagram"}).count()

// 3. Check required fields
db.user_snapshots.findOne({platform: "instagram"})

// 4. Check user has posts
db.user_snapshots.findOne(
  {platform: "instagram"},
  {posts: {$slice: 1}}
)

// 5. Check all users
db.user_snapshots.aggregate([
  {$match: {platform: "instagram"}},
  {$group: {_id: "$user_id"}},
  {$count: "total"}
])
```

---

## 🔍 After Processing - Query Results

After the pipeline runs, query your results:

```javascript
// Find processed user profiles
db.user_profiles.findOne({platform: "instagram"})

// Find user embeddings
db.user_embeddings.findOne({platform: "instagram"})

// Find all travel-related creators (search in profile_data)
db.user_profiles.find({
  "profile_data.content_topics": "travel"
})

// Find creators with high engagement style
db.user_profiles.find({
  platform: "instagram"
})
.sort({created_at: -1})
.limit(10)

// Search embeddings by similarity (requires vector search index in MongoDB)
db.user_embeddings.aggregate([
  {
    $search: {
      cosmosSearch: {
        vector: [0.123, 0.456, ...],  // Your query vector
        k: 5
      },
      returnScore: "similarityScore"
    }
  }
])
```

---

## 🎯 API Endpoints (via FastAPI Backend)

After data is in MongoDB, access via FastAPI:

### List All Creators
```
GET /api/creators/list
```

Response:
```json
{
  "creators": [
    {
      "id": "123456789",
      "name": "travel_blogger",
      "platform": "instagram",
      "interests": ["travel", "photography"],
      "follower_count": 15000
    }
  ]
}
```

### Get Creator Details
```
GET /api/creators/travel_blogger
```

Response:
```json
{
  "user_id": "123456789",
  "username": "travel_blogger",
  "platform": "instagram",
  "profile_data": {
    "user_style": {...},
    "content_topics": [...],
    "posting_pattern": {...},
    "audience_type": [...]
  }
}
```

### Filter by Style/Interests
```
POST /api/style/creators
Body: {
  "interests": ["travel", "photography"]
}
```

---

## 🐛 Debugging Tips

### View Raw Data
```python
from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGO_URI'])
db = client['instagram_data']

# View one user snapshot
user = db['user_snapshots'].find_one({'platform': 'instagram'})
print(user)

# View processed profile
profile = db['user_profiles'].find_one({'platform': 'instagram'})
print(profile['profile_data'])
```

### Check Processing Status
```python
# Count unprocessed vs processed
raw = db['user_snapshots'].count_documents({'platform': 'instagram'})
processed = db['user_profiles'].count_documents({'platform': 'instagram'})
print(f"Raw: {raw}, Processed: {processed}, Remaining: {raw - processed}")
```

### View Embeddings
```python
embedding = db['user_embeddings'].find_one({'platform': 'instagram'})
print(f"Embedding dimension: {len(embedding['user_style_embedding'])}")
print(f"First 10 values: {embedding['user_style_embedding'][:10]}")
```

---

## 📊 Performance Metrics

Expected results for batch processing:

| Metric | Value |
|--------|-------|
| Time per user | 5-15 seconds |
| API calls per user | 1 (to ChatGPT/Gemini) |
| Cost per user | $0.01-0.02 |
| Embedding size | 384 dimensions |
| Embedding generation | <1 second |
| MongoDB write | <1 second |

**Total for 100 users:**
- Time: 10-25 minutes
- Cost: $1-2
- Storage: ~100 MB (profiles + embeddings)

---

That's everything you need! 🚀
