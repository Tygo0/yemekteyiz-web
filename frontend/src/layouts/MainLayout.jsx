import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const publicLinks = [
  { to: '/', label: 'Weeks' },
  { to: '/contestants', label: 'Contestants' },
  { to: '/episodes', label: 'Episodes' },
  { to: '/dishes', label: 'Dishes' },
  { to: '/scores', label: 'Scores' },
  { to: '/statistics', label: 'Statistics' },
]

const adminLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/automation', label: 'Automation Logs' },
]

function linkClasses({ isActive }) {
  return `text-sm font-medium px-3 py-2 rounded-md transition-colors ${
    isActive ? 'bg-teal text-stone-50' : 'text-ink/70 hover:text-ink hover:bg-stone-200'
  }`
}

export default function MainLayout({ children }) {
  const { isAuthenticated, admin, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b-2 border-ink/10 bg-stone-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-6">
          <NavLink to="/" className="font-display text-xl font-semibold text-ink shrink-0">
            Yemekteyiz
          </NavLink>

          <nav className="flex items-center gap-1 flex-wrap">
            {publicLinks.map((l) => (
              <NavLink key={l.to} to={l.to} className={linkClasses} end={l.to === '/'}>
                {l.label}
              </NavLink>
            ))}
            {isAuthenticated &&
              adminLinks.map((l) => (
                <NavLink key={l.to} to={l.to} className={linkClasses}>
                  {l.label}
                </NavLink>
              ))}
          </nav>

          <div className="shrink-0">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-ink/60">{admin?.username}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm font-medium px-3 py-2 rounded-md border-2 border-ink/15 hover:border-brick hover:text-brick transition-colors"
                >
                  Log out
                </button>
              </div>
            ) : (
              <NavLink
                to="/login"
                className="text-sm font-medium px-3 py-2 rounded-md bg-teal text-stone-50 hover:bg-teal-dark transition-colors"
              >
                Admin login
              </NavLink>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">{children}</main>

      <footer className="border-t-2 border-ink/10 py-6 text-center text-xs text-ink/40">
        Yemekteyiz — fan-built companion site. Not affiliated with the show's broadcaster.
      </footer>
    </div>
  )
}
