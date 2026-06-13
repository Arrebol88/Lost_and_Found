<script setup>
import { ref } from 'vue'
import TypePicker from './components/TypePicker.vue'
import PostForm from './components/PostForm.vue'
import { createPost } from './api.js'

const view = ref('home')
const postType = ref(null)
const submitting = ref(false)

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() { view.value = 'home'; postType.value = null }

async function onSubmit(payload) {
  submitting.value = true
  try {
    await createPost(payload)
    alert('发布成功')
    backHome()
  } catch (e) {
    const detail = e?.response?.data?.detail || '提交失败，请稍后重试'
    alert(detail)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home">
      <button class="primary" data-testid="btn-create" @click="openPicker">发帖</button>
    </section>

    <TypePicker v-else-if="view === 'picker'"
                @pick="pickType" @cancel="backHome" />

    <PostForm v-else
              :post-type="postType"
              @submit="onSubmit"
              @cancel="backHome" />
  </main>
</template>

<style>
:root { font-family: system-ui, -apple-system, "PingFang SC", sans-serif; }
.page { max-width: 640px; margin: 0 auto; padding: 32px 16px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.home { display: flex; justify-content: center; padding: 96px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
</style>
