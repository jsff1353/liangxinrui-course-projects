<template>
  <div class="page">
    <AppHeader active="home" back />

    <main v-loading="loading" class="wrap">
      <template v-if="goods">
        <div class="crumb">
          <span class="crumb-link" @click="router.push('/goods')">首页</span>
          <span class="crumb-sep">/</span>
          <span class="crumb-link" @click="router.push('/goods')">{{ goods.category || '其他' }}</span>
          <span class="crumb-sep">/</span>
          <span class="crumb-cur">{{ goods.title }}</span>
        </div>

        <div class="detail-grid">
          <!-- 左：图片 -->
          <section class="gallery">
            <el-image
              v-if="goods.coverImg"
              :src="goods.coverImg"
              fit="cover"
              class="cover"
              :preview-src-list="[goods.coverImg]"
            />
            <div v-else class="cover cover-fallback">
              <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.4">
                <rect x="3" y="5" width="18" height="14" rx="2.5" />
                <circle cx="8.5" cy="10" r="1.5" />
                <path d="M4 17l5-4.5 4 3.5 3-2.5 4 3.5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span>{{ goods.category || '二手好物' }}</span>
            </div>
            <span v-if="goods.itemCondition" class="cond-badge">{{ conditionText(goods.itemCondition) }}</span>
          </section>

          <!-- 右：信息 -->
          <section class="info">
            <div class="info-top">
              <h1 class="title">{{ goods.title }}</h1>
              <div class="price-row">
                <span class="price"><em>￥</em>{{ formatPrice(goods.price) }}</span>
                <span v-if="hasOrigin" class="origin">原价 ￥{{ formatPrice(goods.originalPrice) }}</span>
                <span class="pill" :class="statusClass(goods.status)">{{ statusText(goods.status) }}</span>
              </div>
            </div>

            <ul class="meta">
              <li><span class="k">分类</span><span class="v">{{ goods.category || '—' }}</span></li>
              <li><span class="k">成色</span><span class="v">{{ conditionText(goods.itemCondition) }}</span></li>
              <li><span class="k">交易地点</span><span class="v">{{ goods.tradePlace || '校内当面交易' }}</span></li>
              <li><span class="k">联系方式</span><span class="v">{{ goods.contact || '下单后联系卖家' }}</span></li>
              <li><span class="k">浏览</span><span class="v">{{ goods.viewCount || 0 }} 次</span></li>
              <li><span class="k">发布时间</span><span class="v">{{ formatTime(goods.createTime) }}</span></li>
            </ul>

            <div class="seller">
              <span class="seller-avatar">{{ (goods.sellerNickname || '同').slice(0, 1) }}</span>
              <div class="seller-info">
                <div class="seller-name">
                  {{ goods.sellerNickname || '匿名卖家' }}
                  <span class="seller-badge">卖家</span>
                </div>
                <div class="seller-campus">{{ goods.sellerCampus || '校区未填写' }}</div>
              </div>
            </div>

            <div class="actions">
              <template v-if="goods.mine">
                <button class="btn-primary" @click="router.push(`/goods/edit/${goods.id}`)">去编辑这件商品</button>
                <button class="btn-ghost" @click="router.push('/my-goods')">我的发布</button>
              </template>
              <template v-else>
                <button class="btn-buy" :disabled="!canBuy" @click="onBuy">{{ buyButtonText }}</button>
                <button class="btn-ghost" @click="router.push('/orders')">我的订单</button>
              </template>
            </div>

            <p class="hint">下单后商品锁定 2 小时，超时未付款会自动取消并重新上架。</p>
          </section>
        </div>

        <section class="block">
          <h2 class="block-title">商品描述</h2>
          <div class="block-body">{{ goods.description || '卖家很懒，没有写描述。' }}</div>
        </section>

        <div class="notice">
          <strong>交易提示</strong>
          请在校内公共区域当面验货、当面付款。平台仅提供信息撮合，不要脱离平台与陌生人进行大额转账。
        </div>
      </template>

      <div v-else-if="!loading" class="empty-state">
        <svg viewBox="0 0 24 24" width="46" height="46" fill="none" stroke="currentColor" stroke-width="1.3">
          <path d="M4 7l8-4 8 4v10l-8 4-8-4V7z" stroke-linejoin="round" />
          <path d="M4 7l8 4 8-4M12 11v10" stroke-linejoin="round" />
        </svg>
        <p class="empty-title">商品不存在或已删除</p>
        <p class="empty-sub">它可能已经被卖家下架了，去首页看看别的</p>
        <button class="empty-btn" @click="router.push('/goods')">回首页逛逛</button>
      </div>
    </main>

    <!-- 下单确认 -->
    <el-dialog v-model="dialogVisible" title="确认下单" width="440px">
      <div class="dlg-goods">
        <el-image v-if="goods?.coverImg" :src="goods.coverImg" fit="cover" class="dlg-cover" />
        <div v-else class="dlg-cover dlg-cover-empty">{{ goods?.category || '商品' }}</div>
        <div class="dlg-info">
          <div class="dlg-title">{{ goods?.title }}</div>
          <div class="dlg-price">￥{{ formatPrice(goods?.price) }}</div>
        </div>
      </div>

      <p class="dlg-label">给卖家留言（可选）</p>
      <el-input
        v-model="remark"
        type="textarea"
        :rows="3"
        maxlength="255"
        show-word-limit
        placeholder="例如：今天下午在图书馆门口交易可以吗"
      />

      <template #footer>
        <button class="btn-ghost" @click="dialogVisible = false">再想想</button>
        <button class="btn-buy" :disabled="submitting" @click="confirmBuy">
          {{ submitting ? '提交中…' : '确认下单' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { getGoodsDetail } from '../api/goods'
import { createOrder } from '../api/order'

const route = useRoute()
const router = useRouter()

const goods = ref(null)
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const remark = ref('')

const canBuy = computed(() => goods.value && goods.value.status === 1 && !goods.value.activeOrderId)

const hasOrigin = computed(
  () => goods.value && goods.value.originalPrice && Number(goods.value.originalPrice) > Number(goods.value.price)
)

const buyButtonText = computed(() => {
  if (!goods.value) return '立即购买'
  if (goods.value.status === 3) return '已售出'
  if (goods.value.status === 0) return '已下架'
  if (goods.value.activeOrderId) return '已有进行中的订单'
  return '立即购买'
})

const load = async () => {
  loading.value = true
  try {
    goods.value = await getGoodsDetail(route.params.id)
  } catch (e) {
    goods.value = null
  } finally {
    loading.value = false
  }
}

const onBuy = () => {
  if (!canBuy.value) return
  remark.value = ''
  dialogVisible.value = true
}

const confirmBuy = async () => {
  submitting.value = true
  try {
    await createOrder({ goodsId: goods.value.id, remark: remark.value })
    ElMessage.success('下单成功，请在 2 小时内完成付款')
    dialogVisible.value = false
    router.push('/orders')
  } catch (e) {
    // 提示由拦截器统一处理；下单失败多半是别人抢先锁定了，刷新一下状态
    load()
  } finally {
    submitting.value = false
  }
}

const conditionText = (v) => ({ 1: '全新', 2: '九成新', 3: '七成新', 4: '五成新及以下' }[v] || '未标注')
const statusText = (v) => ({ 0: '已下架', 1: '在售', 2: '交易中', 3: '已售出' }[v] || '未知')
const statusClass = (v) => ({ 0: 'pill-info', 1: 'pill-ok', 2: 'pill-warn', 3: 'pill-info' }[v] || 'pill-info')

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

/* ---------- 面包屑 ---------- */
.crumb {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px 0 14px;
  font-size: 12.5px;
  color: var(--muted);
  overflow: hidden;
}

.crumb-link {
  cursor: pointer;
  transition: color 0.2s var(--ease);
  white-space: nowrap;
}

.crumb-link:hover {
  color: var(--brand);
}

.crumb-sep {
  color: #cbd4e3;
}

.crumb-cur {
  color: var(--ink-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 主体两栏 ---------- */
.detail-grid {
  display: grid;
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 26px;
  align-items: start;
}

.gallery {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--line);
  background: #f4f6fa;
  box-shadow: var(--shadow-sm);
}

.cover {
  display: block;
  width: 100%;
  aspect-ratio: 1 / 1;
  background: #f4f6fa;
}

.cover :deep(.el-image__inner) {
  transition: transform 0.6s var(--ease);
}

.gallery:hover .cover :deep(.el-image__inner) {
  transform: scale(1.03);
}

.cover-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #b3bccd;
  font-size: 13px;
  background: linear-gradient(135deg, #f5f7fb, #eef2f9);
}

.cond-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 4px 11px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  color: #4b5cd6;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(6px);
  box-shadow: 0 2px 8px rgba(23, 43, 99, 0.12);
}

/* ---------- 右侧信息 ---------- */
.info {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px 26px 22px;
  box-shadow: var(--shadow-xs);
}

.title {
  margin: 0 0 14px;
  font-size: 22px;
  line-height: 1.4;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: var(--ink);
  word-break: break-all;
}

.price-row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line-soft);
}

