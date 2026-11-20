<template>
  <div class="page">
    <AppHeader active="home" />

    <!-- ================= 搜索区 ================= -->
    <section class="hero">
      <div class="hero-glow glow-a"></div>
      <div class="hero-glow glow-b"></div>

      <div class="hero-inner">
        <p class="hero-eye">校内当面交易 · 学生实名 · 验货再付款</p>
        <h1 class="hero-title">同学之间，闲置更划算</h1>

        <div class="search-bar">
          <span class="search-icon">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16l4 4" stroke-linecap="round" />
            </svg>
          </span>
          <input
            v-model="keyword"
            class="search-field"
            type="text"
            placeholder="搜索商品，如：高数教材 / 自行车 / 蓝牙耳机"
            @keyup.enter="onSearch"
          />
          <button v-if="keyword" class="clear-btn" title="清空" @click="clearKeyword">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
            </svg>
          </button>
          <button class="search-btn" @click="onSearch">搜索</button>
        </div>

        <div class="chips">
          <button
            v-for="tab in categoryTabs"
            :key="tab.value"
            class="chip"
            :class="{ active: category === tab.value }"
            @click="selectCategory(tab.value)"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </section>

    <!-- ================= 商品列表 ================= -->
    <main class="wrap">
      <div class="section-head">
        <h2 class="section-title">在售好物</h2>
        <span v-if="total" class="section-count">共 {{ total }} 件</span>
      </div>

      <div v-loading="loading" class="goods-grid">
        <article
          v-for="item in list"
          :key="item.id"
          class="card"
          @click="router.push(`/goods/${item.id}`)"
        >
          <div class="card-cover">
            <el-image v-if="item.coverImg" :src="item.coverImg" :alt="item.title" fit="cover" class="cover-img" lazy>
              <template #error>
                <div class="cover-fallback">
                  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="5" width="18" height="14" rx="2.5" />
                    <circle cx="8.5" cy="10" r="1.5" />
                    <path d="M4 17l5-4.5 4 3.5 3-2.5 4 3.5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <span>{{ item.category || '闲置好物' }}</span>
                </div>
              </template>
            </el-image>
            <div v-else class="cover-fallback">
              <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="5" width="18" height="14" rx="2.5" />
                <circle cx="8.5" cy="10" r="1.5" />
                <path d="M4 17l5-4.5 4 3.5 3-2.5 4 3.5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span>{{ item.category || '闲置好物' }}</span>
            </div>

            <span v-if="item.itemCondition" class="cond-badge">{{ conditionText(item.itemCondition) }}</span>
          </div>

          <div class="card-body">
            <h3 class="card-title" :title="item.title">{{ item.title }}</h3>

            <div class="card-price">
              <span class="rmb">￥</span>
              <span class="amount">{{ formatPrice(item.price) }}</span>
              <span
                v-if="item.originalPrice && Number(item.originalPrice) > Number(item.price)"
                class="origin"
              >￥{{ formatPrice(item.originalPrice) }}</span>
            </div>

            <div class="card-meta">
              <span class="tag">{{ item.category || '其他' }}</span>
              <span class="views">浏览 {{ item.viewCount || 0 }}</span>
            </div>
          </div>
        </article>

        <div v-if="!loading && list.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" width="46" height="46" fill="none" stroke="currentColor" stroke-width="1.3">
            <circle cx="11" cy="11" r="7" />
            <path d="M16.5 16.5L21 21" stroke-linecap="round" />
          </svg>
          <p class="empty-title">没找到相关商品</p>
          <p class="empty-sub">换个关键词，或者让 AI 导购帮你找找</p>
          <button class="empty-btn" @click="resetAll">看看全部商品</button>
        </div>
      </div>

      <div v-if="maxPage > 1" class="pager">
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
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { getGoodsPage } from '../api/goods'

const router = useRouter()

// 分类要和后端 / 发布页保持一致
const categories = ['教材', '数码', '生活用品', '运动', '其他']
const categoryTabs = [{ label: '全部', value: '' }, ...categories.map((c) => ({ label: c, value: c }))]

const keyword = ref('')
const category = ref('')
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(12)
const loading = ref(false)

const maxPage = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

