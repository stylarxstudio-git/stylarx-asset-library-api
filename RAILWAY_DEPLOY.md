# Deploy to Railway.app - Step by Step

Railway is the easiest way to deploy your API. It handles HTTPS, domains, and scaling automatically.

## 🚂 Step-by-Step Deployment

### Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. You get $5 free credit to start

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Click **"Configure GitHub App"**
4. Select your repository (you'll need to push this code to GitHub first)

### Step 3: Configure the Service

Railway will automatically detect your Python app. It will:
- Install dependencies from `requirements.txt`
- Run the app using the Dockerfile

### Step 4: Add Environment Variables

1. In Railway dashboard, click on your service
2. Go to **"Variables"** tab
3. Click **"Raw Editor"**
4. Paste this (with your actual values):

```
OUTSETA_DOMAIN=stylarx
OUTSETA_API_KEY=your-outseta-api-key
LEMONSQUEEZY_API_KEY=your-lemonsqueezy-api-key
```

5. Click **"Save"**

### Step 5: Deploy!

Railway will automatically deploy when you:
- Push to GitHub
- Change environment variables

Your first deployment starts immediately!

### Step 6: Get Your URL

1. Click **"Settings"** tab
2. Under **"Domains"**, click **"Generate Domain"**
3. You'll get a URL like: `https://your-app.up.railway.app`
4. **Copy this URL** - you'll need it for the Blender addon!

### Step 7: Test Your API

Visit: `https://your-app.up.railway.app/docs`

You should see the interactive API documentation!

---

## 💰 Pricing

- **$5 free credit** when you sign up
- **$5/month** after that (includes 500 execution hours)
- Automatic HTTPS
- Custom domains supported

---

## 🔄 Updating Your API

Just push changes to GitHub - Railway auto-deploys!

```bash
git add .
git commit -m "Updated API"
git push
```

Railway will detect the changes and redeploy automatically.

---

## 📊 Monitoring

In Railway dashboard:
- **Logs** - View real-time logs
- **Metrics** - CPU, Memory, Network usage
- **Deployments** - See deployment history

---

## 🌐 Custom Domain (Optional)

Want to use your own domain like `api.stylarx.com`?

1. Go to **"Settings"** > **"Domains"**
2. Click **"Custom Domain"**
3. Enter: `api.stylarx.com`
4. Railway gives you CNAME record
5. Add CNAME to your DNS provider
6. Wait for DNS propagation (~5 mins)
7. Done! Railway handles SSL automatically

---

## ❓ Troubleshooting

**App won't start:**
- Check logs in Railway dashboard
- Verify environment variables are set
- Make sure requirements.txt is correct

**Can't access API:**
- Check if deployment succeeded
- Verify the domain is generated
- Test the `/` endpoint first

**502 Bad Gateway:**
- App is probably crashing
- Check logs for Python errors
- Verify all dependencies installed

---

## ✅ What's Next?

1. ✅ Your API is now live!
2. Copy your Railway URL
3. Update the Blender addon with this URL
4. Test login from Blender
5. Start using your asset library!

---

## 🎉 You're Done!

Your API URL: `https://your-app.up.railway.app`

Use this URL in the Blender addon configuration.
