import axios from 'axios'
import { ElMessage } from 'element-plus'

// 浏览器开发：走 Vite 代理 /api；Electron 打包（file://）：直连本机 Flask 服务
const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:5000/api')

const request = axios.create({ baseURL, timeout: 15000 })

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('mc_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data // 页面直接拿到 data
      ElMessage.error(body.message || '操作失败')
      return Promise.reject(new Error(body.message || '操作失败'))
    }
    return body
  },
  (err) => {
    const status = err.response?.status
    const message =
      err.response?.data?.message ||
      (status === 401 ? '登录已过期，请重新登录' : '无法连接服务器，请确认后端服务已启动')
    if (status === 401) {
      localStorage.removeItem('mc_token')
      localStorage.removeItem('mc_user')
      if (!window.location.hash.startsWith('#/login')) window.location.hash = '#/login'
    }
    ElMessage.error(message)
    return Promise.reject(err)
  }
)

export default request
