import { useEffect, useState } from 'react'
import { statisticsService } from '../services/resources'
import { LoadingState, ErrorState } from '../components/StatusStates'
import ScorePaddle from '../components/ScorePaddle'

export default function Statistics() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    statisticsService
      .get()
      .then(setStats)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState label="Crunching the numbers…" />
  if (error) return <ErrorState message={error} />

  const maxCount = Math.max(1, ...Object.values(stats.score_distribution))

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Statistics</h1>
      <p className="text-sm text-ink/50 mb-8">Every number the show has produced, so far.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-4">
            Highest score ever
          </p>
          {stats.highest_score_ever ? (
            <div className="flex items-center gap-4">
              <ScorePaddle value={stats.highest_score_ever.value} size="lg" />
              <div>
                <p className="font-display text-xl font-semibold text-ink">
                  {stats.highest_score_ever.contestant_name}
                </p>
                <p className="text-sm text-ink/50">given by {stats.highest_score_ever.judge_name}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-4">
            Overall average score
          </p>
          {stats.average_score !== null ? (
            <ScorePaddle value={stats.average_score} size="lg" />
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-3">
            Most successful contestant
          </p>
          {stats.most_successful_contestant ? (
            <div>
              <p className="font-display text-xl font-semibold text-ink">
                {stats.most_successful_contestant.contestant_name}
              </p>
              <p className="text-sm text-ink/50">
                average score {stats.most_successful_contestant.average_score}
              </p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-3">
            Most common dish
          </p>
          {stats.most_common_dish ? (
            <div>
              <p className="font-display text-xl font-semibold text-ink">
                {stats.most_common_dish.dish_name}
              </p>
              <p className="text-sm text-ink/50">made {stats.most_common_dish.count} times</p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No dishes yet</p>
          )}
        </div>
      </div>

      <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6 mb-10">
        <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-4">
          Score distribution
        </p>
        <div className="flex items-end gap-2 h-32">
          {Object.entries(stats.score_distribution).map(([value, count]) => (
            <div key={value} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-teal rounded-t-sm"
                style={{ height: `${(count / maxCount) * 100}%`, minHeight: count ? '4px' : '1px' }}
                title={`${count} score${count === 1 ? '' : 's'} of ${value}`}
              />
              <span className="text-xs font-mono text-ink/50">{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Weekly winners</h2>
          <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50">
            {stats.weekly_winners.length === 0 && (
              <p className="p-4 text-sm text-ink/40">No winners set yet.</p>
            )}
            {stats.weekly_winners.map((w) => (
              <div key={w.week_id} className="flex items-center justify-between px-4 py-2.5">
                <span className="text-sm text-ink/70">Week {w.week_number}</span>
                <span className="font-medium text-ink text-sm">{w.winner_name}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Average score by week</h2>
          <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50">
            {stats.average_weekly_score.length === 0 && (
              <p className="p-4 text-sm text-ink/40">No scores yet.</p>
            )}
            {stats.average_weekly_score.map((w) => (
              <div key={w.week_id} className="flex items-center justify-between px-4 py-2.5">
                <span className="text-sm text-ink/70">Week {w.week_number}</span>
                <span className="font-mono font-semibold text-ink text-sm">{w.average_score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
