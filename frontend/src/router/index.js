import { createRouter, createWebHashHistory } from 'vue-router'

// 注意：由于是单页应用 + 弹窗模式，路由主要用于管理不同页面
// 打字主界面始终显示，弹窗通过事件总线控制
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/App.vue'),
    meta: { title: '打字游戏' }
  },
  {
    path: '/vocabulary',
    name: 'Vocabulary',
    component: () => import('@/components/Dialogs/VocabularyTable.vue'),
    meta: { title: '单词表', dialog: true }
  },
  {
    path: '/mistake',
    name: 'Mistake',
    component: () => import('@/components/Dialogs/MistakeTable.vue'),
    meta: { title: '错词表', dialog: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/components/Dialogs/SettingsPanel.vue'),
    meta: { title: '设置', dialog: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 打字游戏`
  }
  next()
})

export default router