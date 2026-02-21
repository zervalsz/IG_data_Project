# Data Collector Refinements - Test Guide

## What Was Updated

### 1. Database Models (`backend/database/models.py`)
- ✅ Added `categories: List[str]` to `UserProfileData`
- ✅ Added `categories: List[str]` to `PostEmbedding`

### 2. Analyzer (`collectors/xiaohongshu/analyzer.py`)
- ✅ Updated GPT prompt to classify users into categories
- ✅ Categories: Lifestyle, Fashion, Food, Fitness, Tech, Wellness, Finance
- ✅ Extracts `categories` from GPT response and stores in `profile_data`

### 3. Pipeline (`collectors/xiaohongshu/pipeline.py`)
- ✅ Added Step 4: Embed individual posts
- ✅ Each post gets its own embedding in `post_embeddings` collection
- ✅ Posts inherit categories from user profile
- ✅ Stores: post_id, user_id, username, embedding, caption, categories, engagement metrics

### 4. TrendService (`backend/api/services/trend_service.py`)
- ✅ Updated category names: Finance, Wellness, Food, Fitness, Fashion, Tech, Lifestyle
- ✅ `get_creators_by_category()` now uses stored categories (with keyword fallback)
- ✅ Updated category mappings and display names

## How to Test

### Step 1: Test with One User

```bash
cd /workspaces/IG_data_Project/collectors/xiaohongshu

# Run pipeline for one existing user
python3 pipeline.py --user_id <USER_ID>
```

**Expected output:**
```
步骤 2: 调用DeepSeek API分析用户画像...
✅ 分析完成
   - 内容主题: X 个
   - 内容风格: X 个

步骤 3: 保存到MongoDB...
✅ 已更新 user_profiles
✅ 已更新 user_embeddings

步骤 4: 处理单个帖子embedding...
   - 分类: Food, Lifestyle
✅ 帖子embedding完成: XX 个新增, 0 个跳过
```

### Step 2: Verify Database

```python
cd /workspaces/IG_data_Project/backend
python3 -c "
from database import UserProfileRepository, PostEmbeddingRepository

profile_repo = UserProfileRepository()
post_repo = PostEmbeddingRepository()

# Check one profile
profile = profile_repo.collection.find_one({})
print('Profile categories:', profile.get('profile_data', {}).get('categories'))

# Check post count
post_count = post_repo.collection.count_documents({})
print(f'Total post embeddings: {post_count}')

# Check one post
post = post_repo.collection.find_one({})
if post:
    print(f\"Sample post categories: {post.get('categories')}\")
    print(f\"Sample post caption: {post.get('caption', '')[:100]}...\")
"
```

### Step 3: Test API Endpoint

```bash
curl -X POST "http://localhost:5001/api/trend/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Food",
    "platform": "instagram",
    "tone": "casual",
    "length": "short",
    "format": "post"
  }'
```

**Expected:** Should find creators with "Food" in their categories and analyze their posts.

### Step 4: Recrawl All Users

```bash
# Only run this after testing with one user!
cd /workspaces/IG_data_Project/collectors/xiaohongshu
python3 pipeline.py --all
```

## New Data Flow

```
1. Collector (collector.py)
   └─> Fetches user posts from TikHub API
   └─> Stores in user_snapshots

2. Analyzer (analyzer.py)
   └─> Calls DeepSeek GPT with updated prompt
   └─> Extracts: user_style, content_topics, CATEGORIES
   └─> Returns profile_data with categories

3. Pipeline (pipeline.py)
   └─> Step 1: Read snapshot
   └─> Step 2: Analyze user → get categories
   └─> Step 3: Save user_profile with categories
   └─> Step 4: Embed EACH post with user's categories ← NEW!

4. TrendService
   └─> Filter creators by stored categories
   └─> Query post_embeddings by category
   └─> Generate trend content
```

## Categories Mapping

| Category  | Keywords (fallback)                              |
|-----------|--------------------------------------------------|
| Finance   | finance, invest, money, debt, wealth, budget     |
| Wellness  | mental, wellness, psychology, health, mindfulness|
| Food      | food, cook, recipe, kitchen, meal                |
| Fitness   | fitness, workout, sport, exercise, training      |
| Fashion   | fashion, style, outfit, clothing, trend          |
| Tech      | tech, technology, software, coding, ai, digital  |
| Lifestyle | (default/catch-all)                              |

## Troubleshooting

**Issue:** "DEEPSEEK_API_KEY环境变量未设置"  
**Solution:** Make sure `.env` file has `DEEPSEEK_API_KEY=sk-...`

**Issue:** "ModuleNotFoundError: No module named 'FlagEmbedding'"  
**Solution:** `pip install -U FlagEmbedding`

**Issue:** No categories in profile_data  
**Solution:** GPT might not be returning categories. Check analyzer prompt or API response.

**Issue:** All users still categorized as "Lifestyle"  
**Solution:** Re-run pipeline.py to regenerate profiles with new GPT prompt.

## Next Steps After Testing

1. ✅ Verify categories are stored correctly
2. ✅ Verify post embeddings are created
3. ✅ Test API with different categories
4. 🔄 Run full recrawl with `--all`
5. 📊 Check frontend shows creators in correct categories
6. 🚀 Commit changes to git
