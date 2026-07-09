import { useEffect, useState } from 'react'
import { statisticsService, weekService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'
import ScorePaddle from '../components/ScorePaddle'

export default function Statistics() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const [weeks, setWeeks] = useState([])
  const [selectedWeekId, setSelectedWeekId] = useState('')
  const [voteMatrix, setVoteMatrix] = useState(null)
  const [voteMatrixError, setVoteMatrixError] = useState(null)
  const [voteMatrixLoading, setVoteMatrixLoading] = useState(false)

  useEffect(() => {
    Promise.all([statisticsService.get(), weekService.list()])
      .then(([s, w]) => {
        setStats(s)
        setWeeks(w)
        setSelectedWeekId((id) => id || w[w.length - 1]?.id || '')
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedWeekId) return
    setVoteMatrixLoading(true)
    setVoteMatrixError(null)
    statisticsService
      .voteMatrix(selectedWeekId)
      .then(setVoteMatrix)
      .catch((err) => setVoteMatrixError(err.message))
      .finally(() => setVoteMatrixLoading(false))
  }, [selectedWeekId])

  if (loading) return <LoadingState label="Crunching the numbers…" />
  if (error) return <ErrorState message={error} />

  const maxCount = Math.max(1, ...Object.values(stats.score_distribution))

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Statistics</h1>
      <p className="text-sm text-ink/50 mb-8">Every number the show has produced, so far.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 tracking-wide mb-4">
            HIGHEST SCORE EVER
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
          <p className="text-xs font-medium text-ink/50 tracking-wide mb-4">
            OVERALL AVERAGE SCORE
          </p>
          {stats.average_score.average !== null ? (
            <div>
              {/* Not a ScorePaddle — that component is sized for a single-digit
                  1-10 judge score, not a decimal average, which would overflow it. */}
              <p className="font-display text-4xl font-semibold text-ink">
                {stats.average_score.average}
                <span className="text-lg text-ink/40 font-normal"> / 10</span>
              </p>
              <p className="text-sm text-ink/50 mt-1">
                across {stats.average_score.count} score{stats.average_score.count === 1 ? '' : 's'}, all-time
              </p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 tracking-wide mb-3">
            MOST SUCCESSFUL CONTESTANT{stats.most_successful_contestants.length > 1 ? 'S' : ''}
          </p>
          {stats.most_successful_contestants.length > 0 ? (
            <div>
              <p className="font-display text-xl font-semibold text-ink">
                {stats.most_successful_contestants.map((c) => c.contestant_name).join(' & ')}
              </p>
              <p className="text-sm text-ink/50">
                {stats.most_successful_contestants[0].total_score} total points
              </p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6">
          <p className="text-xs font-medium text-ink/50 tracking-wide mb-3">
            MOST COMMON DISH
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
        <p className="text-xs font-medium text-ink/50 tracking-wide mb-4">
          SCORE DISTRIBUTION
        </p>
        <div className="flex items-end gap-2 h-32">
          {Object.entries(stats.score_distribution).map(([value, count]) => (
            // h-full (not the old flex-col wrapper) so the bar's percentage
            // height actually resolves against the chart's 128px — a plain
            // "items-end" parent aligns flex items, it doesn't stretch them,
            // so the old wrapper div was only ever as tall as its own content.
            <div key={value} className="flex-1 h-full flex items-end">
              <div
                className="w-full bg-teal rounded-t-sm"
                style={{ height: `${(count / maxCount) * 100}%`, minHeight: count ? '4px' : '1px' }}
                title={`${count} score${count === 1 ? '' : 's'} of ${value}`}
              />
            </div>
          ))}
        </div>
        <div className="flex gap-2 mt-1">
          {Object.keys(stats.score_distribution).map((value) => (
            <span key={value} className="flex-1 text-center text-xs font-mono text-ink/50">
              {value}
            </span>
          ))}
        </div>
      </div>

      <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6 mb-10">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <p className="text-xs font-medium text-ink/50 tracking-wide">VOTE MATRIX</p>
          <div>
            <label htmlFor="vote-matrix-week" className="sr-only">Week</label>
            <select
              id="vote-matrix-week"
              value={selectedWeekId}
              onChange={(e) => setSelectedWeekId(e.target.value)}
              className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
            >
              {weeks.map((w) => (
                <option key={w.id} value={w.id}>
                  Week {w.week_number}
                </option>
              ))}
            </select>
          </div>
        </div>

        {weeks.length === 0 ? (
          <EmptyState title="No weeks yet" hint="Add a week first to see who scored whom." />
        ) : voteMatrixLoading || !voteMatrix ? (
          <LoadingState label="Loading vote matrix…" />
        ) : voteMatrixError ? (
          <ErrorState message={voteMatrixError} />
        ) : voteMatrix.contestants.length === 0 ? (
          <EmptyState title="No contestants for this week yet" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr>
                  <th className="text-left p-2"></th>
                  {voteMatrix.judges.map((judge) => (
                    <th key={judge} className="text-center p-2 font-medium text-ink/60 whitespace-nowrap">
                      {judge}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {voteMatrix.contestants.map((c) => (
                  <tr key={c.id} className="border-t-2 border-ink/10">
                    <td className="p-2 font-medium text-ink whitespace-nowrap">{c.name}</td>
                    {voteMatrix.judges.map((judge) => (
                      <td key={judge} className="text-center p-2 font-mono">
                        {voteMatrix.matrix[c.id]?.[judge] ?? '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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
                <span className="font-medium text-ink text-sm">
                  {w.winners.map((winner) => winner.name).join(' & ')}
                </span>
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
