import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { episodeService, contestantService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function Episodes() {
  const { isAuthenticated } = useAuth()
  const [episodes, setEpisodes] = useState([])
  const [contestants, setContestants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ contestant_id: '', broadcast_date: '', video_url: '' })
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({ broadcast_date: '', video_url: '' })
  const [editError, setEditError] = useState(null)

  function loadAll() {
    setLoading(true)
    Promise.all([episodeService.list(), contestantService.list()])
      .then(([e, c]) => {
        setEpisodes(e)
        setContestants(c)
        setForm((f) => ({ ...f, contestant_id: f.contestant_id || c[0]?.id || '' }))
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
      await episodeService.create({
        contestant_id: Number(form.contestant_id),
        broadcast_date: form.broadcast_date || undefined,
        video_url: form.video_url || undefined,
      })
      setForm((f) => ({ ...f, broadcast_date: '', video_url: '' }))
      loadAll()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this episode and its dishes/scores?')) return
    try {
      await episodeService.remove(id)
      loadAll()
    } catch (err) {
      setError(err.message)
    }
  }

  function startEdit(ep) {
    setEditingId(ep.id)
    setEditForm({ broadcast_date: ep.broadcast_date || '', video_url: ep.video_url || '' })
    setEditError(null)
  }

  async function handleUpdate(e, id) {
    e.preventDefault()
    setEditError(null)
    try {
      await episodeService.update(id, {
        broadcast_date: editForm.broadcast_date || null,
        video_url: editForm.video_url || null,
      })
      setEditingId(null)
      loadAll()
    } catch (err) {
      setEditError(err.message)
    }
  }

  if (loading) return <LoadingState label="Loading episodes…" />
  if (error) return <ErrorState message={error} />

  const contestantName = (id) => contestants.find((c) => c.id === id)?.name || `Contestant ${id}`

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Episodes</h1>
      <p className="text-sm text-ink/50 mb-8">One episode per contestant's cooking segment.</p>

      {episodes.length === 0 ? (
        <EmptyState title="No episodes yet" />
      ) : (
        <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50 mb-8">
          {episodes.map((e) =>
            editingId === e.id ? (
              <form
                key={e.id}
                onSubmit={(ev) => handleUpdate(ev, e.id)}
                className="flex flex-wrap items-end gap-3 px-5 py-3"
              >
                <div>
                  <label htmlFor={`edit-broadcast-date-${e.id}`} className="block text-xs font-medium text-ink/60 mb-1">Broadcast date</label>
                  <input
                    id={`edit-broadcast-date-${e.id}`}
                    type="date"
                    value={editForm.broadcast_date}
                    onChange={(ev) => setEditForm({ ...editForm, broadcast_date: ev.target.value })}
                    className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                  />
                </div>
                <div>
                  <label htmlFor={`edit-video-url-${e.id}`} className="block text-xs font-medium text-ink/60 mb-1">Video URL</label>
                  <input
                    id={`edit-video-url-${e.id}`}
                    value={editForm.video_url}
                    onChange={(ev) => setEditForm({ ...editForm, video_url: ev.target.value })}
                    className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-64"
                  />
                </div>
                {editError && <ErrorState message={editError} />}
                <button
                  type="submit"
                  className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => setEditingId(null)}
                  className="rounded-md border-2 border-ink/15 text-sm font-medium px-4 py-1.5 hover:bg-stone-200"
                >
                  Cancel
                </button>
              </form>
            ) : (
              <div key={e.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="font-medium text-ink">{contestantName(e.contestant_id)}</p>
                  <p className="text-xs text-ink/50">{e.broadcast_date || 'Broadcast date TBD'}</p>
                </div>
                <div className="flex items-center gap-3">
                  {e.video_url && (
                    <a
                      href={e.video_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm text-teal font-medium hover:underline"
                    >
                      Watch
                    </a>
                  )}
                  {isAuthenticated && (
                    <>
                      <button
                        onClick={() => startEdit(e)}
                        className="text-sm text-teal font-medium hover:underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(e.id)}
                        className="text-sm text-brick font-medium hover:underline"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
            ),
          )}
        </div>
      )}

      {isAuthenticated && (
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Add an episode</h2>
          <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-3">
            <div>
              <label htmlFor="create-contestant" className="block text-xs font-medium text-ink/60 mb-1">Contestant</label>
              <select
                id="create-contestant"
                value={form.contestant_id}
                onChange={(e) => setForm({ ...form, contestant_id: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              >
                {contestants.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="create-broadcast-date" className="block text-xs font-medium text-ink/60 mb-1">Broadcast date</label>
              <input
                id="create-broadcast-date"
                type="date"
                value={form.broadcast_date}
                onChange={(e) => setForm({ ...form, broadcast_date: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <div>
              <label htmlFor="create-video-url" className="block text-xs font-medium text-ink/60 mb-1">Video URL</label>
              <input
                id="create-video-url"
                value={form.video_url}
                onChange={(e) => setForm({ ...form, video_url: e.target.value })}
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-64"
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !contestants.length}
              className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
            >
              {submitting ? 'Adding…' : 'Add episode'}
            </button>
          </form>
          {!contestants.length && (
            <p className="text-xs text-ink/40 mt-2">Add a contestant first.</p>
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
