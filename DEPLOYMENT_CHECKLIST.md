# 🚀 Covert Agenda - Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Code Preparation
- [x] `requirements.txt` exists with all dependencies
- [x] `Procfile` exists with `web: gunicorn app:app`
- [x] `runtime.txt` specifies Python version
- [x] Database configuration handles PostgreSQL URLs
- [x] Environment variables are properly configured

### 2. GitHub Repository
- [x] All code is committed and pushed to GitHub
- [x] Repository is public (for free Render tier)
- [x] No sensitive data in code (passwords, API keys, etc.)

## 🎯 Render Deployment Steps

### Step 1: Sign Up for Render
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Verify your email address

### Step 2: Create New Web Service
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your Covert Agenda app

### Step 3: Configure the Service
- **Name**: `covert-agenda` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: `Free`

### Step 4: Set Environment Variables
Add these environment variables in Render dashboard:

```
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ADMIN_PASSWORD=your-admin-password-here
FLASK_ENV=production
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (usually 2-5 minutes)
3. Your app will be available at `https://your-app-name.onrender.com`

## 🔧 Post-Deployment Setup

### 1. Test Your App
- [ ] Visit your app URL
- [ ] Test admin login
- [ ] Create a game
- [ ] Join a game
- [ ] Test challenge completion

### 2. Custom Domain (Optional)
- [ ] Add custom domain in Render dashboard
- [ ] Configure DNS settings with your domain provider

### 3. Database Setup
- [ ] First visit will automatically create database tables
- [ ] Sample challenges will be added automatically

## 🚨 Important Notes

### Free Tier Limitations
- **Sleep after 15 minutes** of inactivity
- **750 hours/month** (about 31 days)
- **Cold starts** - first request after sleep may be slow

### Security
- Change the default admin password after deployment
- Use a strong SECRET_KEY
- Never commit sensitive data to GitHub

### Monitoring
- Check Render logs for any errors
- Monitor app performance in Render dashboard

## 🔄 Updates and Maintenance

### To Update Your App
1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically redeploy

### To Check Logs
1. Go to your service in Render dashboard
2. Click "Logs" tab
3. Monitor for any errors or issues

## 🆘 Troubleshooting

### Common Issues
- **Build fails**: Check requirements.txt and Python version
- **App crashes**: Check logs for error messages
- **Database errors**: Ensure PostgreSQL URL is correct
- **Slow loading**: Normal for free tier after sleep

### Getting Help
- Check Render documentation
- Review Flask deployment guides
- Check app logs for specific error messages

---

**Your app is ready for deployment! 🎉** 