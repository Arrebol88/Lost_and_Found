<script setup>
import { imageUrl } from '../api.js'

defineProps({ items: { type: Array, required: true } })
const emit = defineEmits(['delete'])

function fmt(t) {
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<template>
  <ul class="list">
    <li v-for="c in items" :key="c.id" class="item">
      <div class="body">
        <p class="content">{{ c.content }}</p>
        <img v-if="c.image_path" :src="imageUrl(c.image_path)" alt="评论图片" class="thumb" />
        <p class="time">{{ fmt(c.created_at) }}</p>
      </div>
      <button
        v-if="c.mine"
        :data-testid="`comment-del-${c.id}`"
        class="del"
        @click="emit('delete', c.id)"
      >删除</button>
    </li>
  </ul>
</template>

<style scoped>
.list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; }
.item { display: flex; justify-content: space-between; gap: var(--sp-3); padding: var(--sp-4) 0; border-bottom: 1px solid var(--border); }
.item:last-child { border-bottom: 0; }
.body { min-width: 0; flex: 1; }
.content { margin: 0 0 var(--sp-2); color: var(--text-2); white-space: pre-wrap; word-break: break-word; line-height: 1.7; }
.thumb { width: 56px; height: 56px; border-radius: var(--radius-sm); object-fit: cover; }
.time { margin: var(--sp-1) 0 0; font-size: var(--fz-meta); color: var(--text-3); }
.del { color: var(--text-3); background: transparent; border: 0; cursor: pointer; align-self: flex-start; padding: var(--sp-1) var(--sp-2); font: inherit; font-size: var(--fz-mini); opacity: 0; transition: opacity 160ms; }
.item:hover .del { opacity: 1; }
.del:hover { color: var(--danger); }
</style>
