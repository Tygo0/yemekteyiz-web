import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { contestantService, weekService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function Contestants() {
  const { isAuthenticated } = useAuth()
  const [contestants, setContestants] = useState([])
  const [weeks, setWeeks] = useState([])
  const [weekFilter, setWeekFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ week_id: '', name: '', age: '', city: '', profession: '' })
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function loadAll() {
    setLoading(true)
    Promise.all([contestantService.list(), weekService.list()])
      .then(([c, w]) => {
        setContestants(c)
        setWeeks(w)
        setForm((f) => ({ ...f, week_id: f.week_id || w[0]?.id || '' }))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(loadAll, [])

  async function handleCreate(e) {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await contestantService.create({
        week_id: Number(form.week_id),
        name: form.name,
        age: form.age ? Number(form.age) : undefined,
        city: form.city || undefined,
        profession: form.profession || undefined,
      })
      setForm((f) => ({ ...f, name: '', age: '', city: '', profession: '' }))
      loadAll()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this contestant?')) return
    try {
      await contestantService.remove(id)
      loadAll()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingState label="Loading contestants…" />
  if (error) return <ErrorState message={error} />

  const weekLabel = (id) => {
    const w = weeks.find((w) => w.id === id)
    return w ? `Week ${w.week_number}` : `Week ${id}`
  }

  const visible = weekFilter
    ? contestants.filter((c) => c.week_id === Number(weekFilter))
    : contestants

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Contestants</h1>
      <p className="text-sm text-ink/50 mb-4">Everyone who's cooked on the show.</p>

      <div className="mb-6">
        <select
          value={weekFilter}
          onChange={(e) => setWeekFilter(e.target.value)}
          className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-stone-50 text-sm"
        >
          <option value="">All weeks</option>
          {weeks.map((w) => (
            <option key={w.id} value={w.id}>
              Week {w.week_number}
            </option>
          ))}
        </select>
      </div>

      {visible.length === 0 ? (
        <EmptyState title="No contestants found" />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {visible.map((c) => (
            <div key={c.id} className="border-2 border-ink/10 bg-stone-50 rounded-lg p-4">
              <p className="font-display text-lg font-semibold text-ink">{c.name}</p>
              <p className="text-sm text-ink/50">
                {[c.profession, c.city].filter(Boolean).join(' · ') || weekLabel(c.week_id)}
              </p>
              <p className="text-xs text-ink/40 mt-1">{weekLabel(c.week_id)}</p>
              {isAuthenticated && (
                <button
                  onClick={() => handleDelete(c.id)}
                  className="text-xs text-brick font-medium hover:underline mt-2"
                >
                  Delete
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {isAuthenticated && (
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a contestant</h2>
          <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Week</label>
              <select
                value={form.week_id}
                onChange={(e) => setForm({ ...form, week_id: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              >
                {weeks.map((w) => (
                  <option key={w.id} value={w.id}>
                    Week {w.week_number}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Age</label>
              <input
                type="number"
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-20"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">City</label>
              <input
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Profession</label>
              <input
                value={form.profession}
                onChange={(e) => setForm({ ...form, profession: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !weeks.length}
              className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
            >
              {submitting ? 'Adding…' : 'Add contestant'}
            </button>
          </form>
          {!weeks.length && (
            <p className="text-xs text-ink/40 mt-2">Add a week first before adding contestants.</p>
          )}
          {formError && (
            <div className="mt-3">
              <ErrorState message={formError} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
