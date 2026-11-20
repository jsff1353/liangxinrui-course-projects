import { ElMessage } from 'element-plus'

/** 判断是否为随包内置的演示音频（相对路径，由前端静态服务同源托管）。 */
export function isDemoAudio(url) {
  return /(^|\/)demo\/audio\//i.test(url || '')
}

/** 相对资源地址补全为同源绝对地址，供系统浏览器打开。 */
export function resolveMusicUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  try {
    return new URL(url, window.location.href).href
  } catch {
    return url
  }
}

/** 在 Electron 中调用主进程打开系统浏览器；纯网页环境降级为 window.open。 */
export function openMusicLink(url) {
  if (!url) {
    ElMessage.warning('这首歌还没有填写音乐链接')
    return
  }
  if (isDemoAudio(url)) {
    ElMessage.info('这是随包内置的演示音频，点「试听」即可离线播放，无需打开外链')
    return
  }
  const target = resolveMusicUrl(url)
  if (!/^https?:\/\//i.test(target)) {
    ElMessage.warning('请填写以 http(s):// 开头的有效链接')
    return
  }
  if (window.electronAPI?.openExternal) {
    window.electronAPI.openExternal(target)
  } else {
    window.open(target, '_blank', 'noopener,noreferrer')
  }
}

/** 判断是否为可直接被 <audio> 播放的音频直链。 */
export function isDirectAudio(url) {
  return /\.(mp3|wav|flac|m4a|aac|ogg|opus)(\?|#|$)/i.test(url || '')
}
