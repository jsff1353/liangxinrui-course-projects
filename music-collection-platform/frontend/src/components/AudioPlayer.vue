<template>
  <el-dialog v-model="visible" :title="`试听 · ${song?.title || ''}`" width="460px" destroy-on-close>
    <div v-if="song" class="player">
      <div class="player-top">
        <SongCover :src="song.cover" :seed="song.id" :size="62" />
        <div>
          <div class="player-name">{{ song.title }}</div>
          <div class="muted" style="font-size: 12px; margin-top: 6px">{{ song.artist || '未知歌手' }}</div>
        </div>
      </div>
      <audio v-if="song.url" :src="song.url" controls preload="metadata" style="width: 100%; margin-top: 18px" />
      <el-alert
        v-if="isDemo"
        type="success"
        :closable="false"
        show-icon
        style="margin-top: 14px"
        title="随包内置的原创演示音频，离线也能播放。可拖动进度条、调节音量。"
      />
      <el-alert
        v-else-if="!isDirectAudio(song.url)"
        type="info"
        :closable="false"
        show-icon
        style="margin-top: 14px"
        title="若上方无法播放，说明该链接不是音频直链，可点击「打开原链接」访问来源页面。"
      />
      <div style="text-align: right; margin-top: 16px">
        <el-button @click="openMusicLink(song.url)">{{ isDemo ? '内置音频说明' : '打开原链接' }}</el-button>
        <el-button type="primary" @click="visible = false">关闭</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import SongCover from './SongCover.vue'
import { isDemoAudio, isDirectAudio, openMusicLink } from '../utils/songActions'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  song: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue'])
const isDemo = computed(() => isDemoAudio(props.song?.url))
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
.player-top { display: flex; align-items: center; gap: 14px; }
.player-name { font-size: 16px; font-weight: 700; }
</style>
