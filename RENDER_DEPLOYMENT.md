# Deployment Guide for Render

This guide will help you deploy your XHS Data Analysis application to Render for free.

## Prerequisites

- GitHub account
- Render account (free) - Sign up at https://render.com
- Your code pushed to GitHub
- MongoDB Atlas database (free tier)
- OpenAI API key

## Architecture

Your application consists of two services:
1. **Backend**: FastAPI service (Python) - Handles API requests and database
2. **Frontend**: Next.js application (Node.js) - User interface

## Deployment Steps

### Step 1: Sign Up for Render

1. Go to https://dashboard.render.com/register
2. Click "Sign up with GitHub" (recommended)
3. Authorize Render to access your repositories

### Step 2: Deploy Using Blueprint (Recommended)

1. In your Render dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub account (if not already connected)
3. Select your repository: `xhs_data_Project`
4. Render will detect the `render.yaml` file automatically
5. Click **"Apply"** to start deployment

### Step 3: Add Environment Variables

After the services are created, you need to add your secret environment variables:

#### For Backend Service (`xhs-data-backend`):

1. Go to your backend service in Render dashboard
2. Click **"Environment"** in the left sidebar
3. Add these environment variables:
   - **MONGO_URI**: Your MongoDB connection string
     - Example: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
   - **OPENAI_API_KEY**: Your OpenAI API key
     - Example: `sk-proj-...`
   - **DATABASE_NAME**: `tikhub_xhs` (or your database name)

4. Click **"Save Changes"**
5. Render will automatically redeploy with these variables

### Step 4: Verify Deployment

Once both services are deployed:

1. **Backend URL**: `https://xhs-data-backend.onrender.com`
   - Test: Visit `https://xhs-data-backend.onrender.com/api/health`
   - You should see a health check response

2. **Frontend URL**: `https://xhs-data-frontend.onrender.com`
   - This is your public application URL
   - Share this with users!

### Step 5: Update Frontend Environment Variable (if needed)

If your backend URL is different from `xhs-data-backend.onrender.com`:

1. Go to your frontend service
2. Click **"Environment"**
3. Update **NEXT_PUBLIC_API_BASE_URL** to match your backend URL
4. Save and redeploy

## Alternative: Manual Deployment

If you prefer not to use Blueprint:

### Deploy Backend Manually:

1. Click **"New +"** → **"Web Service"**
2. Connect to your GitHub repo
3. Configure:
   - **Name**: `xhs-data-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. Add environment variables (see Step 3 above)
5. Click **"Create Web Service"**

### Deploy Frontend Manually:

1. Click **"New +"** → **"Web Service"**
2. Connect to your GitHub repo
3. Configure:
   - **Name**: `xhs-data-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: `Node`
   - **Build Command**: `corepack enable && pnpm install && pnpm build`
   - **Start Command**: `pnpm start`
   - **Plan**: Free
4. Add environment variable:
   - **NEXT_PUBLIC_API_BASE_URL**: `https://xhs-data-backend.onrender.com`
5. Click **"Create Web Service"**

## Important Notes

### Free Tier Limitations:
- **Automatic spin down**: Services sleep after 15 minutes of inactivity
- **Cold start**: First request after sleep takes 30-90 seconds
- **750 hours/month**: Enough for 24/7 operation
- **Shared CPU**: Slower performance than paid tiers

### Troubleshooting:

**Backend fails to start:**
- Check that MONGO_URI is correct
- Verify MongoDB Atlas allows connections from anywhere (0.0.0.0/0)
- Check backend logs in Render dashboard

**Frontend can't connect to backend:**
- Verify NEXT_PUBLIC_API_BASE_URL is set correctly
- Check backend is running and accessible
- Make sure backend has CORS enabled (already configured)

**Cold start is too slow:**
- This is expected on free tier
- Upgrade to paid tier ($7/month) to keep services always-on

## MongoDB Atlas Setup

If you don't have MongoDB Atlas set up:

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free cluster (M0 tier)
3. Create a database user
4. Get your connection string
5. In Network Access, add `0.0.0.0/0` to allow connections from anywhere
6. Use this connection string as your MONGO_URI

## OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Use this as your OPENAI_API_KEY

## Auto-Deploy on Push

Once set up, any push to your `main` branch will automatically trigger a new deployment on Render!

## Support

If you encounter issues:
- Check Render logs (click on your service → "Logs")
- Verify all environment variables are set
- Check that your GitHub repository is up to date
