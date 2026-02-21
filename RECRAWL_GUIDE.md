# Data Collector Refinements - Complete Guide

## ✅ What Was Updated

### Backend Models & Services

1. **Database Models** (`backend/database/models.py`)
   - Added `categories: List[str]` to `UserProfileData`
   - Added `categories: List[str]` to `PostEmbedding`

2. **TrendServiceUpdates** (`backend/api/services/trend_service.py`)
   - Updated category names: Lifestyle, Fashion, Food, Fitness, Tech, Wellness, Finance
   - `get_creators_by_category()` uses stored categories (with keyword fallback)
   - Updated all category mappings

3. **API Router** (`backend/api/routers/trend_router.py`)
   - Updated category descriptions to match new capitalized names

### Xiaohongshu Collector (小红书)

4. **Analyzer** (`collectors/xiaohongshu/analyzer.py`)
   - ✅ Updated GPT prompt to request categories
   - ✅ Extracts categories from DeepSeek response
   - ✅ Stores in `profile_data.categories`

5. **Pipeline** (`collectors/xiaohongshu/pipeline.py`)
   - ✅ Added Step 4: Individual post embedding
   - ✅ Each post inherits categories from user
   - ✅ Stores in `post_embeddings` collection

### Instagram Collector

6. **Analyzer** (`collectors/instagram/analyzer.py`)
   - ✅ Updated OpenAI/Gemini prompt to request categories
   - ✅ Added categories to JSON response schema

7. **Pipeline** (`collectors/instagram/pipeline.py`)
   - ✅ Added Step 4: Individual post embedding
   - ✅ Each post inherits categories from user
   - ✅ Stores in `post_embeddings` collection

---

## 🚀 How to Recrawl Your Data

### Option 1: Reprocess Existing Instagram Data (RECOMMENDED)

Since you already have 11 Instagram users in the database, the fastest approach is to reprocess them with the updated pipeline:

```bash
cd /workspaces/IG_data_Project/collectors/instagram

# Test with ONE user first
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent.parent / 'backend'))
from database import UserSnapshotRepository
repo = UserSnapshotRepository()
snap = repo.collection.find_one({'platform': 'instagram'})
if snap:
    print(f'Test user: {snap.get(\"user_id\")}')
"

# Then run pipeline for that user
python3 pipeline.py --user <USER_ID>
```

**Expected output:**
```
🎯 Processing Instagram user: <USER_ID>
📥 Step 1: Reading data from MongoDB...
✅ Found user: username
   - Posts: 50
   - Followers: 10000

🤖 Step 2: Analyzing user profile...
✅ Analysis complete
   - Topics: 5
   - Embedding: 512 dimensions

💾 Step 3: Saving to MongoDB...
✅ Updated user_profiles

📝 Step 4: Processing individual post embeddings...
   - Categories: Food, Lifestyle
✅ Post embeddings complete: 50 new, 0 skipped
```

**Then process all users:**
```bash
python3 pipeline.py --all
```

### Option 2: Collect New Xiaohongshu Data

If you want to collect fresh data from Xiaohongshu:

```bash
cd /workspaces/IG_data_Project/collectors/xiaohongshu

# 1. Collect data for a user
# Edit collector.py and set USER_ID
python3 collector.py

# 2. Process with pipeline
python3 pipeline.py --user_id <USER_ID>

# 3. Repeat for all users you want to add
```

---

## 🧪 Verification Steps

### 1. Check Categories Were Assigned

```bash
cd /workspaces/IG_data_Project/backend
python3 -c "
from database import UserProfileRepository

repo = UserProfileRepository ()
profiles = list(repo.collection.find({'platform': 'instagram'}))

print('=== USER CATEGORIES ===')
for p in profiles:
    username = p.get('username', p.get('user_id'))
    categories = p.get('profile_data', {}).get('categories', [])
    print(f'{username:30} → {categories}')
"
```

