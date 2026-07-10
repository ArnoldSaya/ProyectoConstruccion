<template>
  <div class="card" style="max-width: 900px;">
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
        <div class="product-thumb">
          <img v-if="p.image_url" :src="p.image_url" :alt="p.name_prod" class="product-img" />
          <div v-else class="product-img placeholder">
            <span>📦</span>
            <small>Sin imagen</small>
          </div>
        </div>
        <div class="product-body">
          <h3>{{ p.name_prod }}</h3>
          <p class="price">S/ {{ p.price }} / día</p>
          <span class="badge" :class="p.status">{{ p.status }}</span>
          <div class="actions">
            <button class="btn-secondary" :disabled="busy === p._id" @click="openEdit(p)">✏️ Editar</button>
            <button class="btn-danger" :disabled="deleting === p._id" @click="remove(p)">
              {{ deleting === p._id ? 'Eliminando...' : '🗑 Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ MODAL DE EDICIÓN ============ -->
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

        <!-- ===== UPLOADER DE FOTO EN EDICIÓN ===== -->
        <div class="edit-uploader">
          <p class="uploader-label">Foto del producto</p>

          <div
            class="drop-zone"
            :class="{ 'drag-over': isDragging, 'has-preview': editPreviewUrl }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onEditDrop"
            @click="!editPreviewUrl && editGalleryInput?.click()"
          >
            <template v-if="editPreviewUrl">
              <img :src="editPreviewUrl" alt="Vista previa" class="drop-preview" />
              <div class="preview-overlay">
                <button type="button" class="btn-overlay" @click.stop="editGalleryInput?.click()">🔄 Cambiar</button>
                <button type="button" class="btn-overlay btn-overlay-danger" @click.stop="clearEditPhoto()">🗑 Quitar</button>
              </div>
            </template>
            <template v-else>
              <div class="drop-placeholder">
                <span class="drop-icon">📷</span>
                <p class="drop-text">Arrastra una imagen<br><span>o haz clic para elegir</span></p>
              </div>
            </template>
          </div>

          <div class="photo-actions">
            <button type="button" class="btn-photo" @click="editCameraInput?.click()">
              <span>📷</span> Tomar foto
            </button>
            <button type="button" class="btn-photo" @click="editGalleryInput?.click()">
              <span>🖼️</span> Galería
            </button>
          </div>

          <div v-if="editUploading" class="upload-progress">
            <div class="upload-progress-bar" :style="{ width: editUploadProgress + '%' }"></div>
          </div>
          <p v-if="editUploading" class="upload-status">Subiendo imagen... {{ editUploadProgress }}%</p>
          <p class="photo-hint">JPG, PNG, GIF o WEBP · máx. 5 MB</p>

          <input ref="editCameraInput" class="hidden-input" type="file" accept="image/*" capture="environment" @change="onEditFileSelected" />
          <input ref="editGalleryInput" class="hidden-input" type="file" accept="image/*" @change="onEditFileSelected" />
        </div>
        <!-- ========================================= -->

        <p v-if="editError" class="alert alert-error">{{ editError }}</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeEdit">Cancelar</button>
          <button class="btn-primary" :disabled="saving" @click="save">
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? (editUploading ? 'Subiendo foto...' : 'Guardando...') : 'Guardar cambios' }}
          </button>
        </div>
      </div>
    </div>
    <!-- =========================================== -->
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getProductsByOwner, deleteProduct, updateProduct, getCategories, uploadProductImage } from '../services/products'
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
const isDragging = ref(false)

// Foto en edición
const editCameraInput = ref(null)
const editGalleryInput = ref(null)
const editSelectedFile = ref(null)
const editPreviewUrl = ref('')
const editUploading = ref(false)
const editUploadProgress = ref(0)

const form = reactive({
  name_prod: '',
  description: '',
  category_id: '',
  price: '',
  details: '',
  status: 'disponible',
  image_url: null
})

// ===== Carga de datos =====
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
  } catch {
    error.value = 'No se pudieron cargar tus productos.'
  } finally {
    loading.value = false
  }
}

// ===== Modal editar =====
function openEdit(p) {
  editId.value = p._id
  form.name_prod = p.name_prod
  form.description = p.description || ''
  form.category_id = p.category_id || ''
  form.price = p.price
  form.details = p.details || ''
  form.status = p.status || 'disponible'
  form.image_url = p.image_url || null

  // Mostrar la imagen actual como preview
  clearEditPhoto()
  if (p.image_url) editPreviewUrl.value = p.image_url

  editError.value = ''
  editing.value = true
}

function closeEdit() {
  editing.value = false
  editId.value = null
  clearEditPhoto()
}

// ===== Manejo de foto en edición =====
function onEditDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) processEditFile(file)
}

function onEditFileSelected(event) {
  const file = event.target.files?.[0]
  if (file) processEditFile(file)
}

function processEditFile(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowed.includes(file.type)) {
    editError.value = 'Formato no permitido. Usa JPG, PNG, GIF o WEBP.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    editError.value = 'La imagen supera los 5 MB.'
    return
  }
  editError.value = ''
  editSelectedFile.value = file
  // Si habia un objectURL local, revocarlo
  if (editPreviewUrl.value && editPreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(editPreviewUrl.value)
  }
  editPreviewUrl.value = URL.createObjectURL(file)
}