.price {
  font-size: 32px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.6px;
  line-height: 1;
}

.price em {
  font-style: normal;
  font-size: 17px;
  font-weight: 600;
  margin-right: 1px;
}

.origin {
  font-size: 13px;
  color: var(--muted-2);
  text-decoration: line-through;
}

.meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2px 24px;
  margin: 16px 0 6px;
  padding: 0;
  list-style: none;
}

.meta li {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px dashed #f1f4f9;
}

.meta .k {
  flex: 0 0 62px;
  color: var(--muted);
}

.meta .v {
  color: var(--ink-2);
  word-break: break-all;
}

/* 卖家 */
.seller {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #f6f9ff, #f8f7ff);
  border: 1px solid #eef2fb;
}

.seller-avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b6ef6, #7c86f8);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}

.seller-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
}

.seller-badge {
  padding: 1px 6px;
  border-radius: 5px;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 10.5px;
  font-weight: 600;
}

.seller-campus {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted);
}

/* 按钮 */
.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-buy,
.btn-primary {
  flex: 1;
  height: 46px;
  border: none;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: filter 0.2s var(--ease), transform 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.btn-buy {
  background: linear-gradient(135deg, #fb7185, #ef4444);
  box-shadow: 0 12px 24px -12px rgba(239, 68, 68, 0.9);
}

.btn-primary {
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  box-shadow: var(--shadow-brand);
}

.btn-buy:hover:not(:disabled),
.btn-primary:hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
}

.btn-buy:disabled {
  background: #e8ecf3;
  color: #a3adbd;
  box-shadow: none;
  cursor: not-allowed;
}

.btn-ghost {
  height: 46px;
  padding: 0 22px;
  border: 1px solid #dbe4f7;
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--ink-2);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
  flex-shrink: 0;
}

