<script setup>
const props = defineProps({ filters: { type: Object, required: true } })
const emit = defineEmits(['update:filters'])

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

const TIME_RANGES = [
  ['within_1d', '一天以内'],
  ['within_3d', '三天以内'],
  ['within_7d', '七天以内'],
  ['older_than_7d', '七天以外']
]

const LOCATIONS = [
  ['gulou', '鼓楼校区'],
  ['xianlin', '仙林校区'],
  ['suzhou', '苏州校区'],
  ['pukou', '浦口校区']
]

function update(key, value) {
  emit('update:filters', { ...props.filters, [key]: value })
}
</script>

<template>
  <div class="filters">
    <label>物品种类
      <select data-testid="filter-category" :value="filters.category" @change="update('category', $event.target.value)">
        <option value="">全部</option>
        <option v-for="[v, t] in CATEGORIES" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>
    <label>丢失/捡到时间
      <select data-testid="filter-time" :value="filters.time_range" @change="update('time_range', $event.target.value)">
        <option value="">全部</option>
        <option v-for="[v, t] in TIME_RANGES" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>
    <label>丢失/捡到地点
      <select data-testid="filter-location" :value="filters.location" @change="update('location', $event.target.value)">
        <option value="">全部</option>
        <option v-for="[v, t] in LOCATIONS" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>
  </div>
</template>

<style scoped>
.filters { display: flex; flex-wrap: wrap; gap: var(--sp-3) var(--sp-4); padding: var(--sp-3) var(--sp-4); margin-bottom: var(--sp-4); background: var(--surface-2); border-radius: var(--radius-md); }
.filters label { display: inline-flex; align-items: center; gap: var(--sp-2); font-size: var(--fz-meta); color: var(--text-2); }
.filters select { background: var(--surface); color: var(--text-1); border: 1px solid var(--border-strong); border-radius: var(--radius-sm); padding: var(--sp-1) var(--sp-3); font: inherit; font-size: var(--fz-meta); cursor: pointer; }
.filters select:hover { border-color: var(--text-3); }
.filters select:focus { border-color: var(--accent); outline: none; }
</style>
