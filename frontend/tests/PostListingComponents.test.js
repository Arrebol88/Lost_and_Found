import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PostFilters from '../src/components/PostFilters.vue'
import PostCard from '../src/components/PostCard.vue'
import PostList from '../src/components/PostList.vue'

describe('PostFilters', () => {
  it('渲染三个过滤器且默认全部', async () => {
    const w = mount(PostFilters, { props: { filters: { category: '', time_range: '', location: '' } } })
    expect(w.find('[data-testid="filter-category"]').exists()).toBe(true)
    expect(w.find('[data-testid="filter-time"]').exists()).toBe(true)
    expect(w.find('[data-testid="filter-location"]').exists()).toBe(true)
    expect(w.get('[data-testid="filter-category"]').element.value).toBe('')
    expect(w.text()).toContain('全部')
  })

  it('修改过滤器时 emit update:filters', async () => {
    const w = mount(PostFilters, { props: { filters: { category: '', time_range: '', location: '' } } })
    await w.get('[data-testid="filter-location"]').setValue('gulou')
    expect(w.emitted()['update:filters'][0][0]).toEqual({ category: '', time_range: '', location: 'gulou' })
  })
})

describe('PostCard', () => {
  const post = {
    title: '黑色耳机',
    location: 'xianlin',
    event_time: '2026-06-12T18:30:00',
    image_path: 'uploads/a.png'
  }

  it('只展示卡片摘要字段', () => {
    const w = mount(PostCard, { props: { post } })
    expect(w.text()).toContain('黑色耳机')
    expect(w.text()).toContain('仙林校区')
    expect(w.text()).toContain('2026-06-12 18:30')
    expect(w.find('img').attributes('src')).toBe('/uploads/a.png')
    expect(w.text()).not.toContain('联系方式')
  })

  it('点击卡片 emit select 含 post.id', async () => {
    const w = mount(PostCard, { props: { post: { id: 7, title: 't', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null } } })
    await w.get('[data-testid="post-card"]').trigger('click')
    expect(w.emitted().select[0][0]).toBe(7)
  })
})

describe('PostList', () => {
  it('无数据时显示空状态', () => {
    const w = mount(PostList, { props: { posts: [], loading: false } })
    expect(w.text()).toContain('暂无帖子')
  })

  it('加载中显示提示', () => {
    const w = mount(PostList, { props: { posts: [], loading: true } })
    expect(w.text()).toContain('加载中')
  })

  it('渲染帖子卡片', () => {
    const posts = [{ id: 1, title: '雨伞', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null }]
    const w = mount(PostList, { props: { posts, loading: false } })
    expect(w.text()).toContain('雨伞')
    expect(w.text()).toContain('鼓楼校区')
  })
})
