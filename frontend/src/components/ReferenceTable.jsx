import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Download, ChevronDown } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import CategoryBadge from './CategoryBadge'
import StatusBadge from './StatusBadge'
import { Card } from './ui/card'
import API_URL from '../config/api'

export default function ReferenceTable({ references }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [formattingResults, setFormattingResults] = useState({})
  const [formattingErrors, setFormattingErrors] = useState({})
  const [formattingLoading, setFormattingLoading] = useState({})
  const [selectedStyles, setSelectedStyles] = useState({})
  const [openDropdown, setOpenDropdown] = useState(null)

  const categories = ['all', ...new Set(references.map(r => r.type))]
  const statuses = ['all', ...new Set(references.map(r => r.status))]
  const styleOptions = ['APA', 'MLA', 'IEEE', 'Chicago', 'Harvard']

  const getRowKey = (ref, index) => `${ref.original_reference}-${index}`

  const filteredReferences = useMemo(() => {
    return references.filter((ref) => {
      const urlEntries = (ref.url_details && ref.url_details.length > 0)
        ? ref.url_details.map(detail => detail.url)
        : ref.urls

      const matchesSearch =
        searchQuery === '' ||
        ref.original_reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
        urlEntries.some(url => url.toLowerCase().includes(searchQuery.toLowerCase()))

      const matchesCategory = categoryFilter === 'all' || ref.type === categoryFilter
      const matchesStatus = statusFilter === 'all' || ref.status === statusFilter

      return matchesSearch && matchesCategory && matchesStatus
    })
  }, [references, searchQuery, categoryFilter, statusFilter])

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(filteredReferences, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `refcheck-references-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleFormatReference = async (referenceText, style, rowKey) => {
    if (!style) return

    setFormattingErrors(prev => ({ ...prev, [rowKey]: null }))
    setFormattingLoading(prev => ({ ...prev, [rowKey]: true }))

    try {
      const response = await fetch(`${API_URL}/format_reference`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ style, reference: referenceText })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to format reference')
      }

      const data = await response.json()
      setFormattingResults(prev => ({
        ...prev,
        [rowKey]: {
          style,
          text: data.formatted_reference || ''
        }
      }))
    } catch (err) {
      setFormattingErrors(prev => ({
        ...prev,
        [rowKey]: err.message || 'Failed to format reference'
      }))
    } finally {
      setFormattingLoading(prev => ({ ...prev, [rowKey]: false }))
    }
  }

  const handleStyleChange = (referenceText, rowKey, style) => {
    setSelectedStyles(prev => ({ ...prev, [rowKey]: style }))
    setOpenDropdown(null)
    handleFormatReference(referenceText, style, rowKey)
  }
  const toggleDropdown = (rowKey) => {
    setOpenDropdown(prev => (prev === rowKey ? null : rowKey))
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              References ({filteredReferences.length})
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-300 mt-1">
              Found {references.length} total references
            </p>
          </div>
          <Button onClick={handleExportJSON} className="bg-green-600 hover:bg-green-700">
            <Download className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Search references or URLs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white dark:bg-slate-900 dark:border-slate-700 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm text-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.filter(c => c !== 'all').map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm text-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statuses</option>
              {statuses.filter(s => s !== 'all').map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-200">Reference</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-200">Category</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-200">URLs</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-200">Status</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-200">Styles</th>
              </tr>
            </thead>
            <tbody>
              {filteredReferences.map((ref, index) => {
                const rowKey = getRowKey(ref, index)
                const isDropdownOpen = openDropdown === rowKey
                const isLoading = Boolean(formattingLoading[rowKey])
                return (
                <motion.tr
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-gray-100 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors bg-white dark:bg-transparent"
                >
                  <td className="py-4 px-4">
                    <div className="space-y-2">
                      <p className="text-xs text-gray-900 dark:text-gray-100 leading-relaxed">{ref.original_reference}</p>
                      <div className="flex flex-wrap items-center gap-3">
                        <div className="relative inline-block text-left">
                          <button
                            type="button"
                            onClick={() => toggleDropdown(rowKey)}
                            disabled={isLoading}
                            className="inline-flex items-center justify-between gap-1 w-32 px-2 py-1.5 border border-gray-300 dark:border-slate-700 rounded-md text-[11px] bg-white dark:bg-slate-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <span className="truncate">
                              {selectedStyles[rowKey] || 'Select citation style'}
                            </span>
                            <ChevronDown
                              className={`w-3.5 h-3.5 text-gray-500 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                            />
                          </button>
                          {isDropdownOpen && (
                            <div className="absolute z-10 mt-2 w-32 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-md shadow-lg text-[11px]">
                              {styleOptions.map(style => (
                                <button
                                  key={style}
                                  type="button"
                                  className="w-full text-left px-2 py-1.5 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800"
                                  onClick={() => handleStyleChange(ref.original_reference, rowKey, style)}
                                  disabled={isLoading}
                                >
                                  {style}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                        {isLoading && (
                          <p className="text-xs text-gray-500">Formatting...</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <CategoryBadge type={ref.type} />
                  </td>
                  <td className="py-4 px-4">
                    <div className="space-y-1">
                      {ref.urls.length > 0 ? (
                        (ref.url_details && ref.url_details.length > 0
                          ? ref.url_details
                          : ref.urls.map(url => ({ url, source: 'unknown' }))
                        ).map((entry, urlIndex) => (
                          <div key={urlIndex} className="flex items-center gap-2">
                            <a
                              href={entry.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline block truncate max-w-xs"
                            >
                              {entry.url}
                            </a>
                            <span
                              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                                entry.source === 'pdf'
                                  ? 'bg-green-100 text-green-700'
                                  : entry.source === 'research'
                                    ? 'bg-blue-100 text-blue-700'
                                    : entry.source === 'suggested'
                                      ? 'bg-amber-100 text-amber-700'
                                    : 'bg-gray-100 text-gray-600 dark:bg-slate-700 dark:text-gray-200'
                              }`}
                            >
                              {entry.source === 'pdf'
                                ? 'From PDF'
                                : entry.source === 'research'
                                  ? 'Research'
                                  : entry.source === 'suggested'
                                    ? 'Suggested'
                                    : 'Unknown'}
                            </span>
                          </div>
                        ))
                      ) : (
                        <span className="text-xs text-gray-400 dark:text-gray-500">No URLs</span>
                      )}
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <StatusBadge status={ref.status} />
                  </td>
                  <td className="py-4 px-4 align-middle">
                    {(() => {
                      const resultData = formattingResults[rowKey]
                      const error = formattingErrors[rowKey]
                      if (!resultData && !error) {
                        return (
                          <div className="flex items-center justify-center text-[11px] text-gray-400 dark:text-gray-500 min-h-[60px]">
                            <span>No style selected</span>
                          </div>
                        )
                      }
                      return (
                        <div className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-md p-3 space-y-1 text-[11px] leading-snug max-h-28 overflow-y-auto">
                          {resultData && (
                            <>
                              <p className="text-[10px] uppercase text-gray-500 dark:text-gray-400 tracking-wide">
                                {resultData.style} Format
                              </p>
                              <p className="text-[11px] text-gray-700 dark:text-gray-200">{resultData.text}</p>
                            </>
                          )}
                          {error && <p className="text-[11px] text-red-500">{error}</p>}
                        </div>
                      )
                    })()}
                  </td>
                </motion.tr>
              )})}
            </tbody>
          </table>

          {filteredReferences.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No references found matching your filters.
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

