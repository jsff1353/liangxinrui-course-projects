/** 预加载脚本：只暴露必要的最小能力，保持 contextIsolation 开启。 */
const { contextBridge, shell } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  openExternal: (url) => {
    if (/^https?:\/\//i.test(url || '')) shell.openExternal(url)
  }
})
