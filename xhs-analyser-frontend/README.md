# Instagram Creator Intelligence Frontend

Next.js-powered web application for visualizing Instagram creator insights, generating AI content, and analyzing trends.

## 🎯 Overview

Modern, responsive frontend for the Instagram Creator Intelligence platform featuring:

- **Creator Explorer** - Browse and filter 29 Instagram creators by category (8 categories including Celebrity)
- **Style Generator** - Generate content with style consistency scoring and evidence breakdown
- **Trend Generator** - Create trending posts with category-specific templates, formula transparency, and collapsible strategy sections
- **Dual-Language Support** - English and Chinese UI (next-intl)
- **Landing Page Navigation** - Clear two-path navigation without top navigation bar

**Tech Stack:**
- **Framework:** Next.js 16 (App Router with Turbopack)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **i18n:** next-intl (zh/en)
- **Package Manager:** pnpm

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/pnpm
- Backend API running at http://localhost:5000

### Local Development

```bash
# 1. Navigate to frontend folder
cd xhs-analyser-frontend

# 2. Install dependencies
pnpm install
# or: npm install

# 3. Set up environment (.env.local)
cp .env.example .env.local
# Edit if needed (default backend: http://localhost:5000)

# 4. Run development server
pnpm dev
# or: npm run dev
```

**Open:** http://localhost:3000

---

## 📁 Project Structure

```
xhs-analyser-frontend/
├── app/
│   ├── [locale]/                # i18n routes
│   │   ├── page.tsx             # Home page
│   │   ├── creators/[id]/       # Creator detail pages
│   │   ├── style-generator/     # Style generator
│   │   └── trend-generator/     # Trend generator
│   └── api/
│       └── proxy/               # Backend API proxies
│           ├── creators/
│           ├── style/generate/
│           └── trend/generate/
├── src/
│   ├── components/              # React components
│   │   ├── Header.tsx
│   │   ├── LandingPage.tsx
│   │   ├── StyleChatbot.tsx
│   │   ├── AccountCategories.tsx
│   │   └── ...
│   ├── lib/
│   │   └── api.ts              # API client
│   └── data/
│       ├── creators.ts          # Creator data types
│       └── trending.ts          # Trending topics
├── messages/
│   ├── en.json                  # English translations
│   └── zh.json                  # Chinese translations
└── public/                      # Static assets
```

---

## 🎨 Features

### 1. Creator Explorer

Browse creators by category:
- Finance (5 creators)
- Food (4 creators)
- Fitness (3 creators)
- Fashion (2 creators)
- Tech (5 creators)  
- Wellness (3 creators)
- Lifestyle (3 creators)

**View Details:** Click any creator to see:
- Profile summary
- Content topics
- Style analysis
- Recent posts
- Engagement metrics

### 2. Style Generator

Generate content that mimics any creator's style:

1. Select a creator (e.g., herfirst100k)
2. Enter your topic (e.g., "passive income streams")
3. Choose tone (Casual/Engaging/Professional)
4. Select length (Short/Medium/Long)
5. Pick format (Post/Bullet Points/Script)
6. Click "Generate Your Content ✨"

**Output:** AI-generated content that matches the creator's:
- Writing style
- Tone and voice
- Topic focus
- Typical structure

### 3. Trend Generator

Create posts based on trending patterns:

1. Select category (Finance, Food, etc.)
2. Enter target follower count (for engagement projections)
3. Add optional topic
4. Choose tone, length, format
5. Generate content

**Output:**
- **Trend Insights:** Engagement rate, projected likes/comments
- **Evidence:** Common keywords, successful hooks, hashtags
- **hook explanations:** Why each hook works
- **Generated Content:** Post optimized for maximum engagement

---

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```bash
# Backend API URL (default: http://localhost:5000)
NEXT_PUBLIC_API_URL=http://localhost:5000

# Optional: Custom port
PORT=3000
```

### Proxy Routes

All API calls go through Next.js API routes for CORS handling:

- `/api/proxy/creators` → Backend `/api/creators/list`
- `/api/proxy/style/generate` → Backend `/api/style/generate`
- `/api/proxy/trend/generate` → Backend `/api/trend/generate`

**Why?** Avoids CORS issues during development.

---

## 🌐 Internationalization

### Supported Languages

- **English** (`/en/...`)
- **Chinese** (`/zh/...`)

### Add New Language

1. Create `messages/{language}.json`:
```json
{
  "home": {
    "title": "Instagram Creator Intelligence",
    "subtitle": "AI-powered content generation"
  }
}
```

