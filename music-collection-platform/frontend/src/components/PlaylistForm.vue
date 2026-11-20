<template>
  <el-dialog
    v-model="visible"
    :title="playlist ? '编辑歌单' : '创建歌单'"
    width="480px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="86px">
      <el-form-item label="歌单名称" prop="name">
        <el-input v-model="form.name" placeholder="给歌单起个名字" maxlength="100" />
      </el-form-item>
      <el-form-item label="歌单简介" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="选填，记录这个歌单的主题" />
      </el-form-item>
      <el-form-item label="封面地址" prop="cover">
        <el-input v-model="form.cover" placeholder="https://... 选填，留空使用默认封面" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ playlist ? '保存修改' : '创建歌单' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { playlistApi } from '../api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  playlist: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref(null)
const saving = ref(false)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const form = reactive({ name: '', description: '', cover: '' })
const rules = { name: [{ required: true, message: '请输入歌单名称', trigger: 'blur' }] }

watch(visible, (opened) => {
  if (!opened) return
  Object.assign(form, {
    name: props.playlist?.name || '',
    description: props.playlist?.description || '',
    cover: props.playlist?.cover || ''
  })
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
    if (props.playlist) await playlistApi.update(props.playlist.id, { ...form })
    else await playlistApi.create({ ...form })
    ElMessage.success(props.playlist ? '歌单已更新' : '歌单创建成功')
    visible.value = false
    emit('saved')
  } catch {
    // 统一由拦截器提示
  } finally {
    saving.value = false
  }
}
</script>
