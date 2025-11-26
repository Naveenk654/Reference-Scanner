import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import ChatLauncher from './components/ChatLauncher'
import FileUploader from './components/FileUploader'
import ReferenceTable from './components/ReferenceTable'
import Loader from './components/Loader'
import { motion } from 'framer-motion'
import ChatbotPage from './pages/ChatbotPage'
import API_URL from './config/api'

function App() {
  const [references, setReferences] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')
  const location = useLocation()
  const loadingSteps = [
    { title: 'Upload received', description: 'PDF queued for processing' },
    { title: 'Extracting text', description: 'Parsing the document contents' },
    { title: 'Finding references', description: 'Identifying references section' },
    { title: 'Structuring citations', description: 'Formatting raw references' },
    { title: 'Enriching URLs', description: 'Searching for missing links' },
    { title: 'Checking URL status', description: 'Verifying availability' },
    { title: 'Preparing results', description: 'Compiling the final list' },
  ]

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'))
  }

  const handleUpload = async (file) => {
    setLoading(true)
    setError(null)
    setReferences([])

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_URL}/upload_pdf`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to process PDF')
      }

      const data = await response.json()
      setReferences(data.references || [])
    } catch (err) {
      setError(err.message || 'An error occurred while processing the PDF')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const ReferenceView = () => {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Reference Checker
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Upload a research paper PDF to extract and verify references
          </p>
        </div>

        <FileUploader onUpload={handleUpload} disabled={loading} />

        {loading && (
          <div className="mt-8">
            <Loader message="Extracting references..." steps={loadingSteps} />
          </div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-8 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg dark:bg-red-900/30 dark:border-red-900 dark:text-red-100"
          >
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </motion.div>
        )}

        {!loading && references.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-8"
          >
            <ReferenceTable references={references} />
          </motion.div>
        )}
      </motion.div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors">
      <Navbar theme={theme} onToggleTheme={toggleTheme} currentPath={location.pathname} />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <Routes>
          <Route path="/" element={<ReferenceView />} />
          <Route path="/chat" element={<ChatbotPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <ChatLauncher />
    </div>
  )
}

export default App

