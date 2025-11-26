# 🚀 Quick Deployment Checklist

Follow this checklist to deploy your RefCheck application.

## Pre-Deployment

- [ ] Code is pushed to GitHub
- [ ] All environment variables are documented in `backend/.env.example`
- [ ] Tested locally - both frontend and backend work

## Backend Deployment (Render)

- [ ] Created account on [render.com](https://render.com)
- [ ] Created new Web Service from GitHub repository
- [ ] Set Root Directory to: `backend`
- [ ] Set Build Command to: `pip install -r requirements.txt`
- [ ] Set Start Command to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Added environment variable: `MISTRAL_API_KEY`
- [ ] Added environment variable: `TAVILY_API_KEY` (optional)
- [ ] Added environment variable: `PORT` = `10000` (optional)
- [ ] Backend deployed successfully
- [ ] Tested backend health endpoint: `https://your-backend.onrender.com/health`
- [ ] **Note backend URL**: `https://your-backend.onrender.com`

## Frontend Deployment (Vercel)

- [ ] Created account on [vercel.com](https://vercel.com)
- [ ] Imported project from GitHub
- [ ] Set Root Directory to: `frontend`
- [ ] Framework Preset: `Vite` (auto-detected)
- [ ] Added environment variable: `VITE_API_URL` = `https://your-backend.onrender.com`
- [ ] Frontend deployed successfully
- [ ] **Note frontend URL**: `https://your-project.vercel.app`

## Post-Deployment

- [ ] Updated backend CORS with frontend URL
- [ ] Pushed CORS changes to GitHub (triggers auto-deployment)
- [ ] Tested frontend can connect to backend
- [ ] Tested PDF upload functionality
- [ ] Tested chatbot functionality
- [ ] Verified all API endpoints work

## Environment Variables Summary

### Backend (Render)
```
MISTRAL_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here (optional)
PORT=10000 (optional)
ALLOWED_ORIGINS=https://your-frontend.vercel.app (optional)
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend.onrender.com
```

## Troubleshooting

**Backend not responding?**
- Check Render logs
- Verify environment variables are set
- Check if service spun down (first request takes ~30s)

**CORS errors?**
- Verify frontend URL is in backend CORS settings
- Check `ALLOWED_ORIGINS` environment variable

**Frontend can't connect?**
- Verify `VITE_API_URL` is set correctly in Vercel
- Check backend is running and accessible
- Test backend health endpoint directly

## Quick Links

- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Render Dashboard](https://dashboard.render.com)
- [Vercel Dashboard](https://vercel.com/dashboard)

---

**You're all set!** 🎉

