<template>
  <div class="card">
    <h1>Publicar producto</h1>
    <form @submit.prevent="handleSubmit">
      <label>Nombre
        <input v-model="form.name_prod" required />
      </label>
      <label>Descripción
        <textarea v-model="form.description" required></textarea>
      </label>
      <label>Categoría
        <select v-model="form.category_id" required>
          <option value="" disabled>Selecciona una categoría</option>
          <option v-for="cat in categories" :key="cat._id" :value="cat._id">{{ cat.name_cat }}</option>
        </select>
      </label>
      <label>Precio (S/)
        <input v-model="form.price" type="number" step="0.01" required />
      </label>
      <label>Detalles adicionales
        <textarea v-model="form.details"></textarea>
      </label>

      <div class="photo-uploader">
        <img v-if="previewUrl" :src="previewUrl" alt="Vista previa" class="photo-preview" />
        <div class="photo-actions">
          <button type="button" class="btn-secondary" @click="openCamera">📷 Tomar foto</button>
          <button type="button" class="btn-secondary" @click="openGallery">🖼️ Elegir imagen</button>
          <button type="button" class="btn-secondary" v-if="previewUrl" @click="clearPhoto">Quitar</button>
        </div>
        <p class="photo-hint">Toma una foto del producto o elige una imagen (máx. 5 MB).</p>
        <input ref="cameraInput" class="hidden-input" type="file" accept="image/*" capture="environment" @change="onFileSelected" />
        <input ref="galleryInput" class="hidden-input" type="file" accept="image/*" @change="onFileSelected" />
      </div>

      <p v-if="error" class="alert alert-error">{{ error }}</p>
      <p v-if="success" class="alert alert-success">¡Producto publicado!</p>
      <button type="submit" :disabled="loading">{{ loading ? (uploading ? 'Subiendo foto...' : 'Publicando...') : 'Publicar' }}</button>
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

const cameraInput = ref(null)
const galleryInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')

const form = reactive({ name_prod: '', description: '', category_id: '', price: '', details: '' })

function openCamera() {
  cameraInput.value && cameraInput.value.click()
}

function openGallery() {
  galleryInput.value && galleryInput.value.click()
}

function onFileSelected(event) {
  const file = event.target.files && event.target.files[0]
  if (!file) return
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
  } catch (e) {
    error.value = 'No se pudieron cargar las categorias'
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
      const { data } = await uploadProductImage(selectedFile.value)
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
    error.value = e.response?.data?.error?.[0] || 'No se pudo publicar el producto'
  } finally {
    uploading.value = false
    loading.value = false
  }
}

onMounted(loadCategories)
</script>
