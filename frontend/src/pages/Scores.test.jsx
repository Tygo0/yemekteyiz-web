import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../test/utils'
import Scores from './Scores'
import { scoreService, episodeService, contestantService } from '../services/resources'

vi.mock('../services/resources', () => ({
  scoreService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
  episodeService: {
    list: vi.fn(),
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
const sampleEpisodes = [{ id: 1, contestant_id: 1 }]
const sampleScores = [{ id: 1, episode_id: 1, contestant_id: 1, judge_name: 'Zuhal', value: 8 }]

describe('Scores', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    contestantService.list.mockResolvedValue(sampleContestants)
    episodeService.list.mockResolvedValue(sampleEpisodes)
    scoreService.list.mockResolvedValue(sampleScores)
  })

  it('does not show edit/delete/add controls to a logged-out visitor', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false })
    renderWithRouter(<Scores />)

    expect(await screen.findByText(/by Zuhal/i)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
    expect(screen.queryByText(/add a score/i)).not.toBeInTheDocument()
  })

  it('shows edit/delete/add controls to a logged-in admin', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    renderWithRouter(<Scores />)

    expect(await screen.findByText(/by Zuhal/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByText(/add a score/i)).toBeInTheDocument()
  })

  it('submits the add-score form and reloads the list', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    scoreService.create.mockResolvedValue({ id: 2 })
    renderWithRouter(<Scores />)

    await screen.findByText(/add a score/i)

    await userEvent.type(screen.getByLabelText(/judge/i), 'Somer')
    await userEvent.click(screen.getByRole('button', { name: /add score/i }))

    await waitFor(() =>
      expect(scoreService.create).toHaveBeenCalledWith(
        expect.objectContaining({ episode_id: 1, contestant_id: 1, judge_name: 'Somer' }),
      ),
    )
    await waitFor(() => expect(scoreService.list).toHaveBeenCalledTimes(2))
  })

  it('deletes a score after confirmation', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    scoreService.remove.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithRouter(<Scores />)

    await screen.findByText(/by Zuhal/i)
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(scoreService.remove).toHaveBeenCalledWith(1))
  })
})
