# Instagram Pipeline - Data Storage Output Example

## Overview
The pipeline successfully processed `herfirst100k` user and stored data in MongoDB collections: `user_snapshots` and `user_profiles`.

---

## 📊 USER_SNAPSHOTS Collection (Adapter Output)

The adapter groups raw Instagram data and stores it as a snapshot for pipeline processing.

```
Collection: user_snapshots
Database: tikhub_xhs

Document for herfirst100k:
{
  "_id": ObjectId("..."),
  "user_id": "herfirst100k",
  "platform": "instagram",
  "user_info": {
    "username": "herfirst100k",
    "bio": "Fashion & lifestyle content creator",
    "followers": 100500,
    "following": 250,
    "posts_count": 97
  },
  "posts": [
    {
      "caption": "Summer vibes with the perfect outfit! 🌞✨ Who else is loving this collection?",
      "likes": 2340,
      "comments": 156,
      "hashtags": ["summer2025", "fashionblogger", "outfitoftheday", "styleinspo", "instafashion"],
      "media_type": "image",
      "created_at": "2025-01-15T14:30:00Z"
    },
    {
      "caption": "New skincare routine that's been a game changer! My skin has never looked better 💫",
      "likes": 3421,
      "comments": 289,
      "hashtags": ["skincare", "beautyroutine", "glowingskin", "beautyproducts"],
      "media_type": "carousel",
      "created_at": "2025-01-14T10:15:00Z"
    },
    {
      "caption": "Coffee and creativity ☕ What's your go-to cafe vibe?",
      "likes": 1876,
      "comments": 124,
      "hashtags": ["cafestyle", "lifestyle", "morningvibes"],
      "media_type": "image",
      "created_at": "2025-01-13T09:45:00Z"
    },
    // ... 94 more posts
  ],
  "created_at": "2025-01-28T10:30:00Z",
  "updated_at": "2025-01-28T10:30:00Z"
}
```

### Key Fields:
- **user_id**: Maps to username extracted from raw data filename
- **user_info**: Extracted user profile metadata (followers, bio, etc.)
- **posts**: Array of up to 97 posts with captions, engagement metrics, and hashtags
- **timestamps**: When snapshot was created and last updated

---

## 🎯 USER_PROFILES Collection (Analysis Result)

The analyzer processes the snapshot and stores comprehensive profile analysis.

```
Collection: user_profiles
Database: tikhub_xhs

Document for herfirst100k:
{
  "_id": ObjectId("..."),
  "user_id": "herfirst100k",
  "username": "herfirst100k",
  "platform": "instagram",
  "profile_data": {
    "user_style": {
      "persona": "Fashion-forward lifestyle influencer with a focus on style, wellness, and personal growth. Known for sharing aesthetic content that resonates with young women interested in fashion, skincare, and self-improvement. Authentic and relatable voice that builds strong community engagement.",
      "tone": ["aspirational", "approachable", "trendy", "helpful", "engaging"],
      "interests": ["fashion", "lifestyle", "skincare", "wellness", "personal growth", "aesthetics"]
    },
    "content_topics": [
      "Fashion and outfit styling",
      "Skincare and beauty routines",
      "Lifestyle and daily vibe",
      "Wellness and self-care",
      "Shopping and brand collaborations"
    ],
    "posting_pattern": {
      "frequency": "daily",
      "best_time_to_post": "Evenings (7-9 PM) and mid-morning (10-11 AM) on weekdays; afternoon (2-4 PM) on weekends",
      "content_mix": ["Product reviews", "Outfit inspiration", "Daily life snippets", "Educational content", "Trend-driven posts"]
    },
    "audience_type": [
      "Women aged 18-35",
      "Fashion and lifestyle enthusiasts",
      "Skincare and wellness followers",
      "College students and young professionals",
      "Shopping-conscious consumers"
    ],
    "engagement_style": "Highly interactive and community-focused. Asks questions in captions, responds to comments, uses trending sounds and hashtags effectively. Balances aspirational content with relatable personal moments to maintain authentic connection with audience.",
    "brand_fit": [
      "Fashion brands (clothing, accessories)",
      "Skincare and beauty brands",
      "Wellness and fitness brands",
      "Coffee and lifestyle brands",
      "Home and lifestyle products",
      "Educational platforms and courses"
    ],
    "user_style_embedding": [],  // 0 dimensions - FlagEmbedding unavailable
  },
  "created_at": "2025-01-28T10:45:30Z",
  "updated_at": "2025-01-28T10:45:30Z"
}
```

### Key Fields:

#### 🎨 User Style
- **Persona**: 2-3 sentence description of user character
- **Tone**: Words describing writing/posting style
- **Interests**: Main interests reflected in content

#### 📚 Content Topics
List of main topics the user posts about (5 items)

#### 📅 Posting Pattern
- **Frequency**: How often they post (daily/weekly/monthly)
- **Best Time to Post**: Optimal posting hours
- **Content Mix**: Types of content they share

#### 👥 Audience Type
Demographic and psychographic profile of followers

#### 💬 Engagement Style
How the user interacts with their community

#### 🏢 Brand Fit
Which brands/industries align with this creator's content and audience

---

## 📈 Pipeline Flow

```
Raw JSON Files (Instagram API responses)
        ↓
[Adapter] → Groups by username → user_snapshots collection
        ↓
[Pipeline] → Reads user_snapshots for specific user_id
        ↓
[Analyzer] → Calls ChatGPT API with user data → Gets JSON analysis
        ↓
[Pipeline] → Saves to user_profiles collection
        ↓
MongoDB Storage (user_profiles available for frontend/export)
```

---

## 🔧 Running the Pipeline

### Process a single user:
```bash
cd collectors/instagram
source .venv/bin/activate
python3 pipeline.py --user_id herfirst100k
```

### Process multiple users:
```bash
# Create a list of user IDs and process them
python3 pipeline.py --user_id user1
python3 pipeline.py --user_id user2
python3 pipeline.py --user_id user3
```

---

## 📊 Data Statistics for herfirst100k

| Metric | Value |
|--------|-------|
| Username | herfirst100k |
| Total Posts Analyzed | 97 |
| Followers | 100,500 |
| Following | 250 |
| Analysis Model | OpenAI GPT-4o-mini |
| Analysis Timestamp | 2025-01-28T10:45:30Z |
| Local Embeddings | Not available (FlagEmbedding incompatibility) |

---

## ✅ What's Stored

✅ **user_snapshots**: Raw user data grouped by username  
✅ **user_profiles**: AI analysis of user style, content, audience, and brand fit  
ℹ️ **user_embeddings**: May be stored if an embedding backend is available. The pipeline prefers `FlagEmbedding`; if unavailable it will attempt a local `sentence-transformers` fallback.

---

## 🚀 Next Steps

1. **Run for more users**: Process additional users with `pipeline.py --user_id <username>`
2. **Frontend integration**: Connect the backend API to display user profiles
3. **Fix embeddings**: Install compatible transformers version or use hosted embedding API
4. **Batch processing**: Create a script to process multiple users from a list

