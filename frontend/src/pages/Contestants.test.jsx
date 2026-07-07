import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../test/utils'
import Contestants from './Contestants'
import { contestantService, weekService } from '../services/resources'

vi.mock('../services/resources', () => ({
  contestantService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
  weekService: {
    list: vi.fn(),
  },
}))

const mockUseAuth = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

const sampleWeeks = [{ id: 1, week_number: 15 }]
const sampleContestants = [
  { id: 1, week_id: 1, name: 'Ayşe', profession: 'Chef', city: 'Istanbul' },
]

describe('Contestants', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    weekService.list.mockResolvedValue(sampleWeeks)
    contestantService.list.mockResolvedValue(sampleContestants)
  })

  it('does not show edit/delete/add controls to a logged-out visitor', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false })
    renderWithRouter(<Contestants />)

    expect(await screen.findByText('Ayşe')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument()
    expect(screen.queryByText(/add a contestant/i)).not.toBeInTheDocument()
  })

  it('shows edit/delete/add controls to a logged-in admin', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    renderWithRouter(<Contestants />)

    expect(await screen.findByText('Ayşe')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByText(/add a contestant/i)).toBeInTheDocument()
  })

  it('submits the add-contestant form and reloads the list', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    contestantService.create.mockResolvedValue({ id: 2 })
    renderWithRouter(<Contestants />)

    await screen.findByText(/add a contestant/i)

    await userEvent.type(screen.getByLabelText(/^name$/i), 'Mehmet')
    await userEvent.click(screen.getByRole('button', { name: /add contestant/i }))

    await waitFor(() =>
      expect(contestantService.create).toHaveBeenCalledWith(
        expect.objectContaining({ week_id: 1, name: 'Mehmet' }),
      ),
    )
    // loadAll() re-runs after a successful create
    await waitFor(() => expect(contestantService.list).toHaveBeenCalledTimes(2))
  })

  it('deletes a contestant after confirmation', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    contestantService.remove.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithRouter(<Contestants />)

    await screen.findByText('Ayşe')
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(contestantService.remove).toHaveBeenCalledWith(1))
  })

  it('does not delete when the confirmation is dismissed', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    renderWithRouter(<Contestants />)

    await screen.findByText('Ayşe')
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    expect(contestantService.remove).not.toHaveBeenCalled()
  })
})
