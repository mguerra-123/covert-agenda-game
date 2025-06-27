# 🚀 Covert Agenda - Vercel Deployment Guide

## ✅ Pre-Deployment Checklist

### 1. Code Preparation
- [x] `vercel.json` exists with proper configuration
- [x] `requirements.txt` updated for Vercel
- [x] `app.py` configured for serverless environment
- [x] Database configuration handles Vercel environment

### 2. GitHub Repository
- [x] All code is committed and pushed to GitHub
- [x] Repository is public (for free Vercel tier)
- [x] No sensitive data in code

## 🎯 Vercel Deployment Steps

### Step 1: Sign Up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account
3. Verify your email address

### Step 2: Import Your Project
1. Click "New Project"
2. Select "Import Git Repository"
3. Choose your `covert-agenda-game` repository
4. Select the `simple-version` branch

### Step 3: Configure the Project
- **Framework Preset**: `Other`
- **Root Directory**: `./` (leave as default)
- **Build Command**: Leave empty (Vercel auto-detects)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### Step 4: Set Environment Variables
Add these environment variables in Vercel dashboard:

```
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ADMIN_PASSWORD=your-admin-password-here
FLASK_ENV=production
```

### Step 5: Deploy
1. Click "Deploy"
2. Wait for build to complete (usually 1-3 minutes)
3. Your app will be available at `https://your-app-name.vercel.app`

## 🔧 Post-Deployment Setup

### 1. Test Your App
- [ ] Visit your app URL
- [ ] Test admin login
- [ ] Create a game
- [ ] Join a game
- [ ] Test challenge completion

### 2. Custom Domain (Optional)
- [ ] Add custom domain in Vercel dashboard
- [ ] Configure DNS settings with your domain provider

### 3. Database Setup
- [ ] First visit will automatically create database tables
- [ ] Sample challenges will be added automatically

## 🚨 Important Notes

### Vercel Limitations
- **Serverless functions** - Each request is a new function instance
- **Cold starts** - First request may be slower
- **Function timeout** - 10 seconds for free tier
- **No persistent file system** - Database must be external

### Database Considerations
- **SQLite won't work** on Vercel (no persistent storage)
- **Use external database** like:
  - [Supabase](https://supabase.com) (free PostgreSQL)
  - [PlanetScale](https://planetscale.com) (free MySQL)
  - [Railway](https://railway.app) (free PostgreSQL)

### Security
- Change the default admin password after deployment
- Use a strong SECRET_KEY
- Never commit sensitive data to GitHub

## 🔄 Updates and Maintenance

### To Update Your App
1. Make changes to your code
2. Commit and push to GitHub
3. Vercel will automatically redeploy

### To Check Logs
1. Go to your project in Vercel dashboard
2. Click "Functions" tab
3. Monitor for any errors or issues

## 🆘 Troubleshooting

### Common Issues
- **Build fails**: Check requirements.txt and Python version
- **App crashes**: Check function logs for error messages
- **Database errors**: Ensure external database is configured
- **Cold starts**: Normal for serverless functions

### Getting Help
- Check Vercel documentation
- Review Flask serverless guides
- Check function logs for specific error messages

## 📊 Vercel vs Render Comparison

| Feature | Vercel | Render |
|---------|--------|--------|
| **Free Tier** | ✅ Generous | ✅ 750 hours/month |
| **Cold Starts** | ⚠️ Yes | ❌ No (sleeps after 15min) |
| **Database** | ❌ External needed | ✅ Built-in PostgreSQL |
| **Deployment Speed** | ⚡ Very Fast | 🐌 Slower |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🎯 Recommended Setup for Vercel

### 1. Database Setup (Required)
Since Vercel doesn't provide persistent storage, you'll need an external database:

#### Option A: Supabase (Recommended)
1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Get your database URL
4. Add to Vercel environment variables:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

#### Option B: Railway
1. Sign up at [railway.app](https://railway.app)
2. Create a new PostgreSQL database
3. Get your database URL
4. Add to Vercel environment variables

### 2. Update Database Configuration
Your app already handles PostgreSQL URLs correctly, so it should work with external databases.

---

**Your app is ready for Vercel deployment! 🎉**

**Note**: You'll need to set up an external database before deploying, as Vercel doesn't provide persistent storage for SQLite databases. 