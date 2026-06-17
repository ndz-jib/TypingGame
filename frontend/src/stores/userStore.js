import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    name: '玩家',
    points: 0,
    totalPlayTime: 0,
    totalGames: 0,
    wordModeStats: {
      games: 0,
      bestWPM: 0,
      avgAccuracy: 0
    },
    articleModeStats: {
      games: 0,
      bestWPM: 0,
      avgAccuracy: 0
    }
  }),

  actions: {
    async fetchUserInfo() {
      try {
        const res = await api.get('/gamer')
        if (res.code === 200 && res.data) {
          this.name = res.data.name || '玩家'
          this.points = res.data.points || 0
          this.totalPlayTime = res.data.playStats?.totalPlayTime || 0
          this.totalGames = res.data.playStats?.totalGames || 0
          this.wordModeStats = res.data.playStats?.modeStats?.wordMode || { games: 0, bestWPM: 0, avgAccuracy: 0 }
          this.articleModeStats = res.data.playStats?.modeStats?.articleMode || { games: 0, bestWPM: 0, avgAccuracy: 0 }
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    async updateUser(data) {
      try {
        const res = await api.put('/gamer', data)
        if (res.code === 200) {
          await this.fetchUserInfo()
          return true
        }
        return false
      } catch (error) {
        console.error('更新用户信息失败:', error)
        return false
      }
    },

    async updatePoints(points) {
      const currentPoints = this.points
      await this.updateUser({ points: currentPoints + points })
    },

    async updatePlayTime(seconds) {
      await this.updateUser({ totalPlayTime: this.totalPlayTime + seconds })
    }
  }
})