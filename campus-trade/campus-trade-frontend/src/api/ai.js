import request from '../utils/request'

// AI 接口需要单独放宽超时：全局 request 默认 10s，但后端智能体是
// Function Calling 多轮循环（最多 4 轮 × 单轮读超时 20s ≈ 80s），
// 用默认的 10s 会在后端还在查询时前端就断开，导致对话频繁失败。
const AI_CHAT_TIMEOUT = 90000
const AI_DESC_TIMEOUT = 30000

// AI 智能导购智能体：POST /api/ai/chat
// messages = [{ role: 'user' | 'assistant', content: '...' }]
// 返回 { reply, goods: [], aiUsed }，aiUsed=false 表示后端降级成了本地检索
export const aiChat = (messages) =>
  request.post('/ai/chat', { messages }, { timeout: AI_CHAT_TIMEOUT })

// AI 智能发布助手：返回一段描述文案（单轮调用，20s 读超时 + 余量）
export const aiGenerateDesc = (title, category, itemCondition) =>
  request.post('/ai/generate-desc', null, {
    params: { title, category, itemCondition },
    timeout: AI_DESC_TIMEOUT
  })
