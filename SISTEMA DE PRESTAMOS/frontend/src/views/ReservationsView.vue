<template>
  <div>
    <h1>Mis reservas</h1>
    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>
    <div v-else-if="reservations.length === 0" class="empty-state">
      <span class="empty-state-icon">🗓️</span>
      <p>No tienes reservas todavía.</p>
      <router-link to="/" class="btn-link">Explorar productos</router-link>
    </div>
    <div v-else>
      <div class="list-item" v-for="r in reservations" :key="r.id">
        <div>
          <strong>Reserva #{{ r.id }}</strong>
          <p>{{ formatDate(r.start_date) }} → {{ formatDate(r.end_date) }} · S/ {{ formatPrice(r.total_price) }}</p>
        </div>
        <span class="badge" :class="r.status">{{ r.status }}</span>
        <button v-if="r.status === 'pending'" class="btn-secondary" @click="cancel(r.id)">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getUserReservations, updateReservation } from '../services/reservations'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const reservations = ref([])
const loading = ref(false)
const error = ref('')

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatPrice(value) {
  const n = Number(value)
  return Number.isNaN(n) ? value : n.toFixed(2)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await getUserReservations(auth.user.id, { per_page: 50 })
    reservations.value = data.data
  } catch (e) {
    error.value = 'No se pudieron cargar tus reservas.'
  } finally {
    loading.value = false
  }
}

async function cancel(id) {
  try {
    await updateReservation(id, { status: 'cancelled' })
    await load()
  } catch (e) {
    error.value = 'No se pudo cancelar la reserva.'
  }
}

onMounted(load)
</script>
