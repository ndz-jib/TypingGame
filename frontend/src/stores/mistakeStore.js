import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useMistakeStore = defineStore('mistake', {
  state: () => ({
    mistakes: [],
    total: 0,
    currentPage: 1,
    pageSize: 20,
    sortBy: 'time', // 'time' or 'count'
    loading: false
  }),

  getters: {
    totalCount: (state) => state.total,
    totalPages: (state) => Math.ceil(state.total / state.pageSize)
  },

  actions: {
    // 获取错词表（分页）
    async fetchMistakeList(page = 1, sortBy = 'time') {
      this.loading = true
      this.currentPage = page
      this.sortBy = sortBy
      
      const params = new URLSearchParams()
      params.append('sortBy', sortBy)
      params.append('page', page)
      params.append('pageSize', this.pageSize)
      
      const res = await api.get(`/mistake?${params.toString()}`)
      
      if (res.code === 200) {
        this.mistakes = res.data.list
        this.total = res.data.total
      }
      
      this.loading = false
    },

    // 搜索错词
    async searchMistake(keyword, caseSensitive = false) {
      this.loading = true
      
      const res = await api.get('/mistake/search', {
        keyword,
        caseSensitive
      })
      
      if (res.code === 200) {
        this.mistakes = res.data.list
        this.total = res.data.total
      }
      
      this.loading = false
    },

    // 记录错词（游戏中使用）
    async recordMistake(word, context = 'word_mode') {
      const res = await api.post('/mistake/record', { word, context })
      if (res.code === 200) {
        // 刷新当前页
        await this.fetchMistakeList(this.currentPage, this.sortBy)
      }
      return res
    },

    // 删除错词
    async deleteMistake(word) {
      const res = await api.delete(`/mistake/${encodeURIComponent(word)}`)
      if (res.code === 200) {
        await this.fetchMistakeList(this.currentPage, this.sortBy)
      }
      return res
    },

    // 清空错词表
    async clearAll() {
      const res = await api.delete('/mistake')
      if (res.code === 200) {
        await this.fetchMistakeList(1, this.sortBy)
      }
      return res
    }
  }
})