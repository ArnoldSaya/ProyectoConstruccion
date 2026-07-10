import api from './api'

export function getUser(id) {
  return api.get(`/users/${id}`)
}
export function updateUser(id, payload) {
  return api.put(`/users/${id}`, payload)
}
export function becomeRentador() {
  return api.post('/user-roles/self', { role_name: 'rentador' })
}
export function removeRoleSelf(roleName) {
  return api.delete('/user-roles/self', { data: { role_name: roleName } })
}
