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
.list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.item { display: flex; justify-content: space-between; gap: 8px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 10px; background: white; }
.body { min-width: 0; flex: 1; }
.content { margin: 0 0 6px; color: #0f172a; white-space: pre-wrap; word-break: break-word; }
.thumb { max-width: 120px; max-height: 120px; border-radius: 6px; }
.time { margin: 6px 0 0; font-size: 12px; color: #64748b; }
.del { color: #dc2626; background: transparent; border: 0; cursor: pointer; align-self: flex-start; padding: 2px 4px; }
</style>
