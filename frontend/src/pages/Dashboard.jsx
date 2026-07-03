import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { weekService, statisticsService } from '../services/resources'
import { LoadingState, ErrorState } from '../components/StatusStates'
import ScorePaddle from '../components/ScorePaddle'

export default function Dashboard() {
  const { admin } = useAuth()
  const [weeks, setWeeks] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([weekService.list(), statisticsService.get()])
      .then(([weeksData, statsData]) => {
        setWeeks(weeksData)
        setStats(statsData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState label="Loading dashboard…" />
  if (error) return <ErrorState message={error} />

  const latestWeeks = [...weeks].reverse().slice(0, 5)

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">
        Welcome back, {admin?.username}
      </h1>
      <p className="text-sm text-ink/50 mb-8">
        {weeks.length} week{weeks.length === 1 ? '' : 's'} on record.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-5">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-3">
            Highest score ever
          </p>
          {stats.highest_score_ever ? (
            <div className="flex items-center gap-3">
              <ScorePaddle value={stats.highest_score_ever.value} size="sm" />
              <div>
                <p className="font-medium text-ink">{stats.highest_score_ever.contestant_name}</p>
                <p className="text-xs text-ink/50">by {stats.highest_score_ever.judge_name}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-5">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-3">
            Most successful contestant
          </p>
          {stats.most_successful_contestant ? (
            <div>
              <p className="font-medium text-ink">
                {stats.most_successful_contestant.contestant_name}
              </p>
              <p className="text-xs text-ink/50">
                avg {stats.most_successful_contestant.average_score}
              </p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No scores yet</p>
          )}
        </div>

        <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-5">
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-3">
            Most common dish
          </p>
          {stats.most_common_dish ? (
            <div>
              <p className="font-medium text-ink">{stats.most_common_dish.dish_name}</p>
              <p className="text-xs text-ink/50">made {stats.most_common_dish.count} times</p>
            </div>
          ) : (
            <p className="text-sm text-ink/40">No dishes yet</p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mb-3">
        <h2 className="font-display text-xl font-semibold text-ink">Recent weeks</h2>
        <Link to="/" className="text-sm text-teal font-medium hover:underline">
          Manage weeks →
        </Link>
      </div>
      <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50">
        {latestWeeks.length === 0 && (
          <p className="p-5 text-sm text-ink/40">No weeks created yet.</p>
        )}
        {latestWeeks.map((w) => (
          <div key={w.id} className="flex items-center justify-between px-5 py-3">
            <span className="font-medium text-ink">Week {w.week_number}</span>
            <span className="text-sm text-ink/50">
              {w.winner_id ? 'Winner set' : 'Winner not yet set'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
