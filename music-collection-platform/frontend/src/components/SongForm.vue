<template>
  <el-dialog
    v-model="visible"
    :title="song ? '编辑歌曲' : '收藏新歌曲'"
    width="560px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="86px">
      <el-form-item label="歌名" prop="title">
        <el-input v-model="form.title" placeholder="请输入歌曲名称" maxlength="200" />
      </el-form-item>
      <el-form-item label="歌手" prop="artist">
        <el-input v-model="form.artist" placeholder="请输入歌手名称" maxlength="200" />
      </el-form-item>
      <el-form-item label="所属歌单" prop="playlistId">
        <el-select v-model="form.playlistId" placeholder="未分类" clearable style="width: 100%">
          <el-option
            v-for="item in playlists"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="音乐标签" prop="tagIds">
        <el-select v-model="form.tagIds" multiple filterable placeholder="可多选，也可留空" style="width: 100%">
          <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id">
            <span class="dot" :style="{ background: tag.color }" />
            <span style="margin-left: 6px">{{ tag.name }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="音乐链接" prop="url">
        <el-input v-model="form.url" placeholder="https://... 或 ./demo/audio/xxx.wav（内置演示音频）" />
      </el-form-item>
      <el-form-item label="封面地址" prop="cover">
        <el-input v-model="form.cover" placeholder="https://... 可选，留空显示默认封面" />
      </el-form-item>
      <el-form-item label="音乐备注" prop="notes">
        <el-input
          v-model="form.notes"
          type="textarea"
          :rows="3"
          maxlength="5000"
          show-word-limit
          placeholder="记录喜欢这首歌的理由、听到的场景……"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ song ? '保存修改' : '确认收藏' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { songApi } from '../api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  song: { type: Object, default: null },
  playlists: { type: Array, default: () => [] },
  tags: { type: Array, default: () => [] },
  defaultPlaylistId: { type: Number, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref(null)
const saving = ref(false)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const emptyForm = () => ({
  title: '', artist: '', url: '', cover: '', notes: '',
  playlistId: props.defaultPlaylistId ?? null, tagIds: []
})
const form = reactive(emptyForm())

const rules = {
  title: [{ required: true, message: '请输入歌名', trigger: 'blur' }]
}

watch(visible, (opened) => {
  if (!opened) return
  const source = props.song
  Object.assign(form, emptyForm(), source ? {
    title: source.title || '',
    artist: source.artist || '',
    url: source.url || '',
    cover: source.cover || '',
    notes: source.notes || '',
    playlistId: source.playlistId ?? null,
    tagIds: [...(source.tagIds || [])]
  } : {})
  // 弹窗重建后清除上一次的校验提示
  setTimeout(() => formRef.value?.clearValidate(), 0)
})

async function submit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    const payload = { ...form, tagIds: [...form.tagIds], playlistId: form.playlistId || null }
    if (props.song) await songApi.update(props.song.id, payload)
    else await songApi.create(payload)
    ElMessage.success(props.song ? '歌曲已更新' : '收藏成功')
    visible.value = false
    emit('saved')
  } catch {
    // 错误提示由请求拦截器统一展示
  } finally {
    saving.value = false
  }
}
</script>
