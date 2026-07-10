import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'
})

let isRefreshing = false
let pending = []

api.interceptors.request.use((config) => {
  // No sobreescribir si el llamador ya fijo un header (p.ej. /auth/refresh
  // envia el refresh token en vez del access token).
  if (!config.headers.Authorization) {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry && !original._skipAuthRefresh) {
      original._retry = true
      const { useAuthStore } = await import('../stores/auth')
      const auth = useAuthStore()
      if (!isRefreshing) {
        isRefreshing = true
        const ok = await auth.refresh()
        isRefreshing = false
        if (ok) {
          pending.forEach((cb) => cb())
          pending = []
        } else {
          pending = []
          return Promise.reject(error)
        }
      }
      return new Promise((resolve) => {
        pending.push(() => {
          original.headers.Authorization = `Bearer ${localStorage.getItem('token')}`
          resolve(api(original))
        })
      })
    }
    return Promise.reject(error)
  }
)

console.log("API URL:", import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'
});

export default api
