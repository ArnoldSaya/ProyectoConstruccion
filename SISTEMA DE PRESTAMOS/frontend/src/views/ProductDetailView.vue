<template>
  <div>
    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>

    <div v-else-if="product" class="product-detail">
      <div class="card product-detail-main">
        <div class="product-detail-img-wrap" v-if="product.image_url">
          <img :src="product.image_url" :alt="product.name_prod" class="product-detail-img" />
        </div>
        <span class="badge" :class="product.status">{{ product.status }}</span>
        <h1>{{ product.name_prod }}</h1>
        <p class="price price-lg">S/ {{ formatPrice(product.price) }}</p>
        <p>{{ product.description }}</p>
        <p v-if="product.details"><strong>Detalles:</strong> {{ product.details }}</p>
      </div>

      <div class="card product-detail-side" v-if="auth.isAuthenticated">
        <h2>Reservar</h2>
        <form @submit.prevent="handleReserve">
          <label>Fecha de inicio
            <input v-model="reservation.start_date" type="date" required />
          </label>
          <label>Fecha de fin
            <input v-model="reservation.end_date" type="date" required />
          </label>
          <label>Precio total (S/)
            <input v-model="reservation.total_price" type="number" step="0.01" required />
          </label>
          <p v-if="error" class="alert alert-error">{{ error }}</p>
          <p v-if="success" class="alert alert-success">¡Reserva creada!</p>
          <button type="submit" :disabled="loadingReserve">{{ loadingReserve ? 'Reservando...' : 'Reservar' }}</button>
        </form>
      </div>
      <p v-else class="card product-detail-side">
        <router-link to="/login">Inicia sesión</router-link> para reservar este producto.
      </p>
    </div>

    <div v-else class="empty-state">
      <span class="empty-state-icon">🔍</span>
      <p>Producto no encontrado.</p>
      <router-link to="/" class="btn-link">Volver al inicio</router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getProduct } from '../services/products'
import { createReservation } from '../services/reservations'
import { useAuthStore } from '../stores/auth'

const props = defineProps({ id: { type: String, required: true } })

const auth = useAuthStore()
const product = ref(null)
const loading = ref(true)
const error = ref('')
const success = ref(false)
const loadingReserve = ref(false)

const reservation = reactive({ start_date: '', end_date: '', total_price: '' })

function formatPrice(value) {
  const n = Number(value)
  return Number.isNaN(n) ? value : n.toFixed(2)
}

async function loadProduct() {
  loading.value = true
  try {
    const { data } = await getProduct(props.id)
    product.value = data
  } catch (e) {
    product.value = null
  } finally {
    loading.value = false
  }
}

async function handleReserve() {
  error.value = ''
  success.value = false
  loadingReserve.value = true
  try {
    await createReservation({
      renter_user_id: auth.user.id,
      mongo_product_id: props.id,
      start_date: reservation.start_date,
      end_date: reservation.end_date,
      total_price: reservation.total_price
    })
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo crear la reserva'
  } finally {
    loadingReserve.value = false
  }
}

onMounted(loadProduct)
</script>
