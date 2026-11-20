import { defineStore } from 'pinia'
import { authApi, userApi } from '../api'

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('mc_user') || 'null')
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('mc_token') || '',
    info: readUser()
  }),
  getters: {
    isLogin: (state) => Boolean(state.token),
    isAdmin: (state) => state.info?.role === 'admin'
  },
  actions: {
    setSession(data) {
      this.token = data.token
      this.info = data.user
      localStorage.setItem('mc_token', data.token)
      localStorage.setItem('mc_user', JSON.stringify(data.user))
    },
    async login(payload) {
      const data = await authApi.login(payload)
      this.setSession(data)
      return data
    },
    async register(payload) {
      const data = await authApi.register(payload)
      this.setSession(data)
      return data
    },
    async fetchMe() {
      const info = await userApi.me()
      this.info = info
      localStorage.setItem('mc_user', JSON.stringify(info))
      return info
    },
    async updateMe(payload) {
      const info = await userApi.updateMe(payload)
      this.info = info
      localStorage.setItem('mc_user', JSON.stringify(info))
      return info
    },
    logout() {
      this.token = ''
      this.info = null
      localStorage.removeItem('mc_token')
      localStorage.removeItem('mc_user')
    }
  }
})
