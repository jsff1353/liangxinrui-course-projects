<template>
  <div class="page">
    <AppHeader active="my-goods" back />

    <main class="wrap publish">
      <div class="page-head">
        <div>
          <h1 class="page-title">{{ isEdit ? '编辑商品' : '发布闲置' }}</h1>
          <p class="page-sub">信息写得越具体，越容易被同学看中</p>
        </div>
        <button class="link-btn" @click="router.push('/my-goods')">我的发布 →</button>
      </div>

      <div class="layout" v-loading="loading">
        <!-- ============ 左：表单 ============ -->
        <section class="panel form-panel">
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
            <!-- 图片 -->
            <div class="sec">
              <div class="sec-title">商品图片<span class="sec-sub">选填，一张清晰的主图能提升约 3 倍点击</span></div>
              <el-upload
                :show-file-list="false"
                :before-upload="beforeUpload"
                :http-request="doUpload"
                accept="image/*"
              >
                <div v-if="form.coverImg" class="cover" v-loading="uploading">
                  <img :src="form.coverImg" alt="商品图片" />
                  <div class="cover-mask">点击更换</div>
                </div>
                <div v-else class="uploader" v-loading="uploading">
                  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6">
                    <path d="M12 16V5m0 0L7.5 9.5M12 5l4.5 4.5" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M4 15v3a2 2 0 002 2h12a2 2 0 002-2v-3" stroke-linecap="round" />
                  </svg>
                  <span class="up-text">上传主图</span>
                  <span class="up-hint">jpg / png / webp</span>
                </div>
              </el-upload>
              <p class="tip">支持 jpg / png / webp / gif，单张不超过 5MB；不上传也能发布</p>
            </div>

            <!-- 基本信息 -->
            <div class="sec">
              <div class="sec-title">基本信息</div>

              <el-form-item label="商品标题" prop="title">
                <el-input
                  v-model="form.title"
                  maxlength="50"
                  show-word-limit
                  placeholder="例如：高等数学 第七版 上册（少量笔记）"
                />
              </el-form-item>

              <div class="grid2">
                <el-form-item label="分类" prop="category">
                  <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                    <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
                  </el-select>
                </el-form-item>

                <el-form-item label="成色" prop="itemCondition">
                  <el-select v-model="form.itemCondition" placeholder="请选择成色" style="width: 100%">
                    <el-option v-for="c in conditions" :key="c.value" :label="c.label" :value="c.value" />
                  </el-select>
                </el-form-item>
              </div>
            </div>

            <!-- 价格 -->
            <div class="sec">
              <div class="sec-title">价格</div>
              <div class="grid2">
                <el-form-item label="售价" prop="price">
                  <el-input-number v-model="form.price" :min="0.01" :max="999999" :precision="2" :step="1" style="width: 100%" />
                </el-form-item>

                <el-form-item label="原价（选填）">
                  <el-input-number
                    v-model="form.originalPrice"
                    :min="0"
                    :max="999999"
                    :precision="2"
                    :step="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </div>
              <p class="tip">填了原价会在列表里显示划线价；原价不能低于售价</p>
            </div>

            <!-- 交易信息 -->
            <div class="sec">
              <div class="sec-title">交易信息</div>
              <div class="grid2">
                <el-form-item label="交易地点">
                  <el-input v-model="form.tradePlace" maxlength="100" placeholder="例如：科教城校区图书馆门口" />
                </el-form-item>

                <el-form-item label="联系方式">
                  <el-input v-model="form.contact" maxlength="50" placeholder="例如：微信 abc123" />
                </el-form-item>
              </div>
            </div>

            <!-- 描述 -->
            <div class="sec last">
              <div class="sec-title">商品描述<span class="sec-sub">选填，最多 2000 字</span></div>
              <el-form-item prop="description">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="6"
                  maxlength="2000"
                  show-word-limit
                  placeholder="写清楚购买时间、使用情况、有无磕碰、附赠物品、能否小刀，越具体越好卖"
                />
              </el-form-item>
              <div class="desc-bar">
                <button class="ai-desc" :disabled="aiLoading" @click="onAiDesc">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.9">
                    <path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9L12 3z" stroke-linejoin="round" />
                  </svg>
                  {{ aiLoading ? '生成中…' : 'AI 帮我写描述' }}
                </button>
                <span class="tip">根据标题 / 分类 / 成色生成，生成后可以自己改</span>
              </div>
            </div>

            <div class="actions">
              <button class="btn-primary" :disabled="submitting" @click="submit">
                {{ submitting ? '提交中…' : isEdit ? '保存修改' : '立即发布' }}
              </button>
              <button class="btn-ghost" @click="router.back()">取消</button>
            </div>
          </el-form>
        </section>

        <!-- ============ 右：实时预览 + 提示 ============ -->
        <aside class="side">
          <div class="panel preview">
            <div class="preview-label">效果预览</div>
            <div class="pv-cover">
              <img v-if="form.coverImg" :src="form.coverImg" alt="" />
              <div v-else class="pv-empty">{{ form.category || '暂无图片' }}</div>
            </div>
            <div class="pv-body">
              <div class="pv-title">{{ form.title || '商品标题会显示在这里' }}</div>
              <div class="pv-price">
                <em>￥</em>{{ formatPrice(form.price) }}
                <span v-if="form.originalPrice > 0" class="pv-origin">￥{{ formatPrice(form.originalPrice) }}</span>
              </div>
              <div class="pv-tags">
                <span class="pill pill-primary">{{ conditionText(form.itemCondition) }}</span>
                <span class="pill pill-info">{{ form.category || '未分类' }}</span>
              </div>
            </div>
          </div>

          <div class="panel tips">
            <div class="tips-title">发布小贴士</div>
            <ul>
              <li>标题带上「版本 + 成色 + 关键配件」，搜索更容易命中</li>
              <li>价格可以比心理价略高一点，留出小刀空间</li>
              <li>写清交易地点，减少来回沟通成本</li>
              <li>发布后可在「我的发布」随时编辑或下架</li>
            </ul>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { getGoodsDetail, publishGoods, updateGoods } from '../api/goods'
