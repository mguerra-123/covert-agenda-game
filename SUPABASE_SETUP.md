# 🗄️ Supabase Database Setup Guide

## 🎯 **What You're Setting Up**
A cloud database that will store all your Covert Agenda game data (users, games, challenges, etc.) so your app can work on Vercel.

## ✅ **Step 1: Create Database Tables**

### **Option A: Using Supabase SQL Editor (Recommended)**

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Click on your project

2. **Open SQL Editor**
   - In the left sidebar, click **"SQL Editor"**
   - Click **"New Query"**

3. **Run the Database Schema**
   - Copy the contents of `supabase_schema.sql` file
   - Paste it into the SQL editor
   - Click **"Run"** button

4. **Verify Tables Created**
   - Go to **"Table Editor"** in the left sidebar
   - You should see these tables:
     - `users`
     - `games` 
     - `players`
     - `challenges`
     - `completed_challenges`
     - `vetoes`

## ✅ **Step 2: Test Database Connection**

Run this command to test your database:
```bash
python3 test_supabase_api.py
```

You should see:
```
✅ Supabase client created successfully
✅ Database query successful!
```

## ✅ **Step 3: Update Your App for Production**

Once the database is set up, I'll help you:
1. Update your Flask app to use Supabase API
2. Configure environment variables for Vercel
3. Deploy to Vercel

## 🔑 **Your Supabase Configuration**

- **Project URL**: `your-supabase-project-url-here`
- **Anon Key**: `your-anon-key-here`
- **Service Key**: `your-service-key-here`

## 🚨 **Important Security Notes**

- **Never commit API keys to GitHub**
- **Use environment variables in production**
- **The anon key is safe to use in frontend code**
- **The service key should only be used in backend/server code**

## 🎉 **Next Steps**

After you've created the tables:
1. Run the test script to verify everything works
2. Let me know when you're ready to update the Flask app
3. We'll configure it for Vercel deployment

## 📋 **Step-by-Step Instructions**

### **Step 1: Create Supabase Account**
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with your GitHub account
4. Verify your email address

### **Step 2: Create New Project**
1. Click "New Project"
2. **Organization**: Select your personal account
3. **Project Details**:
   - **Name**: `covert-agenda-game`
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you
4. Click "Create new project"
5. Wait 1-2 minutes for setup

### **Step 3: Get Your Database URL**
1. In your project dashboard, click the gear icon (⚙️) on the left sidebar
2. Click "Database" in the settings menu
3. Scroll down to "Connection string" section
4. Copy the "URI" - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
   ```
5. **Important**: Replace `[YOUR-PASSWORD]` with the password you created in Step 2

### **Step 4: Test Your Connection**
1. Open the `test_database.py` file in your project
2. Replace the `SUPABASE_URL` with your actual URL
3. Run the test:
   ```bash
   python3 test_database.py
   ```
4. You should see: "🎉 Database connection test successful!"

### **Step 5: Deploy to Vercel**
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set environment variables:
   ```
   DATABASE_URL=your-supabase-url-here
   SECRET_KEY=your-super-secret-key
   ADMIN_PASSWORD=your-admin-password
   FLASK_ENV=production
   ```
4. Deploy!

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **"Connection failed" error**
- ✅ Check your password is correct
- ✅ Make sure you replaced `[YOUR-PASSWORD]` in the URL
- ✅ Verify your Supabase project is fully set up

#### **"Project not found" error**
- ✅ Wait a few more minutes for project setup
- ✅ Check you're using the correct project ID

#### **"Permission denied" error**
- ✅ Make sure you're using the correct database password
- ✅ Check that your project is active

## 📊 **What This Gives You**

### **Free Tier Limits:**
- **Database**: 500MB storage
- **Bandwidth**: 2GB/month
- **API calls**: 50,000/month
- **Users**: Unlimited

### **For Covert Agenda:**
- ✅ Store unlimited games
- ✅ Store unlimited players
- ✅ Store all challenge data
- ✅ Real-time updates
- ✅ Automatic backups

## 🎉 **You're Ready!**

Once you complete these steps, your Covert Agenda game will have:
- 🌐 **Online database** accessible from anywhere
- 🔄 **Real-time data** for multiplayer games
- 💾 **Automatic backups** of all game data
- ⚡ **Fast performance** for your players

---

**Next**: After setting up Supabase, you can deploy to Vercel and start playing online! 