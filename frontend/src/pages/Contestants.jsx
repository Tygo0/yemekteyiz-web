import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { contestantService, weekService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

const emptyForm = {
  week_id: '',
  name: '',
  age: '',
  city: '',
  profession: '',
  biography: '',
  photo_url: '',
}

export default function Contestants() {
  const { isAuthenticated } = useAuth()
  const [contestants, setContestants] = useState([])
  const [weeks, setWeeks] = useState([])
  const [weekFilter, setWeekFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState(emptyForm)
  const [editError, setEditError] = useState(null)
  const [editSubmitting, setEditSubmitting] = useState(false)

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
        biography: form.biography || undefined,
        photo_url: form.photo_url || undefined,
      })
      setForm((f) => ({ ...emptyForm, week_id: f.week_id }))
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

  function startEdit(c) {
    setEditingId(c.id)
    setEditError(null)
    setEditForm({
      week_id: c.week_id,
      name: c.name || '',
      age: c.age ?? '',
      city: c.city || '',
      profession: c.profession || '',
      biography: c.biography || '',
      photo_url: c.photo_url || '',
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setEditError(null)
  }

  async function handleUpdate(e, id) {
    e.preventDefault()
    setEditError(null)
    setEditSubmitting(true)
    try {
      await contestantService.update(id, {
        name: editForm.name,
        age: editForm.age === '' ? null : Number(editForm.age),
        city: editForm.city || null,
        profession: editForm.profession || null,
        biography: editForm.biography || null,
        photo_url: editForm.photo_url || null,
      })
      setEditingId(null)
      loadAll()
    } catch (err) {
      setEditError(err.message)
    } finally {
      setEditSubmitting(false)
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
          {visible.map((c) =>
            editingId === c.id ? (
              <form
                key={c.id}
                onSubmit={(e) => handleUpdate(e, c.id)}
                className="border-2 border-teal bg-stone-50 rounded-lg p-4 space-y-2 sm:col-span-2 lg:col-span-3"
              >
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label htmlFor={`edit-name-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">Name</label>
                    <input
                      id={`edit-name-${c.id}`}
                      value={editForm.name}
                      onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                      required
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor={`edit-age-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">Age</label>
                    <input
                      id={`edit-age-${c.id}`}
                      type="number"
                      value={editForm.age}
                      onChange={(e) => setEditForm({ ...editForm, age: e.target.value })}
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor={`edit-city-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">City</label>
                    <input
                      id={`edit-city-${c.id}`}
                      value={editForm.city}
                      onChange={(e) => setEditForm({ ...editForm, city: e.target.value })}
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor={`edit-profession-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">Profession</label>
                    <input
                      id={`edit-profession-${c.id}`}
                      value={editForm.profession}
                      onChange={(e) => setEditForm({ ...editForm, profession: e.target.value })}
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor={`edit-photo-url-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">Photo URL</label>
                    <input
                      id={`edit-photo-url-${c.id}`}
                      value={editForm.photo_url}
                      onChange={(e) => setEditForm({ ...editForm, photo_url: e.target.value })}
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label htmlFor={`edit-biography-${c.id}`} className="block text-xs font-medium text-ink/60 mb-1">Biography</label>
                    <textarea
                      id={`edit-biography-${c.id}`}
                      value={editForm.biography}
                      onChange={(e) => setEditForm({ ...editForm, biography: e.target.value })}
                      rows={3}
                      className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                </div>
                {editError && <ErrorState message={editError} />}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={editSubmitting}
                    className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
                  >
                    {editSubmitting ? 'Saving…' : 'Save changes'}
                  </button>
                  <button
                    type="button"
                    onClick={cancelEdit}
                    className="rounded-md border-2 border-ink/15 text-sm font-medium px-4 py-1.5 hover:bg-stone-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div key={c.id} className="border-2 border-ink/10 bg-stone-50 rounded-lg p-4">
                {c.photo_url && (
                  <img
                    src={c.photo_url}
                    alt={c.name}
                    className="w-full h-32 object-cover rounded-md mb-3"
                    onError={(e) => (e.target.style.display = 'none')}
                  />
                )}
                <p className="font-display text-lg font-semibold text-ink">{c.name}</p>
                <p className="text-sm text-ink/50">
                  {[c.profession, c.city].filter(Boolean).join(' · ') || weekLabel(c.week_id)}
                </p>
                <p className="text-xs text-ink/40 mt-1">{weekLabel(c.week_id)}</p>
                {c.biography && <p className="text-sm text-ink/70 mt-2">{c.biography}</p>}
                {isAuthenticated && (
                  <div className="flex gap-3 mt-3">
                    <button
                      onClick={() => startEdit(c)}
                      className="text-xs text-teal font-medium hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(c.id)}
                      className="text-xs text-brick font-medium hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ),
          )}
        </div>
      )}

      {isAuthenticated && (
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a contestant</h2>
          <form onSubmit={handleCreate} className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label htmlFor="create-week" className="block text-xs font-medium text-ink/60 mb-1">Week</label>
                <select
                  id="create-week"
                  value={form.week_id}
                  onChange={(e) => setForm({ ...form, week_id: e.target.value })}
                  required
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                >
                  {weeks.map((w) => (
                    <option key={w.id} value={w.id}>
                      Week {w.week_number}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="create-name" className="block text-xs font-medium text-ink/60 mb-1">Name</label>
                <input
                  id="create-name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div>
                <label htmlFor="create-age" className="block text-xs font-medium text-ink/60 mb-1">Age</label>
                <input
                  id="create-age"
                  type="number"
                  value={form.age}
                  onChange={(e) => setForm({ ...form, age: e.target.value })}
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div>
                <label htmlFor="create-city" className="block text-xs font-medium text-ink/60 mb-1">City</label>
                <input
                  id="create-city"
                  value={form.city}
                  onChange={(e) => setForm({ ...form, city: e.target.value })}
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div>
                <label htmlFor="create-profession" className="block text-xs font-medium text-ink/60 mb-1">Profession</label>
                <input
                  id="create-profession"
                  value={form.profession}
                  onChange={(e) => setForm({ ...form, profession: e.target.value })}
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div>
                <label htmlFor="create-photo-url" className="block text-xs font-medium text-ink/60 mb-1">Photo URL</label>
                <input
                  id="create-photo-url"
                  value={form.photo_url}
                  onChange={(e) => setForm({ ...form, photo_url: e.target.value })}
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
              <div className="sm:col-span-2">
                <label htmlFor="create-biography" className="block text-xs font-medium text-ink/60 mb-1">Biography</label>
                <textarea
                  id="create-biography"
                  value={form.biography}
                  onChange={(e) => setForm({ ...form, biography: e.target.value })}
                  rows={2}
                  className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                />
              </div>
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
