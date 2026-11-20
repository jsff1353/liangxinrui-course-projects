<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-title">管理后台</div>
        <div class="page-sub">用户管理、平台数据统计与违规内容清理</div>
      </div>
      <el-tag type="danger" effect="light">ADMIN</el-tag>
    </div>

    <el-tabs v-model="activeTab" type="border-card" class="admin-tabs">
      <!-- 数据总览 -->
      <el-tab-pane label="数据总览" name="overview">
        <div class="stat-grid" style="grid-template-columns: repeat(4, 1fr)">
          <div class="stat-card"><div><div class="stat-label">注册用户</div><div class="stat-value">{{ overview.userCount }}</div></div></div>
          <div class="stat-card"><div><div class="stat-label">全部歌单</div><div class="stat-value">{{ overview.playlistCount }}</div></div></div>
          <div class="stat-card"><div><div class="stat-label">全部歌曲</div><div class="stat-value">{{ overview.songCount }}</div></div></div>
          <div class="stat-card"><div><div class="stat-label">全部标签</div><div class="stat-value">{{ overview.tagCount }}</div></div></div>
        </div>
        <div class="panel mt-16">
          <h3 style="font-size: 15px; margin-bottom: 12px">最近注册用户</h3>
          <el-table :data="overview.recentUsers" v-loading="loadingOverview">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="username" label="用户名" min-width="140" />
            <el-table-column prop="nickname" label="昵称" min-width="140" />
            <el-table-column label="角色" width="110">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" effect="light" size="small">{{ row.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="注册时间" width="180" />
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <div class="head-actions mb-16">
          <el-input v-model="userKw" placeholder="搜索用户名 / 昵称" clearable style="width: 240px" :prefix-icon="Search" @keyup.enter="onUserSearch" @clear="onUserSearch" />
          <el-button type="primary" @click="onUserSearch">搜索</el-button>
          <el-button @click="userKw = ''; onUserSearch()">重置</el-button>
        </div>
        <el-table :data="users" v-loading="loadingUsers">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" min-width="130" />
          <el-table-column prop="nickname" label="昵称" min-width="130" />
          <el-table-column label="角色" width="110">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" effect="light" size="small">{{ row.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="light" size="small">{{ row.status === 1 ? '正常' : '已禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="注册时间" width="170" />
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="toggleStatus(row)">{{ row.status === 1 ? '禁用' : '启用' }}</el-button>
              <el-button link type="primary" @click="toggleRole(row)">{{ row.role === 'admin' ? '取消管理员' : '设为管理员' }}</el-button>
              <el-button link type="danger" @click="removeUser(row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无用户数据" :image-size="80" /></template>
        </el-table>
        <el-pagination
          v-model:current-page="userPage" :total="userTotal" :page-size="10"
          layout="total, prev, pager, next" background
          style="margin-top: 16px; justify-content: flex-end" @current-change="loadUsers"
        />
      </el-tab-pane>

      <!-- 内容管理 -->
      <el-tab-pane label="数据 / 内容管理" name="content">
        <el-tabs v-model="contentTab">
          <el-tab-pane label="歌曲" name="songs">
            <div class="head-actions mb-16">
              <el-input v-model="songKw" placeholder="搜索歌名 / 歌手" clearable style="width: 240px" :prefix-icon="Search" @keyup.enter="onSongSearch" @clear="onSongSearch" />
              <el-button type="primary" @click="onSongSearch">搜索</el-button>
              <el-button @click="songKw = ''; onSongSearch()">重置</el-button>
            </div>
            <el-table :data="allSongs" v-loading="loadingSongs">
              <el-table-column prop="title" label="歌名" min-width="160" show-overflow-tooltip />
              <el-table-column prop="artist" label="歌手" min-width="120" show-overflow-tooltip />
              <el-table-column prop="owner" label="收藏人" width="120" show-overflow-tooltip />
              <el-table-column prop="playlistName" label="所属歌单" width="130" show-overflow-tooltip />
              <el-table-column prop="notes" label="备注" min-width="160" show-overflow-tooltip />
              <el-table-column prop="createdAt" label="收藏时间" width="170" />
              <el-table-column label="操作" width="110" fixed="right">
                <template #default="{ row }">
                  <el-button link type="danger" @click="removeAnySong(row)">违规删除</el-button>
                </template>
              </el-table-column>
              <template #empty><el-empty description="暂无歌曲数据" :image-size="80" /></template>
            </el-table>
            <el-pagination
              v-model:current-page="songPage" :total="songTotal" :page-size="10"
              layout="total, prev, pager, next" background
              style="margin-top: 16px; justify-content: flex-end" @current-change="loadAllSongs"
            />
          </el-tab-pane>

          <el-tab-pane label="歌单" name="playlists">
            <el-table :data="allPlaylists" v-loading="loadingPlaylists">
              <el-table-column prop="name" label="歌单名称" min-width="170" show-overflow-tooltip />
              <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip />
              <el-table-column prop="owner" label="创建人" width="130" show-overflow-tooltip />
              <el-table-column prop="songCount" label="歌曲数" width="100" />
              <el-table-column prop="createdAt" label="创建时间" width="170" />
              <el-table-column label="操作" width="110" fixed="right">
                <template #default="{ row }">
                  <el-button link type="danger" @click="removeAnyPlaylist(row)">违规删除</el-button>
                </template>
              </el-table-column>
              <template #empty><el-empty description="暂无歌单数据" :image-size="80" /></template>
            </el-table>
            <el-pagination
              v-model:current-page="playlistPage" :total="playlistTotal" :page-size="10"
              layout="total, prev, pager, next" background
              style="margin-top: 16px; justify-content: flex-end" @current-change="loadAllPlaylists"
            />
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '../api'

