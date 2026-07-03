import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { weekService, seasonService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function Weeks() {
  const { isAuthenticated } = useAuth()
  const [weeks, setWeeks] = useState([])
  const [seasons, setSeasons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ season_id: '', week_number: '', youtube_url: '', notes: '' })
  const [newSeasonName, setNewSeasonName] = useState('')
  const [newSeasonYear, setNewSeasonYear] = useState(new Date().getFullYear())
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function loadAll() {
    setLoading(true)
    Promise.all([weekService.list(), seasonService.list()])
      .then(([w, s]) => {
        setWeeks(w)
        setSeasons(s)
        setForm((f) => ({ ...f, season_id: f.season_id || s[0]?.id || '' }))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(loadAll, [])

  async function handleCreateSeason(e) {
    e.preventDefault()
    setFormError(null)
    try {
      const season = await seasonService.create({
        name: newSeasonName,
        year: Number(newSeasonYear),
      })
      setSeasons((prev) => [season, ...prev])
      setForm((f) => ({ ...f, season_id: season.id }))
      setNewSeasonName('')
    } catch (err) {
      setFormError(err.message)
    }
  }

  async function handleCreateWeek(e) {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await weekService.create({
        season_id: Number(form.season_id),
        week_number: Number(form.week_number),
        youtube_url: form.youtube_url || undefined,
        notes: form.notes || undefined,
      })
      setForm((f) => ({ ...f, week_number: '', youtube_url: '', notes: '' }))
      loadAll()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this week and all its contestants?')) return
    try {
      await weekService.remove(id)
      loadAll()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingState label="Loading weeks…" />
  if (error) return <ErrorState message={error} />

  const seasonName = (id) => seasons.find((s) => s.id === id)?.name || `Season ${id}`

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Weeks</h1>
      <p className="text-sm text-ink/50 mb-8">Every week the show has aired, by season.</p>

      {weeks.length === 0 ? (
        <EmptyState
          title="No weeks yet"
          hint={isAuthenticated ? 'Add the first one below.' : 'Check back once the season starts.'}
        />
      ) : (
        <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50 mb-8">
          {weeks.map((w) => (
            <div key={w.id} className="flex items-center justify-between px-5 py-3">
              <div>
                <p className="font-medium text-ink">
                  {seasonName(w.season_id)} — Week {w.week_number}
                </p>
                <p className="text-xs text-ink/50">
                  {w.air_date || 'Air date TBD'}
                  {w.winner_id ? ' · Winner set' : ''}
                </p>
              </div>
              {isAuthenticated && (
                <button
                  onClick={() => handleDelete(w.id)}
                  className="text-sm text-brick font-medium hover:underline"
                >
                  Delete
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {isAuthenticated && (
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5 space-y-6">
          <div>
            <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a season</h2>
            <form onSubmit={handleCreateSeason} className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">Name</label>
                <input
                  value={newSeasonName}
                  onChange={(e) => setNewSeasonName(e.target.value)}
                  required
                  placeholder="Season 1"
                  className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">Year</label>
                <input
                  type="number"
                  value={newSeasonYear}
                  onChange={(e) => setNewSeasonYear(e.target.value)}
                  required
                  className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-24"
                />
              </div>
              <button
                type="submit"
                className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark"
              >
                Add season
              </button>
            </form>
          </div>

          <div className="border-t-2 border-ink/10 pt-6">
            <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a week</h2>
            <form onSubmit={handleCreateWeek} className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">Season</label>
                <select
                  value={form.season_id}
                  onChange={(e) => setForm({ ...form, season_id: e.target.value })}
                  required
                  className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                >
                  {seasons.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.year})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">Week #</label>
                <input
                  type="number"
                  min="1"
                  value={form.week_number}
                  onChange={(e) => setForm({ ...form, week_number: e.target.value })}
                  required
                  className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-20"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">YouTube URL</label>
                <input
                  value={form.youtube_url}
                  onChange={(e) => setForm({ ...form, youtube_url: e.target.value })}
                  className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-64"
                />
              </div>
              <button
                type="submit"
                disabled={submitting || !seasons.length}
                className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
              >
                {submitting ? 'Adding…' : 'Add week'}
              </button>
            </form>
          </div>

          {formError && <ErrorState message={formError} />}
        </div>
      )}
    </div>
  )
}
