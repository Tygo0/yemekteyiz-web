import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ErrorState } from '../components/StatusStates'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(username, password)
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-8">
      <h1 className="font-display text-3xl font-semibold text-ink mb-1">Admin login</h1>
      <p className="text-sm text-ink/50 mb-6">Sign in to manage weeks, contestants, and scores.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-ink/70 mb-1">
            Username
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            className="w-full rounded-md border-2 border-ink/15 px-3 py-2 bg-stone-50 focus:border-teal outline-none"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-ink/70 mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            className="w-full rounded-md border-2 border-ink/15 px-3 py-2 bg-stone-50 focus:border-teal outline-none"
          />
        </div>

        {error && <ErrorState message={error} />}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-teal text-stone-50 font-medium py-2.5 hover:bg-teal-dark transition-colors disabled:opacity-50"
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