import { aiGenerateDesc } from '../api/ai'
import { uploadImage } from '../api/file'

const route = useRoute()
const router = useRouter()

const categories = ['教材', '数码', '生活用品', '运动', '其他']
const conditions = [
  { value: 1, label: '全新' },
  { value: 2, label: '九成新' },
  { value: 3, label: '七成新' },
  { value: 4, label: '五成新及以下' }
]

const formRef = ref(null)
const loading = ref(false)
const uploading = ref(false)
const submitting = ref(false)
const aiLoading = ref(false)
const isEdit = ref(false)

const form = reactive({
  id: null,
  title: '',
  description: '',
  price: null,
  originalPrice: null,
  category: '',
  itemCondition: 2,
  tradePlace: '',
  contact: '',
  coverImg: ''
})

const rules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { max: 50, message: '标题最多 50 个字', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  itemCondition: [{ required: true, message: '请选择成色', trigger: 'change' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  description: [{ max: 2000, message: '描述最多 2000 个字', trigger: 'blur' }]
}

const conditionText = (v) => ({ 1: '全新', 2: '九成新', 3: '七成新', 4: '五成新及以下' }[v] || '成色未选')

const formatPrice = (v) => {
  const n = Number(v || 0)
  if (!Number.isFinite(n) || n <= 0) return '0'
  return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

// 上传前先在前端挡一道，省得大文件白传到后端再被拒
const beforeUpload = (file) => {
  const allow = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  if (!allow.includes(file.type)) {
    ElMessage.error('只支持 jpg / png / webp / gif 图片')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片不能超过 5MB')
    return false
  }
  return true
}

const doUpload = async ({ file }) => {
  uploading.value = true
  try {
    form.coverImg = await uploadImage(file)
    ElMessage.success('图片上传成功')
  } catch (e) {
    // 错误提示由 axios 拦截器统一处理
  } finally {
    uploading.value = false
  }
}

const loadDetail = async (id) => {
  loading.value = true
  try {
    const data = await getGoodsDetail(id)
    Object.assign(form, {
      id: data.id,
      title: data.title,
      description: data.description,
      price: Number(data.price),
      originalPrice: data.originalPrice == null ? null : Number(data.originalPrice),
      category: data.category,
      itemCondition: data.itemCondition || 2,
      tradePlace: data.tradePlace,
      contact: data.contact,
      coverImg: data.coverImg
    })
  } catch (e) {
    router.replace('/my-goods')
  } finally {
    loading.value = false
  }
}

// AI 智能发布助手：把标题/分类/成色发给后端，由大模型生成一段描述（没配 Key 时为本地模板）
const onAiDesc = async () => {
  if (!form.title) {
    ElMessage.warning('请先填写商品标题')
    return
  }
  aiLoading.value = true
  try {
    const text = await aiGenerateDesc(form.title, form.category, form.itemCondition)
    form.description = text
    ElMessage.success('描述已生成，可以自己再改改')
  } catch (e) {
    // 错误提示由 axios 拦截器统一处理
  } finally {
    aiLoading.value = false
  }
}

const submit = async () => {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  if (form.originalPrice != null && form.originalPrice < form.price) {
    ElMessage.warning('原价不能低于售价')
    return
  }

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateGoods(form.id, { ...form })
      ElMessage.success('修改成功')
    } else {
      await publishGoods({ ...form })
      ElMessage.success('发布成功')
    }
    router.push('/my-goods')
  } catch (e) {
    // 错误提示由 axios 拦截器统一处理
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    loadDetail(id)
  }
})
</script>