2. Update `middleware.ts`:
```typescript
export const locales = ['en', 'zh', 'fr'];
export const defaultLocale = 'en';
```

3. Restart dev server

### Usage in Components

```typescript
import { useTranslations } from 'next-intl';

export default function Component() {
  const t = useTranslations('home');
  return <h1>{t('title')}</h1>;
}
```

---

## 🏗️ Development

### Adding New Components

```tsx
// src/components/MyComponent.tsx
export default function MyComponent() {
  return (
    <div className="...">
      {/* Use Tailwind classes */}
    </div>
  );
}
```

### API Integration

```tsx
// Using the API client
import { fetchCreators, generateStyle } from '@/lib/api';

const creators = await fetchCreators('instagram');
const content = await generateStyle({
  creator_name: 'herfirst100k',
  user_topic: 'investing basics'
});
```

### Styling

Uses Tailwind CSS:
```tsx
<div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow-sm">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
</div>
```

---

## 📦 Building for Production

### Build

```bash
# Create production build
pnpm build

# Preview production build
pnpm start
```

### Deploy

#### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Or connect GitHub repository to Vercel dashboard.

**Environment Variables:**
- Set `NEXT_PUBLIC_API_URL` to production backend URL

#### Docker

```bash
# Build image
docker build -t instagram-frontend:latest .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://your-backend.com \
  instagram-frontend:latest
```

#### Static Export

```bash
# Update next.config.ts
export default {
  output: 'export'
}

# Build static files
pnpm build

# Deploy /out folder to any static host
```

---

## 🎯 Component Guide

### Header

Navigation bar with language switcher.

**Props:** None  
**Usage:** Auto-included in layout

### LandingPage

Home page with feature showcase.

**Sections:**
- Hero
- How It Works
- Features grid
- CTA

### StyleChatbot

AI content generation in creator's style.

**Props:**
- `selectedCreator?`: Pre-selected creator (optional)

**Events:**
- Generates content via `/api/proxy/style/generate`

### AccountCategories

Category-based creator browse.

**Props:**
- `creators`: Array of creator objects

**Features:**
- Tab navigation by category
- Creator cards with stats
- Detail modal

---

## 🐛 Troubleshooting

**Issue:** `CORS error when calling backend`  
**Fix:** Backend must allow origin `http://localhost:3000` or use proxy routes

**Issue:** `404 on creator pages`  
**Fix:** Ensure creator exists in backend (`/api/creators/{username}`)

**Issue:** `Translations not loading`  
**Fix:** Check `messages/{locale}.json` exists and middleware is configured

**Issue:** `Slow API responses`  
**Fix:** Backend may be generating AI content (can take 10-30s for GPT)

**Issue:** `Build fails with i18n error`  
**Fix:** Update `next-intl` to latest version: `pnpm update next-intl`

---

## 📚 Related Documentation

- **Backend API:** See `../backend/README.md` for API endpoints
- **Collectors:** See `../collectors/instagram/README.md` for data pipeline

---

## 🎨 Design System

### Colors

```
Primary: Indigo (#6366F1)
Success: Green (#10B981)
Warning: Orange (#F59E0B)
Error: Red (#EF4444)
```

### Typography

- Headings: Inter (font-sans)
- Body: Inter
- Code: JetBrains Mono (font-mono)

### Spacing

Uses Tailwind spacing scale (0.25rem increments):
- `p-4` = 1rem padding
- `gap-6` = 1.5rem gap
- `mt-8` = 2rem margin-top

---

## 🔗 Key Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| next | React framework | 14.x |
| react | UI library | 18.x |
| typescript | Type safety | 5.x |
| tailwindcss | Styling | 3.x |
| next-intl | i18n | Latest |
| @radix-ui/* | UI primitives | Latest |

---

## 💡 Tips

1. **Performance:** Use Next.js Image component for optimized images
2. **SEO:** Add metadata to page.tsx files for better SEO
3. **Types:** Define TypeScript interfaces in `src/types/`
4. **Testing:** Add tests with Jest + React Testing Library
5. **Accessibility:** Use semantic HTML and ARIA labels

---

## 🚀 Next Steps

After starting the frontend:

1. **Explore Creators:** Browse by category at http://localhost:3000
2. **Generate Content:** Try Style Generator with different creators
3. **Analyze Trends:** Use Trend Generator for each category
4. **Check Languages:** Switch between English/Chinese

**Need Data?** Run the collectors first: `../collectors/instagram/README.md`
