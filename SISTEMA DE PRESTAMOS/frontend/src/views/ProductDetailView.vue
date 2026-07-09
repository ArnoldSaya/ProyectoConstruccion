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
        <div v-if="product.details" class="product-details">
          <h4>Detalles</h4>
          <ul>
            <li v-for="(value, key) in parsedDetails" :key="key">
              <strong>{{ formatKey(key) }}:</strong> {{ value }}
            </li>
          </ul>
        </div>
      </div>

      <div class="card product-detail-side" v-if="auth.isAuthenticated">
        <h2 v-if="!reservationCreated">Reservar</h2>
        <h2 v-else>Reserva confirmada — Factura</h2>

        <form v-if="!reservationCreated" @submit.prevent="handleReserve">
          <label>Fecha de inicio
            <div class="date-selects">
              <select v-model="startDay" required>
                <option value="">Día</option>
                <option v-for="d in startDays" :key="d" :value="d">{{ d }}</option>
              </select>
              <select v-model="startMonth" required>
                <option value="">Mes</option>
                <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
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
                <option v-for="d in endDays" :key="d" :value="d">{{ d }}</option>
              </select>
              <select v-model="endMonth" required>
                <option value="">Mes</option>
                <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
              <select v-model="endYear" required>
                <option value="">Año</option>
                <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </label>

          <div class="price-summary">
            <div class="price-row"><span>Precio/día</span><span>S/ {{ formatPrice(product.price) }}</span></div>
            <div class="price-row"><span>Días</span><span>{{ daysDiff }}</span></div>
            <div class="price-row"><span>Subtotal</span><span>S/ {{ formatPrice(computedTotal) }}</span></div>
            <div class="price-row fee"><span>Comisión plataforma ({{ (COMMISSION_RATE * 100).toFixed(0) }}%)</span><span>− S/ {{ formatPrice(platformFee) }}</span></div>
            <div class="price-row earnings"><span>Gana el rentador</span><span>S/ {{ formatPrice(ownerEarnings) }}</span></div>
            <div class="price-row total"><span>Total a pagar</span><span>S/ {{ formatPrice(computedTotal) }}</span></div>
          </div>

          <p v-if="error" class="alert alert-error">{{ error }}</p>
          <button type="submit" :disabled="loadingReserve || !validStartDate || !validEndDate || daysDiff < 1">
            {{ loadingReserve ? 'Reservando...' : 'Reservar' }}
          </button>
        </form>

        <div v-else class="invoice">
          <div class="invoice-header">
            <span class="invoice-code">INV-{{ reservationId }}</span>
            <span class="invoice-date">{{ formatDate(new Date().toISOString()) }}</span>
          </div>
          <div class="invoice-row"><strong>Producto:</strong> {{ product.name_prod }}</div>
          <div class="invoice-row"><strong>Fecha inicio:</strong> {{ formatDate(startDateObj) }}</div>
          <div class="invoice-row"><strong>Fecha fin:</strong> {{ formatDate(endDateObj) }}</div>
          <div class="invoice-row"><strong>Días:</strong> {{ daysDiff }}</div>
          <div class="invoice-row"><strong>Precio/día:</strong> S/ {{ formatPrice(product.price) }}</div>
          <div class="invoice-row"><strong>Subtotal:</strong> S/ {{ formatPrice(computedTotal) }}</div>
          <div class="invoice-row fee"><strong>Comisión plataforma ({{ (COMMISSION_RATE * 100).toFixed(0) }}%):</strong> − S/ {{ formatPrice(platformFee) }}</div>
          <div class="invoice-row earnings"><strong>Gana el rentador:</strong> S/ {{ formatPrice(ownerEarnings) }}</div>
          <div class="invoice-row total"><strong>Total pagado:</strong> S/ {{ formatPrice(computedTotal) }}</div>
          <div class="invoice-row"><strong>Estado:</strong> <span class="badge confirmed">Confirmada</span></div>
          <button @click="newReservation" class="btn-secondary">Nueva reserva</button>
        </div>
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

