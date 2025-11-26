import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Moon, Sun, BookOpenCheck, Sparkles } from 'lucide-react'
import { Button } from './ui/button'

const navLinks = [
  { label: 'References', to: '/' },
  { label: 'Research Copilot', to: '/chat' },
]

export default function Navbar({ theme, onToggleTheme, currentPath = '/' }) {
  const isDark = theme === 'dark'

  return (
    <nav className="bg-white dark:bg-slate-900 shadow-sm border-b dark:border-slate-800 transition-colors">
      <div className="container mx-auto px-4 py-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center space-x-6">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 shadow-lg shadow-blue-500/30 flex items-center justify-center text-white group-hover:scale-105 transition-transform">
                  <BookOpenCheck className="w-5 h-5" />
                </div>
                <Sparkles className="w-4 h-4 text-amber-300 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">Reference Checker</span>
            </Link>

            <nav className="hidden md:flex items-center gap-3">
              {navLinks.map(link => {
                const isActive = currentPath === link.to
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`px-3 py-2 text-sm font-semibold rounded-full transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400'
                    }`}
                  >
                    {link.label}
                  </Link>
                )
              })}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600 dark:text-gray-300 hidden sm:block">
              Reference Verification System
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onToggleTheme}
              className="border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-200"
            >
              {isDark ? (
                <>
                  <Sun className="w-4 h-4 mr-2" />
                  Light
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 mr-2" />
                  Dark
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    </nav>
  )
}

