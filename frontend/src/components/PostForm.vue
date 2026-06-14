<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ postType: { type: String, required: true } })
const emit = defineEmits(['submit', 'cancel'])

const CATEGORIES = [
  ['electronics', '电子产品类'],
  ['id_card', '个人证件与卡类'],
  ['bag', '箱包与收纳'],
  ['accessory', '配饰'],
  ['clothing', '衣物'],
  ['daily', '日常小件'],
  ['study', '办公与学习'],
  ['sports', '运动与户外'],
  ['personal_care', '个人护理与健康']
]

const LOCATIONS = [
  ['gulou', '鼓楼校区'],
  ['xianlin', '仙林校区'],
  ['suzhou', '苏州校区'],
  ['pukou', '浦口校区']
]

const FOUND_OPTIONS = [
  ['self_pickup', '自取'],
  ['contact', '联系方式'],
  ['handed_over', '已移交管理处']
]

const title = ref('')
const category = ref('')
const location = ref('')
const eventTime = ref('')
const description = ref('')
const contactType = ref(props.postType === 'lost' ? 'owner_contact' : 'self_pickup')
const contactDetail = ref('')
const imageFile = ref(null)
const error = ref('')

const maxTime = computed(() => {
  const d = new Date()
  d.setSeconds(0, 0)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
})

function onFile(e) {
  const f = e.target.files?.[0] || null
  if (!f) { imageFile.value = null; return }
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
    error.value = '图片必须是 jpg/png/webp'
    e.target.value = ''
    return
  }
  if (f.size > 5 * 1024 * 1024) {
    error.value = '图片不能超过 5MB'
    e.target.value = ''
    return
  }
  error.value = ''
  imageFile.value = f
}

function validate() {
  if (!title.value.trim()) return '请填写物品名称'
  if (title.value.length > 50) return '物品名称不能超过 50 字'
  if (!category.value) return '请选择物品种类'
  if (!location.value) return '请选择地点'
  if (!eventTime.value) return '请选择时间'
  if (!contactDetail.value.trim()) return '请填写联系方式描述'
  return ''
}

function onSubmit() {
  const msg = validate()
  if (msg) { error.value = msg; return }
  error.value = ''
  emit('submit', {
    post_type: props.postType,
    title: title.value,
    category: category.value,
    description: description.value || null,
    location: location.value,
    event_time: eventTime.value,
    contact_type: contactType.value,
    contact_detail: contactDetail.value,
    image: imageFile.value
  })
}
</script>

<template>
  <form class="form" @submit.prevent="onSubmit">
    <h2>{{ postType === 'lost' ? '寻物帖' : '寻主帖' }}</h2>

    <label>物品名称 *
      <input data-testid="title" v-model="title" maxlength="50" />
    </label>

    <label>物品种类 *
      <select data-testid="category" v-model="category">
        <option value="" disabled>请选择</option>
        <option v-for="[v, t] in CATEGORIES" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>

    <label>物品图片
      <input type="file" accept="image/jpeg,image/png,image/webp" @change="onFile" />
    </label>

    <label>物品描述
      <textarea v-model="description" maxlength="500" rows="3" />
    </label>

    <label>{{ postType === 'lost' ? '丢失' : '捡到' }}地点 *
      <select data-testid="location" v-model="location">
        <option value="" disabled>请选择</option>
        <option v-for="[v, t] in LOCATIONS" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>

    <label>{{ postType === 'lost' ? '丢失' : '捡到' }}时间 *
      <input data-testid="event-time" type="datetime-local" v-model="eventTime" :max="maxTime" />
    </label>

    <fieldset v-if="postType === 'found'" data-testid="contact-options">
      <legend>联系方式 *</legend>
      <label v-for="[v, t] in FOUND_OPTIONS" :key="v" class="radio">
        <input type="radio" :data-testid="`ct-${v}`" :value="v" v-model="contactType" />
        {{ t }}
      </label>
    </fieldset>

    <label>{{ postType === 'lost' ? '联系方式 *' : '联系方式具体描述 *' }}
      <textarea data-testid="contact-detail" v-model="contactDetail" maxlength="200" rows="2" />
    </label>

    <p v-if="error" class="error" data-testid="error">{{ error }}</p>

    <div class="actions">
      <button type="submit" class="primary">提交</button>
      <button type="button" class="link" @click="emit('cancel')">取消</button>
    </div>
  </form>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: var(--sp-3); padding: var(--sp-4) 0; max-width: 720px; margin: 0 auto; }
.form > label { display: flex; flex-direction: column; gap: var(--sp-1); font-size: var(--fz-meta); color: var(--text-2); }
.form input, .form select, .form textarea {
  padding: var(--sp-2) var(--sp-3); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-sm); font: inherit; color: var(--text-1);
}
.form input:focus, .form select:focus, .form textarea:focus { outline: none; border-color: var(--accent); }
fieldset { border: 1px solid var(--border-strong); border-radius: var(--radius-sm); padding: var(--sp-2) var(--sp-3); color: var(--text-2); font-size: var(--fz-meta); }
fieldset .radio { display: flex; flex-direction: row; align-items: center; gap: var(--sp-2); }
.error { color: var(--danger); font-size: var(--fz-meta); }
.actions { display: flex; gap: var(--sp-3); margin-top: var(--sp-3); }
.primary { background: var(--accent); color: var(--surface); border: 0; padding: var(--sp-3) var(--sp-5); border-radius: var(--radius-sm); cursor: pointer; font: inherit; }
.primary:hover:not(:disabled) { background: var(--accent-hover); }
.primary:disabled { background: var(--border-strong); cursor: not-allowed; }
.link { background: transparent; border: 0; color: var(--text-3); cursor: pointer; font: inherit; }
.link:hover { color: var(--text-1); }
</style>
