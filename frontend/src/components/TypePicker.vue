<script setup>
const emit = defineEmits(['pick', 'cancel'])
</script>

<template>
  <div class="picker">
    <h2>选择帖子类型</h2>
    <button class="primary" data-testid="btn-found" @click="emit('pick', 'found')">
      我捡到了东西（寻主帖）
    </button>
    <button class="primary" data-testid="btn-lost" @click="emit('pick', 'lost')">
      我丢了东西（寻物帖）
    </button>
    <button class="link" data-testid="btn-cancel" @click="emit('cancel')">返回</button>
  </div>
</template>

<style scoped>
.picker { display: flex; flex-direction: column; gap: 16px; padding: 32px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.link { background: transparent; border: 0; color: #2563eb; cursor: pointer; padding: 8px 0; }
</style>
