<template>
  <div class="page">
    <div class="page-head">
      <div>
        <el-button link :icon="ArrowLeft" style="margin-left: -8px" @click="router.push('/playlists')">返回歌单列表</el-button>
        <div class="page-title">{{ detail?.name || '歌单详情' }}</div>
        <div class="page-sub">{{ detail?.description || '这个歌单还没有简介' }} · 共 {{ detail?.songCount ?? 0 }} 首</div>
      </div>
      <div class="head-actions">
        <el-button :icon="Edit" @click="playlistDialog = true">编辑歌单</el-button>
        <el-button type="danger" plain :icon="Delete" @click="removePlaylist">删除歌单</el-button>
        <el-button type="primary" :icon="Plus" @click="openSongCreate">添加歌曲</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="head-actions mb-16">
        <el-input v-model="kw" placeholder="搜索本歌单内的歌曲" clearable style="width: 260px" :prefix-icon="Search" @keyup.enter="loadSongs" />
        <el-button type="primary" @click="loadSongs">搜索</el-button>
        <el-button v-if="kw" @click="kw = ''; loadSongs()">重置</el-button>
      </div>
      <SongTable
        :songs="detail?.songs || []"
        :loading="loading"
        :show-playlist="false"
        @edit="openSongEdit"
        @remove="removeSong"
        @play="openPlayer"
        @open="(song) => openMusicLink(song.url)"
      />
    </div>

    <SongForm
      v-model="songDialog"
      :song="editingSong"
      :playlists="playlists"
      :tags="tags"
      :default-playlist-id="id"
      @saved="load"
    />
    <PlaylistForm v-model="playlistDialog" :playlist="detail" @saved="load" />
    <AudioPlayer v-model="playerVisible" :song="playingSong" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Edit, Plus, Search } from '@element-plus/icons-vue'
import { playlistApi, songApi, tagApi } from '../api'
import SongTable from '../components/SongTable.vue'
import SongForm from '../components/SongForm.vue'
import PlaylistForm from '../components/PlaylistForm.vue'
import AudioPlayer from '../components/AudioPlayer.vue'
import { openMusicLink } from '../utils/songActions'

const route = useRoute()
const router = useRouter()
const id = computed(() => Number(route.params.id))

const detail = ref(null)
const playlists = ref([])
const tags = ref([])
const kw = ref('')
const loading = ref(false)
const songDialog = ref(false)
const editingSong = ref(null)
const playlistDialog = ref(false)
const playerVisible = ref(false)
const playingSong = ref(null)

async function load() {
  loading.value = true
  try {
    const [d, p, t] = await Promise.all([
      playlistApi.get(id.value),
      playlistApi.list(),
      tagApi.list()
    ])
    detail.value = d
    playlists.value = p
    tags.value = t
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

async function loadSongs() {
  loading.value = true
  try {
    const res = await songApi.list({ playlistId: id.value, kw: kw.value, size: 100 })
    if (detail.value) detail.value.songs = res.list
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

function openSongCreate() {
  editingSong.value = null
  songDialog.value = true
}

function openSongEdit(song) {
  editingSong.value = song
  songDialog.value = true
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
    load()
  } catch {
    // 统一错误提示
  }
}

async function removePlaylist() {
  try {
    await ElMessageBox.confirm(
      `确定删除歌单「${detail.value?.name}」吗？其中歌曲会保留并移至「未分类」。`,
      '删除确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await playlistApi.remove(id.value)
    ElMessage.success('歌单已删除')
    router.push('/playlists')
  } catch {
    // 统一错误提示
  }
}

watch(id, load)
onMounted(load)
</script>
