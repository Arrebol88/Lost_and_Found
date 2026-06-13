import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'
import { listPosts } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  createPost: vi.fn(),
  listPosts: vi.fn(),
  imageUrl: p => `/${p}`
}))

describe('App homepage listing', () => {
  beforeEach(() => {
    listPosts.mockResolvedValue([])
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
})
