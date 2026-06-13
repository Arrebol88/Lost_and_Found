import { describe, it, expect, beforeEach } from 'vitest'
import * as api from '../src/api.js'
import { ensureAnonId } from '../src/api.js'

describe('ensureAnonId', () => {
  beforeEach(() => { localStorage.clear() })

  it('首次调用生成并持久化 UUID', () => {
    const id = ensureAnonId()
    expect(id).toMatch(/^[0-9a-f-]{36}$/i)
    expect(localStorage.getItem('nju_anon_id')).toBe(id)
  })

  it('已有则复用', () => {
    localStorage.setItem('nju_anon_id', 'cccccccc-cccc-cccc-cccc-cccccccccccc')
    expect(ensureAnonId()).toBe('cccccccc-cccc-cccc-cccc-cccccccccccc')
  })
})

describe('post update/delete API surface', () => {
  it('暴露 updatePost 与 deletePost', () => {
    expect(typeof api.updatePost).toBe('function')
    expect(typeof api.deletePost).toBe('function')
  })
})
