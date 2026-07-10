<template>
  <div class="callback-wrap">
    <div class="callback-card">
      <!-- Loading -->
      <div v-if="status === 'loading'" class="callback-state">
        <div class="callback-spinner"></div>
        <p class="callback-title">Iniciando sesión con Google...</p>
        <p class="callback-sub">Por favor espera un momento</p>
      </div>

      <!-- Error -->
      <div v-else class="callback-state">
        <div class="callback-icon error-icon">⚠️</div>
        <p class="callback-title">Error al iniciar sesión</p>
        <p class="callback-sub alert-error-text">{{ errorMessage }}</p>
        <router-link to="/login" class="callback-btn">Volver a intentar</router-link>
      </div>
    </div>
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

const ERROR_MESSAGES = {
  oauth_failed:       'El proceso de autenticación con Google falló. Por favor vuelve a intentarlo.',
  missing_user_info:  'No se pudo obtener tu información de Google. Intenta de nuevo.',
}

onMounted(async () => {
  // El backend puede redirigir con ?error= si algo salió mal
  const backendError = route.query.error
  if (backendError) {
    status.value = 'error'
    errorMessage.value = ERROR_MESSAGES[backendError] || 'Ocurrió un error durante el inicio de sesión con Google.'
    return
  }

  const token = route.query.token
  const refresh = route.query.refresh

  if (!token) {
    status.value = 'error'
    errorMessage.value = 'No se recibió un token de autenticación. Por favor vuelve a intentarlo.'
    return
  }

  try {
    await auth.loginWithToken(token, refresh)
    router.replace('/')
  } catch {
    status.value = 'error'
    errorMessage.value = 'No se pudo completar el inicio de sesión con Google.'
  }
})
</script>

<style scoped>
.callback-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg, #f4f5f7);
  padding: 1rem;
}

.callback-card {
  background: #fff;
  border: 1px solid #e2e5eb;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  max-width: 360px;
  width: 100%;
  text-align: center;
  box-shadow: 0 4px 24px rgba(15,23,42,.08);
}

.callback-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

/* Spinner */
.callback-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.callback-icon { font-size: 2.5rem; }

.callback-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2430;
  margin: 0;
}

.callback-sub {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}

.alert-error-text {
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
}

.callback-btn {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.6rem 1.4rem;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.92rem;
  transition: background 0.15s;
}
.callback-btn:hover { background: #1d4ed8; }
</style>
