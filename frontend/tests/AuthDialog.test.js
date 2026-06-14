import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import AuthDialog from '../src/components/AuthDialog.vue'
import * as api from '../src/api.js'

vi.mock('../src/api.js', () => ({
  register: vi.fn(),
  login: vi.fn(),
}))

describe('AuthDialog', () => {
  beforeEach(() => {
    api.register.mockReset()
    api.login.mockReset()
  })

  it('登录成功后 emit success 携带 token+user', async () => {
    api.login.mockResolvedValue({ token: 'tk', user: { id: 1, username: 'alice' } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-username"]').setValue('alice')
    await w.get('[data-testid="auth-password"]').setValue('hunter2')
    await w.get('[data-testid="auth-submit"]').trigger('click')
    await flushPromises()
    expect(api.login).toHaveBeenCalledWith('alice', 'hunter2')
    expect(w.emitted().success[0][0].user.username).toBe('alice')
  })

  it('切到注册 tab 后调用 register', async () => {
    api.register.mockResolvedValue({ token: 'tk', user: { id: 2, username: 'bob' } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-tab-register"]').trigger('click')
    await w.get('[data-testid="auth-username"]').setValue('bob')
    await w.get('[data-testid="auth-password"]').setValue('hunter2')
    await w.get('[data-testid="auth-submit"]').trigger('click')
    await flushPromises()
    expect(api.register).toHaveBeenCalledWith('bob', 'hunter2')
  })

  it('后端 detail 错误显示给用户', async () => {
    api.login.mockRejectedValue({ response: { data: { detail: '用户名或密码错误' } } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-username"]').setValue('alice')
    await w.get('[data-testid="auth-password"]').setValue('wrong')
    await w.get('[data-testid="auth-submit"]').trigger('click')
    await flushPromises()
    expect(w.get('[data-testid="auth-error"]').text()).toBe('用户名或密码错误')
  })

  it('点击取消 emit close', async () => {
    const w = mount(AuthDialog)
    await w.get('.btn-ghost').trigger('click')
    expect(w.emitted().close).toBeTruthy()
  })
})
