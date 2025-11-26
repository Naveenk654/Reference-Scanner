# 🚀 Deployment Guide - RefCheck

This guide will help you deploy your RefCheck application for **FREE** using the best free hosting services.

## 📋 Table of Contents
1. [Deployment Strategy](#deployment-strategy)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Alternative Options](#alternative-options)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment Strategy

**Recommended Free Stack:**
- **Backend**: [Render](https://render.com) - Free tier (750 hours/month)
- **Frontend**: [Vercel](https://vercel.com) - Free tier (unlimited)

**Why this combination?**
- ✅ Both are completely free
- ✅ Easy setup with GitHub integration
- ✅ Automatic deployments on git push
- ✅ Excellent performance
- ✅ Built-in SSL certificates

---

## 📦 Prerequisites

Before deploying, ensure you have:

1. ✅ **GitHub Account** - [Sign up here](https://github.com)
2. ✅ **Git Repository** - Your code pushed to GitHub
3. ✅ **MistralAI API Key** - [Get one here](https://console.mistral.ai/)
4. ✅ **Tavily API Key** (Optional) - [Get one here](https://tavily.com) for web search features

---

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Your Backend

First, we need to make a few changes to your backend for production:

#### 1.1 Create a `Procfile` for Render

Create `backend/Procfile` (no extension):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 1.2 Update CORS Settings

Update `backend/main.py` to allow your frontend domain.

#### 1.3 Create `runtime.txt` (Optional)

Create `backend/runtime.txt` to specify Python version:
```
python-3.11.0
```

### Step 2: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for deployment"
git branch -M main

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 3: Deploy on Render

1. **Sign up/Login**: Go to [render.com](https://render.com) and sign up with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Service**:
   - **Name**: `refcheck-backend` (or any name you like)
   - **Region**: Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable":
   - `MISTRAL_API_KEY` = `your-mistral-api-key-here`
   - `TAVILY_API_KEY` = `your-tavily-api-key-here` (optional)
   - `PORT` = `10000` (Render sets this automatically, but good to have)

5. **Create Service**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your backend URL will be: `https://refcheck-backend.onrender.com` (or your custom name)

6. **Note**: Render free tier spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds.

### Step 4: Update CORS in Backend

After deployment, update `backend/main.py` to include your Render URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://your-frontend.vercel.app",  # Add your Vercel URL here
        "*"  # For development, remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push** this change to trigger a new deployment.

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Prepare Your Frontend

#### 1.1 Create Environment Variable File

Create `frontend/.env.production`:
```env
VITE_API_URL=https://your-backend.onrender.com
```

#### 1.2 Update API Calls

Update `frontend/src/App.jsx` to use environment variable:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';
```

Then replace all `http://localhost:8002` with `API_URL`.

#### 1.3 Update Vite Config

Update `frontend/vite.config.js` to remove proxy in production:

```javascript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: process.env.NODE_ENV === 'development' ? {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    } : undefined,
  },
})
```

### Step 2: Deploy on Vercel

1. **Sign up/Login**: Go to [vercel.com](https://vercel.com) and sign up with GitHub

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select your repository

3. **Configure Project**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Add Environment Variables**:
   - Click "Environment Variables"
   - Add: `VITE_API_URL` = `https://your-backend.onrender.com`
   - Select: Production, Preview, Development

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be live at: `https://your-project.vercel.app`

6. **Custom Domain** (Optional):
   - Go to Project Settings → Domains
   - Add your custom domain (free)

---

## 🔄 Alternative Options

### Option 1: Railway (Backend)

**Pros**: 
- $5 free credit monthly
- No spin-down (always on)
- Easy setup

**Steps**:
1. Sign up at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select repository
4. Add environment variables
5. Deploy!

### Option 2: Fly.io (Backend)

**Pros**:
- Free tier with 3 shared VMs
- Global edge network
- No spin-down

**Steps**:
1. Install Fly CLI: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"`
2. Sign up: `fly auth signup`
3. In `backend/` directory: `fly launch`
4. Follow prompts
5. Add secrets: `fly secrets set MISTRAL_API_KEY=your-key`

### Option 3: Netlify (Frontend)

**Pros**:
- Free tier
- Great for static sites
- Easy setup

**Steps**:
1. Sign up at [netlify.com](https://netlify.com)
2. Add new site → Import from Git
3. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
4. Add environment variable: `VITE_API_URL`

---

## 🛠️ Step-by-Step: Complete Deployment

### Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed on Render
- [ ] Backend URL obtained (e.g., `https://refcheck-backend.onrender.com`)
- [ ] CORS updated in backend to allow frontend domain
- [ ] Frontend updated to use environment variable for API URL
- [ ] Frontend deployed on Vercel
- [ ] Environment variable `VITE_API_URL` set in Vercel
- [ ] Test the deployed application

### Detailed Steps

#### 1. Prepare Repository

```bash
# Make sure everything is committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Deploy Backend First

Follow [Backend Deployment (Render)](#backend-deployment-render) steps above.

**Wait for backend to be live** and note the URL (e.g., `https://refcheck-backend.onrender.com`)

#### 3. Update Frontend Code

Update `frontend/src/App.jsx`:

```javascript
// At the top of the file
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// Then in handleUpload function, replace:
const response = await fetch('http://localhost:8002/upload_pdf', {
// With:
const response = await fetch(`${API_URL}/upload_pdf`, {
```

Do the same for all API calls in your frontend code.

#### 4. Update Backend CORS

Update `backend/main.py` CORS origins to include your Vercel URL.

#### 5. Deploy Frontend

Follow [Frontend Deployment (Vercel)](#frontend-deployment-vercel) steps above.

#### 6. Test

Visit your Vercel URL and test:
- Upload a PDF
- Check if references are processed
- Verify API calls work

---

## 🐛 Troubleshooting

### Backend Issues

**"Application failed to respond"**
- Check Render logs: Go to your service → Logs
- Verify environment variables are set correctly
- Check if `requirements.txt` is correct

**"Module not found"**
- Ensure all dependencies are in `requirements.txt`
- Check build logs for installation errors

**"CORS error"**
- Verify frontend URL is in CORS `allow_origins` list
- Check if backend is running (Render might be spinning up)

**"Slow first request"**
- Normal on Render free tier (spins down after 15 min)
- First request after spin-down takes ~30 seconds
- Consider Railway or Fly.io for always-on service

### Frontend Issues

**"API calls failing"**
- Check `VITE_API_URL` environment variable in Vercel
- Verify backend URL is correct
- Check browser console for errors

**"Build fails"**
- Check Vercel build logs
- Ensure `package.json` has correct build script
- Verify all dependencies are listed

**"Environment variable not working"**
- Vite requires `VITE_` prefix for env variables
- Rebuild after adding environment variables
- Check Vercel environment variable settings

### General Issues

**"Can't connect to backend"**
- Verify backend is running (check Render dashboard)
- Test backend health endpoint: `https://your-backend.onrender.com/health`
- Check CORS settings

**"PDF upload fails"**
- Check file size limits (Render has limits)
- Verify backend logs for errors
- Check if MistralAI API key is valid

---

## 📝 Post-Deployment Checklist

- [ ] Backend health check works: `https://your-backend.onrender.com/health`
- [ ] Frontend loads correctly
- [ ] PDF upload works
- [ ] References are processed
- [ ] CORS errors resolved
- [ ] Environment variables set correctly
- [ ] Custom domain configured (if desired)
- [ ] SSL certificates active (automatic on both platforms)

---

## 💡 Tips for Production

1. **Monitor Usage**: 
   - Render free tier: 750 hours/month
   - Vercel free tier: Unlimited (with limits on bandwidth)

2. **Optimize Performance**:
   - Enable caching in Vercel
   - Use CDN for static assets
   - Optimize images

3. **Security**:
   - Never commit `.env` files
   - Use environment variables in hosting platforms
   - Enable HTTPS (automatic on both platforms)

4. **Scaling**:
   - Render: Upgrade to paid plan for always-on
   - Vercel: Free tier is usually sufficient for small apps

---

## 🎉 You're Done!

Your RefCheck application should now be live and accessible to the world!

**Backend**: `https://your-backend.onrender.com`  
**Frontend**: `https://your-project.vercel.app`

Any changes you push to GitHub will automatically trigger new deployments!

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Guide](https://vitejs.dev/guide/build.html)

---

**Need Help?** Check the logs in Render/Vercel dashboards for detailed error messages.

