<template>
  <div class="card publish-card">
    <h1>Publicar producto</h1>

    <form @submit.prevent="handleSubmit">
      <label>Nombre
        <input v-model="form.name_prod" placeholder="Ej: Taladro percutor Bosch" required />
      </label>

      <label>Descripción
        <textarea v-model="form.description" placeholder="Describe tu producto, estado, características..." required></textarea>
      </label>

      <label>Categoría
        <select v-model="form.category_id" required>
          <option value="" disabled>Selecciona una categoría</option>
          <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name_cat }}</option>
        </select>
      </label>

      <label>Precio por día (S/)
        <input v-model="form.price" type="number" step="0.01" min="0" placeholder="0.00" required />
      </label>

      <label>Detalles adicionales
        <textarea v-model="form.details" placeholder="Condiciones, accesorios incluidos, instrucciones..."></textarea>
      </label>

      <!-- ========== UPLOADER DE FOTO ========== -->
      <div class="uploader-section">
        <p class="uploader-label">Foto del producto</p>

        <!-- Zona de drop / preview -->
        <div
          class="drop-zone"
          :class="{ 'drag-over': isDragging, 'has-preview': previewUrl }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="!previewUrl && openGallery()"
        >
          <!-- Vista previa -->
          <template v-if="previewUrl">
            <img :src="previewUrl" alt="Vista previa" class="drop-preview" />
            <div class="preview-overlay">
              <button type="button" class="btn-overlay" @click.stop="openGallery()">🔄 Cambiar</button>
              <button type="button" class="btn-overlay btn-overlay-danger" @click.stop="clearPhoto()">🗑 Quitar</button>
            </div>
          </template>

          <!-- Placeholder -->
          <template v-else>
            <div class="drop-placeholder">
              <span class="drop-icon">📷</span>
              <p class="drop-text">Arrastra una imagen aquí<br><span>o haz clic para elegir</span></p>
            </div>
          </template>
        </div>

        <!-- Botones de acción -->
        <div class="photo-actions">
          <button type="button" class="btn-photo" @click="openCamera()">
            <span>📷</span> Tomar foto
          </button>
          <button type="button" class="btn-photo" @click="openGallery()">
            <span>🖼️</span> Galería
          </button>
        </div>

        <!-- Barra de progreso de carga -->
        <div v-if="uploading" class="upload-progress">
          <div class="upload-progress-bar" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p v-if="uploading" class="upload-status">Subiendo imagen... {{ uploadProgress }}%</p>

        <p class="photo-hint">JPG, PNG, GIF o WEBP · máx. 5 MB</p>

        <!-- Inputs ocultos -->
        <input ref="cameraInput" class="hidden-input" type="file" accept="image/*" capture="environment" @change="onFileSelected" />
        <input ref="galleryInput" class="hidden-input" type="file" accept="image/*" @change="onFileSelected" />
      </div>
      <!-- ======================================= -->

      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <p v-if="success" class="alert alert-success">✅ ¡Producto publicado con éxito!</p>

      <button type="submit" :disabled="loading" class="btn-submit">
        <span v-if="loading" class="btn-spinner"></span>
        {{ loading ? (uploading ? 'Subiendo foto...' : 'Publicando...') : 'Publicar producto' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getCategories, createProduct, uploadProductImage } from '../services/products'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const categories = ref([])
const error = ref('')
const success = ref(false)
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)

const cameraInput = ref(null)
const galleryInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')

const form = reactive({
  name_prod: '',
  description: '',
  category_id: '',
  price: '',
  details: ''
})

function openCamera() {
  cameraInput.value?.click()
}

function openGallery() {
  galleryInput.value?.click()
}

function onDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (file) processFile(file)
}

function processFile(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowed.includes(file.type)) {
    error.value = 'Formato no permitido. Usa JPG, PNG, GIF o WEBP.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'La imagen supera los 5 MB.'
    return
  }
  error.value = ''
  selectedFile.value = file
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)
}

function clearPhoto() {
  selectedFile.value = null
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  if (cameraInput.value) cameraInput.value.value = ''
  if (galleryInput.value) galleryInput.value.value = ''
}

async function loadCategories() {
  try {
    const { data } = await getCategories({ per_page: 50 })
    categories.value = data.data
  } catch {
    error.value = 'No se pudieron cargar las categorías.'
  }
}

async function handleSubmit() {
  error.value = ''
  success.value = false
  loading.value = true
  try {
    let imageUrl = null
    if (selectedFile.value) {
      uploading.value = true
      uploadProgress.value = 0

      // Simular progreso mientras sube
      const progressInterval = setInterval(() => {
        if (uploadProgress.value < 85) uploadProgress.value += 10
      }, 150)

      const { data } = await uploadProductImage(selectedFile.value)
      clearInterval(progressInterval)
      uploadProgress.value = 100
      imageUrl = data.url
      uploading.value = false
    }

    await createProduct({ ...form, owner_id: auth.user.id, image_url: imageUrl })
    success.value = true
    form.name_prod = ''
    form.description = ''
    form.category_id = ''
    form.price = ''
    form.details = ''
    clearPhoto()
  } catch (e) {
    error.value = e.response?.data?.error?.[0] || 'No se pudo publicar el producto.'
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    loading.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.publish-card {
  max-width: 520px;
}

/* ===== Drop zone ===== */
.uploader-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.uploader-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-muted);
  margin: 0;
}

.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: 12px;
  background: #f8fafc;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  overflow: hidden;
}
.drop-zone:hover,
.drop-zone.drag-over {
  border-color: var(--color-primary);
  background: #eff6ff;
}
.drop-zone.has-preview {
  cursor: default;
  border-style: solid;
  border-color: var(--color-border);
  min-height: 200px;
}

.drop-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  user-select: none;
}
.drop-icon { font-size: 2.2rem; }
.drop-text {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.88rem;
  text-align: center;
  line-height: 1.5;
}
.drop-text span { color: var(--color-primary); font-weight: 500; }

.drop-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s;
}
.drop-zone.has-preview:hover .preview-overlay { opacity: 1; }

.btn-overlay {
  background: rgba(255,255,255,0.9);
  color: #1f2430;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  font-size: 0.87rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-overlay:hover { background: #fff; }
.btn-overlay-danger { background: rgba(220,38,38,0.85); color: #fff; }
.btn-overlay-danger:hover { background: #dc2626; }

/* ===== Botones foto ===== */
.photo-actions {
  display: flex;
  gap: 0.6rem;
}
.btn-photo {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: #fff;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.55rem 0.75rem;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-photo:hover { background: #f1f5f9; border-color: var(--color-primary); }

/* ===== Progreso de carga ===== */
.upload-progress {
  height: 6px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}
.upload-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 99px;
  transition: width 0.2s ease;
}
.upload-status {
  font-size: 0.82rem;
  color: var(--color-primary);
  margin: 0;
  text-align: center;
}

.photo-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  text-align: center;
}
.hidden-input { display: none; }

/* ===== Botón submit ===== */
.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  font-size: 1rem;
}
.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
