<template>
  <div class="cover-box" :style="{ width: size + 'px', height: size + 'px', background: bg }">
    <img v-if="src && !failed" :src="src" alt="cover" @error="failed = true" />
    <span v-else>♪</span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  size: { type: Number, default: 44 },
  seed: { type: [Number, String], default: 0 }
})

const failed = ref(false)
watch(() => props.src, () => { failed.value = false })

const gradients = [
  'linear-gradient(135deg, #8b7cf8, #b8a5fb)',
  'linear-gradient(135deg, #5aa9f8, #7fd7f0)',
  'linear-gradient(135deg, #42c6b4, #8ce0b0)',
  'linear-gradient(135deg, #ff91b8, #ffc09e)',
  'linear-gradient(135deg, #ffa94d, #ffd479)',
  'linear-gradient(135deg, #7f8cf7, #a6b1ff)'
]

function hashCode(value) {
  let hash = 0
  for (const ch of String(value)) hash = (hash * 31 + ch.charCodeAt(0)) | 0
  return Math.abs(hash)
}

const bg = computed(() => gradients[hashCode(props.seed || props.src || 'm') % gradients.length])
</script>
