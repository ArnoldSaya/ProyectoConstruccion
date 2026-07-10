<template>
  <div>
    <h1>Favoritos</h1>
    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>
    <div v-else-if="favorites.length === 0" class="empty-state">
      <span class="empty-state-icon">💙</span>
      <p>Aún no tienes favoritos.</p>
      <router-link to="/" class="btn-link">Explorar productos</router-link>
    </div>
    <div v-else>
      <div class="list-item" v-for="fav in favorites" :key="fav.id">
        <router-link :to="{ name: 'product-detail', params: { id: fav.mongo_product_id } }">
          {{ fav.productName || 'Ver producto' }}
        </router-link>
        <button class="btn-secondary" @click="remove(fav.id)">Quitar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getUserFavorites, removeFavorite } from '../services/favorites'
import { getProduct } from '../services/products'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const favorites = ref([])
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await getUserFavorites(auth.user.id, { per_page: 50 })
    const list = data.data || data
    favorites.value = list
    await Promise.all(list.map(async (fav) => {
      try {
        const { data: product } = await getProduct(fav.mongo_product_id)
        fav.productName = product.name_prod
      } catch (e) {
        fav.productName = null
      }
    }))
  } catch (e) {
    error.value = 'No se pudieron cargar tus favoritos.'
  } finally {
    loading.value = false
  }
}

async function remove(id) {
  try {
    await removeFavorite(id)
    await load()
  } catch (e) {
    error.value = 'No se pudo quitar el favorito.'
  }
}

onMounted(load)
</script>