.btn-ghost:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

.hint {
  margin: 12px 0 0;
  font-size: 12px;
  color: var(--muted-2);
}

/* ---------- 描述 / 提示 ---------- */
.block {
  margin-top: 20px;
  padding: 22px 26px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
}

.block-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 700;
}

.block-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 14px;
  margin-right: 9px;
  border-radius: 3px;
  background: linear-gradient(180deg, var(--brand), var(--brand-2));
  vertical-align: -1px;
}

.block-body {
  font-size: 14px;
  line-height: 1.9;
  color: var(--ink-2);
  white-space: pre-wrap;
  word-break: break-word;
}

.notice {
  margin-top: 16px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  background: #fffbeb;
  border: 1px solid #fdf0cd;
  font-size: 12.5px;
  line-height: 1.8;
  color: #92700e;
}

.notice strong {
  display: inline-block;
  margin-right: 8px;
  color: #b45309;
}

/* ---------- 下单弹窗 ---------- */
.dlg-goods {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 16px;
  border-radius: var(--radius-md);
  background: #f7f9fd;
}

.dlg-cover {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-sm);
  background: #e9eef7;
  flex-shrink: 0;
}

.dlg-cover-empty {
  display: grid;
  place-items: center;
  font-size: 11.5px;
  color: var(--muted);
}

.dlg-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 6px;
}

.dlg-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--price);
}

.dlg-label {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--muted);
}

/* ---------- 响应式 ---------- */
@media (max-width: 899px) {
  .detail-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 18px;
  }

  .cover {
    aspect-ratio: 16 / 10;
  }

  .info {
    padding: 20px 18px;
  }

  .title {
    font-size: 19px;
  }

  .price {
    font-size: 27px;
  }

  .meta {
    grid-template-columns: minmax(0, 1fr);
  }

  .actions {
    flex-direction: column;
  }

  .btn-ghost {
    width: 100%;
  }
}
</style>
