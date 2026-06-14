<script setup>
import PostCard from './PostCard.vue'

defineProps({
  posts: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})
const emit = defineEmits(['select'])
</script>

<template>
  <div>
    <p v-if="loading" class="state">加载中...</p>
    <p v-else-if="posts.length === 0" class="state empty">暂无帖子</p>
    <div v-else class="grid">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @select="(id) => emit('select', id)"
      />
    </div>
  </div>
</template>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sp-5); }
@media (max-width: 1024px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px)  { .grid { grid-template-columns: 1fr; gap: var(--sp-4); } }
.state { text-align: center; color: var(--text-3); padding: var(--sp-7) 0; font-size: var(--fz-meta); }
.empty { border: 1px dashed var(--border-strong); border-radius: var(--radius-md); padding: var(--sp-6) var(--sp-5); }
</style>
