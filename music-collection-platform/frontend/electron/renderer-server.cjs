/**
 * 生产模式下用本机轻量静态服务托管 dist 目录。
 * 相比直接 loadFile(file://)，可彻底避免 Chromium 对 file:// 下 ES Module 的限制，
 * 并让打包后的页面行为与浏览器开发模式保持一致。端口由系统自动分配。
 */
const http = require('http')
const fs = require('fs')
const path = require('path')

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.map': 'application/json; charset=utf-8'
}

let server = null
let activeUrl = null

function startRendererServer() {
  if (activeUrl) return Promise.resolve(activeUrl)

  return new Promise((resolve, reject) => {
    const root = path.join(__dirname, '..', 'dist')
    if (!fs.existsSync(path.join(root, 'index.html'))) {
      reject(new Error('未找到 frontend/dist/index.html，请先执行 npm run build'))
      return
    }

    server = http.createServer((req, res) => {
      let pathname
      try {
        pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname)
      } catch {
        pathname = '/index.html'
      }
      // 没有扩展名的路径统一回退到 SPA 入口
      if (pathname === '/' || !path.extname(pathname)) pathname = '/index.html'

      // 防止目录穿越
      const safePath = pathname.replace(/\.\./g, '')
      const filePath = path.join(root, safePath)
      if (!filePath.startsWith(root)) {
        res.writeHead(403)
        res.end('Forbidden')
        return
      }

      fs.stat(filePath, (err, stat) => {
        if (err || !stat.isFile()) {
          res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
          res.end('Not Found')
          return
        }
        const headers = {
          'Content-Type': MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream',
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'no-cache'
        }
        // 演示音频体积较大，支持 Range 才能让 <audio> 正常拖动进度条 / 边下边播
        const range = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range || '')
        if (range) {
          const start = range[1] ? Number(range[1]) : 0
          const end = range[2] ? Math.min(Number(range[2]), stat.size - 1) : stat.size - 1
          if (Number.isNaN(start) || Number.isNaN(end) || start > end || start >= stat.size) {
            res.writeHead(416, { 'Content-Range': `bytes */${stat.size}` })
            res.end()
            return
          }
          res.writeHead(206, {
            ...headers,
            'Content-Range': `bytes ${start}-${end}/${stat.size}`,
            'Content-Length': end - start + 1
          })
          fs.createReadStream(filePath, { start, end }).pipe(res)
          return
        }
        res.writeHead(200, { ...headers, 'Content-Length': stat.size })
        if (req.method === 'HEAD') {
          res.end()
          return
        }
        fs.createReadStream(filePath).pipe(res)
      })
    })

    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => {
      activeUrl = `http://127.0.0.1:${server.address().port}/index.html`
      console.log('[renderer] 本地页面服务:', activeUrl)
      resolve(activeUrl)
    })
  })
}

function stopRendererServer() {
  if (server) {
    server.close()
    server = null
    activeUrl = null
  }
}

module.exports = { startRendererServer, stopRendererServer }
