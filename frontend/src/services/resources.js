import api from './api'

/**
 * Builds a small CRUD client for a REST resource. All six of our resources
 * (seasons, weeks, contestants, episodes, dishes, scores) follow the exact
 * same GET/POST/PUT/DELETE shape, so generating the client once here avoids
 * six near-identical copies of the same four functions.
 */
function createResourceService(path) {
  return {
    list: (params = {}) => api.get(path, { params }).then((r) => r.data),
    get: (id) => api.get(`${path}/${id}`).then((r) => r.data),
    create: (data) => api.post(path, data).then((r) => r.data),
    update: (id, data) => api.put(`${path}/${id}`, data).then((r) => r.data),
    remove: (id) => api.delete(`${path}/${id}`).then((r) => r.data),
  }
}

export const seasonService = createResourceService('/seasons')
export const weekService = createResourceService('/weeks')
export const contestantService = createResourceService('/contestants')
export const episodeService = createResourceService('/episodes')
export const dishService = createResourceService('/dishes')
export const scoreService = createResourceService('/scores')

export const statisticsService = {
  get: () => api.get('/statistics').then((r) => r.data),
}

export const automationService = {
  status: () => api.get('/automation/status').then((r) => r.data),
  logs: () => api.get('/automation/logs').then((r) => r.data),
}
