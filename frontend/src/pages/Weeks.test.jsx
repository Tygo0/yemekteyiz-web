import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../test/utils'
import Weeks from './Weeks'
import { weekService, seasonService, contestantService } from '../services/resources'

vi.mock('../services/resources', () => ({
  weekService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
  seasonService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  contestantService: {
    list: vi.fn(),
  },
}))

const mockUseAuth = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

const sampleSeasons = [{ id: 1, name: 'Season 1', year: 2024 }]
const sampleWeeks = [{ id: 1, season_id: 1, week_number: 15, air_date: '2024-05-01' }]
const sampleContestants = []

describe('Weeks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    seasonService.list.mockResolvedValue(sampleSeasons)
    weekService.list.mockResolvedValue(sampleWeeks)
    contestantService.list.mockResolvedValue(sampleContestants)
  })

  it('does not show edit/delete/add controls to a logged-out visitor', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false })
    renderWithRouter(<Weeks />)

    expect(await screen.findByText(/Season 1 — Week 15/i)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
    expect(screen.queryByText(/add a week/i)).not.toBeInTheDocument()
  })

  it('shows edit/delete/add controls to a logged-in admin', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    renderWithRouter(<Weeks />)

    expect(await screen.findByText(/Season 1 — Week 15/i)).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /edit/i }).length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByText(/add a week/i)).toBeInTheDocument()
  })

  it('submits the add-week form and reloads the list', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    weekService.create.mockResolvedValue({ id: 2 })
    renderWithRouter(<Weeks />)

    await screen.findByText(/add a week/i)

    await userEvent.clear(screen.getByLabelText(/^week #$/i))
    await userEvent.type(screen.getByLabelText(/^week #$/i), '16')
    await userEvent.click(screen.getByRole('button', { name: /add week/i }))

    await waitFor(() =>
      expect(weekService.create).toHaveBeenCalledWith(
        expect.objectContaining({ season_id: 1, week_number: 16 }),
      ),
    )
    await waitFor(() => expect(weekService.list).toHaveBeenCalledTimes(2))
  })

  it('deletes a week after confirmation', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    weekService.remove.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithRouter(<Weeks />)

    await screen.findByText(/Season 1 — Week 15/i)
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(weekService.remove).toHaveBeenCalledWith(1))
  })
})
