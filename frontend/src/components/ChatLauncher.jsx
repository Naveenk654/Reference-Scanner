import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export default function ChatLauncher() {
  const [hovered, setHovered] = useState(false)
  const [showLabel, setShowLabel] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const pulseTimer = setInterval(() => {
      setShowLabel(true)
      setTimeout(() => setShowLabel(false), 2000)
    }, 7000)
    return () => clearInterval(pulseTimer)
  }, [])

  if (location.pathname === '/chat') {
    return null
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 pointer-events-none">
      <div className="flex flex-col items-end pointer-events-auto">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: hovered || showLabel ? 1 : 0, y: hovered || showLabel ? 0 : 10 }}
          transition={{ duration: 0.3 }}
          className="mb-2 px-3 py-1 rounded-full bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 text-xs font-semibold text-gray-800 dark:text-gray-100 shadow pointer-events-none"
        >
          Ask me anything
        </motion.div>
        <motion.button
          type="button"
          onClick={() => navigate('/chat')}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
          className="w-14 h-14 rounded-full bg-gradient-to-br from-orange-400 to-red-500 text-white shadow-lg flex items-center justify-center cursor-pointer"
          aria-label="Open Copilot chat"
          animate={{
            y: hovered ? -4 : 0,
            boxShadow: hovered
              ? '0 15px 25px rgba(0,0,0,0.25)'
              : '0 10px 20px rgba(0,0,0,0.2)',
          }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          whileTap={{ scale: 0.95 }}
        >
          <motion.div
            animate={{ y: [0, -4, 0] }}
            transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
          >
            <Sparkles className="w-6 h-6" />
          </motion.div>
        </motion.button>
      </div>
    </div>
  )
}

