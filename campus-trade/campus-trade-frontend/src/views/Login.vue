<template>
  <div class="login-page">
    <!-- 左：品牌区 -->
    <section class="brand-side">
      <div class="glow glow-1" />
      <div class="glow glow-2" />

      <div class="brand-top">
        <span class="brand-mark">校</span>
        <span class="brand-name">校园二手集市</span>
      </div>

      <div class="brand-copy">
        <h1>把闲置<br />交给下一个需要它的人</h1>
        <p>教材、数码、生活用品，同学之间当面交易，省心又省钱。</p>

        <ul class="features">
          <li>
            <span class="f-dot" />
            商品真实在售，价格成色直接来自数据库
          </li>
          <li>
            <span class="f-dot" />
            AI 导购小集，一句话帮你找到合适的闲置
          </li>
          <li>
            <span class="f-dot" />
            下单即锁定，2 小时内付款，超时自动释放
          </li>
        </ul>
      </div>

      <p class="brand-foot">广州工程技术职业学院 · 软件技术（大数据方向）</p>
    </section>

    <!-- 右：表单区 -->
    <section class="form-side">
      <div class="card">
        <h2 class="title">{{ isRegister ? '注册新账号' : '欢迎回来' }}</h2>
        <p class="subtitle">{{ isRegister ? '创建一个账号就能发布闲置了' : '登录后即可浏览和发布校园闲置' }}</p>

        <div class="form" @keyup.enter="submit">
          <label class="field">
            <span class="label">用户名</span>
            <div class="input-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="12" cy="8.5" r="3.5" />
                <path d="M5 20c0-3.4 3.1-5.5 7-5.5s7 2.1 7 5.5" stroke-linecap="round" />
              </svg>
              <input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
            </div>
          </label>

          <label class="field">
            <span class="label">密码</span>
            <div class="input-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8">
                <rect x="5" y="10.5" width="14" height="9.5" rx="2.5" />
                <path d="M8.5 10.5V8a3.5 3.5 0 017 0v2.5" stroke-linecap="round" />
              </svg>
              <input
                v-model="form.password"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请输入密码"
                autocomplete="current-password"
              />
              <button class="eye" type="button" :title="showPwd ? '隐藏密码' : '显示密码'" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M2.5 12S6 6.5 12 6.5 21.5 12 21.5 12 18 17.5 12 17.5 2.5 12 2.5 12z" stroke-linejoin="round" />
                  <circle cx="12" cy="12" r="2.6" />
                </svg>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M4 4l16 16" stroke-linecap="round" />
                  <path d="M9.5 9.7A3 3 0 0012 15a3 3 0 002.3-1.1" stroke-linecap="round" />
                  <path d="M6.4 6.9C4.1 8.4 2.5 12 2.5 12s3.5 5.5 9.5 5.5c1.3 0 2.4-.25 3.4-.65" stroke-linecap="round" />
                  <path d="M17.6 15.1c2.3-1.5 3.9-3.1 3.9-3.1S18 6.5 12 6.5c-.6 0-1.2.06-1.7.16" stroke-linecap="round" />
                </svg>
              </button>
            </div>
          </label>

          <label v-if="isRegister" class="field">
            <span class="label">昵称<span class="opt">选填</span></span>
            <div class="input-wrap">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 4l1.6 3.9 3.9 1.6-3.9 1.6L12 15l-1.6-3.9L6.5 9.5l3.9-1.6L12 4z" stroke-linejoin="round" />
                <path d="M17.5 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7.7-1.8z" stroke-linejoin="round" />
              </svg>
              <input v-model="form.nickname" placeholder="默认使用用户名" />
            </div>
          </label>

          <button class="submit" :disabled="loading" @click="submit">
            {{ loading ? '处理中…' : isRegister ? '注 册' : '登 录' }}
          </button>
        </div>

        <div class="switch-line">
          <span>{{ isRegister ? '已有账号？' : '还没有账号？' }}</span>
          <button class="link" @click="isRegister = !isRegister">{{ isRegister ? '去登录' : '去注册' }}</button>
        </div>

        <div v-if="!isRegister" class="demo">
          <span class="demo-label">演示账号</span>
          <button class="demo-chip" @click="fill('admin')">admin / 123456（管理员）</button>
          <button class="demo-chip" @click="fill('stu001')">stu001 / 123456（学生）</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '../api/user'

const router = useRouter()
const isRegister = ref(false)
const loading = ref(false)
const showPwd = ref(false)
const form = reactive({ username: '', password: '', nickname: '' })

