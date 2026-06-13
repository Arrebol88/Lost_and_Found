<script setup>
import { onMounted, ref } from 'vue'
import {
  createComment,
  deleteComment,
  deletePost,
  getPost,
  imageUrl,
  listComments,
  toggleLike
} from '../api.js'
import CommentForm from './CommentForm.vue'
import CommentList from './CommentList.vue'
import PostEdit from './PostEdit.vue'

const props = defineProps({ postId: { type: Number, required: true } })
const emit = defineEmits(['back'])

const post = ref(null)
const comments = ref([])
const showContact = ref(false)
const error = ref('')
const mode = ref('view')

const LOCATION_TEXT = {
  gulou: '鼓楼校区',
  xianlin: '仙林校区',
  suzhou: '苏州校区',
  pukou: '浦口校区'
}
const CATEGORY_TEXT = {
  electronics: '电子产品类',
  id_card: '个人证件与卡类',
  bag: '箱包与收纳',
  accessory: '配饰',
  clothing: '衣物',
  daily: '日常小件',
  study: '办公与学习',
  sports: '运动与户外',
  personal_care: '个人护理与健康'
}
const CONTACT_TEXT = {
  self_pickup: '自取',
  contact: '联系方式',
  handed_over: '已移交管理处',
  owner_contact: '联系失主'
}

function fmt(t) {
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadAll() {
  try {
    post.value = await getPost(props.postId)
    comments.value = await listComments(props.postId)
  } catch (e) {
    if (e?.response?.status === 404) {
      error.value = '帖子不存在或已被删除'
    } else {
      error.value = '加载失败，请稍后再试'
    }
  }
}

async function onLike() {
  if (!post.value) return
  try {
    const r = await toggleLike(props.postId)
    post.value.liked_by_me = r.liked
    post.value.like_count = r.like_count
  } catch (e) {
    error.value = '点赞失败，请稍后再试'
  }
}

async function onSubmitComment(payload) {
  try {
    await createComment(props.postId, payload)
    comments.value = await listComments(props.postId)
  } catch (e) {
    error.value = '评论发表失败，请稍后再试'
  }
}

async function onDeleteComment(id) {
  if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
    if (!window.confirm('确认删除这条评论？')) return
  }
  try {
    await deleteComment(id)
    comments.value = await listComments(props.postId)
  } catch (e) {
    error.value = '删除失败，请稍后再试'
  }
}

function onEdit() { mode.value = 'edit' }
function onCancelEdit() { mode.value = 'view' }
function onSaved(updated) {
  post.value = updated
  mode.value = 'view'
}
async function onDeletePost() {
  if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
    if (!window.confirm('确认删除该帖子？此操作不可恢复')) return
  }
  try {
    await deletePost(props.postId)
    emit('back')
  } catch (e) {
    error.value = '删除失败，请稍后再试'
  }
}

onMounted(loadAll)
</script>

<template>
  <section class="detail">
    <header class="bar">
      <button class="back" @click="emit('back')">返回</button>
      <div v-if="post && post.mine && mode === 'view'" class="actions">
        <button data-testid="post-edit" class="ghost" @click="onEdit">编辑</button>
        <button data-testid="post-delete" class="danger" @click="onDeletePost">删除</button>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <template v-if="mode === 'view'">
    <article v-if="post" class="post">
      <h2>{{ post.title }}</h2>
      <p class="meta">
        <span class="tag">{{ post.post_type === 'lost' ? '寻物帖' : '寻主帖' }}</span>
        <span>{{ CATEGORY_TEXT[post.category] || post.category }}</span>
        <span>{{ LOCATION_TEXT[post.location] || post.location }}</span>
        <span>{{ fmt(post.event_time) }}</span>
      </p>
      <img v-if="post.image_path" :src="imageUrl(post.image_path)" alt="物品图片" class="hero" />
      <p v-if="post.description" class="desc">{{ post.description }}</p>

      <div class="contact">
        <p>联系方式类型：{{ CONTACT_TEXT[post.contact_type] || post.contact_type }}</p>
        <button
          v-if="!showContact"
          data-testid="reveal-contact"
          class="link"
          @click="showContact = true"
        >查看联系方式</button>
        <p v-else class="contact-detail">{{ post.contact_detail }}</p>
      </div>

      <div class="like-row">
        <button data-testid="like-btn" class="like" @click="onLike">
          {{ post.liked_by_me ? '已点赞' : '点赞' }}
        </button>
        <span data-testid="like-count" class="like-count">{{ post.like_count }}</span>
      </div>
    </article>

    <section v-if="post" class="comments">
      <h3>评论</h3>
      <CommentForm @submit="onSubmitComment" />
      <CommentList :items="comments" @delete="onDeleteComment" />
    </section>
    </template>
    <PostEdit v-else-if="post" :post="post" @saved="onSaved" @cancel="onCancelEdit" />
  </section>
</template>

<style scoped>
.detail { max-width: 720px; margin: 0 auto; padding: 16px; }
.bar { display: flex; margin-bottom: 12px; }
.bar { justify-content: space-between; align-items: center; }
.actions { display: flex; gap: 8px; }
.ghost { background: transparent; border: 1px solid #cbd5e1; padding: 4px 12px; border-radius: 6px; cursor: pointer; }
.danger { background: #dc2626; color: white; border: 0; padding: 4px 12px; border-radius: 6px; cursor: pointer; }
.back { background: transparent; border: 1px solid #cbd5e1; padding: 4px 12px; border-radius: 6px; cursor: pointer; }
.error { color: #dc2626; }
.post { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.post h2 { margin: 0 0 8px; color: #0f172a; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; color: #64748b; font-size: 13px; margin: 0 0 12px; }
.tag { background: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 999px; font-size: 12px; }
.hero { max-width: 100%; border-radius: 8px; margin-bottom: 12px; }
.desc { color: #0f172a; white-space: pre-wrap; word-break: break-word; }
.contact { padding: 12px 0; border-top: 1px dashed #e2e8f0; border-bottom: 1px dashed #e2e8f0; margin: 12px 0; }
.contact p { margin: 4px 0; }
.contact-detail { font-weight: 600; color: #0f172a; }
.link { background: transparent; border: 0; color: #2563eb; padding: 0; cursor: pointer; font: inherit; }
.like-row { display: flex; align-items: center; gap: 12px; }
.like { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 6px 16px; border-radius: 999px; cursor: pointer; }
.like-count { color: #0f172a; font-weight: 600; }
.comments { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; }
.comments h3 { margin: 0 0 8px; }
</style>
