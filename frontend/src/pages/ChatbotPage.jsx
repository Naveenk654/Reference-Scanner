import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Copy, Loader2, Plus } from 'lucide-react'
import API_URL from '../config/api'

export default function ChatbotPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copiedId, setCopiedId] = useState(null)
  const [showMenu, setShowMenu] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!question.trim()) {
      setError('Please enter a question for the chatbot.')
      return
    }

    setError(null)
    const userMessage = { role: 'user', content: question.trim() }
    const updatedHistory = [...messages, userMessage]
    setMessages(updatedHistory)
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          history: updatedHistory,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Chatbot request failed')
      }

      const data = await response.json()
      const botMessage = { role: 'assistant', content: data.answer }
      setMessages(prev => [...prev, botMessage])
      setQuestion('')
    } catch (err) {
      setError(err.message || 'Failed to contact chatbot')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      setError('Failed to copy to clipboard')
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setQuestion('')
    setError(null)
    setShowMenu(false)
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-4"
      >
        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200 text-sm font-semibold">
          <Sparkles className="w-4 h-4" />
          Research Copilot
          </div>
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowMenu(prev => !prev)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-200 dark:border-blue-700 bg-white dark:bg-slate-900 text-sm font-semibold text-blue-700 dark:text-blue-200 shadow-sm hover:bg-blue-50 dark:hover:bg-slate-800 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Chat
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg shadow-lg overflow-hidden z-10">
                <button
                  type="button"
                  onClick={handleNewChat}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800"
                >
                  Start fresh
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessages([])
                    setShowMenu(false)
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800"
                >
                  Clear responses
                </button>
              </div>
            )}
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Ask the Groq Copilot</h1>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Ask any research question, request summaries, or get help exploring literature. Powered by Groq + Tavily.
        </p>
      </motion.div>

      <div className="space-y-4">
        <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-5 shadow-sm min-h-[420px]">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm text-center">
              Start chatting to see responses here. The assistant will remember the conversation.
            </div>
          ) : (
            <div className="space-y-4 max-h-[520px] overflow-y-auto pr-2">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`rounded-lg p-4 text-sm shadow-sm border ${
                    msg.role === 'user'
                      ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-100 dark:border-blue-800 text-blue-900 dark:text-blue-100'
                      : 'bg-gray-50 dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-800 dark:text-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                      {msg.role === 'user' ? 'You' : 'RefAssist'}
                    </span>
                    {msg.role === 'assistant' && (
                      <button
                        type="button"
                        onClick={() => handleCopy(msg.content, index)}
                        className="text-gray-500 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-300 text-xs inline-flex items-center gap-1"
                      >
                        <Copy className="w-3.5 h-3.5" />
                        {copiedId === index ? 'Copied' : 'Copy'}
                      </button>
                    )}
                  </div>
                  <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-4">
          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-3"
          >
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything about research papers or references..."
              className="w-full rounded-lg border border-gray-300 dark:border-slate-700 bg-gray-50 dark:bg-slate-800 text-sm text-gray-900 dark:text-gray-100 px-3 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-lg disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Thinking...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Ask Copilot
                </>
              )}
            </button>

            {error && (
              <p className="text-sm text-red-500">
                {error}
              </p>
            )}
          </form>

          <p className="text-xs text-gray-500 dark:text-gray-400">
            Tip: reference text is optional—just ask about any topic or paste a snippet in your question.
          </p>
        </div>
      </div>
    </div>
  )
}

