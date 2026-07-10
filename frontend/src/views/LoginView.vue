<template>
  <div class="card">
    <h1>Ingresar</h1>
    <form @submit.prevent="handleSubmit">
      <label>Email
        <input v-model="email" type="email" required />
      </label>
      <label>Contraseña
        <input v-model="password" type="password" required />
      </label>
      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <button type="submit" :disabled="loading">{{ loading ? 'Ingresando...' : 'Ingresar' }}</button>
    </form>
    <div class="divider">o</div>
    <button type="button" class="google-btn" @click="continueWithGoogle">Continuar con Google</button>
    <p>¿No tienes cuenta? <router-link to="/registro">Regístrate</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(route.query.redirect || '/')
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo iniciar sesión'
  } finally {
    loading.value = false
  }
}

function continueWithGoogle() {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'
  window.location.href = `${apiUrl}/auth/google/login`
}
</script>
