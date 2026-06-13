<script setup>
import { onMounted, ref, watch } from 'vue'
import TypePicker from './components/TypePicker.vue'
import PostForm from './components/PostForm.vue'
import PostFilters from './components/PostFilters.vue'
import PostList from './components/PostList.vue'
import PostDetail from './components/PostDetail.vue'
import { createPost, listPosts } from './api.js'

const view = ref('home')
const postType = ref(null)
const activeTab = ref('lost')
const filters = ref({ category: '', time_range: '', location: '' })
const posts = ref([])
const loading = ref(false)
const submitting = ref(false)
const selectedPostId = ref(null)

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() {
  view.value = 'home'
  postType.value = null
  selectedPostId.value = null
}

async function onDetailBack() {
  backHome()
  await loadPosts()
}

function onSelectPost(id) {
  selectedPostId.value = id
  view.value = 'detail'
}

async function loadPosts() {
  loading.value = true
  try {
    posts.value = await listPosts({ post_type: activeTab.value, ...filters.value })
  } catch (e) {
    posts.value = []
  } finally {
    loading.value = false
  }
}

function switchTab(type) {
  activeTab.value = type
}

async function onSubmit(payload) {
  submitting.value = true
  try {
    await createPost(payload)
    alert('发布成功')
    backHome()
    await loadPosts()
  } catch (e) {
    const detail = e?.response?.data?.detail || '提交失败，请稍后重试'
    alert(detail)
  } finally {
    submitting.value = false
  }
}

onMounted(loadPosts)
watch([activeTab, filters], loadPosts, { deep: true })
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home">
      <PostFilters :filters="filters" @update:filters="filters = $event" />
      <PostList :posts="posts" :loading="loading" @select="onSelectPost" />
      <button class="primary floating" data-testid="btn-create" @click="openPicker">发帖</button>
      <nav class="bottom-nav">
        <button data-testid="tab-lost" :class="{ active: activeTab === 'lost' }" @click="switchTab('lost')">寻物</button>
        <button data-testid="tab-found" :class="{ active: activeTab === 'found' }" @click="switchTab('found')">寻主</button>
      </nav>
    </section>

    <PostDetail
      v-else-if="view === 'detail' && selectedPostId !== null"
      :post-id="selectedPostId"
      @back="onDetailBack"
    />

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
body { margin: 0; background: #f8fafc; }
.page { max-width: 640px; margin: 0 auto; padding: 24px 16px 88px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.home { position: relative; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.floating { position: fixed; right: max(16px, calc((100vw - 640px) / 2 + 16px)); bottom: 76px; box-shadow: 0 8px 20px #1e293b33; }
.bottom-nav { position: fixed; left: 0; right: 0; bottom: 0; display: flex; justify-content: center; background: white; border-top: 1px solid #e2e8f0; }
.bottom-nav button { width: min(50%, 320px); padding: 14px 0; border: 0; background: white; color: #64748b; font-size: 15px; cursor: pointer; }
.bottom-nav button.active { color: #2563eb; font-weight: 700; }
</style>
