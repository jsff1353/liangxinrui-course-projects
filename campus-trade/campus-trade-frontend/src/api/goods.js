import request from '../utils/request'

// 分页列表，返回 MyBatis-Plus 的 Page 对象：{ records, total, current, size }
export const getGoodsPage = (params) => request.get('/goods/page', { params })

export const getGoodsDetail = (id) => request.get(`/goods/${id}`)

// 发布商品，返回新商品 id
export const publishGoods = (data) => request.post('/goods', data)

// 编辑商品
export const updateGoods = (id, data) => request.put(`/goods/${id}`, data)

// 我的发布：params = { pageNum, pageSize, status }
export const getMyGoods = (params) => request.get('/goods/my', { params })

// 上架(1) / 下架(0)
export const changeGoodsStatus = (id, status) =>
  request.put(`/goods/${id}/status`, null, { params: { status } })

export const deleteGoods = (id) => request.delete(`/goods/${id}`)
