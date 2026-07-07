import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from './AuthContext'
import { authService } from '../services/authService'

vi.mock('../services/authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    me: vi.fn(),
  },
}))

function Probe() {
  const { admin, isAuthenticated, loading, login, logout } = useAuth()
  return (
    <div>
      <p>loading: {String(loading)}</p>
      <p>authenticated: {String(isAuthenticated)}</p>
      <p>admin: {admin?.username ?? 'none'}</p>
      <button onClick={() => login('admin', 'pw')}>login</button>
      <button onClick={() => logout()}>logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('starts unauthenticated with no saved token', async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByText('loading: false')).toBeInTheDocument())
    expect(screen.getByText('authenticated: false')).toBeInTheDocument()
    expect(authService.me).not.toHaveBeenCalled()
  })

  it('restores the session from a saved token on mount', async () => {
    localStorage.setItem('yemekteyiz_token', 'saved-token')
    authService.me.mockResolvedValue({ id: 1, username: 'admin' })

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByText('authenticated: true')).toBeInTheDocument())
    expect(screen.getByText('admin: admin')).toBeInTheDocument()
  })

  it('drops a saved token that no longer validates', async () => {
    localStorage.setItem('yemekteyiz_token', 'stale-token')
    authService.me.mockRejectedValue(new Error('unauthorized'))

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByText('authenticated: false')).toBeInTheDocument())
    expect(localStorage.getItem('yemekteyiz_token')).toBeNull()
  })

  it('login stores the token and updates admin state', async () => {
    authService.login.mockResolvedValue({
      access_token: 'new-token',
      admin: { id: 2, username: 'newadmin' },
    })

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByText('loading: false')).toBeInTheDocument())

    await act(async () => {
      await userEvent.click(screen.getByText('login'))
    })

    expect(localStorage.getItem('yemekteyiz_token')).toBe('new-token')
    expect(screen.getByText('admin: newadmin')).toBeInTheDocument()
  })

  it('logout clears the token and admin state', async () => {
    localStorage.setItem('yemekteyiz_token', 'saved-token')
    authService.me.mockResolvedValue({ id: 1, username: 'admin' })
    authService.logout.mockResolvedValue({})

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByText('authenticated: true')).toBeInTheDocument())

    await act(async () => {
      await userEvent.click(screen.getByText('logout'))
    })

    expect(screen.getByText('authenticated: false')).toBeInTheDocument()
    expect(localStorage.getItem('yemekteyiz_token')).toBeNull()
  })
})
