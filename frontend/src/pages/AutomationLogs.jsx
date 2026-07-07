import { useEffect, useState } from 'react'
import { automationService } from '../services/resources'
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates'

export default function AutomationLogs() {
  const [status, setStatus] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  if (loading) return <LoadingState label="Checking automation status…" />
  if (error) return <ErrorState message={error} />

  return (
    <div>
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Automation Logs</h1>
      <p className="text-sm text-ink/50 mb-8">
        Status of the AI pipeline that watches for new episodes. Imports are
        triggered by running the automation pipeline itself (see
        automation/cli.py) against a specific video and week — not from this
        page — since each run depends on real AI-extracted data.
      </p>

      <div className="border-2 border-ink/10 bg-stone-50 rounded-lg p-6 mb-6">
        <p className="text-xs font-medium text-ink/50 uppercase tracking-wide mb-1">
          Current status
        </p>
        <p className="font-display text-xl font-semibold text-ink capitalize">{status.status}</p>
        {status.note && <p className="text-sm text-ink/50 mt-1">{status.note}</p>}
      </div>

      <h2 className="font-display text-lg font-semibold text-ink mb-3">Recent runs</h2>
      {logs.length === 0 ? (
        <EmptyState
          title="No automation runs yet"
          hint="Runs will appear here once the AI pipeline has imported an episode."
        />
      ) : (
        <div className="border-2 border-ink/10 rounded-lg divide-y-2 divide-ink/10 bg-stone-50">
          {logs.map((log) => (
            <div key={log.id} className="px-5 py-3 text-sm text-ink/70 flex items-center justify-between gap-4">
              <div>
                <span
                  className={`inline-block text-xs font-medium tracking-wide rounded px-2 py-0.5 mr-3 ${
                    log.status === 'success'
                      ? 'bg-teal/10 text-teal-dark'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {/* CSS text-transform: uppercase is locale-sensitive — in
                      Turkish browsers it turns "failure" into "FAİLURE"
                      (dotted İ). Uppercasing the literal string in JS instead
                      avoids that entirely. */}
                  {log.status === 'success' ? 'SUCCESS' : 'FAILURE'}
                </span>
                Week {log.week_id} — {log.contestant_count} contestant(s)
                {log.error_message && (
                  <span className="block text-ink/50 mt-1">{log.error_message}</span>
                )}
              </div>
              <span className="text-xs text-ink/40 whitespace-nowrap">
                {new Date(log.created_at).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
