<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand">
        <img src="/logo.svg" alt="AlquilaYa" class="brand-logo" />
        <span>AlquilaYa</span>
      </router-link>
      <button class="nav-toggle" @click="open = !open" :aria-expanded="open" aria-label="Abrir menú">
        <span></span><span></span><span></span>
      </button>
      <nav :class="{ open }">
        <router-link to="/" @click="close">Inicio</router-link>
        <template v-if="auth.isAuthenticated">
          <router-link v-if="auth.isRentador" to="/publicar" @click="close">Publicar</router-link>
          <router-link to="/mis-reservas" @click="close">Mis reservas</router-link>
          <router-link to="/favoritos" @click="close">Favoritos</router-link>
          <router-link to="/perfil" @click="close" class="nav-user">
            {{ auth.user?.full_name || 'Mi perfil' }}
            <span v-if="auth.isRentador" class="role-badge role-rentador">Rentador</span>
            <span v-else-if="auth.isAdmin" class="role-badge role-admin">Admin</span>
            <span v-else class="role-badge role-cliente">Cliente</span>
          </router-link>
          <button class="link-btn" @click="handleLogout">Salir</button>
        </template>
        <template v-else>
          <router-link to="/login" @click="close">Ingresar</router-link>
          <router-link to="/registro" class="nav-cta" @click="close">Crear cuenta</router-link>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const open = ref(false)

watch(() => route.fullPath, () => {
  open.value = false
})

function close() {
  open.value = false
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-user {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.role-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.role-cliente {
  background: #e2e8f0;
  color: #475569;
}
.role-rentador {
  background: #dcfce7;
  color: #166534;
}
.role-admin {
  background: #fee2e2;
  color: #991b1b;
}
</style>
