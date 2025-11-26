export default function StatusBadge({ status }) {
  const getStatusStyles = (status) => {
    const styles = {
      'Working': {
        bg: 'bg-green-100 dark:bg-green-900/40',
        text: 'text-green-800 dark:text-green-200',
        dot: 'bg-green-500 dark:bg-green-300',
      },
      'Not Working': {
        bg: 'bg-red-100 dark:bg-red-900/40',
        text: 'text-red-800 dark:text-red-200',
        dot: 'bg-red-500 dark:bg-red-300',
      },
      'Timeout': {
        bg: 'bg-yellow-100 dark:bg-yellow-900/40',
        text: 'text-yellow-800 dark:text-yellow-200',
        dot: 'bg-yellow-500 dark:bg-yellow-300',
      },
      'Broken': {
        bg: 'bg-orange-100 dark:bg-orange-900/40',
        text: 'text-orange-800 dark:text-orange-200',
        dot: 'bg-orange-500 dark:bg-orange-300',
      },
      'Unknown': {
        bg: 'bg-gray-100 dark:bg-slate-700',
        text: 'text-gray-800 dark:text-gray-100',
        dot: 'bg-gray-500 dark:bg-gray-300',
      },
    }
    return styles[status] || styles['Unknown']
  }

  const style = getStatusStyles(status)

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${style.dot}`} />
      <span className={`text-xs font-medium ${style.text}`}>{status}</span>
    </div>
  )
}

