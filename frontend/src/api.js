import axios from 'axios'

// 开发态走 vite 代理（baseURL 空），生产态浏览器直接访问后端 8000
const baseURL = import.meta.env.PROD ? 'http://localhost:8000' : ''
const http = axios.create({ baseURL })

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

export function imageUrl(path) {
  if (!path) return ''
  if (import.meta.env.PROD) return `${baseURL}/${path}`
  return `/${path}`
}
