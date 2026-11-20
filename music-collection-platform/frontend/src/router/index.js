import { createRouter, createWebHashHistory } from 'vue-router'

// Electron 通过 file:// 加载页面，必须使用 hash 路由
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { public: true } },
    { path: '/register', name: 'register', component: () => import('../views/Register.vue'), meta: { public: true } },
    {
      path: '/',
      component: () => import('../layout/index.vue'),
      redirect: '/home',
      children: [
        { path: 'home', name: 'home', component: () => import('../views/Home.vue'), meta: { title: '概览' } },
        { path: 'playlists', name: 'playlists', component: () => import('../views/Playlists.vue'), meta: { title: '我的歌单' } },
        { path: 'playlists/:id', name: 'playlist-detail', component: () => import('../views/PlaylistDetail.vue'), meta: { title: '歌单详情' } },
        { path: 'songs', name: 'songs', component: () => import('../views/Songs.vue'), meta: { title: '全部歌曲' } },
        { path: 'tags', name: 'tags', component: () => import('../views/Tags.vue'), meta: { title: '标签管理' } },
        { path: 'profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { title: '个人中心' } },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('../views/Admin.vue'),
          meta: { title: '管理后台', admin: true }
        }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' }
  ]
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  if (!localStorage.getItem('mc_token')) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin) {
    try {
      const info = JSON.parse(localStorage.getItem('mc_user') || 'null')
      if (info?.role !== 'admin') return { path: '/home' }
    } catch {
      return { path: '/home' }
    }
  }
  return true
})

export default router
