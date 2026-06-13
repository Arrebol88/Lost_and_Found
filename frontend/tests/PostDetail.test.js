import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PostDetail from '../src/components/PostDetail.vue'
import { getPost, toggleLike, listComments, createComment, deleteComment } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  getPost: vi.fn(),
  toggleLike: vi.fn(),
  listComments: vi.fn(),
  createComment: vi.fn(),
  deleteComment: vi.fn(),
  imageUrl: p => `/${p}`
}))

const POST = {
  id: 1,
  post_type: 'lost',
  title: '黑色雨伞',
  category: 'daily',
  image_path: null,
  description: '长柄',
  location: 'gulou',
  event_time: '2026-06-12T18:30:00',
  contact_type: 'owner_contact',
  contact_detail: '微信 abc123',
  created_at: '2026-06-13T10:00:00',
  like_count: 1,
  liked_by_me: false
}

describe('PostDetail', () => {
  beforeEach(() => {
    getPost.mockReset()
    toggleLike.mockReset()
    listComments.mockReset()
    createComment.mockReset()
    deleteComment.mockReset()
    getPost.mockResolvedValue({ ...POST })
    listComments.mockResolvedValue([])
  })

  it('默认隐藏 contact_detail 直到点击查看', async () => {
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    expect(w.text()).not.toContain('微信 abc123')
    await w.get('[data-testid="reveal-contact"]').trigger('click')
    expect(w.text()).toContain('微信 abc123')
  })

  it('点赞按钮切换数字与状态', async () => {
    toggleLike.mockResolvedValueOnce({ liked: true, like_count: 2 })
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    await w.get('[data-testid="like-btn"]').trigger('click')
    await flushPromises()
    expect(w.get('[data-testid="like-count"]').text()).toBe('2')
    expect(w.get('[data-testid="like-btn"]').text()).toContain('已点赞')
  })

  it('提交评论后调用 createComment 并刷新列表', async () => {
    createComment.mockResolvedValue({
      id: 9, post_id: 1, content: '我也见过', image_path: null,
      created_at: '2026-06-13T11:00:00', mine: true
    })
    listComments.mockResolvedValueOnce([])
    listComments.mockResolvedValueOnce([
      { id: 9, post_id: 1, content: '我也见过', image_path: null,
        created_at: '2026-06-13T11:00:00', mine: true }
    ])
    const w = mount(PostDetail, { props: { postId: 1 } })
    await flushPromises()
    await w.get('textarea').setValue('我也见过')
    await w.get('[data-testid="comment-submit"]').trigger('click')
    await flushPromises()
    expect(createComment).toHaveBeenCalledWith(1, { content: '我也见过', image: null })
    expect(w.text()).toContain('我也见过')
  })
})
