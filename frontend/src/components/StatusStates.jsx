export function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-2 py-8 text-ink/50 font-body text-sm">
      <span className="inline-block w-4 h-4 border-2 border-teal border-t-transparent rounded-full animate-spin" />
      {label}
    </div>
  )
}

export function ErrorState({ message }) {
  return (
    <div className="border-2 border-brick bg-brick-light text-brick rounded-lg px-4 py-3 text-sm font-medium">
      {message || 'Something went wrong.'}
    </div>
  )
}

export function EmptyState({ title, hint }) {
  return (
    <div className="border-2 border-dashed border-ink/15 rounded-lg px-6 py-10 text-center">
      <p className="font-display text-lg text-ink">{title}</p>
      {hint && <p className="text-sm text-ink/50 mt-1">{hint}</p>}
    </div>
  )
}
