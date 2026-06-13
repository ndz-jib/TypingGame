import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { spawn } from 'child_process'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow = null
let flaskProcess = null

// 启动 Flask 后端
const startFlask = () => {
  const flaskPath = path.join(__dirname, '../../serve.py')
  flaskProcess = spawn('python', [flaskPath], {
    cwd: path.join(__dirname, '../..')
  })
  
  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`)
  })
  
  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`)
  })
}

// 创建窗口
const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: true,
    titleBarStyle: 'default'
  })
  
  // 开发环境加载 Vite dev server
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 重启应用
const restartApp = () => {
  app.relaunch()
  app.exit()
}

// IPC 处理
ipcMain.handle('restart-app', () => {
  restartApp()
})

// 应用生命周期
app.whenReady().then(() => {
  startFlask()
  // 等待 Flask 启动
  setTimeout(() => {
    createWindow()
  }, 2000)
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (flaskProcess) {
      flaskProcess.kill()
    }
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})