// 页码只显示当前页附近的 5 个，避免页数多了把布局撑坏
const pageList = computed(() => {
  const pages = []
  const end = Math.min(maxPage.value, Math.max(1, pageNum.value - 2) + 4)
  const start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const conditionText = (v) =>
  ({ 1: '全新', 2: '九成新', 3: '七成新', 4: '五成新及以下' })[v] || ''

const formatPrice = (v) => {
  const n = Number(v || 0)
  if (!Number.isFinite(n)) return '0'
  return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0+$/, '').replace(/\.$/, '')
}

const loadGoods = async () => {
  loading.value = true
  try {
    // 拦截器已拆包，这里拿到的就是 Page 对象
    const page = await getGoodsPage({
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      keyword: keyword.value,
      category: category.value
    })
    list.value = page.records || []
    total.value = Number(page.total || 0)
    // 搜索 / 删页后当前页可能超出范围，自动回退
    if (pageNum.value > maxPage.value) {
      pageNum.value = maxPage.value
      await loadGoods()
    }
  } catch (e) {
    // 错误提示由拦截器统一处理
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  pageNum.value = 1
  loadGoods()
}

const selectCategory = (value) => {
  if (category.value === value) return
  category.value = value
  onSearch()
}

const clearKeyword = () => {
  keyword.value = ''
  onSearch()
}

const resetAll = () => {
  keyword.value = ''
  category.value = ''
  onSearch()
}

const goPage = (p) => {
  if (p < 1 || p > maxPage.value || p === pageNum.value) return
  pageNum.value = p
  loadGoods()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadGoods)
</script>

<style scoped>
.page {
  min-height: 100vh;
}

/* ---------- Hero 搜索区 ---------- */
.hero {
  position: relative;
  overflow: hidden;
  padding: 46px 24px 34px;
  background: linear-gradient(180deg, #f4f8ff 0%, var(--page-bg) 100%);
  border-bottom: 1px solid var(--line);
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(64px);
  pointer-events: none;
}

.glow-a {
  width: 380px;
  height: 380px;
  top: -170px;
  left: 6%;
  background: rgba(59, 110, 246, 0.16);
}

.glow-b {
  width: 320px;
  height: 320px;
  top: -140px;
  right: 8%;
  background: rgba(99, 102, 241, 0.13);
}

.hero-inner {
  position: relative;
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.hero-eye {
  margin: 0 0 12px;
  font-size: 12.5px;
  letter-spacing: 1.6px;
  color: #7d8aa3;
}

.hero-title {
  margin: 0 0 26px;
  font-size: 30px;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: 0.4px;
  background: linear-gradient(120deg, var(--ink) 20%, var(--brand) 90%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 54px;
  padding: 0 8px 0 16px;
  background: #fff;
  border: 1px solid #e6ebf5;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  transition: border-color 0.22s var(--ease), box-shadow 0.22s var(--ease);
}

.search-bar:focus-within {
  border-color: #b9caf7;
  box-shadow: 0 16px 38px -18px rgba(59, 110, 246, 0.55), 0 0 0 4px rgba(59, 110, 246, 0.08);
}

.search-icon {
  display: grid;
  place-items: center;
  color: #9aa5b8;
  flex-shrink: 0;
}

.search-field {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14.5px;
  color: var(--ink);
  font-family: inherit;
}

.search-field::placeholder {
  color: #a9b3c4;
}

.clear-btn {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: #f1f4f9;
  color: var(--muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s var(--ease), color 0.2s var(--ease);
}

.clear-btn:hover {
  background: #e6ebf4;
  color: #5a6474;
}

.search-btn {
  flex-shrink: 0;
  height: 40px;
  padding: 0 24px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 1px;
  box-shadow: var(--shadow-brand);
  transition: filter 0.2s var(--ease), transform 0.2s var(--ease);
}

.search-btn:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.chip {
  height: 32px;
  padding: 0 15px;
  border: 1px solid #e6ebf5;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  color: #5a6474;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.chip:hover {
  border-color: #c7d6f9;
  color: var(--brand);
  background: #fff;
}

.chip.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-weight: 600;
  box-shadow: var(--shadow-brand);
}

/* ---------- 列表标题 ---------- */
.section-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin: 30px 0 18px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.section-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 15px;
  margin-right: 9px;
  border-radius: 3px;
  background: linear-gradient(180deg, var(--brand), var(--brand-2));
  vertical-align: -1.5px;
}

.section-count {
  font-size: 12.5px;
  color: var(--muted);
}

/* ---------- 卡片网格：电脑 4 列，平板 3 列，手机 2 列 ---------- */
.goods-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  min-height: 260px;
  align-content: start;
}

.card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-xs);
  transition: transform 0.32s var(--ease), box-shadow 0.32s var(--ease), border-color 0.32s ease;
  will-change: transform;
}

.card:hover {
  transform: translateY(-6px);
  border-color: #dbe4f7;
  box-shadow: var(--shadow-lg);
}

.card-cover {
  position: relative;
  aspect-ratio: 4 / 3;
  background: #f4f6fa;
  overflow: hidden;
}

.card-cover :deep(.el-image) {
  display: block;
  width: 100%;
  height: 100%;
}

.card-cover :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease);
}

.card:hover .card-cover :deep(.el-image__inner) {
  transform: scale(1.06);
}

.cover-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #b3bccd;
  font-size: 12.5px;
  background: linear-gradient(135deg, #f5f7fb, #eef2f9);
}

.cond-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: #4b5cd6;
  font-size: 11.5px;
  font-weight: 600;
  backdrop-filter: blur(6px);
  box-shadow: 0 2px 6px rgba(23, 43, 99, 0.1);
}

.card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 13px 14px 14px;
}

.card-title {
  margin: 0 0 8px;
  min-height: 40px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.45;
  color: var(--ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}

.card-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-top: auto;
}

.rmb {
  font-size: 13px;
  font-weight: 600;
  color: var(--price);
}

.amount {
  font-size: 20px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.3px;
}

.origin {
  margin-left: 6px;
  font-size: 12px;
  color: var(--muted-2);
  text-decoration: line-through;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 9px;
  font-size: 12px;
  color: var(--muted);
}

.tag {
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--brand-soft);
  color: #4f5bd5;
  font-size: 11.5px;
}

.views {
  color: var(--muted-2);
}

/* ---------- 响应式 ---------- */
@media (max-width: 1199px) {
  .goods-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }
}

@media (max-width: 899px) {
  .hero {
    padding: 36px 20px 28px;
  }

  .hero-title {
    font-size: 25px;
    margin-bottom: 20px;
  }
}

@media (max-width: 767px) {
  .goods-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .card-body {
    padding: 10px 11px 12px;
  }

  .card-title {
    font-size: 13px;
    min-height: 37px;
  }

  .amount {
    font-size: 18px;
  }

  .search-bar {
    height: 48px;
    padding-left: 12px;
    border-radius: 14px;
  }

  .search-btn {
    height: 36px;
    padding: 0 16px;
    font-size: 13px;
  }

  .hero-title {
    font-size: 21px;
  }

  .hero-eye {
    font-size: 11.5px;
    letter-spacing: 1px;
  }
}

@media (max-width: 420px) {
  .chip {
    height: 30px;
    padding: 0 12px;
    font-size: 12.5px;
  }
}
</style>
