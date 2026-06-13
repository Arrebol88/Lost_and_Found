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

describe('App homepage listing', () => {
  beforeEach(() => {
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
})
