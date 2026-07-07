import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { Routes, Route } from 'react-router-dom'
import { renderWithRouter } from '../test/utils'
import ProtectedRoute from './ProtectedRoute'

const mockUseAuth = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

function renderProtected(route) {
  return renderWithRouter(
    <Routes>
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <p>Secret dashboard</p>
          </ProtectedRoute>
        }
      />
      <Route path="/login" element={<p>Login page</p>} />
    </Routes>,
    { route },
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading state while auth is still resolving', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, loading: true })
    renderProtected('/dashboard')
    expect(screen.getByText(/checking session/i)).toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, loading: false })
    renderProtected('/dashboard')
    expect(screen.getByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('Secret dashboard')).not.toBeInTheDocument()
  })

  it('renders the protected content when authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, loading: false })
    renderProtected('/dashboard')
    expect(screen.getByText('Secret dashboard')).toBeInTheDocument()
  })
})
