<template>
  <div class="page">
    <AppHeader active="ai" />

    <main class="chat-shell">
      <div class="chat-head">
        <div class="who">
          <span class="ai-mark">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.9">
              <path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9L12 3z" stroke-linejoin="round" />
              <path d="M18 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z" stroke-linejoin="round" />
            </svg>
          </span>
          <div>
            <div class="who-name">AI 智能导购 <span class="who-badge">智能体 · 小集</span></div>
            <div class="who-sub">所有商品直接查库返回，价格成色与在售信息一致</div>
          </div>
        </div>
        <button class="ghost-btn" @click="clearChat">清空对话</button>
      </div>

      <div ref="scrollRef" class="chat-body">
        <!-- 开场白：不进 messages，避免污染上下文 -->
        <div class="row assistant">
          <div class="avatar ai">AI</div>
          <div class="bubble">
            <p class="text">
              你好，我是小集，校园二手交易平台的导购助手。<br />
              告诉我你要买什么、预算多少，我去库里给你找真实在售的商品。
            </p>
            <div class="quick">
              <button v-for="q in quickQuestions" :key="q" class="quick-chip" @click="sendQuick(q)">
                {{ q }}
              </button>
            </div>
          </div>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="row" :class="m.role">
          <div v-if="m.role === 'assistant'" class="avatar ai">AI</div>

          <div class="bubble">
            <p class="text">{{ m.content }}</p>

            <!-- 商品卡片：全部来自后端查库结果，模型只负责组织语言 -->
            <div v-if="m.goods && m.goods.length" class="goods">
              <div v-for="g in m.goods" :key="g.id" class="goods-item" @click="router.push(`/goods/${g.id}`)">
                <div class="thumb">
                  <img v-if="g.coverImg" :src="g.coverImg" alt="" />
                  <div v-else class="thumb-empty">{{ g.category || '二手' }}</div>
                </div>
                <div class="g-meta">
                  <div class="g-name" :title="g.title">{{ g.title }}</div>
                  <div class="g-sub">
                    <span class="g-price"><em>￥</em>{{ formatPrice(g.price) }}</span>
                    <span class="pill pill-info">{{ conditionText(g.itemCondition) }}</span>
                    <span v-if="g.tradePlace" class="g-place">{{ g.tradePlace }}</span>
                  </div>
                </div>
                <span class="g-go">查看 →</span>
              </div>
            </div>

            <div v-if="m.aiUsed === false" class="degrade">本次为本地关键词检索，未调用大模型</div>
          </div>

          <div v-if="m.role === 'user'" class="avatar me">{{ meText }}</div>
        </div>

        <div v-if="sending" class="row assistant">
          <div class="avatar ai">AI</div>
          <div class="bubble thinking">
            <span class="dot" />
            <span class="dot" />
            <span class="dot" />
            <span class="think-text">小集正在翻数据库…</span>
          </div>
        </div>
      </div>

      <div class="composer">
        <textarea
          v-model="input"
          rows="2"
          maxlength="500"
          class="input"
          placeholder="例如：两百块以内有没有能用的蓝牙耳机？回车发送，Shift+回车换行"
          @keydown.enter="onEnter"
        />
        <div class="composer-bar">
          <span class="counter">{{ input.length }} / 500</span>
          <button class="send-btn" :disabled="sending || !input.trim()" @click="send()">
            {{ sending ? '发送中…' : '发送' }}
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h13M13 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { aiChat } from '../api/ai'

const router = useRouter()

const quickQuestions = ['两百块以内的耳机', '有没有便宜的高数教材', '推荐一辆能代步的自行车', '怎么付款？多久内要付']

// 每条消息：{ role, content, goods?, aiUsed? }，goods 只在助手消息里出现
const messages = ref([])
const input = ref('')
const sending = ref(false)
const scrollRef = ref(null)

const meText = computed(() => {
  const info = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return String(info.nickname || info.username || '我').slice(0, 1).toUpperCase()
})

const conditionText = (v) => ({ 1: '全新', 2: '九成新', 3: '七成新', 4: '五成新及以下' }[v] || '成色未标注')

