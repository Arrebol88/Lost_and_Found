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
.picker { display: flex; flex-direction: column; gap: var(--sp-3); padding: var(--sp-6) 0; max-width: 480px; margin: 0 auto; }
.picker h2 { font-size: var(--fz-h2); color: var(--text-1); font-weight: 600; margin: 0 0 var(--sp-3); }
.primary { background: var(--accent); color: var(--surface); border: 0; padding: var(--sp-3) var(--sp-5); border-radius: var(--radius-sm); font: inherit; cursor: pointer; text-align: left; }
.primary:hover { background: var(--accent-hover); }
.link { background: transparent; border: 0; color: var(--text-3); cursor: pointer; padding: var(--sp-2) 0; font: inherit; align-self: flex-start; }
.link:hover { color: var(--text-1); }
</style>
