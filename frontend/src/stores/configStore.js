import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useConfigStore = defineStore('config', {
  state: () => ({
    soundEnabled: true,
    vibrationEnabled: true,
    autoSaveOnExit: true,
    fontPath: './data/font/default.ttf'
  }),

  actions: {
    async fetchConfig() {
      try {
        const res = await api.get('/config')
        if (res.code === 200 && res.data) {
          this.soundEnabled = res.data.customSettings?.soundEnabled ?? true
          this.vibrationEnabled = res.data.customSettings?.vibrationEnabled ?? true
          this.autoSaveOnExit = res.data.gameSettings?.autoSaveOnExit ?? true
          this.fontPath = res.data.customSettings?.fontPath || './data/font/default.ttf'
        }
      } catch (error) {
        console.error('获取配置失败:', error)
      }
    },

    async updateConfig(updates) {
      try {
        const current = {
          soundEnabled: this.soundEnabled,
          vibrationEnabled: this.vibrationEnabled,
          autoSaveOnExit: this.autoSaveOnExit
        }
        const newConfig = { ...current, ...updates }
        
        const res = await api.put('/config', {
          customSettings: {
            soundEnabled: newConfig.soundEnabled,
            vibrationEnabled: newConfig.vibrationEnabled,
            fontPath: this.fontPath
          },
          gameSettings: {
            autoSaveOnExit: newConfig.autoSaveOnExit
          }
        })
        
        if (res.code === 200) {
          Object.assign(this, newConfig)
          return true
        }
        return false
      } catch (error) {
        console.error('更新配置失败:', error)
        return false
      }
    },

    async resetConfig() {
      try {
        const res = await api.post('/config/reset')
        if (res.code === 200) {
          await this.fetchConfig()
          return true
        }
        return false
      } catch (error) {
        console.error('重置配置失败:', error)
        return false
      }
    }
  }
})