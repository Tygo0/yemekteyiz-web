import { useEffect, useState } from 'react'
import { automationService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function AutomationLogs() {
  const [status, setStatus] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [triggerMessage, setTriggerMessage] = useState(null)

  function loadAll() {
    setLoading(true)
    Promise.all([automationService.status(), automationService.logs()])
      .then(([s, l]) => {
        setStatus(s)
        setLogs(l.logs)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(loadAll, [])

  async function handleTrigger() {
    setTriggerMessage(null)
    try {
      const result = await automationService.triggerImport()
      setTriggerMessage(result.message)
    } catch (err) {
      // A 501 here is expected until Phase 6 — surface the backend's own
      // message rather than treating it as a generic failure.
      setTriggerMessage(err.response?.data?.message || err.message)
    }
  }

  if (loading) return <LoadingState label="Checking automation status…" />
  if (error) return <ErrorState message={error} />

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Automation Logs</h1>
      <p className="text-sm text-ink/50 mb-8">
        Status of the AI pipeline that watches for new episodes.
      </p>

      <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6 mb-6 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-1">
            Current status
          </p>
          <p className="font-display text-xl font-semibold text-ink capitalize">{status.status}</p>
          {status.note && <p className="text-sm text-ink/50 mt-1">{status.note}</p>}
        </div>
        <button
          onClick={handleTrigger}
          className="rounded-md bg-teal text-stone-50 text-sm font-medium px-4 py-2 hover:bg-teal-dark"
        >
          Trigger import
        </button>
      </div>

      {triggerMessage && (
        <div className="mb-6 border-2 border-gold bg-gold-light text-ink rounded-lg px-4 py-3 text-sm">
          {triggerMessage}
        </div>
      )}

      <h2 className="font-display text-lg font-semibold text-ink mb-3">Recent runs</h2>
      {logs.length === 0 ? (
        <EmptyState
          title="No automation runs yet"
          hint="The AI pipeline (downloader, OCR, vision, speech) is built in Phase 6."
        />
      ) : (
        <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50">
          {logs.map((log, i) => (
            <div key={i} className="px-5 py-3 text-sm text-ink/70">
              {JSON.stringify(log)}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
