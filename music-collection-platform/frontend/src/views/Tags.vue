<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-title">标签管理</div>
        <div class="page-sub">自定义音乐标签，给歌曲打标签后可快速筛选，共 {{ list.length }} 个标签</div>
      </div>
      <div class="head-actions">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建标签</el-button>
      </div>
    </div>

    <div v-loading="loading">
      <div v-if="list.length" class="tag-grid">
        <div v-for="tag in list" :key="tag.id" class="tag-card">
          <div class="tag-head">
            <span class="tag-badge" :style="{ background: tag.color + '22', color: tag.color }">
              <span class="dot" :style="{ background: tag.color }" />{{ tag.name }}
            </span>
            <span class="muted" style="font-size: 12px">{{ tag.songCount }} 首歌曲</span>
          </div>
          <div class="muted" style="font-size: 12px; margin-top: 16px">创建于 {{ (tag.createdAt || '').slice(0, 10) }}</div>
          <div class="tag-actions">
            <el-button link type="primary" size="small" @click="viewSongs(tag)">查看歌曲</el-button>
            <el-button link type="primary" size="small" @click="openEdit(tag)">编辑</el-button>
            <el-button link type="danger" size="small" @click="removeTag(tag)">删除</el-button>
          </div>
        </div>
      </div>
      <div v-else class="panel">
        <el-empty description="还没有标签，新建「轻音乐」「学习」「单曲循环」试试吧" :image-size="110">
          <el-button type="primary" @click="openCreate">新建标签</el-button>
        </el-empty>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑标签' : '新建标签'" width="420px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="86px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：轻音乐" maxlength="50" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <div class="color-row">
            <span
              v-for="color in presetColors"
              :key="color"
              class="color-item"
              :class="{ active: form.color === color }"
              :style="{ background: color }"
              @click="form.color = color"
            />
            <el-color-picker v-model="form.color" size="small" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { tagApi } from '../api'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const saving = ref(false)
const formRef = ref(null)
const form = reactive({ name: '', color: '#7C6BF5' })
const presetColors = ['#7C6BF5', '#4C9AFF', '#36CFC9', '#FF85C0', '#FFA940', '#73D13D', '#F56C6C', '#909399']
const rules = { name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }] }

async function load() {
  loading.value = true
  try {
    list.value = await tagApi.list()
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', color: '#7C6BF5' })
  dialogVisible.value = true
  setTimeout(() => formRef.value?.clearValidate(), 0)
}

function openEdit(tag) {
  editing.value = tag
  Object.assign(form, { name: tag.name, color: tag.color })
  dialogVisible.value = true
  setTimeout(() => formRef.value?.clearValidate(), 0)
}

function viewSongs(tag) {
  router.push({ path: '/songs', query: { tagId: tag.id } })
}

async function submit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  const payload = { name: form.name, color: form.color || '#7C6BF5' }
  try {
    if (editing.value) await tagApi.update(editing.value.id, payload)
    else await tagApi.create(payload)
    ElMessage.success(editing.value ? '标签已更新' : '标签创建成功')
    dialogVisible.value = false
    load()
  } catch {
    // 统一错误提示
  } finally {
    saving.value = false
  }
}

async function removeTag(tag) {
  try {
    await ElMessageBox.confirm(
      `确定删除标签「${tag.name}」吗？已打该标签的歌曲会自动移除此标签。`,
      '删除确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await tagApi.remove(tag.id)
    ElMessage.success('标签已删除')
    load()
  } catch {
    // 统一错误提示
  }
}

onMounted(load)
</script>

<style scoped>
.tag-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(238px, 1fr)); gap: 16px; }
.tag-card {
  background: #fff; border: 1px solid var(--mc-border); border-radius: 14px;
  box-shadow: var(--mc-shadow); padding: 18px;
}
.tag-head { display: flex; align-items: center; justify-content: space-between; }
.tag-badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 20px; padding: 5px 12px; font-size: 13px; font-weight: 600; }
.tag-actions { margin-top: 14px; border-top: 1px solid #f2f3fa; padding-top: 8px; text-align: right; }
.color-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.color-item { width: 22px; height: 22px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: transform .15s; }
.color-item:hover { transform: scale(1.12); }
.color-item.active { border-color: #22263a; box-shadow: 0 0 0 2px #fff inset; }
</style>
