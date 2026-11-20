import request from '../utils/request'

/**
 * 上传图片。
 * 注意这里不能手动设置 Content-Type，交给 axios 根据 FormData 自动生成
 * multipart/form-data 并带上 boundary，手写一个 'multipart/form-data'
 * 会丢掉 boundary 导致后端直接报 400。
 */
export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/file/upload', formData)
}
