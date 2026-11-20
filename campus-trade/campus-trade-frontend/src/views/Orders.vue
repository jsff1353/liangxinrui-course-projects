<template>
  <div class="page">
    <AppHeader active="orders" />

    <main class="wrap">
      <div class="page-head">
        <div>
          <h1 class="page-title">我的订单</h1>
          <p class="page-sub">共 {{ total }} 笔交易记录</p>
        </div>

        <div class="seg">
          <button
            v-for="r in roles"
            :key="r.value"
            class="seg-btn"
            :class="{ active: role === r.value }"
            @click="changeRole(r.value)"
          >
            {{ r.label }}
          </button>
        </div>
      </div>

      <div class="toolbar">
        <div class="chips">
          <button
            v-for="c in tabs"
            :key="c.value"
            class="chip"
            :class="{ active: status === c.value }"
            @click="changeTab(c.value)"
          >
            {{ c.label }}
          </button>
        </div>
        <button class="icon-btn" title="刷新" @click="load">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9">
            <path d="M20 11a8 8 0 10-2.6 6" stroke-linecap="round" />
            <path d="M20 5v6h-6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>

      <div v-loading="loading" class="list">
        <template v-if="list.length">
          <article v-for="o in list" :key="o.id" class="order">
            <div class="order-top">
              <div class="order-no">
                <span class="no-label">订单号</span>
                <span class="no-val">{{ o.orderNo }}</span>
              </div>
              <div class="order-top-right">
                <span class="order-time">{{ formatTime(o.createTime) }}</span>
                <span class="pill" :class="statusClass(o.status)">{{ statusText(o.status) }}</span>
              </div>
            </div>

            <div class="order-body">
              <div class="thumb" @click="router.push(`/goods/${o.goodsId}`)">
                <img v-if="o.goodsCover" :src="o.goodsCover" alt="" />
                <div v-else class="thumb-empty">{{ o.goodsCategory || '二手' }}</div>
              </div>

              <div class="main">
                <h3 class="order-title" @click="router.push(`/goods/${o.goodsId}`)">{{ o.goodsTitle }}</h3>
                <div class="order-meta">
                  <span>{{ role === 'buyer' ? '卖家' : '买家' }}：{{ role === 'buyer' ? o.sellerNickname || '—' : o.buyerNickname || '—' }}</span>
                  <span class="dot">·</span>
                  <span>{{ o.goodsCategory || '其他' }}</span>
                </div>
                <div v-if="o.remark" class="remark">留言：{{ o.remark }}</div>
                <div v-if="o.status === 3 && o.cancelReason" class="cancel-reason">取消原因：{{ o.cancelReason }}</div>
                <div v-if="o.payTime" class="pay-time">付款时间：{{ formatTime(o.payTime) }}</div>
                <div v-if="o.finishTime" class="pay-time">完成时间：{{ formatTime(o.finishTime) }}</div>
              </div>

              <div class="amount-col">
                <span class="amount"><em>￥</em>{{ formatPrice(o.amount) }}</span>
                <span class="amount-label">实付金额</span>
              </div>
            </div>

            <div class="order-ops">
              <template v-if="o.status === 0">
                <span class="tip">请在 2 小时内完成付款</span>
                <button class="btn-ghost" @click="onCancel(o)">取消订单</button>
                <button class="btn-pay" @click="onPay(o)">去付款</button>
              </template>

              <template v-else-if="o.status === 1">
                <span class="tip">{{ role === 'buyer' ? '收到货后请及时确认' : '等待买家确认收货' }}</span>
                <button v-if="role === 'buyer'" class="btn-ghost" @click="onCancel(o)">取消订单</button>
                <button v-if="role === 'buyer'" class="btn-pay" @click="onFinish(o)">确认收货</button>
              </template>

              <template v-else-if="o.status === 2">
                <span class="tip tip-ok">交易已完成</span>
              </template>

              <template v-else>
                <span class="tip">订单已取消</span>
              </template>
            </div>
          </article>

          <div v-if="total > pageSize" class="pager">
            <button class="page-btn" :disabled="pageNum <= 1" @click="goPage(pageNum - 1)">上一页</button>
            <button
              v-for="p in pageList"
              :key="p"
              class="page-btn num"
              :class="{ active: p === pageNum }"
              @click="goPage(p)"
            >
              {{ p }}
            </button>
            <button class="page-btn" :disabled="pageNum >= maxPage" @click="goPage(pageNum + 1)">下一页</button>
          </div>
        </template>

        <div v-else-if="!loading" class="empty-state">
          <svg viewBox="0 0 24 24" width="46" height="46" fill="none" stroke="currentColor" stroke-width="1.3">
            <path d="M6 3h9l4 4v14H6z" stroke-linejoin="round" />
            <path d="M9 10h7M9 14h7M9 18h4" stroke-linecap="round" />
          </svg>
          <p class="empty-title">{{ role === 'buyer' ? '还没有买到的宝贝' : '还没有卖出的东西' }}</p>
          <p class="empty-sub">{{ role === 'buyer' ? '去首页看看有没有心仪的闲置' : '发布一些闲置，等同学来下单' }}</p>
          <button class="empty-btn" @click="router.push(role === 'buyer' ? '/goods' : '/goods/publish')">
            {{ role === 'buyer' ? '去逛逛' : '去发布' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { getMyOrders, payOrder, finishOrder, cancelOrder } from '../api/order'

const router = useRouter()

const roles = [
  { label: '我买到的', value: 'buyer' },
  { label: '我卖出的', value: 'seller' }
]

const tabs = [
  { label: '全部', value: '' },
  { label: '待付款', value: 0 },
  { label: '待收货', value: 1 },
  { label: '已完成', value: 2 },
  { label: '已取消', value: 3 }
]

const role = ref('buyer')
const status = ref('')
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = 5
const loading = ref(false)

const maxPage = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const pageList = computed(() => {
  const pages = []
  const start = Math.max(1, Math.min(pageNum.value - 2, maxPage.value - 4))
  const end = Math.min(maxPage.value, start + 4)
  for (let p = start; p <= end; p++) pages.push(p)
  return pages
})

const load = async () => {
  loading.value = true
  try {
    const res = await getMyOrders({
      pageNum: pageNum.value,
      pageSize,
      role: role.value,
      status: status.value === '' ? undefined : status.value
    })
    list.value = res?.records || []
    total.value = res?.total || 0
  } catch (e) {
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const changeRole = (v) => {
  if (role.value === v) return
  role.value = v
  pageNum.value = 1
  load()
}

const changeTab = (v) => {
  if (status.value === v) return
  status.value = v
  pageNum.value = 1
  load()
}

const goPage = (p) => {
  if (p < 1 || p > maxPage.value || p === pageNum.value) return
  pageNum.value = p
  load()
}

const onPay = async (o) => {
  try {
    await ElMessageBox.confirm(`确认支付 ￥${formatPrice(o.amount)} 吗？（演示环境为模拟支付）`, '订单付款', {
      confirmButtonText: '确认支付',
      cancelButtonText: '再等等',
      type: 'info'
    })
  } catch (e) {
    return
  }

  try {
    await payOrder(o.id)
    ElMessage.success('付款成功')
    load()
  } catch (e) {
    load()
  }
}

const onFinish = async (o) => {
  try {
    await ElMessageBox.confirm('请确认已经当面验货并拿到商品，确认后订单将完成。', '确认收货', {
      confirmButtonText: '已收到',
      cancelButtonText: '还没收到',
      type: 'warning'
    })
  } catch (e) {
    return
  }

  try {
    await finishOrder(o.id)
    ElMessage.success('交易完成')
    load()
  } catch (e) {
    load()
  }
}

const onCancel = async (o) => {
  let reason = ''
  try {
    const { value } = await ElMessageBox.prompt('请填写取消原因（100 字以内）', '取消订单', {
      confirmButtonText: '确认取消',
      cancelButtonText: '再想想',
      inputPlaceholder: '例如：和卖家约不上时间了',
      inputValidator: (val) => {
        if (val && val.length > 100) return '原因不能超过 100 字'
        return true
      }
    })
    reason = value || ''
  } catch (e) {
    return
  }

  try {
    await cancelOrder(o.id, reason)
    ElMessage.success('订单已取消')
    load()
  } catch (e) {
    load()
  }
}

const statusText = (v) => ({ 0: '待付款', 1: '待收货', 2: '已完成', 3: '已取消' }[v] || '未知')
const statusClass = (v) => ({ 0: 'pill-warn', 1: 'pill-primary', 2: 'pill-ok', 3: 'pill-info' }[v] || 'pill-info')

const formatPrice = (v) => {
  const n = Number(v || 0)
  if (!Number.isFinite(n)) return '0'
  return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0+$/, '').replace(/\.$/, '')
}

const formatTime = (t) => (t ? t.replace('T', ' ').slice(0, 16) : '')

onMounted(load)
</script>

<style scoped>
.page {
  min-height: 100vh;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 26px 0 18px;
}

/* 买家/卖家切换 */
.seg {
  display: inline-flex;
  padding: 3px;
  border-radius: 12px;
  background: #eef2f9;
}

.seg-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 9px;
  background: transparent;
  color: var(--ink-2);
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.22s var(--ease);
}

.seg-btn.active {
  background: #fff;
  color: var(--brand);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(23, 43, 99, 0.1);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 14px;
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  padding: 7px 15px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fff;
  color: var(--ink-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.chip:hover {
  border-color: #c7d7fb;
  color: var(--brand);
}

.chip.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  box-shadow: 0 8px 18px -10px rgba(59, 110, 246, 0.9);
}

.icon-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fff;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.icon-btn:hover {
  color: var(--brand);
  border-color: #c7d7fb;
  background: #f8faff;
}

/* 订单卡片 */
.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 220px;
}

.order {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
  transition: box-shadow 0.28s var(--ease), transform 0.28s var(--ease), border-color 0.28s var(--ease);
}

.order:hover {
  transform: translateY(-2px);
  border-color: #e2ebfd;
  box-shadow: var(--shadow-md);
}

.order-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 18px;
  background: #fafbfe;
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
}

.order-no {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.no-label {
  color: var(--muted-2);
  flex-shrink: 0;
}

.no-val {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  color: var(--ink-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-top-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.order-time {
  color: var(--muted-2);
}

.order-body {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) 120px;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
}

.thumb {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #f4f6fa;
  cursor: pointer;
  flex-shrink: 0;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease);
}

.order:hover .thumb img {
  transform: scale(1.06);
}

.thumb-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 11.5px;
  color: #b3bccd;
  background: linear-gradient(135deg, #f5f7fb, #eef2f9);
}

.main {
  min-width: 0;
}

.order-title {
  margin: 0 0 7px;
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s var(--ease);
}

.order-title:hover {
  color: var(--brand);
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
  flex-wrap: wrap;
}

.dot {
  color: #d3dae6;
}

.remark,
.cancel-reason,
.pay-time {
  margin-top: 6px;
  font-size: 12px;
  color: var(--muted);
  word-break: break-all;
}

.cancel-reason {
  color: #b45309;
}

.amount-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.amount {
  font-size: 19px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.3px;
}

.amount em {
  font-style: normal;
  font-size: 12px;
  font-weight: 600;
}

.amount-label {
  font-size: 11px;
  color: var(--muted-2);
}

.order-ops {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 18px 14px;
  border-top: 1px dashed var(--line);
}

.tip {
  margin-right: auto;
  font-size: 12px;
  color: var(--muted);
}

.tip-ok {
  color: var(--ok);
}

.btn-pay {
  height: 34px;
  padding: 0 18px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #fb7185, #ef4444);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 10px 20px -12px rgba(239, 68, 68, 0.95);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease);
}

.btn-pay:hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
}

.btn-ghost {
  height: 34px;
  padding: 0 16px;
  border: 1px solid #dbe4f7;
  border-radius: 10px;
  background: #fff;
  color: var(--ink-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.btn-ghost:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

/* 响应式 */
@media (max-width: 899px) {
  .order-body {
    grid-template-columns: 60px minmax(0, 1fr);
    row-gap: 8px;
  }

  .thumb {
    width: 60px;
    height: 60px;
  }

  .amount-col {
    flex-direction: row;
    align-items: baseline;
    gap: 8px;
    grid-column: 2;
  }

  .amount {
    font-size: 17px;
  }

  .order-ops {
    flex-wrap: wrap;
  }

  .tip {
    width: 100%;
    margin-bottom: 6px;
  }
}

@media (max-width: 640px) {
  .page-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .seg {
    width: 100%;
  }

  .seg-btn {
    flex: 1;
  }

  .order-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .order-top-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
