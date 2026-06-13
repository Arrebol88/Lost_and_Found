<script setup>
import { computed, ref } from 'vue'

const emit = defineEmits(['submit'])

const content = ref('')
const image = ref(null)
const error = ref('')

const disabled = computed(() => content.value.trim().length === 0)

function onFile(e) {
  const f = e.target.files?.[0] || null
  if (!f) {
    image.value = null
    error.value = ''
    return
  }
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
    error.value = '图片必须是 jpg/png/webp'
    e.target.value = ''
    image.value = null
    return
  }
  if (f.size > 5 * 1024 * 1024) {
    error.value = '图片不能超过 5MB'
    e.target.value = ''
    image.value = null
    return
  }
  error.value = ''
  image.value = f
}

function onSubmit() {
  if (disabled.value) return
  emit('submit', { content: content.value.trim(), image: image.value })
  content.value = ''
  image.value = null
}
</script>

<template>
  <div class="comment-form">
    <textarea
      v-model="content"
      maxlength="200"
      rows="2"
      placeholder="写点什么..."
    ></textarea>
    <input type="file" accept="image/jpeg,image/png,image/webp" @change="onFile" />
    <p v-if="error" class="error">{{ error }}</p>
    <button
      data-testid="comment-submit"
      :disabled="disabled"
      class="primary"
      @click="onSubmit"
    >评论</button>
  </div>
</template>

<style scoped>
.comment-form { display: flex; flex-direction: column; gap: 8px; padding: 12px 0; }
textarea { padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px; resize: vertical; font: inherit; }
.primary { background: #2563eb; color: white; border: 0; padding: 8px 16px; border-radius: 6px; align-self: flex-start; cursor: pointer; }
.primary:disabled { background: #94a3b8; cursor: not-allowed; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
</style>
