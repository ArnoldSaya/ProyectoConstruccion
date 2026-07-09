import api from './api'

export function getUserFavorites(userId, params = {}) {
  return api.get(`/favorites/user/${userId}`, { params })
}
export function addFavorite(payload) {
  return api.post('/favorites', payload)
}
export function removeFavorite(id) {
  return api.delete(`/favorites/${id}`)
}
