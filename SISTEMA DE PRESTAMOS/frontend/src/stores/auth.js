import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    roles: (state) => state.user?.roles || [],
    hasRole: (state) => (role) => (state.user?.roles || []).includes(role),
    isCliente: (state) => (state.user?.roles || []).includes('cliente'),
    isRentador: (state) => (state.user?.roles || []).includes('rentador'),
    isAdmin: (state) => (state.user?.roles || []).includes('admin')
  },
  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this._setSession(data.token, data.refresh_token, data.user)
      return data.user
    },
    async register(payload) {
      const { data } = await api.post('/auth/register', payload)
      this._setSession(data.token, data.refresh_token, data.user)
      return data.user
    },
    async loginWithGoogleIdToken(idToken) {
      // Alternativa para cuando se use el SDK de Google Identity Services
      // en el cliente (boton renderizado por Google) en vez del redirect.
      const { data } = await api.post('/auth/google/token', { id_token: idToken })
      this._setSession(data.token, data.refresh_token, data.user)
      return data.user
    },
    async loginWithToken(token, refresh) {
      // Usado tras el flujo de redireccion: /api/auth/google/login ->
      // Google -> /api/auth/google/callback -> /oauth-callback?token=...&refresh=...
      this._setSession(token, refresh, null)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },
    async refresh() {
      if (!this.refreshToken) return false
      try {
        const { data } = await api.post('/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${this.refreshToken}` },
          _skipAuthRefresh: true
        })
        this.token = data.token
        localStorage.setItem('token', data.token)
        return true
      } catch (e) {
        this.logout()
        return false
      }
    },
    logout() {
      this.token = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },
    _setSession(token, refreshToken, user) {
      this.token = token
      this.refreshToken = refreshToken || null
      this.user = user
      localStorage.setItem('token', token)
      if (refreshToken) localStorage.setItem('refresh_token', refreshToken)
      if (user) localStorage.setItem('user', JSON.stringify(user))
    }
  }
})
