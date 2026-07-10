<template>
  <div class="card">
    <h1>Mis productos</h1>
    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <p v-if="success" class="alert alert-success">{{ success }}</p>

    <div v-if="loading" class="spinner-wrap"><span class="spinner"></span></div>

    <p v-else-if="products.length === 0" class="empty-state">
      Aún no has publicado productos.
      <router-link to="/publicar" class="link">Publica tu primer producto</router-link>
    </p>

    <div v-else class="grid">
      <div v-for="p in products" :key="p._id" class="product-card">
        <img v-if="p.image_url" :src="p.image_url" :alt="p.name_prod" class="product-img" />
        <div v-else class="product-img placeholder">Sin imagen</div>
        <div class="product-body">
          <h3>{{ p.name_prod }}</h3>
          <p class="price">S/ {{ p.price }} / día</p>
          <p class="status" :class="p.status === 'disponible' ? 'ok' : 'busy'">{{ p.status }}</p>
          <div class="actions">
            <button class="btn-secondary" :disabled="busy === p._id" @click="openEdit(p)">Editar</button>
            <button class="btn-danger" :disabled="deleting === p._id" @click="remove(p)">
              {{ deleting === p._id ? 'Eliminando...' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de edicion -->
    <div v-if="editing" class="modal-overlay" @click.self="closeEdit">
      <div class="modal">
        <h2>Editar producto</h2>
        <label>Nombre
          <input v-model="form.name_prod" required />
        </label>
        <label>Descripción
          <textarea v-model="form.description" required></textarea>
        </label>
        <label>Categoría
          <select v-model="form.category_id" required>
            <option value="" disabled>Selecciona una categoría</option>
            <option v-for="c in categories" :key="c._id" :value="c._id">{{ c.name_cat }}</option>
          </select>
        </label>
        <label>Precio (S/)
          <input v-model="form.price" type="number" step="0.01" required />
        </label>
        <label>Detalles
          <textarea v-model="form.details"></textarea>
        </label>
        <label>Estado
          <select v-model="form.status">
            <option value="disponible">Disponible</option>
            <option value="no_disponible">No disponible</option>
          </select>
        </label>
        <p v-if="editError" class="alert alert-error">{{ editError }}</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeEdit">Cancelar</button>
          <button class="btn-primary" :disabled="saving" @click="save">
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getProductsByOwner, deleteProduct, updateProduct, getCategories } from '../services/products'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const products = ref([])
const categories = ref([])
const loading = ref(true)
const deleting = ref(null)
const busy = ref(null)
const error = ref('')
const success = ref('')

const editing = ref(false)
const saving = ref(false)
const editError = ref('')
const editId = ref(null)
const form = reactive({ name_prod: '', description: '', category_id: '', price: '', details: '', status: 'disponible' })

async function load() {
  error.value = ''
  loading.value = true
  try {
    const [prodRes, catRes] = await Promise.all([
      getProductsByOwner(auth.user.id),
      getCategories({ per_page: 50 })
    ])
    products.value = prodRes.data.data || []
    categories.value = catRes.data.data || []
  } catch (e) {
    error.value = 'No se pudieron cargar tus productos.'
  } finally {
    loading.value = false
  }
}

function openEdit(p) {
  editId.value = p._id
  form.name_prod = p.name_prod
  form.description = p.description || ''
  form.category_id = p.category_id || ''
  form.price = p.price
  form.details = p.details || ''
  form.status = p.status || 'disponible'
  editError.value = ''
  editing.value = true
}

function closeEdit() {
  editing.value = false
  editId.value = null
}

async function save() {
  saving.value = true
  editError.value = ''
  try {
    await updateProduct(editId.value, { ...form })
    success.value = 'Producto actualizado.'
    closeEdit()
    await load()
  } catch (e) {
    editError.value = e.response?.data?.error?.[0] || 'No se pudo actualizar el producto'
  } finally {
    saving.value = false
  }
}

async function remove(p) {
  if (!confirm(`¿Eliminar "${p.name_prod}"?`)) return
  deleting.value = p._id
  error.value = ''
  success.value = ''
  try {
    await deleteProduct(p._id)
    success.value = 'Producto eliminado.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo eliminar el producto'
  } finally {
    deleting.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.product-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.product-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}
.product-img.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
  font-size: 13px;
}
.product-body { padding: 12px; }
.product-body h3 { margin: 0 0 4px; font-size: 16px; }
.price { font-weight: 700; color: #0f172a; margin: 0 0 4px; }
.status { font-size: 12px; margin: 0 0 10px; }
.status.ok { color: #166534; }
.status.busy { color: #b45309; }
.actions { display: flex; gap: 8px; }
.actions button { flex: 1; }
.btn-secondary {
  background: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1;
  border-radius: 8px; padding: 8px; cursor: pointer;
}
.btn-danger {
  background: #ef4444; color: #fff; border: none;
  border-radius: 8px; padding: 8px; cursor: pointer;
}
.btn-primary {
  background: #2563eb; color: #fff; border: none;
  border-radius: 8px; padding: 8px 16px; cursor: pointer;
}
.btn-primary:disabled, .btn-danger:disabled, .btn-secondary:disabled { opacity: 0.6; }
.link { color: #2563eb; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,.5);
  display: flex; align-items: center; justify-content: center; z-index: 50;
}
.modal {
  background: #fff; border-radius: 12px; padding: 20px;
  width: 90%; max-width: 440px; max-height: 90vh; overflow: auto;
}
.modal label { display: block; margin-bottom: 10px; font-size: 13px; }
.modal input, .modal textarea, .modal select {
  width: 100%; margin-top: 4px; padding: 8px;
  border: 1px solid #cbd5e1; border-radius: 8px;
}
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
</style>