**Expected output:**
```
=== USER CATEGORIES ===
user1                          → ['Food', 'Lifestyle']
user2                          → ['Finance']
user3                          → ['Wellness', 'Lifestyle']
...
```

### 2. Check Post Embeddings

```bash
python3 -c "
from database import PostEmbeddingRepository

repo = PostEmbeddingRepository()
count = repo.collection.count_documents({'platform': 'instagram'})
print(f'Total post embeddings: {count}')

# Sample one
post = repo.collection.find_one({'platform': 'instagram'})
if post:
    print(f\"\\nSample post:\")
    print(f\"  ID: {post.get('post_id')}\")
    print(f\"  User: {post.get('username')}\")
    print(f\"  Categories: {post.get('categories')}\")
    print(f\"  Caption: {post.get('caption', '')[:100]}...\")
    print(f\"  Embedding dim: {post.get('dimension')}\")
"
```

**Expected output:**
```
Total post embeddings: 550

Sample post:
  ID: ABC123
  User: username
  Categories: ['Food', 'Lifestyle']
  Caption: Check out this amazing recipe...
  Embedding dim: 512
```

### 3. Test API with Categories

```bash
# Restart backend first
cd /workspaces/IG_data_Project/backend
lsof -ti:5001 | xargs kill -9 2>/dev/null
sleep 2
uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload &

# Wait a few seconds, then test
sleep 5

curl -X POST "http://localhost:5001/api/trend/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Food",
    "platform": "instagram"
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Success: {data.get(\"success\")}')
print(f'Creators analyzed: {data.get(\"creators_analyzed\")}')
print(f'Posts analyzed: {data.get(\"posts_analyzed\")}')
print(f'Content preview: {data.get(\"content\", \"\")[:200]}')
"
```

---

## 📊 Category Distribution

After recrawling, check how your creators are distributed:

```python
from database import UserProfileRepository
from collections import Counter

repo = UserProfileRepository()
profiles = repo.collection.find({'platform': 'instagram'})

all_categories = []
for p in profiles:
    cats = p.get('profile_data', {}).get('categories', [])
    all_categories.extend(cats)

distribution = Counter(all_categories)
print("\\nCategory Distribution:")
for cat, count in distribution.most_common():
    print(f"  {cat:15} {count:3} creators")
```

---

## 🎯 Frontend Integration

After recrawling, your frontend at `localhost:3000/trend-generator` should now:
- Show creators properly categorized
- Display different content for Food vs Finance vs Fitness
- Generate trends based on actual category data

**Test all categories:**
1. Lifestyle
2. Fashion
3. Food
4. Fitness
5. Tech
6. Wellness
7. Finance

---

## ⚠️ Important Notes

1. **Backup First**: Your current data will be updated in-place
2. **API Costs**: Reprocessing all users calls OpenAI/Gemini API (costs money)
3. **Time**: Processing 11 users takes ~5-10 minutes
4. **Embeddings**: Requires FlagEmbedding or sentence-transformers installed

## 🐛 Troubleshooting

**"No categories found"**
- GPT might not return categories → Check API response
- Re-run pipeline for that user

**"All users categorized as Lifestyle"**
- This is the fallback if GPT doesn't assign specific categories
- Check if OpenAI/Gemini API key is valid
- Increase post sample size (currently using first 20-50 posts)

**"Post embeddings not created"**
- Check if FlagEmbedding model is loaded
- Check for errors in Step 4 output
- Verify `post_id` exists in posts

---

## 🎉 Success Criteria

✅ All users have `categories` in `profile_data`  
✅ Post count in `post_embeddings` matches total posts across all users  
✅ API returns different creators for different categories  
✅ Frontend shows diverse content (not all "Lifestyle")  
✅ Evidence section shows relevant keywords/hashtags per category

Ready to recrawl? Start with **Option 1** (reprocess existing Instagram data).
