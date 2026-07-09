<template>
  <div>
    <div class="page-header">
      <h1>Productos disponibles</h1>
      <p class="page-subtitle">Encuentra lo que necesitas y resérvalo en minutos.</p>
    </div>

    <div class="filters">
      <select v-model="selectedCategory" @change="loadProducts(1)">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name_cat }}</option>
      </select>
    </div>

    <p v-if="error" class="alert alert-error">{{ error }}</p>

    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>
    <div v-else-if="products.length === 0" class="empty-state">
      <span class="empty-state-icon">📤</span>
      <p>No hay productos para mostrar.</p>
    </div>
    <div class="grid" v-else>
      <ProductCard v-for="product in products" :key="product._id" :product="product" />
    </div>

    <div class="pagination" v-if="pages > 1">
      <button :disabled="page <= 1" @click="loadProducts(page - 1)">← Anterior</button>
      <span>Página {{ page }} de {{ pages }}</span>
      <button :disabled="page >= pages" @click="loadProducts(page + 1)">Siguiente →</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import { getCategories, getProducts } from '../services/products'

const categories = ref([])
const products = ref([])
const selectedCategory = ref('')
const page = ref(1)
const pages = ref(1)
const loading = ref(false)
const error = ref('')

async function loadCategories() {
  try {
    const { data } = await getCategories({ per_page: 50 })
    categories.value = data.data
  } catch (e) {
    // No bloqueamos la vista si fallan las categorias
  }
}

async function loadProducts(targetPage = 1) {
  loading.value = true
  error.value = ''
  try {
    const params = { page: targetPage, per_page: 12 }
    if (selectedCategory.value) params.category_id = selectedCategory.value
    const { data } = await getProducts(params)
    products.value = data.data
    page.value = data.page
    pages.value = data.pages || 1
  } catch (e) {
    error.value = 'No se pudieron cargar los productos. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadProducts(1)
})
</script>
