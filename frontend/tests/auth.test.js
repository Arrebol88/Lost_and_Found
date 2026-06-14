import { describe, it, expect, beforeEach } from 'vitest'
import { setSession, getToken, currentUser, logout, isAuthed } from '../src/auth.js'

describe('auth session store', () => {
  beforeEach(() => {
    localStorage.clear()
    logout()
  })

  it('setSession 后 getToken/currentUser 可读', () => {
    setSession('tk', { id: 1, username: 'alice' })
    expect(getToken()).toBe('tk')
    expect(currentUser.value).toEqual({ id: 1, username: 'alice' })
    expect(isAuthed()).toBe(true)
  })

  it('logout 清空 token 与 user', () => {
    setSession('tk', { id: 1, username: 'a' })
    logout()
    expect(getToken()).toBe(null)
    expect(currentUser.value).toBe(null)
    expect(isAuthed()).toBe(false)
  })
})
