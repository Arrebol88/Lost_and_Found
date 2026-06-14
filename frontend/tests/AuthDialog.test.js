import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import AuthDialog from '../src/components/AuthDialog.vue'
import * as api from '../src/api.js'

vi.mock('../src/api.js', () => ({
  register: vi.fn(),
  login: vi.fn(),
}))

async function fillAndSubmit(w, { username, password }) {
  await w.get('[data-testid="auth-username"]').setValue(username)
  await w.get('[data-testid="auth-password"]').setValue(password)
  await w.get('form').trigger('submit')
  await flushPromises()
}

describe('AuthDialog', () => {
  beforeEach(() => {
    api.register.mockReset()
    api.login.mockReset()
  })

  it('登录成功后 emit success 携带 token+user', async () => {
    api.login.mockResolvedValue({ token: 'tk', user: { id: 1, username: 'alice' } })
    const w = mount(AuthDialog)
    await fillAndSubmit(w, { username: 'alice', password: 'hunter2' })
    expect(api.login).toHaveBeenCalledWith('alice', 'hunter2')
    expect(w.emitted().success[0][0].user.username).toBe('alice')
  })

  it('切到注册 tab 后调用 register', async () => {
    api.register.mockResolvedValue({ token: 'tk', user: { id: 2, username: 'bob' } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-tab-register"]').trigger('click')
    await fillAndSubmit(w, { username: 'bob', password: 'hunter2' })
    expect(api.register).toHaveBeenCalledWith('bob', 'hunter2')
  })

  it('后端 detail 错误显示给用户', async () => {
    api.login.mockRejectedValue({ response: { data: { detail: '用户名或密码错误' } } })
    const w = mount(AuthDialog)
    await fillAndSubmit(w, { username: 'alice', password: 'wrong' })
    expect(w.get('[data-testid="auth-error"]').text()).toBe('用户名或密码错误')
  })

  it('注册时密码 < 6 位本地校验阻断（不调用 API）', async () => {
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-tab-register"]').trigger('click')
    await fillAndSubmit(w, { username: 'bob', password: '123' })
    expect(api.register).not.toHaveBeenCalled()
    expect(w.get('[data-testid="auth-error"]').text()).toContain('至少 6 位')
  })

  it('后端 422 数组型 detail 友好展示', async () => {
    api.login.mockRejectedValue({
      response: {
        data: {
          detail: [{ loc: ['body', 'password'], msg: 'String should have at least 6 characters', type: 'string_too_short' }]
        }
      }
    })
    const w = mount(AuthDialog)
    await fillAndSubmit(w, { username: 'alice', password: 'hunter2' })
    const text = w.get('[data-testid="auth-error"]').text()
    expect(text).toMatch(/密码不合法/)
  })

  it('点击取消 emit close', async () => {
    const w = mount(AuthDialog)
    await w.get('.btn-ghost').trigger('click')
    expect(w.emitted().close).toBeTruthy()
  })
})
