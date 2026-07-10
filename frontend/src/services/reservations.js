import api from './api'

export function getReservations(params = {}) {
  return api.get('/reservations', { params })
}
export function getReservation(id) {
  return api.get(`/reservations/${id}`)
}
export function getUserReservations(userId, params = {}) {
  return api.get(`/reservations/user/${userId}`, { params })
}
export function createReservation(payload) {
  return api.post('/reservations', payload)
}
export function updateReservation(id, payload) {
  return api.put(`/reservations/${id}`, payload)
}
export function deleteReservation(id) {
  return api.delete(`/reservations/${id}`)
}