// Valores por defecto: hoy + 1 día
const today = new Date()
const tomorrow = new Date(today)
tomorrow.setDate(tomorrow.getDate() + 1)

function pad2(n) { return String(n).padStart(2, '0') }

startDay.value = pad2(today.getDate())
startMonth.value = pad2(today.getMonth() + 1)
startYear.value = String(today.getFullYear())
endDay.value = pad2(tomorrow.getDate())
endMonth.value = pad2(tomorrow.getMonth() + 1)
endYear.value = String(tomorrow.getFullYear())

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

const startDateObj = computed(() => buildDate(startDay.value, startMonth.value, startYear.value))
const endDateObj = computed(() => buildDate(endDay.value, endMonth.value, endYear.value))

const daysDiff = computed(() => {
  if (!startDateObj.value || !endDateObj.value) return 0
  const start = new Date(startDateObj.value)
  const end = new Date(endDateObj.value)
  const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
})

const computedTotal = computed(() => {
  if (!product.value || daysDiff.value < 1) return 0
  return product.value.price * daysDiff.value
})

const COMMISSION_RATE = 0.10 // 10 % para la plataforma
const platformFee = computed(() => +(computedTotal.value * COMMISSION_RATE).toFixed(2))
const ownerEarnings = computed(() => +(computedTotal.value - platformFee.value).toFixed(2))

const parsedDetails = computed(() => {
  if (!product.value?.details) return {}
  const raw = product.value.details
  if (typeof raw === 'object') return raw
  try {
    return JSON.parse(raw)
  } catch {
    // Intenta limpiar el string (comillas simples, espacios, etc.)
    try {
      return JSON.parse(raw.replace(/'/g, '"'))
    } catch {
      return { info: raw }
    }
  }
})

function formatKey(key) {
  return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
}

const reservationCreated = ref(false)
const reservationId = ref('')

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}/${month}/${year}`
}

function newReservation() {
  reservationCreated.value = false
  reservationId.value = ''
  error.value = ''
}

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
  loadingReserve.value = true
  try {
    const start_date = buildDate(startDay.value, startMonth.value, startYear.value)
    const end_date = buildDate(endDay.value, endMonth.value, endYear.value)
    const response = await createReservation({
      renter_user_id: auth.user.id,
      mongo_product_id: props.id,
      start_date,
      end_date,
      total_price: computedTotal.value
    })
    reservationId.value = response.data.id
    reservationCreated.value = true
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

.price-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  margin: 12px 0;
}
.price-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
}
.price-row.total {
  border-top: 1px solid #e2e8f0;
  margin-top: 4px;
  padding-top: 10px;
  font-weight: 700;
  font-size: 15px;
}
.price-row.fee {
  color: #ef4444;
  font-size: 13px;
}
.price-row.earnings {
  color: #16a34a;
  font-weight: 600;
  font-size: 13px;
}
.price-output {
  display: block;
  margin-top: 4px;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.invoice {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
}
.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 12px;
  margin-bottom: 12px;
}
.invoice-code {
  font-family: monospace;
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}
.invoice-date { font-size: 13px; color: #64748b; }
.invoice-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  border-bottom: 1px solid #f1f5f9;
}
.invoice-row:last-child { border-bottom: none; }
.invoice-row.total {
  border-top: 2px solid #e2e8f0;
  margin-top: 8px;
  padding-top: 12px;
  font-weight: 700;
  font-size: 15px;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.badge.confirmed { background: #dcfce7; color: #166534; }
.badge.pending { background: #fef3c7; color: #92400e; }
.btn-secondary {
  margin-top: 12px;
  background: #f1f5f9;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  width: 100%;
}
.btn-secondary:hover { background: #e2e8f0; }

.product-details {
  margin-top: 12px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.product-details h4 {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
.product-details ul {
  margin: 0;
  padding: 0;
  list-style: none;
}
.product-details li {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #f1f5f9;
}
.product-details li:last-child { border-bottom: none; }
.product-details li strong { color: #475569; }
.product-details li span { color: #1e293b; font-weight: 500; }
</style>
