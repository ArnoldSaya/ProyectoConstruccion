<template>
  <div class="card">
    <h1>Mi perfil</h1>
    <div v-if="initialLoading" class="spinner-wrap"><span class="spinner"></span></div>
    <form v-else @submit.prevent="handleSubmit">
      <div class="roles-row" v-if="auth.roles.length">
        <span class="role-badge" :class="roleClass(r)" v-for="r in auth.roles" :key="r">{{ r }}</span>
      </div>

      <p v-if="auth.hasRole('cliente') && !auth.isRentador" class="alert alert-info">
        ¿Tienes productos para alquilar? Conviértete en rentador para publicarlos.
        <button type="button" class="btn-secondary" :disabled="promoting" @click="activateRentador">
          {{ promoting ? 'Activando...' : 'Conviértete en rentador' }}
        </button>
      </p>

      <label>Nombre completo
        <input v-model="form.full_name" required />
      </label>
      <label>Email
        <input v-model="form.email" type="email" required />
      </label>
      <label>Teléfono
        <input v-model="form.phone" />
      </label>
      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <p v-if="success" class="alert alert-success">Perfil actualizado.</p>
      <button type="submit" :disabled="loading">{{ loading ? 'Guardando...' : 'Guardar cambios' }}</button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { updateUser, becomeRentador } from '../services/users'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const error = ref('')
const success = ref(false)
const loading = ref(false)
const promoting = ref(false)
const initialLoading = ref(true)

const form = reactive({ full_name: '', email: '', phone: '' })

function roleClass(role) {
  if (role === 'rentador') return 'role-rentador'
  if (role === 'admin') return 'role-admin'
  return 'role-cliente'
}

onMounted(async () => {
  try {
    await auth.fetchMe()
    form.full_name = auth.user.full_name
    form.email = auth.user.email
    form.phone = auth.user.phone || ''
  } catch (e) {
    error.value = 'No se pudo cargar tu perfil.'
  } finally {
    initialLoading.value = false
  }
})

async function activateRentador() {
  promoting.value = true
  try {
    await becomeRentador()
    await auth.fetchMe()
    const redirect = route.query.redirect
    if (redirect) router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo activar el rol de rentador'
  } finally {
    promoting.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  success.value = false
  loading.value = true
  try {
    await updateUser(auth.user.id, { ...form })
    await auth.fetchMe()
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo actualizar el perfil'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.roles-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.role-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.role-cliente { background: #e2e8f0; color: #475569; }
.role-rentador { background: #dcfce7; color: #166534; }
.role-admin { background: #fee2e2; color: #991b1b; }
.btn-secondary {
  margin-left: 10px;
  background: #f1f5f9;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
}
.btn-secondary:disabled { opacity: 0.6; cursor: default; }
</style>
