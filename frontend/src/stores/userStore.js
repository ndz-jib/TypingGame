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

  getters: {
    // 格式化总游玩时间
    formattedPlayTime: (state) => {
      const hours = Math.floor(state.totalPlayTime / 3600)
      const minutes = Math.floor((state.totalPlayTime % 3600) / 60)
      if (hours > 0) return `${hours}h ${minutes}m`
      return `${minutes}m`
    },
    
    // 单词模式显示数据
    wordModeDisplay: (state) => ({
      games: state.wordModeStats.games,
      bestWPM: state.wordModeStats.bestWPM,
      avgAccuracy: (state.wordModeStats.avgAccuracy * 100).toFixed(1) + '%'
    }),
    
    // 文章模式显示数据
    articleModeDisplay: (state) => ({
      games: state.articleModeStats.games,
      bestWPM: state.articleModeStats.bestWPM,
      avgAccuracy: (state.articleModeStats.avgAccuracy * 100).toFixed(1) + '%'
    })
  },

  actions: {
    async fetchUserInfo() {
      try {
        const res = await api.get('/gamer')
        if (res.code === 200 && res.data) {
          this.name = res.data.name || '玩家'
          // 确保 points 正确读取（后端使用 score 字段）
          this.points = typeof res.data.score === 'number' ? res.data.score : 0
          this.totalPlayTime = res.data.playStats?.totalPlayTime || 0
          this.totalGames = res.data.playStats?.totalGames || 0
          this.wordModeStats = res.data.playStats?.modeStats?.wordMode || { 
            games: 0, 
            bestWPM: 0, 
            avgAccuracy: 0 
          }
          this.articleModeStats = res.data.playStats?.modeStats?.articleMode || { 
            games: 0, 
            bestWPM: 0, 
            avgAccuracy: 0 
          }
          
          console.log('用户信息已更新:', {
            name: this.name,
            points: this.points,
            totalGames: this.totalGames,
            wordModeGames: this.wordModeStats.games,
            articleModeGames: this.articleModeStats.games
          })
        } else {
          console.warn('获取用户信息返回异常:', res)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    async updateUser(data) {
      try {
        console.log('更新用户信息:', data)
        const res = await api.put('/gamer', data)
        if (res.code === 200) {
          await this.fetchUserInfo()
          return true
        } else {
          console.error('更新用户信息失败:', res.message)
          return false
        }
      } catch (error) {
        console.error('更新用户信息异常:', error)
        return false
      }
    },

    // 更新积分（通过累加方式）
    async updatePoints(pointsToAdd) {
      if (typeof pointsToAdd !== 'number' || pointsToAdd <= 0) {
        console.warn('无效的积分增量:', pointsToAdd)
        return false
      }
      const newPoints = this.points + pointsToAdd
      console.log(`积分更新: ${this.points} -> ${newPoints} (+${pointsToAdd})`)
      return await this.updateUser({ score: newPoints })
    },

    // 更新游玩时间（累加）
    async updatePlayTime(seconds) {
      if (typeof seconds !== 'number' || seconds <= 0) {
        console.warn('无效的游玩时间:', seconds)
        return false
      }
      const newTime = this.totalPlayTime + seconds
      console.log(`游玩时间更新: ${this.totalPlayTime}s -> ${newTime}s (+${seconds}s)`)
      return await this.updateUser({ 
        playStats: { totalPlayTime: newTime } 
      })
    },

    // 重置玩家数据（谨慎使用）
    async resetUserData() {
      if (!confirm('确定要重置所有玩家数据吗？此操作不可恢复！')) {
        return false
      }
      
      try {
        const res = await api.put('/gamer', {
          name: '玩家',
          score: 0,
          playStats: {
            totalPlayTime: 0,
            totalGames: 0,
            totalCorrectChars: 0,
            totalWrongChars: 0,
            modeStats: {
              wordMode: { games: 0, bestWPM: 0, avgAccuracy: 0 },
              articleMode: { games: 0, bestWPM: 0, avgAccuracy: 0 }
            }
          }
        })
        if (res.code === 200) {
          await this.fetchUserInfo()
          console.log('玩家数据已重置')
          return true
        }
        return false
      } catch (error) {
        console.error('重置玩家数据失败:', error)
        return false
      }
    }
  }
})