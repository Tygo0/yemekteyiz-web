import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// Most pages only need routing context, not full auth state — tests that
// care about auth mock '../hooks/useAuth' directly instead of going through
// a real AuthProvider, so they can control isAuthenticated without faking
// a whole login flow.
export function renderWithRouter(ui, { route = '/' } = {}) {
  return render(<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>)
}
