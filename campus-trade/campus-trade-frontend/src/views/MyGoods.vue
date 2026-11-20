<template>
  <div class="page">
    <AppHeader active="my-goods" />

    <main class="wrap">
      <div class="page-head">
        <div>
          <h1 class="page-title">我的发布</h1>
          <p class="page-sub">在这里管理你发布的所有闲置，共 {{ total }} 件</p>
        </div>
        <button class="btn-primary" @click="router.push('/goods/publish')">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 5v14M5 12h14" stroke-linecap="round" />
          </svg>
          发布闲置
        </button>
      </div>

      <!-- 筛选 -->
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

      <!-- 列表 -->
      <div v-loading="loading" class="list">
        <template v-if="list.length">
          <article v-for="row in list" :key="row.id" class="row">
            <div class="thumb" @click="router.push(`/goods/${row.id}`)">
              <img v-if="row.coverImg" :src="row.coverImg" alt="" />
              <div v-else class="thumb-empty">{{ row.category || '二手' }}</div>
            </div>

            <div class="main">
              <h3 class="row-title" @click="router.push(`/goods/${row.id}`)">{{ row.title }}</h3>
              <div class="row-meta">
                <span class="pill" :class="statusClass(row.status)">{{ statusText(row.status) }}</span>
                <span class="dot">·</span>
                <span>{{ conditionText(row.itemCondition) }}</span>
                <span class="dot">·</span>
                <span>{{ row.viewCount || 0 }} 次浏览</span>
                <span class="dot">·</span>
                <span>{{ formatTime(row.createTime) }}</span>
              </div>
            </div>

            <div class="price-col">
              <span class="price"><em>￥</em>{{ formatPrice(row.price) }}</span>
              <span v-if="hasOrigin(row)" class="origin">￥{{ formatPrice(row.originalPrice) }}</span>
            </div>

            <div class="ops">
              <button v-if="row.status === 0 || row.status === 1" class="op" @click="router.push(`/goods/edit/${row.id}`)">
                编辑
              </button>
              <button v-if="row.status === 0" class="op op-ok" @click="onToggle(row, 1)">上架</button>
              <button v-if="row.status === 1" class="op" @click="onToggle(row, 0)">下架</button>
              <button v-if="row.status !== 2" class="op op-err" @click="onDelete(row)">删除</button>
            </div>
          </article>

          <!-- 分页 -->
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
            <path d="M4 7l8-4 8 4v10l-8 4-8-4V7z" stroke-linejoin="round" />
            <path d="M4 7l8 4 8-4M12 11v10" stroke-linejoin="round" />
          </svg>
          <p class="empty-title">{{ status === '' ? '你还没有发布过闲置' : '这个状态下没有商品' }}</p>
          <p class="empty-sub">把宿舍里用不上的东西挂上来，说不定有人正需要</p>
          <button class="empty-btn" @click="router.push('/goods/publish')">去发布</button>
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
import { getMyGoods, changeGoodsStatus, deleteGoods } from '../api/goods'

const router = useRouter()

const tabs = [
  { label: '全部', value: '' },
  { label: '在售', value: 1 },
  { label: '已下架', value: 0 },
  { label: '交易中', value: 2 },
  { label: '已售出', value: 3 }
]

const status = ref('')
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = 8
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
    const res = await getMyGoods({
      pageNum: pageNum.value,
      pageSize,
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

const onToggle = async (row, target) => {
  try {
    await changeGoodsStatus(row.id, target)
    ElMessage.success(target === 1 ? '已重新上架' : '已下架')
    load()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

const onDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？删除后无法恢复。`, '删除商品', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (e) {
    return
  }

  try {
    await deleteGoods(row.id)
    ElMessage.success('已删除')
    if (list.value.length === 1 && pageNum.value > 1) pageNum.value -= 1
    load()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

const conditionText = (v) => ({ 1: '全新', 2: '九成新', 3: '七成新', 4: '五成新及以下' }[v] || '未标注')
const statusText = (v) => ({ 0: '已下架', 1: '在售', 2: '交易中', 3: '已售出' }[v] || '未知')
const statusClass = (v) => ({ 0: 'pill-info', 1: 'pill-ok', 2: 'pill-warn', 3: 'pill-info' }[v] || 'pill-info')
const hasOrigin = (row) => row.originalPrice && Number(row.originalPrice) > Number(row.price)

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

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 18px;
  border: none;
  border-radius: 11px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-brand);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease);
}

.btn-primary:hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
}

/* 筛选栏 */
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

/* 列表 */
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 220px;
}

.row {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr) 120px auto;
  align-items: center;
  gap: 16px;
  padding: 14px 18px 14px 14px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.28s var(--ease), transform 0.28s var(--ease), border-color 0.28s var(--ease);
}

.row:hover {
  transform: translateY(-2px);
  border-color: #e2ebfd;
  box-shadow: var(--shadow-md);
}

.thumb {
  width: 76px;
  height: 76px;
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

.row:hover .thumb img {
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

.row-title {
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

.row-title:hover {
  color: var(--brand);
}

.row-meta {
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

.price-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.price {
  font-size: 17px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.3px;
}

.price em {
  font-style: normal;
  font-size: 11.5px;
  font-weight: 600;
}

.origin {
  font-size: 11.5px;
  color: var(--muted-2);
  text-decoration: line-through;
}

.ops {
  display: flex;
  align-items: center;
  gap: 6px;
}

.op {
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: #fff;
  color: var(--ink-2);
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
  white-space: nowrap;
}

.op:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

.op-ok:hover {
  border-color: #a7e3c0;
  color: var(--ok);
  background: #f2fbf6;
}

.op-err:hover {
  border-color: #fbc9c9;
  color: #dc2626;
  background: #fef4f4;
}

/* 响应式 */
@media (max-width: 899px) {
  .row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px 12px;
    padding: 14px;
  }

  .thumb {
    width: 64px;
    height: 64px;
  }

  .main {
    flex: 1 1 calc(100% - 80px);
  }

  .price-col {
    flex: 0 0 auto;
    flex-direction: row;
    align-items: baseline;
    gap: 8px;
    margin-left: 76px;
  }

  .ops {
    margin-left: auto;
  }
}

@media (max-width: 520px) {
  .price-col {
    margin-left: 0;
  }

  .ops {
    width: 100%;
    justify-content: flex-end;
    padding-top: 10px;
    border-top: 1px dashed var(--line);
  }
}

@media (max-width: 640px) {
  .page-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
