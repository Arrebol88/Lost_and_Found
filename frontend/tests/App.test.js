import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'
import { createComment, deleteComment, getPost, listComments, listPosts, toggleLike } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  createPost: vi.fn(),
  listPosts: vi.fn(),
  getPost: vi.fn(),
  toggleLike: vi.fn(),
  listComments: vi.fn(),
  createComment: vi.fn(),
  deleteComment: vi.fn(),
  updatePost: vi.fn(),
  deletePost: vi.fn(),
  imageUrl: p => `/${p}`
}))

vi.mock('../src/auth.js', async () => {
  const { ref } = await import('vue')
  const currentUser = ref(null)
  return {
    currentUser,
    setSession: (token, user) => { currentUser.value = user },
    logout: () => { currentUser.value = null },
    getToken: () => null,
    isAuthed: () => !!currentUser.value,
    __setUser: (u) => { currentUser.value = u },
  }
})

import * as authMock from '../src/auth.js'
function setMockUser(u) { authMock.__setUser ? authMock.__setUser(u) : (authMock.currentUser.value = u) }

describe('App homepage listing', () => {
  beforeEach(() => {
    setMockUser(null)
    listPosts.mockReset()
    listPosts.mockResolvedValue([])
    getPost.mockReset()
    listComments.mockResolvedValue([])
  })

  it('默认加载寻物帖子', async () => {
    mount(App)
    await flushPromises()
    expect(listPosts).toHaveBeenCalledWith({ post_type: 'lost', category: '', time_range: '', location: '' })
  })

  it('底部导航切换到寻主后加载 found', async () => {
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="tab-found"]').trigger('click')
    await flushPromises()
    expect(listPosts).toHaveBeenLastCalledWith({ post_type: 'found', category: '', time_range: '', location: '' })
  })

  it('展示过滤器和发帖按钮', async () => {
    const w = mount(App)
    await flushPromises()
    expect(w.find('[data-testid="filter-category"]').exists()).toBe(true)
    expect(w.find('[data-testid="filter-time"]').exists()).toBe(true)
    expect(w.find('[data-testid="filter-location"]').exists()).toBe(true)
    expect(w.find('[data-testid="btn-create"]').exists()).toBe(true)
  })

  it('点击列表卡片切换到 detail 视图', async () => {
    listPosts.mockResolvedValue([
      { id: 5, title: 'x', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null }
    ])
    getPost.mockResolvedValue({
      id: 5, post_type: 'lost', title: 'x', category: 'daily',
      image_path: null, description: '', location: 'gulou',
      event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
      contact_detail: '...', created_at: '2026-06-13T10:00:00',
      like_count: 0, liked_by_me: false
    })
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="post-card"]').trigger('click')
    await flushPromises()
    expect(w.findComponent({ name: 'PostDetail' }).exists()).toBe(true)
  })

  it('帖子详情发出 back 后刷新首页列表', async () => {
    listPosts.mockResolvedValue([
      { id: 5, title: 'x', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null }
    ])
    getPost.mockResolvedValue({
      id: 5, post_type: 'lost', title: 'x', category: 'daily',
      image_path: null, description: '', location: 'gulou',
      event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
      contact_detail: '...', created_at: '2026-06-13T10:00:00',
      like_count: 0, liked_by_me: false, mine: true
    })
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="post-card"]').trigger('click')
    await flushPromises()
    const before = listPosts.mock.calls.length
    await w.findComponent({ name: 'PostDetail' }).vm.$emit('back')
    await flushPromises()
    expect(listPosts.mock.calls.length).toBeGreaterThan(before)
  })

  it('未登录点击 我要发帖 弹出 AuthDialog', async () => {
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="btn-create"]').trigger('click')
    expect(w.findComponent({ name: 'AuthDialog' }).exists()).toBe(true)
  })

  it('未登录切到 我的帖子 显示登录提示，不调用 listPosts(mine)', async () => {
    const w = mount(App)
    await flushPromises()
    listPosts.mockClear()
    await w.get('[data-testid="tab-mine"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-testid="mine-need-login"]').exists()).toBe(true)
    const mineCalls = listPosts.mock.calls.filter(c => c[0] && c[0].mine === true)
    expect(mineCalls.length).toBe(0)
  })

  it('登录后切到 我的帖子 调 listPosts mine=true', async () => {
    setMockUser({ id: 1, username: 'alice' })
    const w = mount(App)
    await flushPromises()
    listPosts.mockClear()
    await w.get('[data-testid="tab-mine"]').trigger('click')
    await flushPromises()
    expect(listPosts).toHaveBeenLastCalledWith(expect.objectContaining({ mine: true }))
  })
})
