import { ref } from 'vue'

const TOKEN_KEY = 'nju_token'
const USER_KEY = 'nju_user'

function readUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const currentUser = ref(readUser())

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || null
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  currentUser.value = user
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  currentUser.value = null
}

export function isAuthed() {
  return !!getToken()
}
