/**
 * The show's judges physically hold up numbered paddles to score contestants —
 * this component is that gesture, rendered. It's the one signature visual
 * element reused everywhere a score appears (stats cards, score lists,
 * dashboard highlights), so it carries real meaning rather than being a
 * decorative shape.
 *
 * Color logic: gold for high scores (8-10), ink for mid-range (4-7), brick
 * for low scores (1-3) — the paddle color itself communicates the verdict.
 */
function paddleTone(value) {
  if (value >= 8) return 'bg-gold-light text-gold border-gold'
  if (value <= 3) return 'bg-brick-light text-brick border-brick'
  return 'bg-stone-50 text-ink border-ink/20'
}

export default function ScorePaddle({ value, label, size = 'md' }) {
  const sizes = {
    sm: 'w-12 h-14 text-2xl',
    md: 'w-16 h-20 text-3xl',
    lg: 'w-24 h-28 text-5xl',
  }

  return (
    <div className="inline-flex flex-col items-center gap-1.5">
      <div
        className={`${sizes[size]} ${paddleTone(value)} flex items-center justify-center rounded-lg border-2 font-mono font-bold shadow-sm`}
        aria-label={label ? `${label}: ${value}` : `Score: ${value}`}
      >
        {value}
      </div>
      {label && (
        <span className="text-xs font-medium text-ink/60 text-center max-w-[6rem] truncate">
          {label}
        </span>
      )}
    </div>
  )
}
