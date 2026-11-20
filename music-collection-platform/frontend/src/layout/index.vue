<template>
  <el-container class="layout">
    <el-aside width="216px" class="aside">
      <div class="logo">
        <div class="logo-icon">♪</div>
        <div>
          <div class="logo-text">音乐收藏</div>
          <div class="logo-sub">MUSIC COLLECTION</div>
        </div>
      </div>

      <el-menu :default-active="activeMenu" router class="menu">
        <el-menu-item index="/home"><el-icon><House /></el-icon><span>概览</span></el-menu-item>
        <el-menu-item index="/playlists"><el-icon><List /></el-icon><span>我的歌单</span></el-menu-item>
        <el-menu-item index="/songs"><el-icon><Headset /></el-icon><span>全部歌曲</span></el-menu-item>
        <el-menu-item index="/tags"><el-icon><PriceTag /></el-icon><span>标签管理</span></el-menu-item>
        <el-menu-item index="/profile"><el-icon><User /></el-icon><span>个人中心</span></el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/admin">
          <el-icon><Setting /></el-icon><span>管理后台</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-foot">纯净 · 无广告 · 专注收藏</div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">{{ route.meta.title || '音乐收藏管理' }}</div>
        <div class="header-right">
          <el-tag v-if="userStore.isAdmin" type="danger" effect="light" size="small">管理员</el-tag>
          <el-dropdown @command="onCommand">
            <span class="user-chip">
              <el-avatar :size="28" :src="userStore.info?.avatar || ''" class="avatar">
                {{ (userStore.info?.nickname || 'U').charAt(0) }}
              </el-avatar>
              <span>{{ userStore.info?.nickname || '未登录' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile"><el-icon><User /></el-icon>个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() =>
  route.path.startsWith('/playlists/') ? '/playlists' : route.path
)

onMounted(() => {
  // 同步最新的角色 / 资料，失败时由请求拦截器统一处理
  userStore.fetchMe().catch(() => {})
})

async function onCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    } catch {
      return
    }
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout { height: 100%; }
.aside {
  background: #fff; border-right: 1px solid var(--mc-border);
  display: flex; flex-direction: column; padding: 0 12px;
}
.logo { display: flex; align-items: center; gap: 12px; padding: 24px 12px 26px; }
.logo-icon {
  width: 38px; height: 38px; border-radius: 11px; color: #fff; font-size: 22px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, #7c6bf5, #b39dfb);
  box-shadow: 0 6px 14px rgba(124, 107, 245, .28);
}
.logo-text { font-size: 16px; font-weight: 700; }
.logo-sub { font-size: 9px; letter-spacing: 1.4px; color: var(--mc-muted); margin-top: 2px; }
.menu { flex: 1; }
.menu :deep(.el-menu-item) { height: 44px; margin-bottom: 4px; border-radius: 9px; color: var(--mc-sub); }
.menu :deep(.el-menu-item:hover) { background: #f7f6ff; color: var(--mc-primary); }
.aside-foot { font-size: 11px; color: #b9bdcd; text-align: center; padding: 18px 0 20px; }
.header {
  height: 64px; background: #fff; border-bottom: 1px solid var(--mc-border);
  display: flex; align-items: center; justify-content: space-between;
}
.header-title { font-size: 15px; font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 14px; }
.user-chip { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; color: var(--mc-text); }
.avatar { background: var(--mc-primary-light); color: var(--mc-primary-dark); font-weight: 600; }
.main { padding: 22px 26px; overflow-y: auto; }
</style>
