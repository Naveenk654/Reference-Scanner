# RefCheck - Reference Verification System

A production-grade full-stack application for extracting, classifying, and verifying references from research paper PDFs using FastAPI, LangChain RAG, MistralAI, and React.

## 🚀 Features

- **PDF Upload**: Drag & drop or browse to upload research paper PDFs
- **RAG Extraction**: Uses LangChain + Chroma to extract References section
- **AI Classification**: MistralAI LLM classifies references into 5 categories:
  - Research Paper
  - News Article
  - YouTube Video
  - General Web Reference
  - Unknown
- **URL Verification**: Checks URL status (Working / Not Working / Timeout / Broken)
- **Modern UI**: React + Vite + Tailwind + ShadCN components
- **Search & Filter**: Filter by category and status, search references
- **Export**: Download results as JSON

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── pdf_extractor.py    # PDF text extraction
│   │   ├── rag_service.py      # RAG with Chroma vector store
│   │   ├── reference_processor.py  # MistralAI reference processing
│   │   └── url_checker.py      # URL status checking
│   └── requirements.txt        # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   ├── FileUploader.jsx
    │   │   ├── ReferenceTable.jsx
    │   │   ├── CategoryBadge.jsx
    │   │   ├── StatusBadge.jsx
    │   │   ├── Loader.jsx
    │   │   └── ui/              # ShadCN UI components
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- MistralAI API key (get one at https://mistral.ai)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MistralAI API key:

**Recommended: Create a `.env` file in the backend directory:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
MISTRAL_API_KEY=your-mistral-api-key-here
```

Get your API key from: https://console.mistral.ai/

**Note:** The application uses `mistral-small` model by default. The `.env` file is automatically loaded when the application starts.

5. Run the backend server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## 📖 Usage

1. Open `http://localhost:5173` in your browser
2. Upload a research paper PDF (drag & drop or browse)
3. Wait for processing (extraction → RAG → classification → URL checking)
4. View results in the table with:
   - Reference text
   - Category badges
   - URLs (clickable)
   - Status indicators
5. Use search and filters to find specific references
6. Export results as JSON

## 🔧 Configuration

### Backend Configuration

Edit `backend/services/reference_processor.py` to change:
- LLM model (currently using Ollama Mistral)
- Temperature settings
- Prompt template

### Frontend Configuration

Edit `frontend/vite.config.js` to change:
- API proxy settings
- Port number

## 🧪 API Endpoints

### POST `/upload_pdf`
Upload and process a PDF file.

**Request:**
- `file`: PDF file (multipart/form-data)

**Response:**
```json
{
  "success": true,
  "references": [
    {
      "original_reference": "...",
      "urls": ["..."],
      "type": "Research Paper",
      "status": "Working"
    }
  ],
  "message": "Successfully processed X references"
}
```

### GET `/health`
Health check endpoint.

## 🎨 Tech Stack

**Backend:**
- FastAPI
- LangChain
- ChromaDB (vector store)
- HuggingFace Embeddings
- MistralAI (via Ollama or API)
- PyPDF

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- ShadCN UI
- Framer Motion
- Axios

## 📝 Notes

- The system uses RAG to intelligently extract the References section
- URL checking may take time for many references
- For production, consider using MistralAI API directly instead of Ollama
- Vector store is created temporarily and cleaned up after processing

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (needs 3.8+)
- Ensure all dependencies are installed
- Verify MISTRAL_API_KEY is set: `echo $MISTRAL_API_KEY` (Linux/Mac) or `echo %MISTRAL_API_KEY%` (Windows)

**Frontend won't start:**
- Check Node.js version: `node --version` (needs 18+)
- Delete `node_modules` and `package-lock.json`, then `npm install` again

**PDF processing fails:**
- Ensure PDF is not password-protected
- Check if PDF contains a References section
- Verify Ollama/MistralAI is accessible

## 📄 License

MIT License

