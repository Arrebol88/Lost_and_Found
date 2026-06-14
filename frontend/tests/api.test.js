import { describe, it, expect } from 'vitest'
import * as api from '../src/api.js'

describe('post update/delete API surface', () => {
  it('暴露 updatePost 与 deletePost', () => {
    expect(typeof api.updatePost).toBe('function')
    expect(typeof api.deletePost).toBe('function')
  })
})

describe('auth API surface', () => {
  it('暴露 register / login / fetchMe', () => {
    expect(typeof api.register).toBe('function')
    expect(typeof api.login).toBe('function')
    expect(typeof api.fetchMe).toBe('function')
  })
})
