<template>
  <el-table :data="songs" v-loading="loading" style="width: 100%" row-key="id">
    <el-table-column label="歌曲" min-width="230">
      <template #default="{ row }">
        <div class="song-cell">
          <SongCover :src="row.cover" :seed="row.id" :size="42" />
          <div class="song-meta">
            <div class="ellipsis song-title">{{ row.title }}</div>
            <div class="ellipsis song-sub">{{ row.artist || '未知歌手' }}</div>
          </div>
        </div>
      </template>
    </el-table-column>

    <el-table-column v-if="showPlaylist" prop="playlistName" label="所属歌单" width="140" show-overflow-tooltip />

    <el-table-column label="标签" min-width="150">
      <template #default="{ row }">
        <span v-for="tag in row.tags" :key="tag.id" class="tag-chip" :style="{ background: tag.color + '1f', color: tag.color }">
          <span class="dot" :style="{ background: tag.color }" />{{ tag.name }}
        </span>
        <span v-if="!row.tags || !row.tags.length" class="muted">—</span>
      </template>
    </el-table-column>

    <el-table-column prop="notes" label="音乐备注" min-width="170" show-overflow-tooltip>
      <template #default="{ row }"><span :class="{ muted: !row.notes }">{{ row.notes || '暂无备注' }}</span></template>
    </el-table-column>

    <el-table-column v-if="showOwner" prop="owner" label="收藏人" width="120" show-overflow-tooltip />

    <el-table-column prop="createdAt" label="收藏时间" width="155" />

    <el-table-column label="操作" width="188" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" :disabled="!row.url" @click="emit('play', row)">试听</el-button>
        <el-button link type="primary" :disabled="!row.url" @click="emit('open', row)">链接</el-button>
        <el-button link type="primary" @click="emit('edit', row)">编辑</el-button>
        <el-button link type="danger" @click="emit('remove', row)">删除</el-button>
      </template>
    </el-table-column>

    <template #empty>
      <el-empty description="还没有收藏歌曲，点击「新增歌曲」开始吧" :image-size="90" />
    </template>
  </el-table>
</template>

<script setup>
import SongCover from './SongCover.vue'

defineProps({
  songs: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  showPlaylist: { type: Boolean, default: true },
  showOwner: { type: Boolean, default: false }
})
const emit = defineEmits(['edit', 'remove', 'play', 'open'])
</script>

<style scoped>
.song-cell { display: flex; align-items: center; gap: 11px; }
.song-meta { min-width: 0; }
.song-title { font-size: 13px; font-weight: 600; }
.song-sub { font-size: 12px; color: var(--mc-muted); margin-top: 3px; }
</style>
