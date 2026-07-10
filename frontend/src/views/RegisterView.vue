<template>
  <div class="card">
    <h1>Crear cuenta</h1>
    <form @submit.prevent="handleSubmit">
      <label>Nombre completo
        <input v-model="form.full_name" required />
      </label>
      <label>Email
        <input v-model="form.email" type="email" required />
      </label>
      <label>Teléfono
        <input v-model="form.phone" />
      </label>
      <label>Contraseña
        <input v-model="form.password" type="password" required />
      </label>
      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <button type="submit" :disabled="loading">{{ loading ? 'Creando...' : 'Crear cuenta' }}</button>
    </form>
    <div class="divider">o</div>
    <button type="button" class="google-btn" @click="continueWithGoogle">Registrarme con Google</button>
    <p>¿Ya tienes cuenta? <router-link to="/login">Ingresa</router-link></p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const form = reactive({ full_name: '', email: '', phone: '', password: '' })
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register({ ...form })
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo crear la cuenta'
  } finally {
    loading.value = false
  }
}

function continueWithGoogle() {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'
  window.location.href = `${apiUrl}/auth/google/login`
}
</script>
