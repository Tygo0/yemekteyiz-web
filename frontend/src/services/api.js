import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
})

// Attach the JWT (if we have one) to every outgoing request, so individual
// service functions never need to think about auth headers.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('yemekteyiz_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalize error shape so components can just read err.message.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.error || error.message || 'Something went wrong'
    return Promise.reject({ ...error, message })
  },
)

export default api
