import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithRouter } from '../test/utils'
import AutomationLogs from './AutomationLogs'
import { automationService } from '../services/resources'

vi.mock('../services/resources', () => ({
  automationService: {
    status: vi.fn(),
    logs: vi.fn(),
  },
}))

describe('AutomationLogs', () => {
  it('renders status and log history, with no trigger-import button', async () => {
    automationService.status.mockResolvedValue({ status: 'idle', note: 'no scheduler running' })
    automationService.logs.mockResolvedValue({
      logs: [
        { id: 1, status: 'success', week_id: 1, contestant_count: 4, error_message: null, created_at: '2026-01-05T10:00:00Z' },
        { id: 2, status: 'failure', week_id: 999, contestant_count: 4, error_message: 'Week 999 not found', created_at: '2026-01-05T10:01:00Z' },
      ],
    })

    renderWithRouter(<AutomationLogs />)

    await waitFor(() => expect(screen.getByText('idle')).toBeInTheDocument())

    // Regression: this button always 400'd (posted no body against a real
    // endpoint that now requires structured data) — it was removed entirely.
    expect(screen.queryByRole('button', { name: /trigger import/i })).not.toBeInTheDocument()

    expect(screen.getByText('SUCCESS')).toBeInTheDocument()
    expect(screen.getByText('FAILURE')).toBeInTheDocument()
    expect(screen.getByText('Week 999 not found')).toBeInTheDocument()
  })

  it('shows an empty state when there are no runs yet', async () => {
    automationService.status.mockResolvedValue({ status: 'idle', note: null })
    automationService.logs.mockResolvedValue({ logs: [] })

    renderWithRouter(<AutomationLogs />)

    expect(await screen.findByText(/no automation runs yet/i)).toBeInTheDocument()
  })
})
