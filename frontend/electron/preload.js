const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  restartApp: () => ipcRenderer.invoke('restart-app'),
  
  // 获取应用版本
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // 检查是否在 Electron 环境中
  isElectron: true
})