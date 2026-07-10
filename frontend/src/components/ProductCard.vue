<template>
  <router-link :to="{ name: 'product-detail', params: { id: product._id } }" class="product-card">
    <div class="product-card-thumb">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name_prod" />
      <template v-else>📦</template>
      <button
        v-if="auth.isAuthenticated"
        type="button"
        class="fav-btn"
        :class="{ active: fav.isFavorite(product._id) }"
        :title="fav.isFavorite(product._id) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        @click.prevent.stop="toggleFav"
      >
        {{ fav.isFavorite(product._id) ? '❤️' : '🤍' }}
      </button>
    </div>
    <div class="product-card-body">
      <h3>{{ product.name_prod }}</h3>
      <p class="product-card-desc">{{ truncate(product.description) }}</p>
      <div class="product-card-footer">
        <span class="price">S/ {{ formatPrice(product.price) }}</span>
        <span class="badge" :class="product.status">{{ product.status }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useFavoritesStore } from '../stores/favorites'

const props = defineProps({
  product: { type: Object, required: true }
})

const auth = useAuthStore()
const fav = useFavoritesStore()

onMounted(() => fav.load())

async function toggleFav() {
  await fav.toggle(props.product._id)
}

function truncate(text, length = 90) {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '…' : text
}

function formatPrice(value) {
  const n = Number(value)
  return Number.isNaN(n) ? value : n.toFixed(2)
}
</script>

<style scoped>
.product-card-thumb {
  position: relative;
}
.fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s ease, background 0.12s ease;
}
.fav-btn:hover {
  transform: scale(1.1);
  background: #fff;
}
.fav-btn.active {
  background: #fff;
}
</style>
