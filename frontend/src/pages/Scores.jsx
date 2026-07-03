import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { scoreService, episodeService, contestantService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'
import ScorePaddle from '../components/ScorePaddle'

export default function Scores() {
  const { isAuthenticated } = useAuth()
  const [scores, setScores] = useState([])
  const [episodes, setEpisodes] = useState([])
  const [contestants, setContestants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({ episode_id: '', judge_name: '', value: 8 })
  const [formError, setFormError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function loadAll() {
    setLoading(true)
    Promise.all([scoreService.list(), episodeService.list(), contestantService.list()])
      .then(([sc, ep, co]) => {
        setScores(sc)
        setEpisodes(ep)
        setContestants(co)
        setForm((f) => ({ ...f, episode_id: f.episode_id || ep[0]?.id || '' }))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(loadAll, [])

  const contestantName = (id) => contestants.find((c) => c.id === id)?.name || `Contestant ${id}`
  const episodeContestantName = (episodeId) => {
    const ep = episodes.find((e) => e.id === Number(episodeId))
    return ep ? contestantName(ep.contestant_id) : ''
  }

  async function handleCreate(e) {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      const episode = episodes.find((ep) => ep.id === Number(form.episode_id))
      await scoreService.create({
        episode_id: Number(form.episode_id),
        contestant_id: episode.contestant_id,
        judge_name: form.judge_name,
        value: Number(form.value),
      })
      setForm((f) => ({ ...f, judge_name: '', value: 8 }))
      loadAll()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingState label="Loading scores…" />
  if (error) return <ErrorState message={error} />

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Scores</h1>
      <p className="text-sm text-ink/50 mb-8">Every individual judge score — never just a total.</p>

      {scores.length === 0 ? (
        <EmptyState title="No scores recorded yet" />
      ) : (
        <div className="flex flex-wrap gap-4 mb-10">
          {scores.map((s) => (
            <div
              key={s.id}
              className="border-2 border-ink/10 bg-stone-50 rounded-lg p-4 flex items-center gap-3"
            >
              <ScorePaddle value={s.value} size="sm" />
              <div>
                <p className="font-medium text-ink text-sm">{contestantName(s.contestant_id)}</p>
                <p className="text-xs text-ink/50">by {s.judge_name}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {isAuthenticated && (
        <div className="border-2 border-ink/10 rounded-lg bg-stone-50 p-5">
          <h2 className="font-display text-lg font-semibold text-ink mb-3">Add a score</h2>
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
                    {episodeContestantName(e.id)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Judge</label>
              <input
                value={form.judge_name}
                onChange={(e) => setForm({ ...form, judge_name: e.target.value })}
                placeholder="Zuhal"
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/60 mb-1">Score (1-10)</label>
              <input
                type="number"
                min="1"
                max="10"
                value={form.value}
                onChange={(e) => setForm({ ...form, value: e.target.value })}
                required
                className="rounded-md border-2 border-ink/15 px-3 py-1.5 bg-white text-sm w-20"
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !episodes.length}
              className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-1.5 hover:bg-teal-dark disabled:opacity-50"
            >
              {submitting ? 'Adding…' : 'Add score'}
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