const fill = (name) => {
  form.username = name
  form.password = '123456'
}

const submit = async () => {
  if (loading.value) {
    return
  }
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    if (isRegister.value) {
      await register({ ...form })
      ElMessage.success('注册成功，请登录')
      isRegister.value = false
    } else {
      // 后端返回 { token, userId, username, nickname, avatar, campus, role }
      const data = await login({ username: form.username, password: form.password })
      localStorage.setItem('token', data.token)
      localStorage.setItem('userInfo', JSON.stringify(data))
      ElMessage.success('登录成功')
      router.push('/goods')
    }
  } catch (e) {
    // 错误提示已在 axios 拦截器里统一处理，这里只负责中止流程
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  background: var(--page-bg);
}

/* ---------- 左侧品牌 ---------- */
.brand-side {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 40px 52px;
  color: #fff;
  background: linear-gradient(150deg, #2f5fe0 0%, #4b6ef5 46%, #6c7cf8 100%);
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  pointer-events: none;
}

.glow-1 {
  width: 320px;
  height: 320px;
  right: -70px;
  top: -80px;
  background: rgba(139, 168, 255, 0.55);
}

.glow-2 {
  width: 260px;
  height: 260px;
  left: -60px;
  bottom: -70px;
  background: rgba(120, 226, 255, 0.35);
}

.brand-top {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 17px;
  font-weight: 700;
  backdrop-filter: blur(6px);
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.brand-copy {
  position: relative;
  margin-top: auto;
  margin-bottom: auto;
  padding: 40px 0;
}

.brand-copy h1 {
  margin: 0 0 16px;
  font-size: 36px;
  line-height: 1.32;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-copy p {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.82);
  max-width: 400px;
}

.features {
  margin: 28px 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.features li {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

.f-dot {
  width: 6px;
  height: 6px;
  margin-top: 7px;
  border-radius: 50%;
  background: #a9c6ff;
  flex-shrink: 0;
}

.brand-foot {
  position: relative;
  margin: 0;
  font-size: 11.5px;
  color: rgba(255, 255, 255, 0.6);
}

/* ---------- 右侧表单 ---------- */
.form-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.card {
  width: 100%;
  max-width: 380px;
}

.title {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: var(--ink);
}

.subtitle {
  margin: 0 0 26px;
  font-size: 13px;
  color: var(--muted);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: block;
}

.label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 7px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--ink-2);
}

.opt {
  font-size: 11px;
  color: var(--muted-2);
  font-weight: 400;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 46px;
  padding: 0 13px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--muted-2);
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.input-wrap:focus-within {
  border-color: #b9caf7;
  box-shadow: 0 0 0 4px rgba(59, 110, 246, 0.08);
  color: var(--brand);
}

.input-wrap input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13.5px;
  color: var(--ink);
}

.input-wrap input::placeholder {
  color: var(--muted-2);
}

.eye {
  border: none;
  background: transparent;
  color: var(--muted-2);
  cursor: pointer;
  padding: 2px;
  display: grid;
  place-items: center;
  transition: color 0.2s var(--ease);
}

.eye:hover {
  color: var(--brand);
}

.submit {
  margin-top: 6px;
  height: 46px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 14.5px;
  font-weight: 600;
  letter-spacing: 2px;
  cursor: pointer;
  box-shadow: var(--shadow-brand);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease), opacity 0.2s var(--ease);
}

.submit:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.switch-line {
  margin-top: 18px;
  font-size: 13px;
  color: var(--muted);
  text-align: center;
}

.link {
  border: none;
  background: transparent;
  color: var(--brand);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 2px 4px;
}

.link:hover {
  text-decoration: underline;
}

.demo {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed var(--line);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.demo-label {
  font-size: 11.5px;
  color: var(--muted-2);
}

.demo-chip {
  padding: 5px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fafbfe;
  color: var(--ink-2);
  font-size: 11.5px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.demo-chip:hover {
  border-color: #c7d6f9;
  color: var(--brand);
  background: #f5f8ff;
}

@media (max-width: 899px) {
  .login-page {
    grid-template-columns: minmax(0, 1fr);
  }

  .brand-side {
    padding: 28px 24px 34px;
  }

  .brand-copy {
    padding: 26px 0 0;
  }

  .brand-copy h1 {
    font-size: 26px;
  }

  .features,
  .brand-foot {
    display: none;
  }

  .form-side {
    padding: 30px 20px 48px;
  }
}
</style>
