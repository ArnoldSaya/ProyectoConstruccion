<template>
  <router-link :to="{ name: 'product-detail', params: { id: product._id } }" class="product-card">
    <div class="product-card-thumb">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name_prod" />
      <template v-else>📦</template>
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
defineProps({
  product: { type: Object, required: true }
})

function truncate(text, length = 90) {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '…' : text
}

function formatPrice(value) {
  const n = Number(value)
  return Number.isNaN(n) ? value : n.toFixed(2)
}
</script>
