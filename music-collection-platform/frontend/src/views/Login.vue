<template>
  <div class="auth-wrap">
    <div class="auth-brand">
      <div>
        <div class="brand-logo">♪ &nbsp;Music Collection</div>
        <h1>把喜欢的歌，<br />好好收藏。</h1>
        <p class="brand-desc">歌单管理 · 标签分类 · 音乐备注 · 快速搜索<br />一个干净、无广告的私人音乐收藏空间</p>
      </div>
      <div class="brand-foot">轻量化纯净音乐收藏管理桌面平台<br />Vue3 + Flask + MySQL + Electron</div>
    </div>

    <div class="auth-panel">
      <div class="auth-title">欢迎回来 👋</div>
      <div class="auth-tip">登录后继续管理你的音乐收藏</div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="submit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">登 录</el-button>
      </el-form>

      <div class="auth-switch">还没有账号？<router-link to="/register">立即注册</router-link></div>
      <div class="auth-demo">管理员演示账号：admin / admin123（初始化数据库后可用）</div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await userStore.login({ ...form })
    ElMessage.success('登录成功，欢迎回来')
    router.push(typeof route.query.redirect === 'string' ? route.query.redirect : '/home')
  } catch {
    // 错误提示由请求拦截器统一展示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.brand-logo { font-size: 15px; font-weight: 600; letter-spacing: 1px; opacity: .95; }
h1 { font-size: 40px; line-height: 1.4; margin-top: 90px; letter-spacing: 2px; }
.brand-desc { margin-top: 22px; font-size: 14px; line-height: 2; opacity: .82; }
.brand-foot { font-size: 12px; line-height: 1.9; opacity: .7; position: relative; z-index: 1; }
.auth-switch { text-align: center; margin-top: 20px; font-size: 13px; color: var(--mc-sub); }
</style>
