export default function CategoryBadge({ type }) {
  const getBadgeStyles = (type) => {
    const styles = {
      'Research Paper': 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900 dark:text-blue-100 dark:border-blue-700',
      'News Article': 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-100 dark:border-yellow-700',
      'YouTube Video': 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-100 dark:border-red-700',
      'General Web Reference': 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900 dark:text-purple-100 dark:border-purple-700',
      'Unknown': 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-slate-700 dark:text-gray-100 dark:border-slate-600',
    }
    return styles[type] || styles['Unknown']
  }

  return (
    <span
      className={`inline-flex items-center px-3 py-0.5 rounded-full text-[0.7rem] font-semibold border whitespace-nowrap ${getBadgeStyles(
        type
      )}`}
    >
      {type}
    </span>
  )
}

