import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload, File, X } from 'lucide-react'
import { Button } from './ui/button'

export default function FileUploader({ onUpload, disabled }) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
      } else {
        alert('Please upload a PDF file')
      }
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
      } else {
        alert('Please upload a PDF file')
      }
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile)
      setSelectedFile(null)
    }
  }

  const handleRemove = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50 dark:bg-slate-800'
            : 'border-gray-300 bg-white hover:border-gray-400 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-slate-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
          id="file-upload"
          disabled={disabled}
        />
        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center cursor-pointer text-gray-900 dark:text-gray-100"
        >
          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <Upload className="w-12 h-12 text-gray-400 mb-4" />
          </motion.div>
          <p className="text-lg font-semibold text-gray-700 dark:text-gray-100 mb-2">
            Drag & drop your PDF here
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-300 mb-4">or</p>
          <Button
            type="button"
            disabled={disabled}
            onClick={() => !disabled && fileInputRef.current?.click()}
          >
            Browse Files
          </Button>
        </label>
      </div>

      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg p-4"
        >
          <div className="flex items-center space-x-3">
            <File className="w-5 h-5 text-blue-500" />
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">{selectedFile.name}</p>
              <p className="text-sm text-gray-500 dark:text-gray-300">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              onClick={handleUpload}
              disabled={disabled}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Upload & Process
            </Button>
            <button
              onClick={handleRemove}
              className="p-2 text-gray-400 hover:text-red-500"
              disabled={disabled}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}

