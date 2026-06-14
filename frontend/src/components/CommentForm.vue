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
.comment-form { display: flex; flex-direction: column; gap: var(--sp-3); padding: var(--sp-4); margin-bottom: var(--sp-4); background: var(--surface-2); border-radius: var(--radius-md); }
textarea { padding: var(--sp-3); background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); resize: vertical; min-height: 64px; font: inherit; color: var(--text-1); }
textarea:focus { outline: none; border-color: var(--accent); }
input[type="file"] { font-size: var(--fz-meta); color: var(--text-3); }
.primary { background: var(--accent); color: var(--surface); border: 0; padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); align-self: flex-start; cursor: pointer; font: inherit; font-size: var(--fz-meta); }
.primary:hover:not(:disabled) { background: var(--accent-hover); }
.primary:disabled { background: var(--border-strong); cursor: not-allowed; }
.error { color: var(--danger); font-size: var(--fz-meta); margin: 0; }
</style>
