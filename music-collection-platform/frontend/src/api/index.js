/** 后端 RESTful 接口封装，按模块分组。 */
import request from './request'

export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data)
}

export const userApi = {
  me: () => request.get('/users/me'),
  updateMe: (data) => request.put('/users/me', data),
  changePassword: (data) => request.put('/users/password', data),
  stats: () => request.get('/users/stats')
}

export const playlistApi = {
  list: () => request.get('/playlists'),
  get: (id) => request.get(`/playlists/${id}`),
  create: (data) => request.post('/playlists', data),
  update: (id, data) => request.put(`/playlists/${id}`, data),
  remove: (id) => request.delete(`/playlists/${id}`)
}

export const songApi = {
  list: (params) => request.get('/songs', { params }),
  get: (id) => request.get(`/songs/${id}`),
  create: (data) => request.post('/songs', data),
  update: (id, data) => request.put(`/songs/${id}`, data),
  remove: (id) => request.delete(`/songs/${id}`)
}

export const tagApi = {
  list: () => request.get('/tags'),
  create: (data) => request.post('/tags', data),
  update: (id, data) => request.put(`/tags/${id}`, data),
  remove: (id) => request.delete(`/tags/${id}`)
}

export const adminApi = {
  overview: () => request.get('/admin/overview'),
  users: (params) => request.get('/admin/users', { params }),
  setStatus: (id, status) => request.put(`/admin/users/${id}/status`, { status }),
  setRole: (id, role) => request.put(`/admin/users/${id}/role`, { role }),
  removeUser: (id) => request.delete(`/admin/users/${id}`),
  songs: (params) => request.get('/admin/songs', { params }),
  removeSong: (id) => request.delete(`/admin/songs/${id}`),
  playlists: (params) => request.get('/admin/playlists', { params }),
  removePlaylist: (id) => request.delete(`/admin/playlists/${id}`)
}
