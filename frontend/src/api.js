import axios from 'axios'

const http = axios.create({ baseURL: '' })

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
