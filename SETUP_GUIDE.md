# RefCheck Setup Guide

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on `http://localhost:5173`

## MistralAI Configuration

The application uses **MistralAI API with `mistral-small` model** by default.

### Setup Steps:

1. Get your API key from https://console.mistral.ai/
2. Create a `.env` file in the `backend` directory:
```bash
cd backend
cp .env.example .env
```

3. Edit `.env` and add your API key:
```bash
MISTRAL_API_KEY=your-mistral-api-key-here
```

4. The application will automatically load the API key from `.env` when it starts.

**Note:** The `.env` file is already in `.gitignore` so your API key won't be committed to version control.

## Testing

1. Open `http://localhost:5173`
2. Upload a research paper PDF
3. Wait for processing
4. View results in the table

## Troubleshooting

### Backend Issues

**Import errors:**
- Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt --force-reinstall`

**Ollama connection error:**
- Check if Ollama is running: `ollama list`
- Start Ollama service if needed

**ChromaDB errors:**
- Ensure sentence-transformers is installed
- First run may download models (takes time)

### Frontend Issues

**npm install fails:**
- Clear cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**Port already in use:**
- Change port in `vite.config.js`
- Or kill process using port 5173

## Production Deployment

### Backend
- Use production ASGI server: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Set up environment variables
- Use proper MistralAI API (not Ollama)

### Frontend
- Build: `npm run build`
- Serve `dist/` folder with nginx or similar
- Update API URL in production

