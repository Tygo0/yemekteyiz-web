import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../test/utils'
import Episodes from './Episodes'
import { episodeService, contestantService } from '../services/resources'

vi.mock('../services/resources', () => ({
  episodeService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
  contestantService: {
    list: vi.fn(),
  },
}))

const mockUseAuth = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

const sampleContestants = [{ id: 1, name: 'Ayşe' }]
const sampleEpisodes = [{ id: 1, contestant_id: 1, broadcast_date: '2024-05-01' }]

describe('Episodes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    contestantService.list.mockResolvedValue(sampleContestants)
    episodeService.list.mockResolvedValue(sampleEpisodes)
  })

  it('does not show edit/delete/add controls to a logged-out visitor', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false })
    renderWithRouter(<Episodes />)

    expect(await screen.findByText('Ayşe')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
    expect(screen.queryByText(/add an episode/i)).not.toBeInTheDocument()
  })

  it('shows edit/delete/add controls to a logged-in admin', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    renderWithRouter(<Episodes />)

    expect(await screen.findByText('Ayşe', { selector: 'p' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByText(/add an episode/i)).toBeInTheDocument()
  })

  it('submits the add-episode form and reloads the list', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    episodeService.create.mockResolvedValue({ id: 2 })
    renderWithRouter(<Episodes />)

    await screen.findByText(/add an episode/i)

    await userEvent.type(screen.getByLabelText(/video url/i), 'https://example.com/video')
    await userEvent.click(screen.getByRole('button', { name: /add episode/i }))

    await waitFor(() =>
      expect(episodeService.create).toHaveBeenCalledWith(
        expect.objectContaining({ contestant_id: 1, video_url: 'https://example.com/video' }),
      ),
    )
    await waitFor(() => expect(episodeService.list).toHaveBeenCalledTimes(2))
  })

  it('deletes an episode after confirmation', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    episodeService.remove.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithRouter(<Episodes />)

    await screen.findByText('Ayşe', { selector: 'p' })
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(episodeService.remove).toHaveBeenCalledWith(1))
  })
})
