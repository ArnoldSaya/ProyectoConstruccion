import { defineStore } from 'pinia'
import { getUserFavorites, addFavorite, removeFavorite } from '../services/favorites'
import { useAuthStore } from './auth'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    // mapa: mongo_product_id -> id del favorito en SQL
    map: {},
    loaded: false,
    loading: false
  }),
  getters: {
    isFavorite: (state) => (productId) => !!state.map[productId]
  },
  actions: {
    async load() {
      const auth = useAuthStore()
      if (!auth.isAuthenticated || !auth.user?.id) return
      if (this.loaded || this.loading) return
      this.loading = true
      try {
        const { data } = await getUserFavorites(auth.user.id, { per_page: 200 })
        this.map = {}
        for (const f of (data.data || [])) {
          this.map[f.mongo_product_id] = f.id
        }
        this.loaded = true
      } finally {
        this.loading = false
      }
    },
    async toggle(productId) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated || !auth.user?.id) return false
      const favId = this.map[productId]
      if (favId) {
        await removeFavorite(favId)
        delete this.map[productId]
        return false
      }
      const { data } = await addFavorite({
        user_id: auth.user.id,
        mongo_product_id: productId
      })
      this.map[productId] = data.id
      return true
    }
  }
})
