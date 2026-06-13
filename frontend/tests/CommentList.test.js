import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CommentList from '../src/components/CommentList.vue'

describe('CommentList', () => {
  const items = [
    { id: 1, content: 'mine', image_path: null, created_at: '2026-06-13T10:00:00', mine: true },
    { id: 2, content: 'other', image_path: null, created_at: '2026-06-13T09:00:00', mine: false }
  ]

  it('仅给 mine 评论展示删除按钮', () => {
    const w = mount(CommentList, { props: { items } })
    const buttons = w.findAll('[data-testid^="comment-del-"]')
    expect(buttons.length).toBe(1)
    expect(buttons[0].attributes('data-testid')).toBe('comment-del-1')
  })

  it('点击删除 emit delete 含 id', async () => {
    const w = mount(CommentList, { props: { items } })
    await w.get('[data-testid="comment-del-1"]').trigger('click')
    expect(w.emitted().delete[0][0]).toBe(1)
  })
})
