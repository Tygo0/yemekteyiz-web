import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithRouter } from '../test/utils'
import Dishes from './Dishes'
import { dishService, episodeService, contestantService } from '../services/resources'

vi.mock('../services/resources', () => ({
  dishService: {
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
const sampleDishes = [{ id: 1, episode_id: 1, name: 'Mercimek Çorbası', category: 'soup' }]

describe('Dishes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    contestantService.list.mockResolvedValue(sampleContestants)
    episodeService.list.mockResolvedValue(sampleEpisodes)
    dishService.list.mockResolvedValue(sampleDishes)
  })

  it('does not show edit/delete/add controls to a logged-out visitor', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false })
    renderWithRouter(<Dishes />)

    expect(await screen.findByText('Mercimek Çorbası')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
    expect(screen.queryByText(/add a dish/i)).not.toBeInTheDocument()
  })

  it('shows edit/delete/add controls to a logged-in admin', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    renderWithRouter(<Dishes />)

    expect(await screen.findByText('Mercimek Çorbası')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByText(/add a dish/i)).toBeInTheDocument()
  })

  it('submits the add-dish form and reloads the list', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    dishService.create.mockResolvedValue({ id: 2 })
    renderWithRouter(<Dishes />)

    await screen.findByText(/add a dish/i)

    await userEvent.type(screen.getByLabelText(/dish name/i), 'Baklava')
    await userEvent.click(screen.getByRole('button', { name: /add dish/i }))

    await waitFor(() =>
      expect(dishService.create).toHaveBeenCalledWith(
        expect.objectContaining({ episode_id: 1, name: 'Baklava' }),
      ),
    )
    await waitFor(() => expect(dishService.list).toHaveBeenCalledTimes(2))
  })

  it('deletes a dish after confirmation', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true })
    dishService.remove.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithRouter(<Dishes />)

    await screen.findByText('Mercimek Çorbası')
    await userEvent.click(screen.getByRole('button', { name: /delete/i }))

    await waitFor(() => expect(dishService.remove).toHaveBeenCalledWith(1))
  })
})
