import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PostDetail from '../src/components/PostDetail.vue'
import { deletePost, getPost, listComments } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  getPost: vi.fn(),
  toggleLike: vi.fn(),
  listComments: vi.fn(),
  createComment: vi.fn(),
  deleteComment: vi.fn(),
  updatePost: vi.fn(),
  deletePost: vi.fn(),
  imageUrl: p => `/${p}`
}))

const baseMine = {
  id: 1, post_type: 'lost', title: '黑色雨伞', category: 'daily',
  image_path: null, description: '长柄', location: 'gulou',
  event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
  contact_detail: '微信 abc123', created_at: '2026-06-13T10:00:00',
  like_count: 0, liked_by_me: false, mine: true
}

describe('PostDetail edit/delete entry', () => {
  beforeEach(() => {
    getPost.mockResolvedValue({ ...baseMine })
    listComments.mockResolvedValue([])
    deletePost.mockReset()
  })

  it('mine=false 不显示编辑/删除按钮', async () => {
    getPost.mockResolvedValue({ ...baseMine, mine: false })
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    expect(w.find('[data-testid="post-edit"]').exists()).toBe(false)
    expect(w.find('[data-testid="post-delete"]').exists()).toBe(false)
  })

  it('mine=true 点击编辑切到 edit 模式', async () => {
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    await w.get('[data-testid="post-edit"]').trigger('click')
    expect(w.findComponent({ name: 'PostEdit' }).exists()).toBe(true)
  })

  it('删除二次确认通过后调用 deletePost 并 emit back', async () => {
    deletePost.mockResolvedValue()
    const spy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    await w.get('[data-testid="post-delete"]').trigger('click')
    await flushPromises()
    expect(deletePost).toHaveBeenCalledWith(1)
    expect(w.emitted().back).toBeTruthy()
    spy.mockRestore()
  })

  it('删除二次确认拒绝时不调用 deletePost', async () => {
    const spy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    await w.get('[data-testid="post-delete"]').trigger('click')
    await flushPromises()
    expect(deletePost).not.toHaveBeenCalled()
    spy.mockRestore()
  })
})
