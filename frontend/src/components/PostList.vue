<script setup>
import PostCard from './PostCard.vue'

defineProps({
  posts: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})
</script>

<template>
  <div class="list">
    <p v-if="loading" class="state">加载中...</p>
    <p v-else-if="posts.length === 0" class="state">暂无帖子</p>
    <PostCard v-else v-for="post in posts" :key="post.id" :post="post" />
  </div>
</template>

<style scoped>
.list { display: flex; flex-direction: column; gap: 10px; }
.state { text-align: center; color: #64748b; padding: 40px 0; }
</style>
