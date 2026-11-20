import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import GoodsList from '../views/GoodsList.vue'
import GoodsDetail from '../views/GoodsDetail.vue'
import GoodsPublish from '../views/GoodsPublish.vue'
import MyGoods from '../views/MyGoods.vue'
import Orders from '../views/Orders.vue'
import Admin from '../views/Admin.vue'
import AiChat from '../views/AiChat.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/goods' },
    { path: '/login', component: Login },
    { path: '/goods', component: GoodsList },
    // 静态路径写在参数路径前面，虽然 vue-router 会自动按优先级匹配，但这样读起来更清楚
    { path: '/goods/publish', component: GoodsPublish },
    { path: '/goods/edit/:id', component: GoodsPublish },
    { path: '/goods/:id', component: GoodsDetail },
    { path: '/my-goods', component: MyGoods },
    { path: '/orders', component: Orders },
    { path: '/ai', component: AiChat },
    { path: '/admin', component: Admin, meta: { admin: true } }
  ]
})

// 登录守卫：没有 token 一律回登录页；管理后台再加一道角色校验
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/login') {
    return '/login'
  }
  if (token && to.path === '/login') {
    return '/goods'
  }
  if (to.meta.admin) {
    let role = 0
    try {
      role = JSON.parse(localStorage.getItem('userInfo') || '{}').role || 0
    } catch (e) {
      role = 0
    }
    if (role !== 1) {
      return '/goods'
    }
  }
})

export default router
