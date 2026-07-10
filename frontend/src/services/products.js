import api from './api'

function dedupeCategories(list) {
  const seen = new Set()
  const unique = []
  for (const c of list || []) {
    const key = (c.name_cat || '').trim().toLowerCase()
    if (!seen.has(key)) {
      seen.add(key)
      unique.push(c)
    }
  }
  return unique
}

export async function getCategories(params = {}) {
  const res = await api.get('/categories', { params })
  const list = Array.isArray(res?.data?.data) ? res.data.data : []
  const unique = dedupeCategories(list)
  res.data.data = unique
  res.data.total = unique.length
  res.data.pages = 1
  return res
}

export function createCategory(payload) {
  return api.post('/categories', payload)
}

export function getProducts(params = {}) {
  return api.get('/products', { params })
}

export function getProduct(id) {
  return api.get(`/products/${id}`)
}

export function getProductsByOwner(ownerId, params = {}) {
  return api.get(`/products/owner/${ownerId}`, { params })
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}`)
}

export function updateProduct(id, payload) {
  return api.put(`/products/${id}`, payload)
}

export function createProduct(payload) {
  return api.post('/products', payload)
}

export function uploadProductImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/uploads', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
