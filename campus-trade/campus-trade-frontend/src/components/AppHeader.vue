<template>
  <header class="nav">
    <div class="nav-inner">
      <button v-if="back" class="back-btn" title="返回上一页" @click="goBack">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 5l-7 7 7 7" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>

      <div class="brand" @click="router.push('/goods')">
        <span class="brand-mark">校</span>
        <span class="brand-text">校园二手<em>集市</em></span>
      </div>

      <nav class="nav-links">
        <button class="nav-link" :class="{ active: active === 'home' }" @click="router.push('/goods')">
          首页
        </button>
        <button class="nav-link ai" :class="{ active: active === 'ai' }" @click="router.push('/ai')">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9L12 3z" stroke-linejoin="round" />
            <path d="M18 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z" stroke-linejoin="round" />
          </svg>
          AI 导购
        </button>
        <button
          class="nav-link"
          :class="{ active: active === 'my-goods' }"
          @click="router.push('/my-goods')"
        >
          我的发布
        </button>
        <button class="nav-link" :class="{ active: active === 'orders' }" @click="router.push('/orders')">
          我的订单
        </button>
        <button v-if="isAdmin" class="nav-link" :class="{ active: active === 'admin' }" @click="router.push('/admin')">
          管理后台
        </button>
      </nav>

      <div class="nav-right">
        <button class="publish-btn" @click="router.push('/goods/publish')">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 5v14M5 12h14" stroke-linecap="round" />
          </svg>
          发布闲置
        </button>

        <div class="user">
          <span class="avatar">{{ avatarText }}</span>
          <span class="hello">{{ userInfo.nickname || userInfo.username || '同学' }}</span>
        </div>

        <button class="logout" @click="logout">退出</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  // 高亮哪一项：home / ai / my-goods / orders / admin
  active: { type: String, default: '' },
  // 详情页这类二级页面显示返回箭头
  back: { type: Boolean, default: false }
})

const router = useRouter()
const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
const isAdmin = computed(() => userInfo.role === 1)
const avatarText = computed(() => {
  const name = userInfo.nickname || userInfo.username || '同学'
  return String(name).slice(0, 1).toUpperCase()
})

// 直接粘贴链接进来时浏览器没有上一页，回退到首页兜底
const goBack = () => {
  if (props.back && window.history.length > 1) {
    router.back()
  } else {
    router.push('/goods')
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  router.push('/login')
}
</script>

<style scoped>
.nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid rgba(235, 239, 246, 0.9);
}

.nav-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: #fff;
  color: var(--ink-2);
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.back-btn:hover {
  border-color: #c7d6f9;
  color: var(--brand);
  transform: translateX(-2px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
}

.brand-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: linear-gradient(135deg, #3b6ef6, #7c86f8);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 6px 14px -6px rgba(59, 110, 246, 0.75);
}

.brand-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.brand-text em {
  font-style: normal;
  font-weight: 600;
  color: var(--brand);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 12px;
  border: none;
  border-radius: 9px;
  background: transparent;
  color: #4a5468;
  font-size: 13.5px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s var(--ease), color 0.2s var(--ease);
}

.nav-link:hover {
  background: #f2f5fc;
  color: var(--brand);
}

.nav-link.active {
  background: var(--brand-soft);
  color: #4f46e5;
  font-weight: 600;
}

.nav-link.ai {
  color: #6d5cf6;
  background: linear-gradient(135deg, #f2f0ff, #eef4ff);
}

.nav-link.ai:hover,
.nav-link.ai.active {
  background: linear-gradient(135deg, #e8e3ff, #e4ecff);
  color: #5b46e8;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.publish-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 15px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 18px -8px rgba(59, 110, 246, 0.9);
  transition: transform 0.2s var(--ease), box-shadow 0.2s var(--ease), filter 0.2s var(--ease);
}

.publish-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
  box-shadow: 0 12px 22px -8px rgba(59, 110, 246, 0.95);
}

.user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #eef2ff, #e6f6ff);
  color: #4b5cd6;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid #e3e9f8;
}

.hello {
  font-size: 13px;
  color: #5a6474;
  max-width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout {
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12.5px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 7px;
  transition: color 0.2s var(--ease), background 0.2s var(--ease);
}

.logout:hover {
  color: #ef4444;
  background: #fff1f1;
}

@media (max-width: 899px) {
  .nav-inner {
    padding: 10px 16px;
    gap: 12px;
  }

  .hello {
    display: none;
  }
}

@media (max-width: 767px) {
  .nav-links .nav-link:not(.ai) {
    display: none;
  }

  .nav-links {
    flex: 0 0 auto;
  }

  .brand-text em {
    display: none;
  }
}

@media (max-width: 420px) {
  .publish-btn {
    padding: 0 11px;
  }

  .publish-btn svg {
    display: none;
  }
}
</style>
