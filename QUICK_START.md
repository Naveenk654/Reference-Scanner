# RefCheck Quick Start

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
- ✅ Python 3.8+ installed
- ✅ Node.js 18+ installed
- ✅ MistralAI API key (get one at https://console.mistral.ai/)

### Step 1: Backend (Terminal 1)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file with your API key
# Copy .env.example to .env and add your MISTRAL_API_KEY
cp .env.example .env
# Then edit .env and add: MISTRAL_API_KEY=your-api-key-here

python main.py
```

✅ Backend running on http://localhost:8000

### Step 2: Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running on http://localhost:5173

### Step 3: Use the App

1. Open http://localhost:5173 in your browser
2. Upload a PDF research paper
3. Wait for processing
4. View results!

## 🎯 What Happens?

1. **PDF Upload** → Text extraction
2. **RAG Retrieval** → Finds References section
3. **AI Classification** → MistralAI classifies each reference
4. **URL Checking** → Verifies each URL status
5. **Display Results** → Beautiful table with filters

## 🔧 Troubleshooting

**Backend won't start?**
- Check Python: `python --version` (needs 3.8+)
- Create `.env` file in backend directory with `MISTRAL_API_KEY=your-key`
- Get API key from: https://console.mistral.ai/

**Frontend won't start?**
- Check Node: `node --version` (needs 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**PDF processing fails?**
- Ensure PDF has a References section
- Check if PDF is password-protected
- Verify `.env` file exists with valid `MISTRAL_API_KEY`

## 📚 Next Steps

- Read full [README.md](README.md) for details
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for advanced setup
- Customize prompts in `backend/services/reference_processor.py`

