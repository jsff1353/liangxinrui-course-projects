<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-title">全部歌曲</div>
        <div class="page-sub">共收录 {{ total }} 首，支持按歌名、歌手、备注与标签搜索</div>
      </div>
      <div class="head-actions">
        <el-button type="primary" :icon="Plus" @click="openCreate">新增歌曲</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="head-actions mb-16">
        <el-input
          v-model="kw"
          placeholder="搜索歌名 / 歌手 / 标签 / 备注"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
        <el-select v-model="tagId" placeholder="按标签筛选" clearable style="width: 150px" @change="onSearch">
          <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
        <el-select v-model="playlistId" placeholder="按歌单筛选" clearable style="width: 160px" @change="onSearch">
          <el-option v-for="item in playlists" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="onSearch">搜索</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <SongTable
        :songs="songs"
        :loading="loading"
        @edit="openEdit"
        @remove="removeSong"
        @play="openPlayer"
        @open="(song) => openMusicLink(song.url)"
      />

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        style="margin-top: 18px; justify-content: flex-end"
        @current-change="loadData"
        @size-change="onSizeChange"
      />
    </div>

    <SongForm v-model="dialogVisible" :song="editingSong" :playlists="playlists" :tags="tags" @saved="afterSave" />
    <AudioPlayer v-model="playerVisible" :song="playingSong" />
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { playlistApi, songApi, tagApi } from '../api'
import SongTable from '../components/SongTable.vue'
import SongForm from '../components/SongForm.vue'
import AudioPlayer from '../components/AudioPlayer.vue'
import { openMusicLink } from '../utils/songActions'

const route = useRoute()
const songs = ref([])
const playlists = ref([])
const tags = ref([])
const kw = ref('')
const tagId = ref(route.query.tagId ? Number(route.query.tagId) : null)
const playlistId = ref(route.query.playlistId ? Number(route.query.playlistId) : null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const editingSong = ref(null)
const playerVisible = ref(false)
const playingSong = ref(null)

async function loadData() {
  loading.value = true
  try {
    const res = await songApi.list({
      kw: kw.value,
      tagId: tagId.value,
      playlistId: playlistId.value,
      page: page.value,
      size: size.value
    })
    songs.value = res.list
    total.value = res.total
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    const [p, t] = await Promise.all([playlistApi.list(), tagApi.list()])
    playlists.value = p
    tags.value = t
  } catch {
    // 统一错误提示
  }
}

function onSearch() {
  page.value = 1
  loadData()
}

function onSizeChange() {
  page.value = 1
  loadData()
}

function reset() {
  kw.value = ''
  tagId.value = null
  playlistId.value = null
  onSearch()
}

function afterSave() {
  loadData()
  loadOptions()
}

function openCreate() {
  editingSong.value = null
  dialogVisible.value = true
}

function openEdit(song) {
  editingSong.value = song
  dialogVisible.value = true
}

function openPlayer(song) {
  playingSong.value = song
  playerVisible.value = true
}

async function removeSong(song) {
  try {
    await ElMessageBox.confirm(`确定删除歌曲「${song.title}」吗？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await songApi.remove(song.id)
    ElMessage.success('歌曲已删除')
    afterSave()
  } catch {
    // 统一错误提示
  }
}

// 从标签页点击「查看歌曲」跳转时同步筛选条件
watch(() => route.query.tagId, (value) => {
  tagId.value = value ? Number(value) : null
  onSearch()
})
watch(() => route.query.playlistId, (value) => {
  playlistId.value = value ? Number(value) : null
  onSearch()
})

onMounted(() => {
  loadOptions()
  loadData()
})
</script>
