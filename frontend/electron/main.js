import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { spawn } from 'child_process'
import { fileURLToPath } from 'url'
import fs from 'fs'
import kill from 'tree-kill'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow = null
let flaskProcess = null
let isQuitting = false

// 获取后端路径
const getBackendPath = () => {
  if (process.env.NODE_ENV === 'development') {
    return {
      cmd: 'python',
      args: [path.join(__dirname, '../../serve.py')],
      cwd: path.join(__dirname, '../..')
    }
  } else {
    const resourcesPath = process.resourcesPath
    const exePath = path.join(resourcesPath, 'backend', 'serve.exe')
    return {
      cmd: exePath,
      args: [],
      cwd: path.dirname(exePath)
    }
  }
}

// 使用 tree-kill 强制杀死进程树
const killFlask = () => {
  return new Promise((resolve) => {
    if (!flaskProcess) {
      resolve()
      return
    }

    const pid = flaskProcess.pid
    console.log(`正在杀死进程树: ${pid}`)

    // 使用 tree-kill 杀死整个进程树
    kill(pid, 'SIGKILL', (err) => {
      if (err) {
        console.error('tree-kill 失败:', err)
        
        // 备用方案：直接杀死进程
        try {
          flaskProcess.kill('SIGKILL')
        } catch (e) {
          console.error('直接杀死失败:', e)
        }
      } else {
        console.log(`进程树 ${pid} 已杀死`)
      }
      
      flaskProcess = null
      resolve()
    })
  })
}

// 启动 Flask 后端
const startFlask = () => {
  const { cmd, args, cwd } = getBackendPath()
  
  console.log(`启动后端: ${cmd}`)
  console.log(`工作目录: ${cwd}`)
  
  // 检查文件是否存在（生产环境）
  if (process.env.NODE_ENV !== 'development') {
    if (!fs.existsSync(cmd)) {
      console.error(`后端 exe 不存在: ${cmd}`)
      const altPath = path.join(path.dirname(app.getAppPath()), '..', 'backend', 'serve.exe')
      if (fs.existsSync(altPath)) {
        flaskProcess = spawn(altPath, [], {
          cwd: path.dirname(altPath),
          detached: false,
          stdio: 'pipe',
          windowsHide: true
        })
      } else {
        console.error('找不到后端程序，应用将退出')
        app.quit()
        return
      }
    } else {
      flaskProcess = spawn(cmd, [], {
        cwd: cwd,
        detached: false,
        stdio: 'pipe',
        windowsHide: true
      })
    }
  } else {
    flaskProcess = spawn(cmd, args, {
      cwd: cwd,
      detached: false,
      stdio: 'pipe'
    })
  }
  
  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`)
  })
  
  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`)
  })
  
  flaskProcess.on('error', (err) => {
    console.error('启动后端失败:', err)
  })
  
  flaskProcess.on('close', (code) => {
    console.log(`Flask 进程退出，代码: ${code}`)
    flaskProcess = null
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
  
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 窗口关闭时清理
  mainWindow.on('close', async (event) => {
    if (!isQuitting) {
      event.preventDefault()
      isQuitting = true
      await killFlask()
      mainWindow.destroy()
    }
  })
}

// IPC 处理
ipcMain.handle('restart-app', () => {
  app.relaunch()
  app.exit()
})

// 应用生命周期
app.whenReady().then(() => {
  startFlask()
  const waitTime = process.env.NODE_ENV === 'development' ? 2000 : 3000
  setTimeout(() => {
    createWindow()
  }, waitTime)
})

// 所有窗口关闭时退出应用
app.on('window-all-closed', async () => {
  if (!isQuitting) {
    isQuitting = true
    await killFlask()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', async (event) => {
  if (!isQuitting) {
    isQuitting = true
    event.preventDefault()
    await killFlask()
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

// 进程信号处理
process.on('exit', () => {
  if (flaskProcess) {
    try {
      kill(flaskProcess.pid, 'SIGKILL')
    } catch (e) {}
  }
})

process.on('SIGINT', async () => {
  await killFlask()
  process.exit()
})

process.on('SIGTERM', async () => {
  await killFlask()
  process.exit()
})