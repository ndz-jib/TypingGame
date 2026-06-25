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
let isRestarting = false

// ==================== 路径配置 ====================

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

// ==================== 进程管理（增强版） ====================

const killFlask = () => {
  return new Promise((resolve) => {
    if (!flaskProcess) {
      console.log('没有 Flask 进程需要杀死')
      resolve()
      return
    }

    const pid = flaskProcess.pid
    console.log(`正在杀死 Flask 进程树: ${pid}`)

    // 方法1：tree-kill
    kill(pid, 'SIGKILL', (err) => {
      if (err) {
        console.error('tree-kill 失败:', err)
        // 方法2：直接杀死
        try {
          process.kill(pid, 'SIGKILL')
          console.log(`直接杀死进程 ${pid} 成功`)
        } catch (e) {
          console.error('直接杀死失败:', e)
        }
      } else {
        console.log(`进程树 ${pid} 已杀死`)
      }
      
      flaskProcess = null
      
      // 等待进程完全终止
      setTimeout(() => {
        resolve()
      }, 1000)
    })
  })
}

const startFlask = () => {
  const { cmd, args, cwd } = getBackendPath()
  
  console.log(`启动后端: ${cmd}`)
  console.log(`工作目录: ${cwd}`)
  
  // 生产环境检查
  if (process.env.NODE_ENV !== 'development') {
    let exePath = cmd
    if (!fs.existsSync(exePath)) {
      const altPath = path.join(path.dirname(app.getAppPath()), '..', 'backend', 'serve.exe')
      if (fs.existsSync(altPath)) {
        exePath = altPath
      } else {
        console.error('找不到后端程序，应用将退出')
        app.quit()
        return
      }
    }
    
    flaskProcess = spawn(exePath, [], {
      cwd: path.dirname(exePath),
      detached: false,
      stdio: 'pipe',
      windowsHide: true,
      shell: false,
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    })
  } else {
    flaskProcess = spawn(cmd, args, {
      cwd: cwd,
      detached: false,
      stdio: 'pipe',
      shell: false,
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    })
  }
  
  // 进程事件
  flaskProcess.on('error', (err) => {
    console.error('启动 Flask 失败:', err)
  })
  
  flaskProcess.on('close', (code, signal) => {
    console.log(`Flask 进程退出，代码: ${code}, 信号: ${signal}`)
    flaskProcess = null
  })
  
  // 日志输出
  if (flaskProcess.stdout) {
    flaskProcess.stdout.on('data', (data) => {
      const msg = data.toString().trim()
      if (msg) console.log(`Flask: ${msg}`)
    })
  }
  
  if (flaskProcess.stderr) {
    flaskProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim()
      if (msg) console.error(`Flask Error: ${msg}`)
    })
  }
}

// ==================== 窗口管理 ====================

const createWindow = () => {
  if (mainWindow) {
    mainWindow.destroy()
    mainWindow = null
  }
  
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: true,
    titleBarStyle: 'default',
    show: false
  })
  
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })
  
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 窗口关闭事件
  mainWindow.on('close', async (event) => {
    if (isRestarting) {
      // 重启中，让进程继续
      return
    }
    
    if (!isQuitting) {
      event.preventDefault()
      isQuitting = true
      console.log('用户关闭窗口，正在清理进程...')
      await killFlask()
      mainWindow.destroy()
    }
  })
}

// ==================== IPC 处理 ====================

ipcMain.handle('restart-app', async () => {
  console.log('收到重启请求')
  
  if (isRestarting) {
    console.log('已经在重启中')
    return
  }
  
  isRestarting = true
  
  try {
    // 1. 杀死 Flask 进程
    await killFlask()
    
    // 2. 关闭窗口
    if (mainWindow) {
      mainWindow.destroy()
      mainWindow = null
    }
    
    // 3. 等待资源释放
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 4. 重新启动 Flask
    startFlask()
    
    // 5. 等待后端启动
    const waitTime = process.env.NODE_ENV === 'development' ? 2000 : 3000
    await new Promise(resolve => setTimeout(resolve, waitTime))
    
    // 6. 重新创建窗口
    createWindow()
    
    isRestarting = false
    isQuitting = false
    console.log('重启完成')
  } catch (error) {
    console.error('重启失败:', error)
    isRestarting = false
    isQuitting = false
  }
})

// ==================== 应用生命周期 ====================

app.whenReady().then(() => {
  startFlask()
  const waitTime = process.env.NODE_ENV === 'development' ? 2000 : 3000
  setTimeout(createWindow, waitTime)
})

app.on('window-all-closed', async () => {
  if (isRestarting) return
  
  if (!isQuitting) {
    isQuitting = true
    await killFlask()
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', async (event) => {
  if (isRestarting) return
  
  if (!isQuitting) {
    isQuitting = true
    event.preventDefault()
    await killFlask()
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null && !isRestarting) {
    createWindow()
  }
})

// ==================== 进程信号处理 ====================

process.on('exit', () => {
  if (flaskProcess) {
    try {
      kill(flaskProcess.pid, 'SIGKILL')
    } catch (e) {
      try { process.kill(flaskProcess.pid, 'SIGKILL') } catch (e2) {}
    }
  }
})

process.on('SIGINT', async () => {
  console.log('收到 SIGINT')
  await killFlask()
  process.exit(0)
})

process.on('SIGTERM', async () => {
  console.log('收到 SIGTERM')
  await killFlask()
  process.exit(0)
})

process.on('uncaughtException', async (err) => {
  console.error('未捕获异常:', err)
  await killFlask()
  process.exit(1)
})

console.log('Electron 主进程已启动')