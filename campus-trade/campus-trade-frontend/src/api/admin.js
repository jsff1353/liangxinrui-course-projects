import request from '../utils/request'

// 概览统计
export const getAdminStats = () => request.get('/admin/stats')

// 用户管理：params = { pageNum, pageSize, keyword }
export const getAdminUsers = (params) => request.get('/admin/users', { params })

// 启用(1) / 禁用(0)
export const changeUserStatus = (id, status) =>
  request.put(`/admin/users/${id}/status`, null, { params: { status } })

// 商品管理：params = { pageNum, pageSize, status, keyword }
export const getAdminGoods = (params) => request.get('/admin/goods', { params })

// 强制上架 / 下架
export const changeAdminGoodsStatus = (id, status) =>
  request.put(`/admin/goods/${id}/status`, null, { params: { status } })

// 订单总览：params = { pageNum, pageSize, status, keyword }
export const getAdminOrders = (params) => request.get('/admin/orders', { params })
