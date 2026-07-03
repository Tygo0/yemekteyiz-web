import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { dishService, episodeService, contestantService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

const CATEGORIES = [
  { value: 'soup', label: 'Soup' },
  { value: 'appetizer', label: 'Appetizer' },
  { value: 'main_course', label: 'Main Course' },
  { value: 'dessert', label: 'Dessert' },
  { value: 'beverage', label: 'Beverage' },
]

export default function Dishes() {
  const { isAuthenticated } = useAuth()
  const [dishes, setDishes] = useState([])
  const [episodes, setEpisodes] = useState([])
  const [contestants, setContestants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ episode_id: '', name: '', category: 'main_course' })
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function loadAll() {
    setLoading(true)
    Promise.all([dishService.list(), episodeService.list(), contestantService.list()])
      .then(([d, e, c]) => {
        setDishes(d)
        setEpisodes(e)
        setContestants(c)
        setForm((f) => ({ ...f, episode_id: f.episode_id || e[0]?.id || '' }))
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
      await dishService.create({
        episode_id: Number(form.episode_id),
        name: form.name,
        category: form.category,
      })
      setForm((f) => ({ ...f, name: '' }))
      loadAll()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this dish?')) return
    try {
      await dishService.remove(id)
      loadAll()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingState label="Loading dishes…" />
  if (error) return <ErrorState message={error} />

  const episodeLabel = (id) => {
    const ep = episodes.find((e) => e.id === id)
    const contestant = ep && contestants.find((c) => c.id === ep.contestant_id)
    return contestant ? contestant.name : `Episode ${id}`
  }
  const categoryLabel = (v) => CATEGORIES.find((c) => c.value === v)?.label || v

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Dishes</h1>
      <p className="text-sm text-ink/50 mb-8">Everything cooked on the show, by category.</p>

      {dishes.length === 0 ? (
        <EmptyState title="No dishes recorded yet" />
      ) : (
        <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50 mb-8">
          {dishes.map((d) => (
            <div key={d.id} className="flex items-center justify-between px-5 py-3">
              <div>
                <p className="font-medium text-ink">{d.name}</p>
                <p className="text-xs text-ink/50">
                  {categoryLabel(d.category)} · {episodeLabel(d.episode_id)}
                </p>
              </div>
              {isAuthenticated && (
                <button
                  onClick={() => handleDelete(d.id)}
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
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a dish</h2>
          <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Episode</label>
              <select
                value={form.episode_id}
                onChange={(e) => setForm({ ...form, episode_id: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              >
                {episodes.map((e) => (
                  <option key={e.id} value={e.id}>
                    {episodeLabel(e.id)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Dish name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Category</label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={submitting || !episodes.length}
              className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
            >
              {submitting ? 'Adding…' : 'Add dish'}
            </button>
          </form>
          {!episodes.length && <p className="text-xs text-ink/40 mt-2">Add an episode first.</p>}
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
