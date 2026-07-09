import api from './api'

export function getUserLocations(userId, params = {}) {
  return api.get(`/locations/user/${userId}`, { params })
}
export function createLocation(payload) {
  return api.post('/locations', payload)
}
export function deleteLocation(id) {
  return api.delete(`/locations/${id}`)
}