<style scoped>
.publish {
  padding-top: 4px;
}

.page-head {
  align-items: flex-end;
}

.link-btn {
  border: none;
  background: transparent;
  color: var(--brand);
  font-size: 13px;
  cursor: pointer;
  padding: 6px 2px;
  transition: opacity 0.2s var(--ease);
}

.link-btn:hover {
  opacity: 0.75;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 296px;
  gap: 18px;
  align-items: start;
}

/* ---------- 表单面板 ---------- */
.form-panel {
  padding: 8px 26px 24px;
}

.sec {
  padding: 18px 0;
  border-bottom: 1px dashed var(--line);
}

.sec:last-of-type {
  border-bottom: none;
}

.sec-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
}

.sec-sub {
  margin-left: 8px;
  font-size: 12px;
  font-weight: 400;
  color: var(--muted-2);
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}

.form-panel :deep(.el-form-item) {
  margin-bottom: 14px;
}

.form-panel :deep(.el-form-item__label) {
  padding-bottom: 5px;
  font-size: 12.5px;
  color: var(--ink-2);
  font-weight: 500;
}

/* ---------- 上传 ---------- */
.uploader {
  width: 132px;
  height: 132px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1.5px dashed #d7e0f0;
  border-radius: var(--radius-md);
  background: #fbfcff;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.24s var(--ease);
}

.uploader:hover {
  border-color: var(--brand);
  background: #f6f9ff;
  color: var(--brand);
  transform: translateY(-1px);
}

.up-text {
  font-size: 12.5px;
  font-weight: 600;
}

.up-hint {
  font-size: 11px;
  color: var(--muted-2);
}

.cover {
  position: relative;
  width: 132px;
  height: 132px;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-mask {
  position: absolute;
  inset: auto 0 0 0;
  height: 28px;
  line-height: 28px;
  text-align: center;
  font-size: 11.5px;
  color: #fff;
  background: rgba(16, 24, 40, 0.52);
  backdrop-filter: blur(4px);
}

.tip {
  margin: 8px 0 0;
  font-size: 11.5px;
  color: var(--muted-2);
  line-height: 1.6;
}

/* ---------- AI 描述 ---------- */
.desc-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.desc-bar .tip {
  margin: 0;
}

.ai-desc {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 14px;
  border: 1px solid #ddd8fe;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #f5f2ff, #eef4ff);
  color: #6d5cf6;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.ai-desc:hover:not(:disabled) {
  background: linear-gradient(135deg, #ece6ff, #e6eeff);
  transform: translateY(-1px);
}

.ai-desc:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ---------- 操作按钮 ---------- */
.actions {
  display: flex;
  gap: 10px;
  padding-top: 22px;
}

.btn-primary {
  height: 42px;
  padding: 0 26px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-brand);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-ghost {
  height: 42px;
  padding: 0 22px;
  border: 1px solid #dbe4f7;
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--ink-2);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s var(--ease);
}

.btn-ghost:hover {
  border-color: #b9caf7;
  color: var(--brand);
  background: #f8faff;
}

/* ---------- 右侧 ---------- */
.side {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: 84px;
}

.preview {
  overflow: hidden;
}

.preview-label {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  border-bottom: 1px solid var(--line-soft);
}

.pv-cover {
  aspect-ratio: 4 / 3;
  background: #f4f6fa;
}

.pv-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pv-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 12px;
  color: #b3bccd;
  background: linear-gradient(135deg, #f5f7fb, #eef2f9);
}

.pv-body {
  padding: 12px 16px 16px;
}

.pv-title {
  font-size: 13.5px;
  font-weight: 600;
  line-height: 1.5;
  color: var(--ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pv-price {
  margin: 8px 0 10px;
  font-size: 20px;
  font-weight: 700;
  color: var(--price);
  letter-spacing: -0.3px;
}

.pv-price em {
  font-style: normal;
  font-size: 12px;
  font-weight: 600;
}

.pv-origin {
  margin-left: 7px;
  font-size: 12px;
  font-weight: 400;
  color: var(--muted-2);
  text-decoration: line-through;
}

.pv-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tips {
  padding: 16px;
}

.tips-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.tips ul {
  margin: 0;
  padding-left: 16px;
}

.tips li {
  font-size: 12px;
  line-height: 1.85;
  color: var(--muted);
}

@media (max-width: 1023px) {
  .layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .side {
    position: static;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 767px) {
  .form-panel {
    padding: 4px 16px 20px;
  }

  .grid2 {
    grid-template-columns: 1fr;
  }

  .side {
    grid-template-columns: 1fr;
  }

  .actions {
    position: sticky;
    bottom: 0;
    padding: 14px 0;
    background: linear-gradient(180deg, rgba(251, 252, 254, 0), var(--page-bg) 30%);
  }
}
</style>
