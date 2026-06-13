import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TypePicker from '../src/components/TypePicker.vue'

describe('TypePicker', () => {
  it('点击寻主帖按钮 emit found', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-found"]').trigger('click')
    expect(w.emitted().pick[0]).toEqual(['found'])
  })

  it('点击寻物帖按钮 emit lost', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-lost"]').trigger('click')
    expect(w.emitted().pick[0]).toEqual(['lost'])
  })

  it('点击返回 emit cancel', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-cancel"]').trigger('click')
    expect(w.emitted().cancel).toBeTruthy()
  })
})
