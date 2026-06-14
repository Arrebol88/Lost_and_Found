import axios from 'axios'
import { getToken, logout } from './auth.js'

// 开发态走 vite 代理（baseURL 空）；生产态默认指向 8000，可通过 VITE_API_BASE 注入
const baseURL = import.meta.env.PROD
  ? (import.meta.env.VITE_API_BASE || 'http://localhost:8000')
  : ''
const http = axios.create({ baseURL })

http.interceptors.request.use((cfg) => {
  cfg.headers = cfg.headers || {}
  const token = getToken()
  if (token) {
    cfg.headers['Authorization'] = `Bearer ${token}`
  }
  return cfg
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err && err.response && err.response.status === 401) {
      logout()
    }
    return Promise.reject(err)
  }
)

export async function register(username, password) {
  const r = await http.post('/api/auth/register', { username, password })
  return r.data
}

export async function login(username, password) {
  const r = await http.post('/api/auth/login', { username, password })
  return r.data
}

export async function fetchMe() {
  const r = await http.get('/api/auth/me')
  return r.data
}

export async function createPost(form) {
  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return
    fd.append(k, v)
  })
  const r = await http.post('/api/posts', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return r.data
}

export async function listPosts(filters) {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== '' && v !== null && v !== undefined && v !== false)
  )
  const r = await http.get('/api/posts', { params })
  return r.data
}

export async function getPost(id) {
  const r = await http.get(`/api/posts/${id}`)
  return r.data
}

export async function toggleLike(id) {
  const r = await http.post(`/api/posts/${id}/likes`)
  return r.data
}

export async function listComments(postId) {
  const r = await http.get(`/api/posts/${postId}/comments`)
  return r.data
}

export async function createComment(postId, { content, image }) {
  const fd = new FormData()
  fd.append('content', content)
  if (image) fd.append('image', image)
  const r = await http.post(`/api/posts/${postId}/comments`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return r.data
}

export async function deleteComment(id) {
  await http.delete(`/api/comments/${id}`)
}

export async function updatePost(id, form) {
  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return
    fd.append(k, v)
  })
  const r = await http.put(`/api/posts/${id}`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return r.data
}

export async function deletePost(id) {
  await http.delete(`/api/posts/${id}`)
}

export function imageUrl(path) {
  if (!path) return ''
  if (import.meta.env.PROD) return `${baseURL}/${path}`
  return `/${path}`
}
