import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, Loader2, Circle } from 'lucide-react'

const defaultSteps = [
  { title: 'Working on it...', description: 'Please wait' },
]

export default function Loader({ message = "Loading...", steps = defaultSteps }) {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    setActiveStep(0)
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1
        }
        return prev
      })
    }, 1800)

    return () => clearInterval(interval)
  }, [steps])

  const renderIcon = (index) => {
    if (index < activeStep) {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />
    }
    if (index === activeStep) {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    }
    return <Circle className="w-5 h-5 text-gray-300 dark:text-gray-600" />
  }

  const currentStep = steps[Math.min(activeStep, steps.length - 1)] || defaultSteps[0]

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <motion.div
        className="w-16 h-16 border-4 border-blue-500 dark:border-blue-400 border-t-transparent rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      <p className="mt-4 text-gray-600 dark:text-gray-200 font-medium">{currentStep.title}</p>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {currentStep.description}
      </p>
    </div>
  )
}

