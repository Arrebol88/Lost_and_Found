import axios from 'axios'

// 开发态走 vite 代理（baseURL 空），生产态浏览器直接访问后端 8000
const baseURL = import.meta.env.PROD ? 'http://localhost:8000' : ''
const http = axios.create({ baseURL })

export function ensureAnonId() {
  let id = localStorage.getItem('nju_anon_id')
  if (!id) {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      id = crypto.randomUUID()
    } else {
      id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0
        const v = c === 'x' ? r : (r & 0x3) | 0x8
        return v.toString(16)
      })
    }
    localStorage.setItem('nju_anon_id', id)
  }
  return id
}

http.interceptors.request.use((cfg) => {
  cfg.headers = cfg.headers || {}
  cfg.headers['X-Anon-Id'] = ensureAnonId()
  return cfg
})

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
    Object.entries(filters).filter(([, v]) => v !== '' && v !== null && v !== undefined)
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

export function imageUrl(path) {
  if (!path) return ''
  if (import.meta.env.PROD) return `${baseURL}/${path}`
  return `/${path}`
}
