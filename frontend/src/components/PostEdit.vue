<script setup>
import { computed, reactive, ref } from 'vue'
import { imageUrl, updatePost } from '../api.js'

const props = defineProps({ post: { type: Object, required: true } })
const emit = defineEmits(['saved', 'cancel'])

const form = reactive({
  title: props.post.title,
  category: props.post.category,
  description: props.post.description || '',
  location: props.post.location,
  event_time: props.post.event_time ? props.post.event_time.slice(0, 16) : '',
  contact_type: props.post.contact_type,
  contact_detail: props.post.contact_detail
})
const newImage = ref(null)
const removeImage = ref(false)
const submitting = ref(false)
const error = ref('')

const CATEGORIES = [
  ['electronics', '电子产品类'], ['id_card', '个人证件与卡类'], ['bag', '箱包与收纳'],
  ['accessory', '配饰'], ['clothing', '衣物'], ['daily', '日常小件'],
  ['study', '办公与学习'], ['sports', '运动与户外'], ['personal_care', '个人护理与健康']
]
const LOCATIONS = [
  ['gulou', '鼓楼校区'], ['xianlin', '仙林校区'],
  ['suzhou', '苏州校区'], ['pukou', '浦口校区']
]
const CONTACT_TYPES = props.post.post_type === 'lost'
  ? [['owner_contact', '联系方式']]
  : [['self_pickup', '自取'], ['contact', '联系方式'], ['handed_over', '已移交管理处']]

const dirty = computed(() => {
  return form.title !== props.post.title
    || form.category !== props.post.category
    || (form.description || '') !== (props.post.description || '')
    || form.location !== props.post.location
    || form.event_time !== (props.post.event_time ? props.post.event_time.slice(0, 16) : '')
    || form.contact_type !== props.post.contact_type
    || form.contact_detail !== props.post.contact_detail
    || newImage.value !== null
    || removeImage.value === true
})

function onFile(e) {
  const f = e.target.files?.[0] || null
  if (!f) { newImage.value = null; return }
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
    error.value = '图片必须是 jpg/png/webp'
    e.target.value = ''
    newImage.value = null
    return
  }
  if (f.size > 5 * 1024 * 1024) {
    error.value = '图片不能超过 5MB'
    e.target.value = ''
    newImage.value = null
    return
  }
  error.value = ''
  newImage.value = f
}

async function onSave() {
  submitting.value = true
  try {
    const payload = { ...form }
    if (newImage.value) payload.image = newImage.value
    if (removeImage.value && !newImage.value) payload.remove_image = 'true'
    const updated = await updatePost(props.post.id, payload)
    emit('saved', updated)
  } catch (e) {
    error.value = e?.response?.data?.detail || '保存失败'
  } finally {
    submitting.value = false
  }
}

function onCancel() {
  if (dirty.value) {
    if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
      if (!window.confirm('放弃未保存的修改？')) return
    }
  }
  emit('cancel')
}
</script>

<template>
  <section class="edit">
    <header class="bar">
      <h2>编辑帖子</h2>
      <button data-testid="edit-cancel" class="ghost" @click="onCancel">取消</button>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="field">
      <label>物品名称 *</label>
      <input data-testid="edit-title" v-model="form.title" maxlength="50" />
    </div>
    <div class="field">
      <label>物品种类 *</label>
      <select data-testid="edit-category" v-model="form.category">
        <option v-for="[v, t] in CATEGORIES" :key="v" :value="v">{{ t }}</option>
      </select>
    </div>
    <div class="field">
      <label>物品描述</label>
      <textarea v-model="form.description" maxlength="500" rows="3"></textarea>
    </div>
    <div class="field">
      <label>{{ post.post_type === 'lost' ? '丢失地点 *' : '捡到地点 *' }}</label>
      <select data-testid="edit-location" v-model="form.location">
        <option v-for="[v, t] in LOCATIONS" :key="v" :value="v">{{ t }}</option>
      </select>
    </div>
    <div class="field">
      <label>{{ post.post_type === 'lost' ? '丢失时间 *' : '捡到时间 *' }}</label>
      <input type="datetime-local" v-model="form.event_time" />
    </div>
    <div class="field">
      <label>联系方式类型 *</label>
      <select v-model="form.contact_type">
        <option v-for="[v, t] in CONTACT_TYPES" :key="v" :value="v">{{ t }}</option>
      </select>
    </div>
    <div class="field">
      <label>{{ post.post_type === 'lost' ? '联系方式 *' : '联系方式具体描述 *' }}</label>
      <input v-model="form.contact_detail" maxlength="200" />
    </div>
    <div class="field">
      <label>图片</label>
      <img v-if="post.image_path && !newImage && !removeImage" :src="imageUrl(post.image_path)" class="thumb" alt="物品图片" />
      <label v-if="post.image_path" class="checkbox">
        <input type="checkbox" v-model="removeImage" />
        移除当前图片
      </label>
      <input type="file" accept="image/jpeg,image/png,image/webp" @change="onFile" />
    </div>

    <button data-testid="edit-save" class="primary" :disabled="submitting" @click="onSave">保存</button>
  </section>
</template>

<style scoped>
.edit { max-width: 720px; margin: 0 auto; padding: 16px; }
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.bar h2 { margin: 0; }
.ghost { background: transparent; border: 1px solid #cbd5e1; padding: 4px 12px; border-radius: 6px; cursor: pointer; }
.error { color: #dc2626; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.field label { font-size: 14px; color: #475569; }
.field input, .field select, .field textarea { padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font: inherit; }
.thumb { max-width: 160px; border-radius: 6px; }
.checkbox { display: inline-flex; align-items: center; gap: 4px; }
.primary { background: #2563eb; color: white; border: 0; padding: 10px 18px; border-radius: 8px; cursor: pointer; }
.primary:disabled { background: #94a3b8; cursor: not-allowed; }
</style>
