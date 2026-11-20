<template>
  <div class="page">
    <div class="banner">
      <div>
        <div class="banner-title">你好，{{ userStore.info?.nickname || '音乐爱好者' }} 👋</div>
        <p class="banner-sub">今天是 {{ today }}，来整理一下你的音乐收藏吧</p>
        <div class="banner-actions">
          <el-button type="primary" round @click="router.push('/playlists')">管理歌单</el-button>
          <el-button round class="ghost-btn" @click="router.push('/songs')">查看全部歌曲</el-button>
        </div>
      </div>
      <div class="banner-note">♪</div>
    </div>

    <div class="stat-grid mt-16">
      <div class="stat-card">
        <div><div class="stat-label">我的歌单</div><div class="stat-value">{{ stats.playlistCount }}</div></div>
        <div class="stat-icon" style="background: linear-gradient(135deg,#8b7cf8,#b8a5fb)"><el-icon :size="22"><List /></el-icon></div>
      </div>
      <div class="stat-card">
        <div><div class="stat-label">收藏歌曲</div><div class="stat-value">{{ stats.songCount }}</div></div>
        <div class="stat-icon" style="background: linear-gradient(135deg,#5aa9f8,#7fd7f0)"><el-icon :size="22"><Headset /></el-icon></div>
      </div>
      <div class="stat-card">
        <div><div class="stat-label">自定义标签</div><div class="stat-value">{{ stats.tagCount }}</div></div>
        <div class="stat-icon" style="background: linear-gradient(135deg,#42c6b4,#8ce0b0)"><el-icon :size="22"><PriceTag /></el-icon></div>
      </div>
    </div>

    <div class="panel mt-16">
      <div class="panel-head">
        <h3>最近收藏</h3>
        <el-button link type="primary" @click="router.push('/songs')">查看全部 →</el-button>
      </div>

      <div v-if="stats.recentSongs.length" v-loading="loading" class="recent-list">
        <div v-for="song in stats.recentSongs" :key="song.id" class="recent-item">
          <SongCover :src="song.cover" :seed="song.id" :size="44" />
          <div class="recent-meta">
            <div class="recent-name ellipsis">{{ song.title }} <span class="muted">- {{ song.artist || '未知歌手' }}</span></div>
            <div class="recent-tags">
              <span v-for="tag in song.tags" :key="tag.id" class="tag-chip" :style="{ background: tag.color + '1f', color: tag.color }">
                <span class="dot" :style="{ background: tag.color }" />{{ tag.name }}
              </span>
              <span v-if="!song.tags.length" class="muted" style="font-size:12px">未打标签</span>
            </div>
          </div>
          <div class="muted recent-time">{{ song.createdAt }}</div>
        </div>
      </div>
      <el-empty v-else description="还没有收藏歌曲，去「全部歌曲」添加第一首吧" :image-size="90" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '../api'
import { useUserStore } from '../store/user'
import SongCover from '../components/SongCover.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const stats = ref({ playlistCount: 0, songCount: 0, tagCount: 0, recentSongs: [] })
const today = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
)

async function load() {
  loading.value = true
  try {
    stats.value = await userApi.stats()
  } catch {
    // 统一错误提示
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.banner {
  border-radius: 16px; padding: 30px 34px; color: #fff; position: relative; overflow: hidden;
  background: linear-gradient(115deg, #6f5ce8 0%, #8978f6 55%, #b29bf9 100%);
  box-shadow: 0 10px 28px rgba(111, 92, 232, .22);
}
.banner-title { font-size: 24px; font-weight: 700; }
.banner-sub { margin-top: 8px; font-size: 13px; opacity: .85; }
.banner-actions { margin-top: 22px; display: flex; gap: 12px; }
.ghost-btn { background: rgba(255,255,255,.16); border-color: rgba(255,255,255,.5); color: #fff; }
.banner-note { position: absolute; right: 44px; top: -54px; font-size: 200px; opacity: .16; }
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.panel-head h3 { font-size: 16px; font-weight: 700; }
.recent-item { display: flex; align-items: center; gap: 13px; padding: 12px 4px; border-bottom: 1px solid #f3f4fa; }
.recent-item:last-child { border-bottom: none; }
.recent-meta { flex: 1; min-width: 0; }
.recent-name { font-size: 13px; font-weight: 600; }
.recent-tags { margin-top: 5px; font-size: 12px; }
.recent-time { font-size: 12px; }
</style>
