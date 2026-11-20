<template>
  <div class="page">
    <AppHeader active="admin" />

    <main class="wrap">
      <div class="page-head">
        <div>
          <h1 class="page-title">管理后台</h1>
          <p class="page-sub">平台运营数据 · 用户与内容治理</p>
        </div>
        <div class="head-actions">
          <button class="ghost-btn" @click="router.push('/goods')">返回前台</button>
          <button class="ghost-btn" @click="router.push('/orders')">我的订单</button>
        </div>
      </div>

      <!-- ============ 自定义 tab ============ -->
      <div class="tabs">
        <button
          v-for="t in tabList"
          :key="t.value"
          class="tab"
          :class="{ active: tab === t.value }"
          @click="tab = t.value"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- ============ 概览 ============ -->
      <section v-if="tab === 'stats'" class="stats">
        <div class="stat-grid">
          <div v-for="c in statCards" :key="c.label" class="stat-card" :class="c.accent">
            <div class="stat-label">{{ c.label }}</div>
            <div class="stat-value">{{ c.value }}</div>
            <div class="stat-sub">{{ c.sub }}</div>
          </div>
        </div>
        <p class="hint">统计口径：成交金额只累计「已付款 / 已完成」的订单，已取消的不计入。</p>
      </section>

      <!-- ============ 用户管理 ============ -->
      <section v-else-if="tab === 'users'" class="panel block">
        <div class="toolbar">
          <div class="field">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16l4 4" stroke-linecap="round" />
            </svg>
            <input v-model="userKeyword" placeholder="搜索用户名或昵称" @keyup.enter="reloadUsers" />
          </div>
          <button class="btn-primary sm" @click="reloadUsers">搜索</button>
          <span class="count">共 {{ userTotal }} 个账号</span>
        </div>

        <el-table v-loading="userLoading" :data="users" class="table">
          <el-table-column prop="id" label="ID" width="64" />
          <el-table-column prop="username" label="用户名" width="130" />
          <el-table-column prop="nickname" label="昵称" width="130" />
          <el-table-column prop="campus" label="校区" width="120" />
          <el-table-column prop="phone" label="手机号" width="126" />
          <el-table-column label="角色" width="88">
            <template #default="{ row }">
              <span class="pill" :class="row.role === 1 ? 'pill-err' : 'pill-info'">
                {{ row.role === 1 ? '管理员' : '学生' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="88">
            <template #default="{ row }">
              <span class="pill" :class="row.status === 1 ? 'pill-ok' : 'pill-err'">
                {{ row.status === 1 ? '正常' : '已禁用' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="140">
            <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="96" fixed="right">
            <template #default="{ row }">
              <button
                v-if="row.role !== 1"
                class="op"
                :class="row.status === 1 ? 'op-err' : 'op-ok'"
                @click="toggleUser(row)"
              >
                {{ row.status === 1 ? '禁用' : '启用' }}
              </button>
              <span v-else class="muted">—</span>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="userMax > 1" class="pager">
          <button class="page-btn" :disabled="userPage <= 1" @click="goPage('users', userPage - 1)">上一页</button>
          <button
            v-for="p in pageListOf(userPage, userMax)"
            :key="p"
            class="page-btn num"
            :class="{ active: p === userPage }"
            @click="goPage('users', p)"
          >
            {{ p }}
          </button>
          <button class="page-btn" :disabled="userPage >= userMax" @click="goPage('users', userPage + 1)">下一页</button>
        </div>
      </section>

      <!-- ============ 商品管理 ============ -->
      <section v-else-if="tab === 'goods'" class="panel block">
        <div class="toolbar">
          <div class="field">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16l4 4" stroke-linecap="round" />
            </svg>
            <input v-model="goodsKeyword" placeholder="搜索商品标题" @keyup.enter="reloadGoods" />
          </div>
          <select v-model="goodsStatus" class="select" @change="reloadGoods">
            <option value="">全部状态</option>
            <option :value="0">已下架</option>
            <option :value="1">在售</option>
            <option :value="2">交易中</option>
            <option :value="3">已售出</option>
          </select>
          <button class="btn-primary sm" @click="reloadGoods">搜索</button>
          <span class="count">共 {{ goodsTotal }} 件商品</span>
        </div>

        <el-table v-loading="goodsLoading" :data="goodsList" class="table">
          <el-table-column prop="id" label="ID" width="64" />
          <el-table-column prop="title" label="标题" min-width="190" show-overflow-tooltip />
          <el-table-column prop="category" label="分类" width="96" />
          <el-table-column label="售价" width="96">
            <template #default="{ row }">
              <span class="money">￥{{ formatPrice(row.price) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="viewCount" label="浏览" width="76" />
          <el-table-column label="状态" width="96">
            <template #default="{ row }">
              <span class="pill" :class="statusClass(row.status)">{{ statusText(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="发布时间" width="140">
            <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="152" fixed="right">
            <template #default="{ row }">
              <button class="op" @click="router.push(`/goods/${row.id}`)">查看</button>
              <button
                v-if="row.status !== 2"
                class="op"
                :class="row.status === 1 ? 'op-err' : 'op-ok'"
                @click="toggleGoods(row)"
              >
                {{ row.status === 1 ? '强制下架' : '恢复上架' }}
              </button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="goodsMax > 1" class="pager">
          <button class="page-btn" :disabled="goodsPage <= 1" @click="goPage('goods', goodsPage - 1)">上一页</button>
          <button
            v-for="p in pageListOf(goodsPage, goodsMax)"
            :key="p"
            class="page-btn num"
            :class="{ active: p === goodsPage }"
            @click="goPage('goods', p)"
          >
            {{ p }}
          </button>
          <button class="page-btn" :disabled="goodsPage >= goodsMax" @click="goPage('goods', goodsPage + 1)">下一页</button>
        </div>
      </section>

      <!-- ============ 订单总览 ============ -->
      <section v-else class="panel block">
        <div class="toolbar">
          <div class="field">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16l4 4" stroke-linecap="round" />
            </svg>
            <input v-model="orderKeyword" placeholder="搜索订单号或商品标题" @keyup.enter="reloadOrders" />
          </div>
          <select v-model="orderStatus" class="select" @change="reloadOrders">
            <option value="">全部状态</option>
            <option :value="0">待付款</option>
            <option :value="1">已付款</option>
            <option :value="2">已完成</option>
            <option :value="3">已取消</option>
          </select>
          <button class="btn-primary sm" @click="reloadOrders">搜索</button>
          <span class="count">共 {{ orderTotal }} 笔订单</span>
        </div>

        <el-table v-loading="orderLoading" :data="orderList" class="table">
          <el-table-column prop="orderNo" label="订单号" width="186" show-overflow-tooltip />
          <el-table-column prop="goodsTitle" label="商品" min-width="170" show-overflow-tooltip />
          <el-table-column label="金额" width="96">
            <template #default="{ row }">
              <span class="money">￥{{ formatPrice(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="buyerNickname" label="买家" width="110" />
          <el-table-column prop="sellerNickname" label="卖家" width="110" />
          <el-table-column label="状态" width="96">
            <template #default="{ row }">
              <span class="pill" :class="orderStatusClass(row.status)">{{ orderStatusText(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="下单时间" width="140">
            <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
          </el-table-column>
        </el-table>

        <div v-if="orderMax > 1" class="pager">
          <button class="page-btn" :disabled="orderPage <= 1" @click="goPage('orders', orderPage - 1)">上一页</button>
          <button
            v-for="p in pageListOf(orderPage, orderMax)"
            :key="p"
            class="page-btn num"
            :class="{ active: p === orderPage }"
            @click="goPage('orders', p)"
          >
            {{ p }}
          </button>
          <button class="page-btn" :disabled="orderPage >= orderMax" @click="goPage('orders', orderPage + 1)">下一页</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import {
  changeAdminGoodsStatus,
  changeUserStatus,
  getAdminGoods,
  getAdminOrders,
  getAdminStats,
  getAdminUsers
} from '../api/admin'

const router = useRouter()
const tab = ref('stats')

const tabList = [
  { label: '数据概览', value: 'stats' },
  { label: '用户管理', value: 'users' },
  { label: '商品管理', value: 'goods' },
  { label: '订单总览', value: 'orders' }
]

// ---------- 概览 ----------
const stats = ref({})

const loadStats = async () => {
  try {
    stats.value = await getAdminStats()
  } catch (e) {
    // 提示由拦截器统一处理
  }
}

const statCards = computed(() => [
  {
    label: '注册用户',
    value: stats.value.userCount ?? '—',
    sub: '平台全部账号',
    accent: 'blue'
  },
  {
    label: '在售商品',
    value: stats.value.onSaleCount ?? '—',
    sub: `全部商品 ${stats.value.goodsCount ?? 0} 件`,
    accent: 'violet'
  },
  {
    label: '累计订单',
    value: stats.value.orderCount ?? '—',
    sub: `今日新增 ${stats.value.todayOrderCount ?? 0} 笔`,
    accent: 'amber'
  },
  {
    label: '成交金额',
    value: `￥${formatPrice(stats.value.tradeAmount ?? 0)}`,
    sub: `已完成 ${stats.value.finishedCount ?? 0} 单`,
    accent: 'rose'
  }
])

// ---------- 用户 ----------
const users = ref([])
const userKeyword = ref('')
const userPage = ref(1)
const userSize = ref(10)
const userTotal = ref(0)
const userLoading = ref(false)

const userMax = computed(() => Math.max(1, Math.ceil(userTotal.value / userSize.value)))

const loadUsers = async () => {
  userLoading.value = true
  try {
    const page = await getAdminUsers({ pageNum: userPage.value, pageSize: userSize.value, keyword: userKeyword.value })
    users.value = page.records || []
    userTotal.value = Number(page.total || 0)
  } catch (e) {
    // 提示由拦截器统一处理
  } finally {
    userLoading.value = false
  }
}

const reloadUsers = () => {
  userPage.value = 1
  loadUsers()
}

const toggleUser = async (row) => {
  const target = row.status === 1 ? 0 : 1
  const action = target === 0 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确认${action}用户「${row.username}」？${target === 0 ? '禁用后该用户无法登录。' : ''}`,
      `${action}用户`,
      { type: 'warning' }
    )
  } catch (e) {
    return
  }
  try {
    await changeUserStatus(row.id, target)
    ElMessage.success(`已${action}`)
    loadUsers()
  } catch (e) {
    // 提示由拦截器统一处理
  }
}

// ---------- 商品 ----------
const goodsList = ref([])
const goodsKeyword = ref('')
const goodsStatus = ref('')
const goodsPage = ref(1)
const goodsSize = ref(10)
const goodsTotal = ref(0)
const goodsLoading = ref(false)

const goodsMax = computed(() => Math.max(1, Math.ceil(goodsTotal.value / goodsSize.value)))

const loadGoods = async () => {
  goodsLoading.value = true
  try {
    const page = await getAdminGoods({
      pageNum: goodsPage.value,
      pageSize: goodsSize.value,
      keyword: goodsKeyword.value,
      status: goodsStatus.value === '' ? undefined : goodsStatus.value
    })
    goodsList.value = page.records || []
    goodsTotal.value = Number(page.total || 0)
  } catch (e) {
    // 提示由拦截器统一处理
  } finally {
    goodsLoading.value = false
  }
}

const reloadGoods = () => {
  goodsPage.value = 1
  loadGoods()
}

const toggleGoods = async (row) => {
  const target = row.status === 1 ? 0 : 1
  const action = target === 0 ? '强制下架' : '恢复上架'
  try {
    await ElMessageBox.confirm(`确认对商品「${row.title}」执行${action}？`, action, { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    await changeAdminGoodsStatus(row.id, target)
    ElMessage.success(`已${action}`)
    loadGoods()
  } catch (e) {
    // 提示由拦截器统一处理
  }
}

// ---------- 订单 ----------
const orderList = ref([])
const orderKeyword = ref('')
const orderStatus = ref('')
const orderPage = ref(1)
const orderSize = ref(10)
const orderTotal = ref(0)
const orderLoading = ref(false)

const orderMax = computed(() => Math.max(1, Math.ceil(orderTotal.value / orderSize.value)))

const loadOrders = async () => {
  orderLoading.value = true
  try {
    const page = await getAdminOrders({
      pageNum: orderPage.value,
      pageSize: orderSize.value,
      keyword: orderKeyword.value,
      status: orderStatus.value === '' ? undefined : orderStatus.value
    })
    orderList.value = page.records || []
    orderTotal.value = Number(page.total || 0)
  } catch (e) {
    // 提示由拦截器统一处理
  } finally {
    orderLoading.value = false
  }
}

const reloadOrders = () => {
  orderPage.value = 1
  loadOrders()
}

// 切到哪个 tab 才加载哪个，避免一进来就发 4 个请求
watch(tab, (val) => {
  if (val === 'stats') loadStats()
  if (val === 'users' && users.value.length === 0) loadUsers()
  if (val === 'goods' && goodsList.value.length === 0) loadGoods()
  if (val === 'orders' && orderList.value.length === 0) loadOrders()
})

const goPage = (type, p) => {
  if (type === 'users') {
    if (p < 1 || p > userMax.value || p === userPage.value) return
    userPage.value = p
    loadUsers()
  } else if (type === 'goods') {
    if (p < 1 || p > goodsMax.value || p === goodsPage.value) return
    goodsPage.value = p
    loadGoods()
  } else {
    if (p < 1 || p > orderMax.value || p === orderPage.value) return
    orderPage.value = p
    loadOrders()
  }
}

// 只显示当前页附近 5 个页码
const pageListOf = (cur, max) => {
  const start = Math.max(1, Math.min(cur - 2, max - 4))
  const end = Math.min(max, start + 4)
  const arr = []
  for (let p = start; p <= end; p++) arr.push(p)
  return arr
}

const statusText = (v) => ({ 0: '已下架', 1: '在售', 2: '交易中', 3: '已售出' }[v] || '未知')
const statusClass = (v) => ({ 0: 'pill-info', 1: 'pill-ok', 2: 'pill-warn', 3: 'pill-info' }[v] || 'pill-info')
const orderStatusText = (v) => ({ 0: '待付款', 1: '已付款', 2: '已完成', 3: '已取消' }[v] || '未知')
const orderStatusClass = (v) => ({ 0: 'pill-warn', 1: 'pill-primary', 2: 'pill-ok', 3: 'pill-info' }[v] || 'pill-info')

const formatPrice = (v) => {
  const n = Number(v || 0)
  if (!Number.isFinite(n)) return '0'
  return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

const formatTime = (t) => (t ? t.replace('T', ' ').slice(0, 16) : '—')

onMounted(loadStats)
</script>

<style scoped>
.head-actions {
  display: flex;
  gap: 8px;
}

.ghost-btn {
  height: 34px;
  padding: 0 15px;
  border: 1px solid #dbe4f7;
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--ink-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.ghost-btn:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

/* ---------- tab ---------- */
.tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  margin-bottom: 18px;
  background: #f1f4fa;
  border-radius: 13px;
  width: fit-content;
}

.tab {
  padding: 9px 18px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--ink-2);
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.22s var(--ease);
}

.tab:hover {
  color: var(--brand);
}

.tab.active {
  background: #fff;
  color: var(--brand);
  font-weight: 600;
  box-shadow: 0 2px 10px -4px rgba(23, 43, 99, 0.22);
}

/* ---------- 概览卡 ---------- */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  padding: 20px 20px 18px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  background: #fff;
  box-shadow: var(--shadow-xs);
  transition: transform 0.28s var(--ease), box-shadow 0.28s var(--ease);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.stat-card::after {
  content: '';
  position: absolute;
  right: -34px;
  top: -34px;
  width: 108px;
  height: 108px;
  border-radius: 50%;
  opacity: 0.16;
}

.stat-card.blue::after {
  background: #3b6ef6;
}

.stat-card.violet::after {
  background: #7c5cf6;
}

.stat-card.amber::after {
  background: #f59e0b;
}

.stat-card.rose::after {
  background: #ef4444;
}

.stat-label {
  font-size: 12.5px;
  color: var(--muted);
}

.stat-value {
  margin-top: 10px;
  font-size: 27px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}

.stat-card.rose .stat-value {
  color: var(--price);
}

.stat-sub {
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--muted-2);
}

.hint {
  margin: 14px 0 0;
  font-size: 12px;
  color: var(--muted-2);
}

/* ---------- 表格面板 ---------- */
.block {
  padding: 18px 18px 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.field {
  display: flex;
  align-items: center;
  gap: 7px;
  height: 36px;
  padding: 0 12px;
  width: 250px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--muted-2);
  transition: all 0.2s var(--ease);
}

.field:focus-within {
  border-color: #b9caf7;
  box-shadow: 0 0 0 4px rgba(59, 110, 246, 0.08);
  color: var(--brand);
}

.field input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--ink);
}

.field input::placeholder {
  color: var(--muted-2);
}

.select {
  height: 36px;
  padding: 0 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--ink-2);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s var(--ease);
}

.select:hover,
.select:focus {
  border-color: #b9caf7;
}

.btn-primary.sm {
  height: 36px;
  padding: 0 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-brand);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease);
}

.btn-primary.sm:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.count {
  margin-left: auto;
  font-size: 12px;
  color: var(--muted-2);
}

/* ---------- Element 表格统一观感 ---------- */
.table {
  --el-table-border-color: var(--line-soft);
  --el-table-header-bg-color: #f7f9fd;
  --el-table-row-hover-bg-color: #f8faff;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table :deep(th.el-table__cell) {
  background: #f7f9fd !important;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  height: 42px;
  border-bottom: 1px solid var(--line);
}

.table :deep(td.el-table__cell) {
  font-size: 13px;
  color: var(--ink-2);
  height: 52px;
}

.table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.money {
  font-weight: 600;
  color: var(--price);
  font-variant-numeric: tabular-nums;
}

.op {
  border: none;
  background: transparent;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 12.5px;
  color: var(--brand);
  cursor: pointer;
  transition: background 0.2s var(--ease), color 0.2s var(--ease);
}

.op:hover {
  background: var(--brand-soft);
}

.op-err {
  color: #dc2626;
}

.op-err:hover {
  background: #fef2f2;
}

.op-ok {
  color: var(--ok);
}

.op-ok:hover {
  background: #eafaf0;
}

.muted {
  color: #c2cad8;
}

@media (max-width: 1023px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .tabs {
    width: 100%;
    overflow-x: auto;
  }

  .tab {
    flex: 1;
    padding: 9px 10px;
    white-space: nowrap;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .field {
    width: 100%;
  }

  .count {
    margin-left: 0;
    width: 100%;
  }
}
</style>
