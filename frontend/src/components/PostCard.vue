<script setup>
import { imageUrl } from '../api.js'

const props = defineProps({ post: { type: Object, required: true } })
const emit = defineEmits(['select'])

const LOCATION_TEXT = {
  gulou: '鼓楼校区',
  xianlin: '仙林校区',
  suzhou: '苏州校区',
  pukou: '浦口校区'
}

function formatTime(value) {
  const d = new Date(value)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function onActivate() {
  emit('select', props.post.id)
}
</script>

<template>
  <article
    class="card"
    data-testid="post-card"
    role="button"
    tabindex="0"
    @click="onActivate"
    @keydown.enter="onActivate"
  >
    <img v-if="post.image_path" class="thumb" :src="imageUrl(post.image_path)" alt="物品图片" />
    <div class="content">
      <h3>{{ post.title }}</h3>
      <p>{{ LOCATION_TEXT[post.location] || post.location }}</p>
      <p>{{ formatTime(post.event_time) }}</p>
    </div>
  </article>
</template>

<style scoped>
.card { display: flex; gap: 12px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; background: white; cursor: pointer; }
.card:hover { border-color: #93c5fd; }
.thumb { width: 72px; height: 72px; object-fit: cover; border-radius: 8px; flex: 0 0 auto; }
.content { min-width: 0; }
h3 { margin: 0 0 8px; font-size: 16px; color: #0f172a; }
p { margin: 4px 0; font-size: 13px; color: #64748b; }
</style>
