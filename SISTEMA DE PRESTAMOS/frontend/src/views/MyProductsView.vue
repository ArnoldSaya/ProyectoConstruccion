<template>
  <div class="card">
    <h1>Mis productos</h1>
    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <p v-if="success" class="alert alert-success">{{ success }}</p>

    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>

    <p v-else-if="products.length === 0" class="empty-state">
      Aún no has publicado productos.
      <router-link to="/publicar" class="link">Publica tu primer producto</router-link>
    </p>

    <div v-else class="grid">
      <div v-for="p in products" :key="p._id" class="product-card">
        <img v-if="p.image_url" :src="p.image_url" :alt="p.name_prod" class="product-img" />
        <div v-else class="product-img placeholder">Sin imagen</div>
        <div class="product-body">
          <h3>{{ p.name_prod }}</h3>
          <p class="price">S/ {{ p.price }} / día</p>
          <p class="status" :class="p.status === 'disponible' ? 'ok' : 'busy'">{{ p.status }}</p>
          <button class="btn-danger" :disabled="deleting === p._id" @click="remove(p)">
            {{ deleting === p._id ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getProductsByOwner, deleteProduct } from '../services/products'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const products = ref([])
const loading = ref(true)
const deleting = ref(null)
const error = ref('')
const success = ref('')

async function load() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await getProductsByOwner(auth.user.id)
    products.value = data.data || []
  } catch (e) {
    error.value = 'No se pudieron cargar tus productos.'
  } finally {
    loading.value = false
  }
}

async function remove(p) {
  if (!confirm(`¿Eliminar "${p.name_prod}"?`)) return
  deleting.value = p._id
  error.value = ''
  success.value = ''
  try {
    await deleteProduct(p._id)
    success.value = 'Producto eliminado.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo eliminar el producto'
  } finally {
    deleting.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.product-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.product-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}
.product-img.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
  font-size: 13px;
}
.product-body {
  padding: 12px;
}
.product-body h3 {
  margin: 0 0 4px;
  font-size: 16px;
}
.price {
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px;
}
.status {
  font-size: 12px;
  margin: 0 0 10px;
}
.status.ok { color: #166534; }
.status.busy { color: #b45309; }
.btn-danger {
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  width: 100%;
}
.btn-danger:disabled { opacity: 0.6; }
.link { color: #2563eb; }
</style>
