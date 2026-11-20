import request from '../utils/request'

// 下单：data = { goodsId, remark }，返回订单VO
export const createOrder = (data) => request.post('/orders', data)

// 我的订单：params = { pageNum, pageSize, role: 'buyer'|'seller', status }
export const getMyOrders = (params) => request.get('/orders/my', { params })

// 付款（模拟支付）
export const payOrder = (id) => request.put(`/orders/${id}/pay`)

// 确认收货
export const finishOrder = (id) => request.put(`/orders/${id}/finish`)

// 取消订单
export const cancelOrder = (id, reason) =>
  request.put(`/orders/${id}/cancel`, null, { params: { reason } })
