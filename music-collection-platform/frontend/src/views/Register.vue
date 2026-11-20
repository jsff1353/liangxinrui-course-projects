<template>
  <div class="auth-wrap">
    <div class="auth-brand">
      <div>
        <div class="brand-logo">♪ &nbsp;Music Collection</div>
        <h1>从今天开始，<br />整理你的歌单。</h1>
        <p class="brand-desc">创建专属歌单、自定义标签、写下每首歌的备注<br />所有数据保存在你自己的数据库中</p>
      </div>
      <div class="brand-foot">注册即成为普通用户，管理员由系统初始化分配</div>
    </div>

    <div class="auth-panel">
      <div class="auth-title">创建账号</div>
      <div class="auth-tip">填写以下信息，30 秒即可开始使用</div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" label-position="top" @keyup.enter="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-32 位字母、数字或下划线" clearable />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="展示在界面上的名字" clearable />
        </el-form-item>
        <el-form-item label="邮箱（选填）" prop="email">
          <el-input v-model="form.email" placeholder="example@mail.com" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="6-64 位密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password placeholder="再次输入密码" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">注册并登录</el-button>
      </el-form>

      <div class="auth-switch">已有账号？<router-link to="/login">返回登录</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '', nickname: '', email: '', password: '', confirmPassword: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]{3,32}$/, message: '需为 3-32 位字母、数字或下划线', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度需为 6-64 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) =>
        value === form.password ? callback() : callback(new Error('两次输入的密码不一致')),
      trigger: 'blur'
    }
  ]
}

async function submit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await userStore.register({
      username: form.username,
      nickname: form.nickname,
      email: form.email,
      password: form.password
    })
    ElMessage.success('注册成功，已自动登录')
    router.push('/home')
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.brand-logo { font-size: 15px; font-weight: 600; letter-spacing: 1px; }
h1 { font-size: 38px; line-height: 1.4; margin-top: 90px; letter-spacing: 2px; }
.brand-desc { margin-top: 22px; font-size: 14px; line-height: 2; opacity: .82; }
.brand-foot { font-size: 12px; opacity: .75; position: relative; z-index: 1; }
.auth-panel { justify-content: center; overflow-y: auto; }
.auth-switch { text-align: center; margin-top: 16px; font-size: 13px; color: var(--mc-sub); }
:deep(.el-form-item__label) { font-size: 12px; color: var(--mc-sub); padding-bottom: 4px; }
:deep(.el-form-item) { margin-bottom: 14px; }
</style>
