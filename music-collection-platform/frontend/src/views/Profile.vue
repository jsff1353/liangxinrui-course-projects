<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-title">个人中心</div>
        <div class="page-sub">查看账号信息、修改资料与登录密码</div>
      </div>
    </div>

    <div class="profile-grid">
      <div class="panel account-card">
        <el-avatar :size="72" :src="profile.avatar || ''" class="big-avatar">
          {{ (profile.nickname || 'U').charAt(0) }}
        </el-avatar>
        <div class="account-name">{{ profile.nickname || '未设置昵称' }}</div>
        <div class="muted" style="font-size: 12px">@{{ userStore.info?.username }}</div>
        <el-tag :type="userStore.isAdmin ? 'danger' : 'primary'" effect="light" size="small" style="margin-top: 14px">
          {{ userStore.isAdmin ? '管理员' : '普通用户' }}
        </el-tag>
        <el-divider />
        <div class="info-row"><span class="muted">账号状态</span><span>{{ userStore.info?.status === 1 ? '正常' : '已禁用' }}</span></div>
        <div class="info-row"><span class="muted">注册时间</span><span>{{ userStore.info?.createdAt || '-' }}</span></div>
        <div class="info-row"><span class="muted">邮箱</span><span>{{ profile.email || '未填写' }}</span></div>
      </div>

      <div class="panel">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本资料" name="profile">
            <el-form ref="profileRef" :model="profile" :rules="profileRules" label-width="90px" style="max-width: 480px; margin-top: 10px">
              <el-form-item label="昵称" prop="nickname">
                <el-input v-model="profile.nickname" maxlength="64" />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profile.email" placeholder="example@mail.com" />
              </el-form-item>
              <el-form-item label="头像地址" prop="avatar">
                <el-input v-model="profile.avatar" placeholder="https://... 选填" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存资料</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="修改密码" name="password">
            <el-form ref="pwdRef" :model="pwd" :rules="pwdRules" label-width="90px" style="max-width: 480px; margin-top: 10px">
              <el-form-item label="原密码" prop="oldPassword">
                <el-input v-model="pwd.oldPassword" type="password" show-password />
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input v-model="pwd.newPassword" type="password" show-password />
              </el-form-item>
              <el-form-item label="确认密码" prop="confirm">
                <el-input v-model="pwd.confirm" type="password" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="savingPwd" @click="savePassword">确认修改</el-button>
              </el-form-item>
            </el-form>
            <div class="auth-demo" style="max-width: 480px">修改成功后需要重新登录</div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '../api'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('profile')
const profileRef = ref(null)
const pwdRef = ref(null)
const savingProfile = ref(false)
const savingPwd = ref(false)

const profile = reactive({ nickname: '', email: '', avatar: '' })
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })

const profileRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}
const pwdRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度需为 6-64 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) =>
        value === pwd.newPassword ? callback() : callback(new Error('两次输入的密码不一致')),
      trigger: 'blur'
    }
  ]
}

function syncProfile(info) {
  profile.nickname = info?.nickname || ''
  profile.email = info?.email || ''
  profile.avatar = info?.avatar || ''
}

async function saveProfile() {
  try {
    await profileRef.value.validate()
  } catch {
    return
  }
  savingProfile.value = true
  try {
    const info = await userStore.updateMe({ ...profile })
    syncProfile(info)
    ElMessage.success('资料已保存')
  } catch {
    // 统一错误提示
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  try {
    await pwdRef.value.validate()
  } catch {
    return
  }
  savingPwd.value = true
  try {
    await userApi.changePassword({ oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
    ElMessage.success('密码修改成功，即将返回登录页')
    setTimeout(() => {
      userStore.logout()
      router.push('/login')
    }, 900)
  } catch {
    // 统一错误提示
  } finally {
    savingPwd.value = false
  }
}

onMounted(() => {
  userStore.fetchMe().then(syncProfile).catch(() => {})
})
</script>

<style scoped>
.profile-grid { display: grid; grid-template-columns: 280px 1fr; gap: 18px; align-items: start; }
.account-card { text-align: center; }
.big-avatar { background: var(--mc-primary-light); color: var(--mc-primary-dark); font-size: 28px; font-weight: 700; }
.account-name { font-size: 17px; font-weight: 700; margin-top: 12px; }
.info-row { display: flex; justify-content: space-between; font-size: 12px; padding: 8px 4px; border-bottom: 1px dashed #f0f1f8; }
.info-row:last-child { border-bottom: none; }
@media (max-width: 900px) { .profile-grid { grid-template-columns: 1fr; } }
</style>
