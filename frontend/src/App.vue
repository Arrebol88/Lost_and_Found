<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import TypePicker from './components/TypePicker.vue'
import PostForm from './components/PostForm.vue'
import PostFilters from './components/PostFilters.vue'
import PostList from './components/PostList.vue'
import PostDetail from './components/PostDetail.vue'
import AuthDialog from './components/AuthDialog.vue'
import { createPost, listPosts } from './api.js'
import { currentUser, logout, setSession } from './auth.js'

const view = ref('home')
const postType = ref(null)
const activeTab = ref('lost')
const filters = ref({ category: '', time_range: '', location: '' })
const posts = ref([])
const loading = ref(false)
const submitting = ref(false)
const selectedPostId = ref(null)
const showAuth = ref(false)

const isMineTab = computed(() => activeTab.value === 'mine')

function openPicker() {
  if (!currentUser.value) {
    showAuth.value = true
    return
  }
  view.value = 'picker'
}
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
    if (isMineTab.value) {
      if (!currentUser.value) {
        posts.value = []
      } else {
        posts.value = await listPosts({ mine: true, ...filters.value })
      }
    } else {
      posts.value = await listPosts({ post_type: activeTab.value, ...filters.value })
    }
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

function onAuthSuccess({ token, user }) {
  setSession(token, user)
  showAuth.value = false
  loadPosts()
}

function onLogout() {
  logout()
  if (isMineTab.value) posts.value = []
}

function onRequireAuth() {
  showAuth.value = true
}

onMounted(loadPosts)
watch([activeTab, filters, currentUser], loadPosts, { deep: true })
</script>

<template>
  <main class="page">
    <header class="hero">
      <div class="hero-text">
        <h1>南哪寻宝</h1>
        <div class="sub">校园丢失 / 拾得物匿名汇集</div>
      </div>
      <div v-if="view === 'home'" class="hero-actions">
        <button class="btn-ghost" @click="loadPosts">刷新</button>
        <button class="btn-primary" data-testid="btn-create" @click="openPicker">我要发帖</button>
        <template v-if="currentUser">
          <span class="user-chip" data-testid="user-chip">{{ currentUser.username }}</span>
          <button class="btn-ghost" data-testid="btn-logout" @click="onLogout">登出</button>
        </template>
        <template v-else>
          <button class="btn-ghost" data-testid="btn-login" @click="showAuth = true">登录 / 注册</button>
        </template>
      </div>
    </header>

    <section v-if="view === 'home'" class="home">
      <nav class="tabs">
        <button data-testid="tab-lost" :class="{ active: activeTab === 'lost' }" @click="switchTab('lost')">寻物</button>
        <button data-testid="tab-found" :class="{ active: activeTab === 'found' }" @click="switchTab('found')">寻主</button>
        <button data-testid="tab-mine" :class="{ active: activeTab === 'mine' }" @click="switchTab('mine')">我的帖子</button>
      </nav>

      <template v-if="isMineTab && !currentUser">
        <div class="empty-auth" data-testid="mine-need-login">
          请先登录后查看你发布的帖子
          <button class="btn-primary" @click="showAuth = true">登录 / 注册</button>
        </div>
      </template>
      <template v-else>
        <PostFilters v-if="!isMineTab" :filters="filters" @update:filters="filters = $event" />
        <PostList :posts="posts" :loading="loading" @select="onSelectPost" />
      </template>
    </section>

    <PostDetail
      v-else-if="view === 'detail' && selectedPostId !== null"
      :post-id="selectedPostId"
      @back="onDetailBack"
      @require-auth="onRequireAuth"
    />

    <TypePicker v-else-if="view === 'picker'"
                @pick="pickType" @cancel="backHome" />

    <PostForm v-else
              :post-type="postType"
              @submit="onSubmit"
              @cancel="backHome" />

    <AuthDialog
      v-if="showAuth"
      @success="onAuthSuccess"
      @close="showAuth = false"
    />
  </main>
</template>

<style scoped>
.page { max-width: 1080px; margin: 0 auto; padding: var(--sp-6) var(--sp-5) var(--sp-7); }
.hero { display: flex; align-items: flex-end; justify-content: space-between; gap: var(--sp-5); margin-bottom: var(--sp-6); }
.hero-text h1 { font-size: var(--fz-display); color: var(--text-1); margin: 0 0 var(--sp-2); font-weight: 600; line-height: 1.3; }
.hero-text .sub { font-size: var(--fz-meta); color: var(--text-3); }
.hero-actions { display: flex; gap: var(--sp-3); align-items: center; flex-wrap: wrap; }
.btn-primary { background: var(--accent); color: var(--surface); border: 0; padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); cursor: pointer; font: inherit; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-ghost { background: var(--surface-2); color: var(--text-1); border: 1px solid var(--border-strong); padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); cursor: pointer; font: inherit; }
.btn-ghost:hover { border-color: var(--text-3); }
.user-chip {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: var(--sp-2) var(--sp-3);
  font-size: var(--fz-meta);
  color: var(--text-2);
}

.tabs { display: inline-flex; gap: var(--sp-1); padding: var(--sp-1); background: var(--surface-2); border-radius: var(--radius-sm); margin-bottom: var(--sp-4); }
.tabs button { background: transparent; border: 0; padding: var(--sp-2) var(--sp-5); font: inherit; font-size: var(--fz-meta); color: var(--text-3); cursor: pointer; border-radius: var(--radius-sm); transition: 160ms; }
.tabs button.active { background: var(--surface); color: var(--accent); box-shadow: var(--shadow-card); font-weight: 600; }
.tabs button:hover:not(.active) { color: var(--text-1); }

.empty-auth {
  border: 1px dashed var(--border-strong);
  background: var(--surface);
  color: var(--text-2);
  border-radius: var(--radius-md);
  padding: var(--sp-6);
  text-align: center;
  display: flex; flex-direction: column; gap: var(--sp-4); align-items: center;
  margin-top: var(--sp-2);
}

@media (max-width: 640px) {
  .page { padding: var(--sp-5) var(--sp-4) var(--sp-6); }
  .hero { flex-direction: column; align-items: flex-start; }
  .hero-actions { width: 100%; }
  .btn-primary, .btn-ghost { flex: 1; }
}
</style>
