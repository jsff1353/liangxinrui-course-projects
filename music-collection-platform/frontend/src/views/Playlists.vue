<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-title">我的歌单</div>
        <div class="page-sub">按主题整理收藏，共 {{ list.length }} 个歌单</div>
      </div>
      <div class="head-actions">
        <el-button type="primary" :icon="Plus" @click="openCreate">新建歌单</el-button>
      </div>
    </div>

    <div v-loading="loading">
      <div v-if="list.length" class="playlist-grid">
        <div v-for="item in list" :key="item.id" class="playlist-card" @click="router.push(`/playlists/${item.id}`)">
          <div class="playlist-cover">
            <img v-if="item.cover && !coverFailed[item.id]" :src="item.cover" alt="" @error="coverFailed[item.id] = true" />
            <span v-else>♪</span>
          </div>
          <div class="playlist-body">
            <div class="playlist-name ellipsis">{{ item.name }}</div>
            <div class="playlist-desc ellipsis">{{ item.description || '这个歌单还没有简介' }}</div>
            <div class="playlist-foot">
              <span class="muted" style="font-size: 12px">{{ item.songCount }} 首 · {{ (item.createdAt || '').slice(0, 10) }}</span>
              <span @click.stop>
                <el-button link type="primary" size="small" @click="openEdit(item)">编辑</el-button>
                <el-button link type="danger" size="small" @click="removeItem(item)">删除</el-button>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="panel">
        <el-empty description="还没有歌单，创建第一个专属歌单吧" :image-size="110">
          <el-button type="primary" @click="openCreate">新建歌单</el-button>
        </el-empty>
      </div>
    </div>

    <PlaylistForm v-model="dialogVisible" :playlist="editing" @saved="load" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { playlistApi } from '../api'
import PlaylistForm from '../components/PlaylistForm.vue'

const router = useRouter()
const route = useRoute()
const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref(null)
const coverFailed = reactive({})

async function load() {
  loading.value = true
  try {
    list.value = await playlistApi.list()
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  dialogVisible.value = true
}

function openEdit(item) {
  editing.value = item
  dialogVisible.value = true
}

async function removeItem(item) {
  try {
    await ElMessageBox.confirm(
      `确定删除歌单「${item.name}」吗？其中的歌曲不会丢失，会移至「未分类」。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await playlistApi.remove(item.id)
    ElMessage.success('歌单已删除')
    load()
  } catch {
    // 统一错误提示
  }
}

onMounted(() => {
  load()
  if (route.query.create === '1') openCreate() // 支持首页快捷入口
})
</script>

<style scoped>
.playlist-name { font-size: 15px; font-weight: 700; }
.playlist-desc { font-size: 12px; color: var(--mc-muted); margin-top: 6px; min-height: 18px; }
</style>
