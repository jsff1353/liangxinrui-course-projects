/**
 * Electron 主进程
 * 1) 优先探测本机 5000 端口的 Flask 服务（开发环境手动启动 / 外部部署）
 * 2) 若未就绪且存在随包分发的 music-api.exe，则自动拉起后端并等待就绪
 * 3) 开发模式加载 Vite dev server，打包后加载 dist/index.html（hash 路由）
 */
const { app, BrowserWindow, Menu, shell, dialog } = require('electron')
const { spawn } = require('child_process')
const http = require('http')
const fs = require('fs')
const path = require('path')
const { startRendererServer, stopRendererServer } = require('./renderer-server.cjs')

const DEV_URL = process.env.VITE_DEV_SERVER_URL || 'http://127.0.0.1:5173'
const API_BASE = process.env.MUSIC_API_BASE || 'http://127.0.0.1:5000'
const isDev = !app.isPackaged

let mainWindow = null
let backendProcess = null

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function pingBackend() {
  return new Promise((resolve) => {
    const req = http.get(`${API_BASE}/api/health`, (res) => {
      res.resume()
      resolve(res.statusCode === 200)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(1000, () => {
      req.destroy()
      resolve(false)
    })
  })
}

async function waitForBackend(timeout = 25000) {
  const start = Date.now()
  while (Date.now() - start < timeout) {
    if (await pingBackend()) return true
    await sleep(600)
  }
  return false
}

function backendExePath() {
  return app.isPackaged
    ? path.join(process.resourcesPath, 'backend', 'music-api.exe')
    : path.join(__dirname, '..', '..', 'backend-dist', 'music-api.exe')
}

function startBackend() {
  const exe = backendExePath()
  if (!fs.existsSync(exe)) return false

  const cwd = path.dirname(exe)
  const env = { ...process.env }
  const envFile = path.join(cwd, '.env')
  if (fs.existsSync(envFile)) env.MUSIC_ENV_FILE = envFile // 允许修改安装目录下的 .env

  // SQLite 数据文件放到用户可写目录，避免安装到 Program Files 后无权创建；
  // 若 .env 中已显式配置 SQLITE_PATH，则以配置文件为准。
  const envText = fs.existsSync(envFile) ? fs.readFileSync(envFile, 'utf8') : ''
  if (!env.SQLITE_PATH && !/^\s*SQLITE_PATH\s*=/m.test(envText)) {
    env.SQLITE_PATH = path.join(app.getPath('userData'), 'music_collection.db')
  }

  try {
    backendProcess = spawn(exe, [], {
      cwd,
      env,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe']
    })
    backendProcess.stdout.on('data', (chunk) => process.stdout.write(`[backend] ${chunk}`))
    backendProcess.stderr.on('data', (chunk) => process.stderr.write(`[backend] ${chunk}`))
    backendProcess.on('error', (err) => console.error('[backend] 启动失败:', err.message))
    console.log('[backend] 已拉起随包后端:', exe)
    return true
  } catch (err) {
    console.error('[backend] 启动异常:', err.message)
    return false
  }
}

function stopBackend() {
  if (!backendProcess || backendProcess.killed) return
  try {
    if (process.platform === 'win32') {
      // PyInstaller onefile 会派生子进程，用 taskkill /T 结束整棵进程树
      spawn('taskkill', ['/pid', String(backendProcess.pid), '/T', '/F'], { windowsHide: true })
    } else {
      backendProcess.kill('SIGTERM')
    }
  } catch (err) {
    console.error('[backend] 停止失败:', err.message)
  }
  backendProcess = null
}

async function ensureBackend() {
  if (await pingBackend()) {
    console.log('[backend] 已连接外部 Flask 服务')
    return true
  }
  if (!startBackend()) {
    console.warn('[backend] 未找到随包后端，请手动启动 backend/run.py 或配置远程服务')
    return false
  }
  const ready = await waitForBackend()
  if (!ready) console.error('[backend] 等待后端就绪超时，请检查数据库配置')
  return ready
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1060,
    minHeight: 680,
    title: '音乐收藏管理',
    backgroundColor: '#f5f6fb',
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      webSecurity: true
    }
  })

  mainWindow.once('ready-to-show', () => mainWindow.show())
  mainWindow.on('closed', () => { mainWindow = null })

  // 页面内的外部链接统一交给系统浏览器打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//i.test(url)) shell.openExternal(url)
    return { action: 'deny' }
  })

  if (isDev) {
    mainWindow.loadURL(DEV_URL)
  } else {
    try {
      // 生产模式通过本地静态服务加载，避免 file:// 对 ES Module 的限制
      mainWindow.loadURL(await startRendererServer())
    } catch (err) {
      dialog.showErrorBox('页面加载失败', `${err.message}\n\n请在 frontend 目录执行 npm run build 后重试。`)
    }
  }
}

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null)
  await ensureBackend()
  await createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  stopBackend()
  stopRendererServer()
})
