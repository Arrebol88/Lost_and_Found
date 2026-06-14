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
    <div class="cover">
      <img v-if="post.image_path" :src="imageUrl(post.image_path)" alt="物品图片" />
      <span v-else class="placeholder">无图片</span>
    </div>
    <div class="body">
      <h3 class="title">{{ post.title }}</h3>
      <div class="meta">
        <span>{{ LOCATION_TEXT[post.location] || post.location }}</span>
        <span class="dot">·</span>
        <span>{{ formatTime(post.event_time) }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card { display: flex; flex-direction: column; background: var(--surface); border-radius: var(--radius-md); box-shadow: var(--shadow-card); cursor: pointer; transition: transform 160ms ease-out, box-shadow 160ms ease-out; overflow: hidden; }
.card:hover { transform: translateY(-2px); box-shadow: var(--shadow-pop); }
.card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.cover { aspect-ratio: 4 / 3; background: var(--surface-2); display: flex; align-items: center; justify-content: center; }
.cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cover .placeholder { color: var(--text-3); font-size: var(--fz-meta); }
.body { padding: var(--sp-3) var(--sp-4) var(--sp-4); display: flex; flex-direction: column; gap: var(--sp-2); }
.title { color: var(--text-1); font-size: var(--fz-body); font-weight: 600; line-height: 1.3; margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta { color: var(--text-3); font-size: var(--fz-meta); display: flex; gap: var(--sp-2); align-items: center; }
.meta .dot { color: var(--border-strong); }
</style>
