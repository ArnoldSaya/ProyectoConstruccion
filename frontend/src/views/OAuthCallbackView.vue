<template>
  <div class="card">
    <div v-if="status === 'loading'" class="spinner-wrap">
      <span class="spinner"></span>
      <p>Verificando tu sesión con Google...</p>
    </div>
    <template v-else>
      <p class="alert alert-error">{{ errorMessage }}</p>
      <router-link to="/login">Volver a intentar</router-link>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const status = ref('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = route.query.token
  const refresh = route.query.refresh
  if (!token) {
    status.value = 'error'
    errorMessage.value = 'No se recibió un token de autenticación de Google.'
    return
  }
  try {
    await auth.loginWithToken(token, refresh)
    router.replace('/')
  } catch (e) {
    status.value = 'error'
    errorMessage.value = 'No se pudo completar el inicio de sesión con Google.'
  }
})
</script>
