# ClarityVault - Render Deployment Guide

## 🚀 Step-by-Step Deployment

### Step 1: Push to GitHub
First, create a GitHub repo and push your code:

```bash
# In your ClarityVault folder
git init
git add .
git commit -m "Initial commit - ClarityVault"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ClarityVault.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub** account
4. Select your **ClarityVault** repository
5. Configure settings:
   - **Name**: `clarityvault` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Step 3: Add Environment Variables

In Render dashboard → **Environment** tab, add these:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | Your first Groq API key |
| `YOUTUBE_API_KEY` | `AIzaSyAMUvuLdZgG50tdYvRz3b6pd5swrgNxvLY` |
| `SUPABASE_URL` | `https://psinfdmhwydraawziiij.supabase.co` |
| `SUPABASE_KEY` | `sb_publishable_cm8SxtfPmvlDR2x-qu5s6g_yYWECrtw` |
| `JWT_SECRET` | `TmV3U2VjcmV0S2V5Rm9ySldUU2lnbmluZ1B1cnBvc2VzMTIzNDU2Nzg=` |

### Step 4: Deploy!

Click **"Create Web Service"** and wait 2-3 minutes.

Your app will be live at: `https://clarityvault.onrender.com`

---

## ⚠️ Important Notes

1. **Free tier**: App sleeps after 15 min of inactivity (first request takes ~30s to wake)
2. **API Keys**: Your 20 Groq keys are already in `config.py` - they'll work on Render too!
3. **Uploads**: PDF uploads work but files are temporary (OK for demo)

## 🎉 That's it!

Your ClarityVault app will be live and accessible from anywhere!
