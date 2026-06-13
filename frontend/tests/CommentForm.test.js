import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CommentForm from '../src/components/CommentForm.vue'

describe('CommentForm', () => {
  it('内容为空时按钮 disabled', () => {
    const w = mount(CommentForm)
    expect(w.get('[data-testid="comment-submit"]').attributes('disabled')).toBeDefined()
  })

  it('填写后点击 emit submit', async () => {
    const w = mount(CommentForm)
    await w.get('textarea').setValue('我也见过')
    await w.get('[data-testid="comment-submit"]').trigger('click')
    expect(w.emitted().submit[0][0]).toEqual({ content: '我也见过', image: null })
  })
})
