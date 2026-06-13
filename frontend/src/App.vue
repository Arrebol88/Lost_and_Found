<script setup>
import { ref } from 'vue'

const view = ref('home')
const postType = ref(null)

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() { view.value = 'home'; postType.value = null }
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home">
      <button class="primary" data-testid="btn-create" @click="openPicker">发帖</button>
    </section>

    <section v-else-if="view === 'picker'" class="picker">
      <h2>选择帖子类型</h2>
      <button class="primary" @click="pickType('found')">我捡到了东西（寻主帖）</button>
      <button class="primary" @click="pickType('lost')">我丢了东西（寻物帖）</button>
      <button class="link" @click="backHome">返回</button>
    </section>

    <section v-else class="form-wrap">
      <p>表单将在任务 11 实装。当前 post_type = {{ postType }}</p>
      <button class="link" @click="backHome">返回</button>
    </section>
  </main>
</template>

<style>
:root { font-family: system-ui, -apple-system, "PingFang SC", sans-serif; }
.page { max-width: 640px; margin: 0 auto; padding: 32px 16px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; }
.home { display: flex; justify-content: center; padding: 96px 0; }
.picker { display: flex; flex-direction: column; gap: 16px; padding: 32px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.link { background: transparent; border: 0; color: #2563eb; cursor: pointer; padding: 8px 0; }
</style>
