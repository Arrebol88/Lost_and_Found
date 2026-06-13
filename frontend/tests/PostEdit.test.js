import { describe, it, expect, beforeEach, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PostEdit from '../src/components/PostEdit.vue'
import { updatePost } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  updatePost: vi.fn(),
  imageUrl: p => `/${p}`
}))

const POST = {
  id: 1, post_type: 'lost', title: '黑色雨伞', category: 'daily',
  image_path: 'uploads/a.png', description: '长柄', location: 'gulou',
  event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
  contact_detail: '微信 abc123', created_at: '2026-06-13T10:00:00',
  like_count: 0, liked_by_me: false, mine: true
}

describe('PostEdit', () => {
  beforeEach(() => { updatePost.mockReset() })

  it('表单预填当前帖子内容', () => {
    const w = mount(PostEdit, { props: { post: POST } })
    expect(w.get('[data-testid="edit-title"]').element.value).toBe('黑色雨伞')
    expect(w.get('[data-testid="edit-location"]').element.value).toBe('gulou')
  })

  it('保存调用 updatePost 并 emit saved', async () => {
    updatePost.mockResolvedValue({ ...POST, title: '新标题' })
    const w = mount(PostEdit, { props: { post: POST } })
    await w.get('[data-testid="edit-title"]').setValue('新标题')
    await w.get('[data-testid="edit-save"]').trigger('click')
    await flushPromises()
    expect(updatePost).toHaveBeenCalled()
    const [, payload] = updatePost.mock.calls[0]
    expect(payload.title).toBe('新标题')
    expect(w.emitted().saved[0][0].title).toBe('新标题')
  })

  it('取消按钮无修改时直接 emit cancel', async () => {
    const w = mount(PostEdit, { props: { post: POST } })
    await w.get('[data-testid="edit-cancel"]').trigger('click')
    expect(w.emitted().cancel).toBeTruthy()
  })
})
