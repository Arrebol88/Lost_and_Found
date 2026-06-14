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
import { currentUser } from '../auth.js'

const props = defineProps({ postId: { type: Number, required: true } })
const emit = defineEmits(['back', 'require-auth'])

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
  if (!currentUser.value) { emit('require-auth'); return }
  try {
    const r = await toggleLike(props.postId)
    post.value.liked_by_me = r.liked
    post.value.like_count = r.like_count
  } catch (e) {
    error.value = '点赞失败，请稍后再试'
  }
}

async function onSubmitComment(payload) {
  if (!currentUser.value) { emit('require-auth'); return }
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
      <button class="back" @click="emit('back')">← 返回</button>
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
        <span class="tag" :class="post.post_type">{{ post.post_type === 'lost' ? '寻物帖' : '寻主帖' }}</span>
        <span>{{ CATEGORY_TEXT[post.category] || post.category }}</span>
        <span class="dot">·</span>
        <span>{{ LOCATION_TEXT[post.location] || post.location }}</span>
        <span class="dot">·</span>
        <span>{{ fmt(post.event_time) }}</span>
        <template v-if="post.author_username">
          <span class="dot">·</span>
          <span class="author" data-testid="post-author">作者：{{ post.author_username }}</span>
        </template>
      </p>
      <img v-if="post.image_path" :src="imageUrl(post.image_path)" alt="物品图片" class="hero" />
      <p v-if="post.description" class="desc">{{ post.description }}</p>

      <div class="contact">
        <p class="contact-type">联系方式类型：{{ CONTACT_TEXT[post.contact_type] || post.contact_type }}</p>
        <button
          v-if="!showContact"
          data-testid="reveal-contact"
          class="contact-toggle"
          @click="showContact = true"
        >查看联系方式</button>
        <p v-else class="contact-detail">{{ post.contact_detail }}</p>
      </div>

      <div class="like-row">
        <button data-testid="like-btn" class="like" :class="{ liked: post.liked_by_me }" @click="onLike">
          <span class="heart">♥</span>
          <span>{{ post.liked_by_me ? '已点赞' : '点赞' }}</span>
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
.detail { max-width: 720px; margin: 0 auto; padding: var(--sp-5); }
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--sp-5); }
.actions { display: flex; gap: var(--sp-2); }
.back, .ghost, .danger { background: var(--surface); border: 1px solid var(--border-strong); padding: var(--sp-1) var(--sp-3); border-radius: var(--radius-sm); cursor: pointer; color: var(--text-2); font: inherit; font-size: var(--fz-meta); }
.back:hover, .ghost:hover { border-color: var(--text-3); }
.danger:hover { color: var(--danger); border-color: var(--danger); }
.error { color: var(--danger); font-size: var(--fz-meta); margin-bottom: var(--sp-3); }

.post { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--sp-6); margin-bottom: var(--sp-5); }
.post h2 { font-size: var(--fz-display); color: var(--text-1); margin: 0 0 var(--sp-3); line-height: 1.3; font-weight: 600; }
.meta { display: flex; flex-wrap: wrap; gap: var(--sp-2); align-items: center; color: var(--text-3); font-size: var(--fz-meta); margin: 0 0 var(--sp-5); }
.meta .dot { color: var(--border-strong); }
.tag { padding: 2px var(--sp-2); border-radius: var(--radius-sm); font-size: var(--fz-mini); font-weight: 500; }
.tag.lost { background: var(--lost-tag-bg); color: var(--lost-tag-fg); }
.tag.found { background: var(--found-tag-bg); color: var(--found-tag-fg); }
.hero { max-width: 100%; border-radius: var(--radius-md); margin-bottom: var(--sp-5); }
.desc { color: var(--text-2); white-space: pre-wrap; word-break: break-word; line-height: 1.7; margin: 0 0 var(--sp-5); }

.contact { background: var(--surface-2); border-radius: var(--radius-md); padding: var(--sp-4); margin-bottom: var(--sp-5); }
.contact-type { margin: 0 0 var(--sp-2); color: var(--text-2); font-size: var(--fz-meta); }
.contact-toggle { display: inline-block; padding: var(--sp-2) var(--sp-4); border: 1px dashed var(--border-strong); background: transparent; border-radius: var(--radius-sm); color: var(--text-3); font: inherit; font-size: var(--fz-meta); cursor: pointer; }
.contact-toggle:hover { color: var(--text-1); border-color: var(--text-3); }
.contact-detail { margin: 0; color: var(--text-1); font-weight: 500; }

.like-row { display: flex; align-items: center; gap: var(--sp-2); padding-top: var(--sp-4); border-top: 1px solid var(--border); }
.like { background: transparent; border: 0; cursor: pointer; color: var(--text-3); font: inherit; display: inline-flex; align-items: center; gap: var(--sp-1); padding: var(--sp-1) var(--sp-2); border-radius: var(--radius-sm); transition: 160ms; }
.like:hover { color: var(--text-1); }
.like.liked { color: var(--accent); }
.like .heart { font-size: 16px; }
.like-count { color: var(--text-3); font-size: var(--fz-meta); }

.comments { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--sp-6); }
.comments h3 { margin: 0 0 var(--sp-4); font-size: var(--fz-h2); color: var(--text-1); font-weight: 600; }

@media (max-width: 640px) {
  .detail { padding: var(--sp-4); }
  .post, .comments { padding: var(--sp-4); }
}
</style>
