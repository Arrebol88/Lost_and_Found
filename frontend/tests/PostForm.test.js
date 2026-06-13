import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PostForm from '../src/components/PostForm.vue'

describe('PostForm', () => {
  it('lost 类型只渲染联系方式文本框', () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    expect(w.find('[data-testid="contact-options"]').exists()).toBe(false)
    expect(w.find('[data-testid="contact-detail"]').exists()).toBe(true)
  })

  it('found 类型渲染 3 个 contact_type 单选', () => {
    const w = mount(PostForm, { props: { postType: 'found' } })
    expect(w.find('[data-testid="contact-options"]').exists()).toBe(true)
    expect(w.findAll('[data-testid^="ct-"]').length).toBe(3)
  })

  it('未填必填项时点提交不会 emit submit', async () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    await w.get('form').trigger('submit.prevent')
    expect(w.emitted().submit).toBeFalsy()
    expect(w.find('[data-testid="error"]').exists()).toBe(true)
  })

  it('lost 类型补齐字段后 emit submit 含 owner_contact', async () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    await w.get('[data-testid="title"]').setValue('黑色雨伞')
    await w.get('[data-testid="category"]').setValue('daily')
    await w.get('[data-testid="location"]').setValue('B201')
    await w.get('[data-testid="event-time"]').setValue('2026-06-12T18:30')
    await w.get('[data-testid="contact-detail"]').setValue('微信 abc123')
    await w.get('form').trigger('submit.prevent')
    expect(w.emitted().submit).toBeTruthy()
    const payload = w.emitted().submit[0][0]
    expect(payload.contact_type).toBe('owner_contact')
    expect(payload.post_type).toBe('lost')
  })
})
