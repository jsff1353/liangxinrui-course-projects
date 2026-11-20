import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  // 配合 vite.config.js 的 proxy，实际请求会转发到 http://localhost:8080/api
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：自动带上 token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一拆包 + 统一报错
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      // 直接返回业务数据，页面里就不用每次写 res.data.data
      return res.data
    }
    ElMessage.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg || '请求失败'))
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      ElMessage.error('登录已失效，请重新登录')
      // 这里用 location 跳转，避免 request.js 与 router 循环依赖
      window.location.href = '/login'
    } else {
      ElMessage.error(error.message || '网络异常，请检查后端是否启动')
    }
    return Promise.reject(error)
  }
)

export default request
