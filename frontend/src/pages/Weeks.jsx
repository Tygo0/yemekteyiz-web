import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { weekService, seasonService, contestantService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function Weeks() {
  const { isAuthenticated } = useAuth()
  const [weeks, setWeeks] = useState([])
  const [seasons, setSeasons] = useState([])
  const [contestants, setContestants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ season_id: '', week_number: '', youtube_url: '', notes: '' })
  const [newSeasonName, setNewSeasonName] = useState('')
  const [newSeasonYear, setNewSeasonYear] = useState(new Date().getFullYear())
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const [editingWeekId, setEditingWeekId] = useState(null)
  const [weekEditForm, setWeekEditForm] = useState({})
  const [weekEditError, setWeekEditError] = useState(null)

  const [editingSeasonId, setEditingSeasonId] = useState(null)
  const [seasonEditForm, setSeasonEditForm] = useState({ name: '', year: '' })
  const [seasonEditError, setSeasonEditError] = useState(null)

  function loadAll() {
    setLoading(true)
    Promise.all([weekService.list(), seasonService.list(), contestantService.list()])
      .then(([w, s, c]) => {
        setWeeks(w)
        setSeasons(s)
        setContestants(c)
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

  function startEditSeason(s) {
    setEditingSeasonId(s.id)
    setSeasonEditForm({ name: s.name, year: s.year })
    setSeasonEditError(null)
  }

  async function handleUpdateSeason(e, id) {
    e.preventDefault()
    setSeasonEditError(null)
    try {
      await seasonService.update(id, {
        name: seasonEditForm.name,
        year: Number(seasonEditForm.year),
      })
      setEditingSeasonId(null)
      loadAll()
    } catch (err) {
      setSeasonEditError(err.message)
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

  function startEditWeek(w) {
    setEditingWeekId(w.id)
    setWeekEditForm({
      week_number: w.week_number,
      air_date: w.air_date || '',
      youtube_url: w.youtube_url || '',
      notes: w.notes || '',
      winner_id: w.winner_id || '',
    })
    setWeekEditError(null)
  }

  function cancelEditWeek() {
    setEditingWeekId(null)
    setWeekEditError(null)
  }

  async function handleUpdateWeek(e, id) {
    e.preventDefault()
    setWeekEditError(null)
    try {
      await weekService.update(id, {
        week_number: Number(weekEditForm.week_number),
        air_date: weekEditForm.air_date || null,
        youtube_url: weekEditForm.youtube_url || null,
        notes: weekEditForm.notes || null,
        winner_id: weekEditForm.winner_id ? Number(weekEditForm.winner_id) : null,
      })
      setEditingWeekId(null)
      loadAll()
    } catch (err) {
      setWeekEditError(err.message)
    }
  }

  if (loading) return <LoadingState label="Loading weeks…" />
  if (error) return <ErrorState message={error} />

  const seasonName = (id) => seasons.find((s) => s.id === id)?.name || `Season ${id}`
  const contestantsForWeek = (weekId) => contestants.filter((c) => c.week_id === weekId)
  const contestantName = (id) => contestants.find((c) => c.id === id)?.name

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
          {weeks.map((w) =>
            editingWeekId === w.id ? (
              <form
                key={w.id}
                onSubmit={(e) => handleUpdateWeek(e, w.id)}
                className="px-5 py-4 space-y-3"
              >
                <div className="flex flex-wrap items-end gap-3">
                  <div>
                    <label className="block text-xs font-medium text-ink/60 mb-1">Week #</label>
                    <input
                      type="number"
                      min="1"
                      value={weekEditForm.week_number}
                      onChange={(e) =>
                        setWeekEditForm({ ...weekEditForm, week_number: e.target.value })
                      }
                      required
                      className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-20"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-ink/60 mb-1">Air date</label>
                    <input
                      type="date"
                      value={weekEditForm.air_date}
                      onChange={(e) =>
                        setWeekEditForm({ ...weekEditForm, air_date: e.target.value })
                      }
                      className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-ink/60 mb-1">YouTube URL</label>
                    <input
                      value={weekEditForm.youtube_url}
                      onChange={(e) =>
                        setWeekEditForm({ ...weekEditForm, youtube_url: e.target.value })
                      }
                      className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-56"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-ink/60 mb-1">Winner</label>
                    <select
                      value={weekEditForm.winner_id}
                      onChange={(e) =>
                        setWeekEditForm({ ...weekEditForm, winner_id: e.target.value })
                      }
                      className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                    >
                      <option value="">No winner set</option>
                      {contestantsForWeek(w.id).map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-ink/60 mb-1">Notes</label>
                  <textarea
                    value={weekEditForm.notes}
                    onChange={(e) => setWeekEditForm({ ...weekEditForm, notes: e.target.value })}
                    rows={2}
                    className="w-full rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
                  />
                </div>
                {weekEditError && <ErrorState message={weekEditError} />}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark"
                  >
                    Save changes
                  </button>
                  <button
                    type="button"
                    onClick={cancelEditWeek}
                    className="rounded-md border-2 border-ink/15 text-sm font-medium px-4 py-1.5 hover:bg-stone-200"
                  >
                    Cancel
                  </button>
                </div>
                {!contestantsForWeek(w.id).length && (
                  <p className="text-xs text-ink/40">
                    Add contestants to this week before you can set a winner.
                  </p>
                )}
              </form>
            ) : (
              <div key={w.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="font-medium text-ink">
                    {seasonName(w.season_id)} — Week {w.week_number}
                  </p>
                  <p className="text-xs text-ink/50">
                    {w.air_date || 'Air date TBD'}
                    {w.winner_id ? ` · Winner: ${contestantName(w.winner_id) || w.winner_id}` : ''}
                  </p>
                </div>
                {isAuthenticated && (
                  <div className="flex gap-3">
                    <button
                      onClick={() => startEditWeek(w)}
                      className="text-sm text-teal font-medium hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(w.id)}
                      className="text-sm text-brick font-medium hover:underline"
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
        <div className="space-y-6">
          <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
            <h2 className="font-display text-lg font-semibold text-ink mb-3">Seasons</h2>
            {seasons.length > 0 && (
              <div className="mb-4 space-y-2">
                {seasons.map((s) =>
                  editingSeasonId === s.id ? (
                    <form
                      key={s.id}
                      onSubmit={(e) => handleUpdateSeason(e, s.id)}
                      className="flex items-end gap-2"
                    >
                      <input
                        value={seasonEditForm.name}
                        onChange={(e) =>
                          setSeasonEditForm({ ...seasonEditForm, name: e.target.value })
                        }
                        required
                        className="rounded-md border-2 border-ink/15 px-3 py-1 bg-white text-sm"
                      />
                      <input
                        type="number"
                        value={seasonEditForm.year}
                        onChange={(e) =>
                          setSeasonEditForm({ ...seasonEditForm, year: e.target.value })
                        }
                        required
                        className="rounded-md border-2 border-ink/15 px-3 py-1 bg-white text-sm w-24"
                      />
                      <button
                        type="submit"
                        className="text-sm text-teal font-medium hover:underline"
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditingSeasonId(null)}
                        className="text-sm text-ink/50 hover:underline"
                      >
                        Cancel
                      </button>
                    </form>
                  ) : (
                    <div key={s.id} className="flex items-center justify-between text-sm">
                      <span className="text-ink/80">
                        {s.name} ({s.year})
                      </span>
                      <button
                        onClick={() => startEditSeason(s)}
                        className="text-teal font-medium hover:underline"
                      >
                        Edit
                      </button>
                    </div>
                  ),
                )}
              </div>
            )}
            {seasonEditError && <ErrorState message={seasonEditError} />}
            <form onSubmit={handleCreateSeason} className="flex flex-wrap items-end gap-3 border-t-2 border-ink/10 pt-4">
              <div>
                <label className="block text-xs font-medium text-ink/60 mb-1">New season name</label>
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

          <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
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
            {formError && (
              <div className="mt-3">
                <ErrorState message={formError} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
