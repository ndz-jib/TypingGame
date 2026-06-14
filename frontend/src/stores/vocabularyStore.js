import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useVocabularyStore = defineStore('vocabulary', {
  state: () => ({
    words: [],
    total: 0,
    currentPage: 1,
    pageSize: 20,
    currentLetter: '',
    loading: false
  }),

  getters: {
    totalCount: (state) => state.total,
    totalPages: (state) => Math.ceil(state.total / state.pageSize)
  },

  actions: {
    // 获取单词表（分页）
    async fetchVocabulary(page = 1, letter = '') {
      this.loading = true
      this.currentPage = page
      this.currentLetter = letter
      
      const params = new URLSearchParams()
      params.append('page', page)
      params.append('pageSize', this.pageSize)
      if (letter) {
        params.append('letter', letter)
      }
      
      const res = await api.get(`/vocabulary?${params.toString()}`)
      
      if (res.code === 200) {
        this.words = res.data.list
        this.total = res.data.total
      }
      
      this.loading = false
    },

    // 搜索单词
    async searchVocabulary(keyword, caseSensitive = false) {
      this.loading = true
      
      const res = await api.get('/vocabulary/search', {
        keyword,
        caseSensitive
      })
      
      if (res.code === 200) {
        this.words = res.data.list
        this.total = res.data.total
      }
      
      this.loading = false
    },

    // 添加单词
    async addWord(word, note = '') {
      const res = await api.post('/vocabulary', { word, note })
      if (res.code === 200) {
        await this.fetchVocabulary(this.currentPage, this.currentLetter)
      }
      return res
    },

    // 删除单词
    async deleteWord(word) {
      const res = await api.delete(`/vocabulary/${encodeURIComponent(word)}`)
      if (res.code === 200) {
        await this.fetchVocabulary(this.currentPage, this.currentLetter)
      }
      return res
    },

    // 更新注释
    async updateNote(word, note) {
      const res = await api.put(`/vocabulary/${encodeURIComponent(word)}/note`, { note })
      if (res.code === 200) {
        // 更新本地数据
        const found = this.words.find(w => w.word === word)
        if (found) {
          found.note = note
        }
      }
      return res
    },

    // 清空单词表（谨慎使用）
    async clearAll() {
      const res = await api.delete('/vocabulary')
      if (res.code === 200) {
        await this.fetchVocabulary(1, '')
      }
      return res
    }
  }
})