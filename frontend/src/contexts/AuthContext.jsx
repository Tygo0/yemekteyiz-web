import { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext(null)

const TOKEN_KEY = 'yemekteyiz_token'

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)

  // On first load, if a token is already saved, verify it's still valid by
  // fetching the current admin. This is what lets a page refresh keep you
  // logged in instead of bouncing back to the login screen every time.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    authService
      .me()
      .then(setAdmin)
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false))
  }, [])

  async function login(username, password) {
    const result = await authService.login(username, password)
    localStorage.setItem(TOKEN_KEY, result.access_token)
    setAdmin(result.admin)
    return result.admin
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setAdmin(null)
    authService.logout().catch(() => {})
  }

  const value = {
    admin,
    isAuthenticated: !!admin,
    loading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
