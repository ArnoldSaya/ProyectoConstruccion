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
            <div class="date-selects">
              <select v-model="startDay" required>
                <option value="">Día</option>
                <option v-for="d in days" :key="d" :value="String(d).padStart(2, '0')">{{ d }}</option>
              </select>
              <select v-model="startMonth" required>
                <option value="">Mes</option>
                <option v-for="(m, i) in months" :key="i" :value="String(i + 1).padStart(2, '0')">{{ m }}</option>
              </select>
              <select v-model="startYear" required>
                <option value="">Año</option>
                <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </label>
          <label>Fecha de fin
            <div class="date-selects">
              <select v-model="endDay" required>
                <option value="">Día</option>
                <option v-for="d in days" :key="d" :value="String(d).padStart(2, '0')">{{ d }}</option>
              </select>
              <select v-model="endMonth" required>
                <option value="">Mes</option>
                <option v-for="(m, i) in months" :key="i" :value="String(i + 1).padStart(2, '0')">{{ m }}</option>
              </select>
              <select v-model="endYear" required>
                <option value="">Año</option>
                <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </label>
          <label>Precio total (S/)
            <input v-model="reservation.total_price" type="number" step="0.01" required />
          </label>
          <p v-if="error" class="alert alert-error">{{ error }}</p>
          <p v-if="success" class="alert alert-success">¡Reserva creada!</p>
          <button type="submit" :disabled="loadingReserve || !validStartDate || !validEndDate">{{ loadingReserve ? 'Reservando...' : 'Reservar' }}</button>
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
import { onMounted, reactive, ref, computed, watch } from 'vue'
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

const startDay = ref('')
const startMonth = ref('')
const startYear = ref('')
const endDay = ref('')
const endMonth = ref('')
const endYear = ref('')
const totalPrice = ref('')

const currentYear = new Date().getFullYear()
const years = computed(() => Array.from({ length: 10 }, (_, i) => currentYear + i))
const months = [
  { value: '01', label: 'Enero' }, { value: '02', label: 'Febrero' }, { value: '03', label: 'Marzo' },
  { value: '04', label: 'Abril' }, { value: '05', label: 'Mayo' }, { value: '06', label: 'Junio' },
  { value: '07', label: 'Julio' }, { value: '08', label: 'Agosto' }, { value: '09', label: 'Septiembre' },
  { value: '10', label: 'Octubre' }, { value: '11', label: 'Noviembre' }, { value: '12', label: 'Diciembre' }
]

function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate()
}
const startDays = computed(() => {
  if (!startYear.value || !startMonth.value) return []
  const days = daysInMonth(+startYear.value, +startMonth.value)
  return Array.from({ length: days }, (_, i) => String(i + 1).padStart(2, '0'))
})
const endDays = computed(() => {
  if (!endYear.value || !endMonth.value) return []
  const days = daysInMonth(+endYear.value, +endMonth.value)
  return Array.from({ length: days }, (_, i) => String(i + 1).padStart(2, '0'))
})

function buildDate(day, month, year) {
  return day && month && year ? `${year}-${month}-${day}` : ''
}

const validStartDate = computed(() => !!buildDate(startDay.value, startMonth.value, startYear.value))
const validEndDate = computed(() => !!buildDate(endDay.value, endMonth.value, endYear.value))

watch([startDay, startMonth, startYear], () => {
  if (startDays.value.length && !startDays.value.includes(startDay.value)) startDay.value = ''
})
watch([endDay, endMonth, endYear], () => {
  if (endDays.value.length && !endDays.value.includes(endDay.value)) endDay.value = ''
})

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
    const start_date = buildDate(startDay.value, startMonth.value, startYear.value)
    const end_date = buildDate(endDay.value, endMonth.value, endYear.value)
    await createReservation({
      renter_user_id: auth.user.id,
      mongo_product_id: props.id,
      start_date,
      end_date,
      total_price: totalPrice.value
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

<style scoped>
.date-selects {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.date-selects select {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: white;
  font-size: 14px;
}
.date-selects select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
</style>
