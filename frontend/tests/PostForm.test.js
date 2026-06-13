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

  it('地点字段是校区 select', () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    const location = w.get('[data-testid="location"]')
    expect(location.element.tagName).toBe('SELECT')
    expect(location.text()).toContain('鼓楼校区')
    expect(location.text()).toContain('仙林校区')
    expect(location.text()).toContain('苏州校区')
    expect(location.text()).toContain('浦口校区')
  })

  it('found 类型联系方式描述 label 更明确', () => {
    const w = mount(PostForm, { props: { postType: 'found' } })
    expect(w.text()).toContain('联系方式具体描述 *')
  })

  it('lost 类型补齐字段后 emit submit 含 owner_contact', async () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    await w.get('[data-testid="title"]').setValue('黑色雨伞')
    await w.get('[data-testid="category"]').setValue('daily')
    await w.get('[data-testid="location"]').setValue('gulou')
    await w.get('[data-testid="event-time"]').setValue('2026-06-12T18:30')
    await w.get('[data-testid="contact-detail"]').setValue('微信 abc123')
    await w.get('form').trigger('submit.prevent')
    expect(w.emitted().submit).toBeTruthy()
    const payload = w.emitted().submit[0][0]
    expect(payload.contact_type).toBe('owner_contact')
    expect(payload.post_type).toBe('lost')
    expect(payload.location).toBe('gulou')
  })
})