const formatPrice = (v) => {
  const n = Number(v || 0)
  if (!Number.isFinite(n)) return '0'
  return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

const scrollToBottom = async () => {
  await nextTick()
  const el = scrollRef.value
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

const onEnter = (e) => {
  // 输入中文时回车是候选项确认，不能当成发送
  if (e.isComposing) {
    return
  }
  if (e.shiftKey) {
    return
  }
  e.preventDefault()
  send()
}

const sendQuick = (q) => {
  if (sending.value) {
    return
  }
  input.value = q
  send()
}

const send = async () => {
  const text = input.value.trim()
  if (!text || sending.value) {
    return
  }
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  sending.value = true
  scrollToBottom()
  try {
    // 只发 role/content 给后端，goods/aiUsed 是本地展示用的
    // 只带最近 10 轮（20 条）：既省 token，也避开后端 @Size(max=20) 校验
    const payload = messages.value.slice(-20).map((m) => ({ role: m.role, content: m.content }))
    const res = await aiChat(payload)
    messages.value.push({
      role: 'assistant',
      content: res.reply || '我这边没组织好语言，你换个说法再试试。',
      goods: res.goods || [],
      aiUsed: !!res.aiUsed
    })
  } catch (e) {
    // 错误提示由拦截器统一处理，这里把用户输入还回去避免白打一行字
    messages.value.pop()
    input.value = text
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

const clearChat = () => {
  messages.value = []
  input.value = ''
  ElMessage.success('对话已清空')
}
</script>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--page-bg);
}

.chat-shell {
  flex: 1;
  min-height: 0;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 14px 24px 18px;
  display: flex;
  flex-direction: column;
}

/* ---------- 顶部信息条 ---------- */
.chat-head {
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 18px;
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
}

.who {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}

.ai-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #6d5cf6, #4f8ef7);
  color: #fff;
  box-shadow: 0 8px 18px -10px rgba(99, 92, 246, 0.95);
  flex-shrink: 0;
}

.who-name {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 8px;
}

.who-badge {
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--brand-soft);
  color: #4f46e5;
  font-size: 11px;
  font-weight: 600;
}

.who-sub {
  margin-top: 3px;
  font-size: 12px;
  color: var(--muted);
}

.ghost-btn {
  height: 32px;
  padding: 0 14px;
  flex-shrink: 0;
  border: 1px solid #dbe4f7;
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--ink-2);
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.ghost-btn:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

/* ---------- 消息区 ---------- */
.chat-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 6px 4px 4px;
}

.row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.row.user {
  justify-content: flex-end;
}

.avatar {
  flex: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 11.5px;
  font-weight: 700;
  color: #fff;
}

.avatar.ai {
  background: linear-gradient(135deg, #6d5cf6, #4f8ef7);
  box-shadow: 0 6px 14px -8px rgba(99, 92, 246, 0.9);
}

.avatar.me {
  background: linear-gradient(135deg, #34c48a, #22a06b);
}

.bubble {
  max-width: 620px;
  padding: 12px 15px;
  border-radius: 4px 14px 14px 14px;
  background: #fff;
  border: 1px solid var(--line);
  font-size: 13.5px;
  line-height: 1.75;
  color: var(--ink);
  box-shadow: var(--shadow-xs);
}

.row.user .bubble {
  border-radius: 14px 4px 14px 14px;
  background: linear-gradient(135deg, var(--brand), #5b7cf8);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 10px 22px -14px rgba(59, 110, 246, 0.95);
}

.text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ---------- 快捷提问 ---------- */
.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 11px;
}

.quick-chip {
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fafbfe;
  color: var(--ink-2);
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.quick-chip:hover {
  border-color: #c7d6f9;
  color: var(--brand);
  background: #f5f8ff;
  transform: translateY(-1px);
}

/* ---------- 商品卡片 ---------- */
.goods {
  margin-top: 11px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.goods-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: #fbfcff;
  cursor: pointer;
  transition: all 0.26s var(--ease);
}

.goods-item:hover {
  border-color: #c7d6f9;
  background: #fff;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.thumb {
  flex: none;
  width: 60px;
  height: 60px;
  border-radius: 10px;
  overflow: hidden;
  background: #f2f5fa;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 11px;
  color: #b3bccd;
  background: linear-gradient(135deg, #f5f7fb, #eef2f9);
}

.g-meta {
  min-width: 0;
  flex: 1;
}

.g-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.g-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.g-price {
  font-size: 15px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.2px;
}

.g-price em {
  font-style: normal;
  font-size: 11px;
  font-weight: 600;
}

.g-place {
  font-size: 11.5px;
  color: var(--muted);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 130px;
}

.g-go {
  flex-shrink: 0;
  font-size: 11.5px;
  color: var(--muted-2);
  transition: color 0.2s var(--ease);
}

.goods-item:hover .g-go {
  color: var(--brand);
}

/* ---------- 思考中 ---------- */
.bubble.thinking {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--muted);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c2cad8;
  animation: blink 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.18s;
}

.dot:nth-child(3) {
  animation-delay: 0.36s;
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

.think-text {
  margin-left: 4px;
  font-size: 12.5px;
}

.degrade {
  margin-top: 9px;
  padding: 6px 10px;
  border-radius: 8px;
  background: #fffaf0;
  border: 1px solid #fde9c4;
  font-size: 11.5px;
  color: var(--warn);
}

/* ---------- 输入区 ---------- */
.composer {
  flex: none;
  margin-top: 12px;
  padding: 12px 14px 12px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.composer:focus-within {
  border-color: #c7d6f9;
  box-shadow: var(--shadow-md);
}

.input {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--ink);
  background: transparent;
}

.input::placeholder {
  color: var(--muted-2);
}

.composer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 9px;
  border-top: 1px dashed var(--line);
}

.counter {
  font-size: 11.5px;
  color: var(--muted-2);
  font-variant-numeric: tabular-nums;
}

.send-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-brand);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease), opacity 0.2s var(--ease);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.send-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

@media (max-width: 767px) {
  .chat-shell {
    padding: 10px 14px 14px;
  }

  .who-sub {
    display: none;
  }

  .bubble {
    max-width: 86vw;
  }
}
</style>