function clearEditPhoto() {
  editSelectedFile.value = null
  if (editPreviewUrl.value && editPreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(editPreviewUrl.value)
  }
  editPreviewUrl.value = ''
  if (editCameraInput.value) editCameraInput.value.value = ''
  if (editGalleryInput.value) editGalleryInput.value.value = ''
}

// ===== Guardar edición =====
async function save() {
  saving.value = true
  editError.value = ''
  try {
    // Si hay un archivo nuevo, subirlo primero
    if (editSelectedFile.value) {
      editUploading.value = true
      editUploadProgress.value = 0

      const progressInterval = setInterval(() => {
        if (editUploadProgress.value < 85) editUploadProgress.value += 10
      }, 150)

      const { data } = await uploadProductImage(editSelectedFile.value)
      clearInterval(progressInterval)
      editUploadProgress.value = 100
      form.image_url = data.url
      editUploading.value = false
    }

    await updateProduct(editId.value, { ...form })
    success.value = 'Producto actualizado correctamente.'
    closeEdit()
    await load()
  } catch (e) {
    editError.value = e.response?.data?.error?.[0] || 'No se pudo actualizar el producto.'
  } finally {
    editUploading.value = false
    editUploadProgress.value = 0
    saving.value = false
  }
}

// ===== Eliminar =====
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
    error.value = e.response?.data?.error?.[0] || 'No se pudo eliminar el producto.'
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

/* ===== Product card ===== */
.product-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.15s, transform 0.15s;
}
.product-card:hover { box-shadow: 0 4px 14px rgba(15,23,42,.1); transform: translateY(-2px); }

.product-thumb { position: relative; height: 150px; }
.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.product-img.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
  gap: 4px;
  font-size: 1.8rem;
}
.product-img.placeholder small { font-size: 11px; }

.product-body { padding: 12px; display: flex; flex-direction: column; gap: 6px; flex: 1; }
.product-body h3 { margin: 0; font-size: 15px; }
.price { font-weight: 700; color: #0f172a; margin: 0; font-size: 14px; }
.actions { display: flex; gap: 8px; margin-top: 4px; }
.actions button { flex: 1; font-size: 13px; }

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
  display: flex; align-items: center; gap: 6px;
}
.btn-primary:disabled, .btn-danger:disabled, .btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { color: #2563eb; }

/* ===== Badge ===== */
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; text-transform: capitalize; background: #e5e7eb; }
.badge.disponible { background: #d1fae5; color: #065f46; }
.badge.no_disponible { background: #fee2e2; color: #991b1b; }

/* ===== Modal ===== */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,.55);
  display: flex; align-items: center; justify-content: center; z-index: 50;
  padding: 1rem;
}
.modal {
  background: #fff; border-radius: 14px; padding: 24px;
  width: 100%; max-width: 480px; max-height: 92vh; overflow-y: auto;
  display: flex; flex-direction: column; gap: 12px;
}
.modal h2 { margin: 0 0 4px; }
.modal label { display: flex; flex-direction: column; gap: 4px; font-size: 13px; font-weight: 500; color: #6b7280; }
.modal input, .modal textarea, .modal select {
  padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px;
  font-size: 14px; font-family: inherit; color: #1f2430;
}
.modal input:focus, .modal textarea:focus, .modal select:focus {
  outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.15);
}
.modal textarea { min-height: 72px; resize: vertical; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }

/* ===== Edit uploader ===== */
.edit-uploader { display: flex; flex-direction: column; gap: 8px; }
.uploader-label { font-size: 13px; font-weight: 500; color: #6b7280; margin: 0; }

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  min-height: 130px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative; overflow: hidden;
}
.drop-zone:hover, .drop-zone.drag-over { border-color: #2563eb; background: #eff6ff; }
.drop-zone.has-preview { cursor: default; border-style: solid; border-color: #cbd5e1; min-height: 160px; }

.drop-placeholder { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 1rem; user-select: none; }
.drop-icon { font-size: 1.8rem; }
.drop-text { margin: 0; color: #94a3b8; font-size: 0.82rem; text-align: center; line-height: 1.5; }
.drop-text span { color: #2563eb; font-weight: 500; }

.drop-preview { width: 100%; height: 160px; object-fit: cover; display: block; }
.preview-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  opacity: 0; transition: opacity 0.2s;
}
.drop-zone.has-preview:hover .preview-overlay { opacity: 1; }
.btn-overlay {
  background: rgba(255,255,255,.9); color: #1f2430; border: none;
  border-radius: 8px; padding: 6px 12px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-overlay:hover { background: #fff; }
.btn-overlay-danger { background: rgba(220,38,38,.85); color: #fff; }
.btn-overlay-danger:hover { background: #dc2626; }

.photo-actions { display: flex; gap: 8px; }
.btn-photo {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px;
  background: #fff; color: #1f2430; border: 1px solid #cbd5e1;
  border-radius: 8px; padding: 7px; font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-photo:hover { background: #f1f5f9; border-color: #2563eb; }

.upload-progress { height: 5px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.upload-progress-bar { height: 100%; background: linear-gradient(90deg, #2563eb, #60a5fa); border-radius: 99px; transition: width 0.2s ease; }
.upload-status { font-size: 12px; color: #2563eb; margin: 0; text-align: center; }

.photo-hint { font-size: 11px; color: #94a3b8; margin: 0; text-align: center; }
.hidden-input { display: none; }

/* ===== Spinner botón ===== */
.btn-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