const activeTab = ref('overview')
const contentTab = ref('songs')

const overview = ref({ userCount: 0, playlistCount: 0, songCount: 0, tagCount: 0, recentUsers: [] })
const loadingOverview = ref(false)

const users = ref([])
const userTotal = ref(0)
const userPage = ref(1)
const userKw = ref('')
const loadingUsers = ref(false)

const allSongs = ref([])
const songTotal = ref(0)
const songPage = ref(1)
const songKw = ref('')
const loadingSongs = ref(false)

const allPlaylists = ref([])
const playlistTotal = ref(0)
const playlistPage = ref(1)
const loadingPlaylists = ref(false)

async function loadOverview() {
  loadingOverview.value = true
  try { overview.value = await adminApi.overview() } catch { /* 统一提示 */ } finally { loadingOverview.value = false }
}
async function loadUsers() {
  loadingUsers.value = true
  try {
    const res = await adminApi.users({ kw: userKw.value, page: userPage.value, size: 10 })
    users.value = res.list
    userTotal.value = res.total
  } catch { /* 统一提示 */ } finally { loadingUsers.value = false }
}
async function loadAllSongs() {
  loadingSongs.value = true
  try {
    const res = await adminApi.songs({ kw: songKw.value, page: songPage.value, size: 10 })
    allSongs.value = res.list
    songTotal.value = res.total
  } catch { /* 统一提示 */ } finally { loadingSongs.value = false }
}
async function loadAllPlaylists() {
  loadingPlaylists.value = true
  try {
    const res = await adminApi.playlists({ page: playlistPage.value, size: 10 })
    allPlaylists.value = res.list
    playlistTotal.value = res.total
  } catch { /* 统一提示 */ } finally { loadingPlaylists.value = false }
}

function onUserSearch() { userPage.value = 1; loadUsers() }
function onSongSearch() { songPage.value = 1; loadAllSongs() }

async function toggleStatus(row) {
  const status = row.status === 1 ? 0 : 1
  try {
    await adminApi.setStatus(row.id, status)
    ElMessage.success(status === 1 ? '账号已启用' : '账号已禁用')
    loadUsers()
    loadOverview()
  } catch { /* 统一提示 */ }
}

async function toggleRole(row) {
  const role = row.role === 'admin' ? 'user' : 'admin'
  try {
    await ElMessageBox.confirm(
      `确定将「${row.username}」${role === 'admin' ? '设为管理员' : '改为普通用户'}吗？`,
      '权限变更', { type: 'warning' }
    )
  } catch { return }
  try {
    await adminApi.setRole(row.id, role)
    ElMessage.success('用户角色已更新')
    loadUsers()
  } catch { /* 统一提示 */ }
}

async function removeUser(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除用户「${row.username}」吗？该用户的歌单、歌曲、标签将一并删除，且不可恢复。`,
      '危险操作', { type: 'warning', confirmButtonText: '确认删除', confirmButtonClass: 'el-button--danger' }
    )
  } catch { return }
  try {
    await adminApi.removeUser(row.id)
    ElMessage.success('用户已删除')
    loadUsers()
    loadOverview()
    loadAllSongs()
    loadAllPlaylists()
  } catch { /* 统一提示 */ }
}

async function removeAnySong(row) {
  try {
    await ElMessageBox.confirm(`确定以「违规内容」为由删除歌曲「${row.title}」吗？`, '违规删除', { type: 'warning' })
  } catch { return }
  try {
    await adminApi.removeSong(row.id)
    ElMessage.success('违规歌曲已删除')
    loadAllSongs()
    loadOverview()
  } catch { /* 统一提示 */ }
}

async function removeAnyPlaylist(row) {
  try {
    await ElMessageBox.confirm(`确定以「违规内容」为由删除歌单「${row.name}」吗？其中歌曲会保留。`, '违规删除', { type: 'warning' })
  } catch { return }
  try {
    await adminApi.removePlaylist(row.id)
    ElMessage.success('违规歌单已删除')
    loadAllPlaylists()
    loadOverview()
  } catch { /* 统一提示 */ }
}

onMounted(() => {
  loadOverview()
  loadUsers()
  loadAllSongs()
  loadAllPlaylists()
})
</script>

<style scoped>
.admin-tabs { border-radius: 14px; overflow: hidden; box-shadow: var(--mc-shadow); }
.admin-tabs :deep(.el-tabs__content) { padding: 18px; }
</style>
