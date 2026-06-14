<script setup>
import { ref } from 'vue'
import { register as apiRegister, login as apiLogin } from '../api.js'

const emit = defineEmits(['success', 'close'])

const mode = ref('login')
const username = ref('')
const password = ref('')
const errorMsg = ref('')
const submitting = ref(false)

async function onSubmit() {
  if (submitting.value) return
  errorMsg.value = ''
  if (!username.value.trim() || !password.value) {
    errorMsg.value = '请输入用户名与密码'
    return
  }
  submitting.value = true
  try {
    const action = mode.value === 'login' ? apiLogin : apiRegister
    const data = await action(username.value.trim(), password.value)
    emit('success', data)
  } catch (err) {
    const detail = err && err.response && err.response.data && err.response.data.detail
    errorMsg.value = typeof detail === 'string'
      ? detail
      : (mode.value === 'login' ? '登录失败' : '注册失败')
  } finally {
    submitting.value = false
  }
}

function switchTo(target) {
  mode.value = target
  errorMsg.value = ''
}

function onKeyDown(e) {
  if (e.key === 'Escape') emit('close')
}
</script>

<template>
  <div class="auth-mask" @click.self="$emit('close')" @keydown="onKeyDown" tabindex="0">
    <div class="auth-dialog" role="dialog" aria-label="登录或注册">
      <div class="tabs">
        <button
          type="button"
          class="tab"
          :class="{ active: mode === 'login' }"
          data-testid="auth-tab-login"
          @click="switchTo('login')"
        >登录</button>
        <button
          type="button"
          class="tab"
          :class="{ active: mode === 'register' }"
          data-testid="auth-tab-register"
          @click="switchTo('register')"
        >注册</button>
      </div>

      <label class="field">
        <span>用户名</span>
        <input
          v-model="username"
          type="text"
          autofocus
          autocomplete="username"
          data-testid="auth-username"
          @keyup.enter="onSubmit"
        />
      </label>
      <label class="field">
        <span>密码</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          data-testid="auth-password"
          @keyup.enter="onSubmit"
        />
      </label>

      <p v-if="errorMsg" class="error" data-testid="auth-error">{{ errorMsg }}</p>

      <div class="actions">
        <button type="button" class="btn-ghost" @click="$emit('close')">取消</button>
        <button
          type="button"
          class="btn-primary"
          :disabled="submitting || !username.trim() || !password"
          data-testid="auth-submit"
          @click="onSubmit"
        >{{ mode === 'login' ? '登录' : '注册' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-mask {
  position: fixed; inset: 0;
  background: rgba(31, 27, 22, 0.32);
  display: grid; place-items: center;
  z-index: 1000;
}
.auth-dialog {
  width: min(92vw, 360px);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-pop);
  padding: var(--sp-5);
  display: flex; flex-direction: column; gap: var(--sp-4);
}
.tabs { display: flex; gap: var(--sp-2); border-bottom: 1px solid var(--border); padding-bottom: var(--sp-2); }
.tab {
  background: transparent;
  border: none;
  padding: var(--sp-2) var(--sp-3);
  color: var(--text-3);
  font-size: var(--fz-body);
  cursor: pointer;
  border-radius: var(--radius-sm);
}
.tab.active { color: var(--text-1); background: var(--surface-2); }
.field { display: flex; flex-direction: column; gap: var(--sp-1); font-size: var(--fz-meta); color: var(--text-2); }
.field input {
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  padding: var(--sp-2) var(--sp-3);
  font-size: var(--fz-body);
  background: var(--surface);
  color: var(--text-1);
}
.field input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.error { color: var(--danger); font-size: var(--fz-meta); margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: var(--sp-2); }
.btn-primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--sp-2) var(--sp-4);
  font-size: var(--fz-body);
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
.btn-ghost {
  background: var(--surface-2);
  color: var(--text-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: var(--sp-2) var(--sp-4);
  font-size: var(--fz-body);
  cursor: pointer;
}
</style>
