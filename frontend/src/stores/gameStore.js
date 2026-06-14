import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useGameStore = defineStore('game', {
  state: () => ({
    isPlaying: false,
    mode: null,
    
    // 单词模式
    wordList: [],
    currentWordIndex: 0,
    wordCards: [],
    wordErrors: [],
    
    // 文章模式
    articleContent: '',
    articleLines: [],
    articleLineInputs: [],
    currentLineIndex: 0,
    currentArticlePart: 1,
    totalArticleParts: 1,
    articlePartsList: [],
    
    // 统计数据
    stats: {
      completed: 0,
      total: 0,
      correctChars: 0,
      accuracy: 1,
      efficiency: 0,
      timeRemaining: 0,
      startTime: null,
      endTime: null,
      errorCount: 0
    },
    
    // 设置
    wordSettings: null,
    articleSettings: null,
    timerEnabled: false,
    timerDuration: 120,
    displayLines: 4,
    
    timer: null
  }),
  
  actions: {
    // ==================== 单词模式 ====================
    
    async initWordMode(settings) {
      this.mode = 'word'
      this.wordSettings = settings
      this.timerEnabled = settings.timer?.enabled || false
      this.timerDuration = settings.timer?.duration || 120
      
      // 检查单词数量
      const wordCount = settings.count || 10
      if (wordCount <= 0) {
        console.error('单词数量无效:', wordCount)
        this.isPlaying = false
        this.mode = null
        return
      }
      
      const res = await api.get('/random/words', { params: { count: wordCount } })
      
      if (res.code === 200 && res.data.words && res.data.words.length > 0) {
        this.wordList = res.data.words
        this.stats.total = this.wordList.length
        this.stats.startTime = Date.now()
        this.stats.correctChars = 0
        this.stats.errorCount = 0
        this.wordErrors = []
        this.initWordCards(settings.layout)
      } else {
        console.error('获取随机单词失败或单词列表为空:', res)
        this.isPlaying = false
        this.mode = null
        // 提示用户
        alert('获取单词失败，请检查网络或稍后重试')
      }
    },
    
    initWordCards(layout) {
      const cardCount = this.getCardCountByLayout(layout)
      this.wordCards = this.wordList.slice(0, cardCount).map((item, idx) => ({
        id: `card_${idx}_${Date.now()}`,
        word: item.word,
        note: item.note || '',
        startTime: Date.now(),
        isCompleted: false
      }))
      this.currentWordIndex = cardCount
    },
    
    getCardCountByLayout(layout) {
      const counts = { '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9 }
      return counts[layout] || 4
    },
    
    handleWordComplete(cardId, isCorrect, wordText, inputText) {
      const card = this.wordCards.find(c => c.id === cardId)
      if (!card || card.isCompleted) return
      
      card.isCompleted = true
      this.stats.completed++
      
      if (isCorrect) {
        this.stats.correctChars += wordText.length
      } else {
        if (!this.wordErrors.includes(wordText)) {
          this.wordErrors.push(wordText)
          this.stats.errorCount++
          api.post('/mistake/record', { word: wordText }).catch(e => console.error(e))
        }
      }
      
      this.stats.accuracy = this.stats.completed > 0 
        ? (this.stats.completed - this.stats.errorCount) / this.stats.completed 
        : 1
      
      if (this.stats.completed === this.stats.total) {
        this.endGame()
      }
    },
    
    getNextWord() {
      if (this.currentWordIndex < this.wordList.length) {
        const item = this.wordList[this.currentWordIndex]
        this.currentWordIndex++
        return { word: item.word, note: item.note || '' }
      }
      return null
    },
    
    replaceWordCard(cardIndex, newWord, newNote) {
      this.wordCards[cardIndex] = {
        id: `card_${cardIndex}_${Date.now()}`,
        word: newWord,
        note: newNote,
        startTime: Date.now(),
        isCompleted: false
      }
    },
    
    // ==================== 文章模式 ====================
    
    async initArticleMode(settings) {
      this.mode = 'article'
      this.articleSettings = settings
      this.timerEnabled = settings.timer?.enabled || false
      this.timerDuration = settings.timer?.duration || 120
      this.displayLines = settings.displayLines || 4
      
      // 检查是否选择了文章
      if (!settings.selectedArticle) {
        console.error('未选择文章')
        this.isPlaying = false
        this.mode = null
        alert('请先选择一篇文章')
        return
      }
      
      if (settings.splitParts && settings.splitParts.length > 0) {
        this.articlePartsList = settings.splitParts
        this.totalArticleParts = settings.totalParts
        this.currentArticlePart = 1
      }
      
      const res = await api.get(`/articles/${settings.selectedArticle}`)
      
      if (res.code === 200 && res.data.content) {
        this.articleContent = res.data.content
        
        // 检查文章内容是否为空
        if (!this.articleContent || this.articleContent.trim() === '') {
          console.error('文章内容为空')
          this.isPlaying = false
          this.mode = null
          alert('文章内容为空，请选择其他文章')
          return
        }
        
        const processRes = await api.post('/article/process', {
          content: this.articleContent,
          lineWidth: settings.lineWidth || 40
        })
        
        if (processRes.code === 200 && processRes.data.lines && processRes.data.lines.length > 0) {
          this.articleLines = processRes.data.lines
          this.articleLineInputs = new Array(this.articleLines.length).fill('')
          this.stats.total = processRes.data.totalChars
          this.stats.startTime = Date.now()
          this.stats.correctChars = 0
          this.stats.errorCount = 0
          this.currentLineIndex = 0
          console.log('文章处理成功，总行数:', this.articleLines.length)
        } else {
          console.error('文章处理失败:', processRes)
          this.isPlaying = false
          this.mode = null
          alert('文章处理失败，请重试')
        }
      } else {
        console.error('获取文章内容失败:', res)
        this.isPlaying = false
        this.mode = null
        alert('获取文章失败，请检查网络或稍后重试')
      }
    },
    
    updateArticleLine(lineIndex, input) {
      if (!this.articleLines || !Array.isArray(this.articleLines)) return
      if (lineIndex >= this.articleLines.length) return
      
      const originalText = this.articleLines[lineIndex]
      if (!originalText || originalText === '') {
        if (this.articleLineInputs[lineIndex] !== '') {
          this.articleLineInputs[lineIndex] = ''
          if (lineIndex === this.currentLineIndex) {
            this.currentLineIndex++
            this.updateArticleProgress()
          }
        }
        return
      }
      
      const prevInput = this.articleLineInputs[lineIndex] || ''
      
      for (let i = prevInput.length; i < input.length; i++) {
        if (i >= originalText.length) break
        
        if (input[i] === originalText[i]) {
          this.stats.correctChars++
        } else if (input[i] !== undefined) {
          const errorWord = this.extractWordAtPosition(originalText, i)
          if (errorWord && !this.wordErrors.includes(errorWord)) {
            this.wordErrors.push(errorWord)
            this.stats.errorCount++
            api.post('/mistake/record', { word: errorWord }).catch(e => console.error(e))
          }
        }
      }
      
      this.articleLineInputs[lineIndex] = input
      this.updateArticleProgress()
      this.updateEfficiency()
    },
    
    // 完全匹配：当前行变成完成栏，移动到下一行
    completeCurrentLine() {
      if (this.currentLineIndex < this.articleLines.length) {
        this.currentLineIndex++
        this.updateArticleProgress()
        
        if (this.currentLineIndex >= this.articleLines.length) {
          this.endGame()
        }
      }
    },
    
    // 强制换行（不匹配）：移动到下一行，当前行保持为待完成栏
    forceMoveToNextLine() {
      if (this.currentLineIndex < this.articleLines.length) {
        this.currentLineIndex++
        this.updateArticleProgress()
        
        if (this.currentLineIndex >= this.articleLines.length) {
          this.endGame()
        }
      }
    },
    
    updateArticleProgress() {
      let completedChars = 0
      for (let i = 0; i <= this.currentLineIndex; i++) {
        completedChars += (this.articleLineInputs[i] || '').length
      }
      this.stats.completed = completedChars
      this.stats.accuracy = this.stats.completed > 0 
        ? this.stats.correctChars / this.stats.completed 
        : 1
    },
    
    extractWordAtPosition(text, position) {
      if (!text || position < 0 || position >= text.length) return null
      if (!/[a-zA-Z]/.test(text[position])) return null
      
      let start = position
      let end = position
      while (start > 0 && /[a-zA-Z]/.test(text[start - 1])) start--
      while (end < text.length && /[a-zA-Z]/.test(text[end])) end++
      
      return text.substring(start, end)
    },
    
    async loadNextArticlePart() {
      if (this.currentArticlePart < this.totalArticleParts) {
        this.currentArticlePart++
        const nextFile = this.articlePartsList[this.currentArticlePart - 1]
        const res = await api.get(`/articles/${nextFile}`)
        
        if (res.code === 200 && res.data.content) {
          this.articleContent = res.data.content
          this.articleLines = this.articleContent.split('\n')
          this.articleLineInputs = new Array(this.articleLines.length).fill('')
          this.currentLineIndex = 0
          this.stats.startTime = Date.now()
          this.stats.correctChars = 0
          this.stats.completed = 0
          this.wordErrors = []
          return true
        }
      }
      return false
    },
    
    async handleWordError(word) {
      if (!this.wordErrors.includes(word)) {
        this.wordErrors.push(word)
        this.stats.errorCount++
        await api.post('/mistake/record', { word }).catch(e => console.error(e))
      }
    },

    handleCharError(char) {
      this.stats.errorCount++
    },

    updateEfficiency() {
      const elapsed = (Date.now() - this.stats.startTime) / 1000
      if (elapsed > 0) {
        this.stats.efficiency = (this.stats.completed / elapsed) * 10
      }
    },
    
    // ==================== 通用方法 ====================
    
    startTimer() {
      if (!this.timerEnabled) return
      if (this.timer) clearInterval(this.timer)
      
      this.stats.timeRemaining = this.timerDuration
      this.timer = setInterval(() => {
        if (this.stats.timeRemaining <= 1) {
          clearInterval(this.timer)
          this.endGame()
        } else {
          this.stats.timeRemaining--
        }
      }, 1000)
    },
    
    calculateWPM() {
      const elapsedSeconds = (this.stats.endTime - this.stats.startTime) / 1000
      if (elapsedSeconds <= 0) return 0
      return Math.round((this.stats.correctChars * 60) / (5 * elapsedSeconds))
    },
    
    async endGame() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      
      this.stats.endTime = Date.now()
      const wpm = this.calculateWPM()
      const elapsed = (this.stats.endTime - this.stats.startTime) / 1000
      
      await this.saveGameRecord(wpm, elapsed)
      this.isPlaying = false
    },
    
    async saveGameRecord(wpm, playTime) {
      const accuracy = this.stats.accuracy
      const endpoint = this.mode === 'word' ? '/gamer/word-record' : '/gamer/article-record'
      await api.post(endpoint, { wpm, accuracy, playTime }).catch(e => console.error(e))
    },
    
    startGame(mode, settings) {
      this.reset()
      this.isPlaying = true
      this.stats.startTime = Date.now()
      
      if (mode === 'word') {
        this.initWordMode(settings)
        if (settings.timer?.enabled) this.startTimer()
      } else if (mode === 'article') {
        this.initArticleMode(settings)
        if (settings.timer?.enabled) this.startTimer()
      }
    },
    
    reset() {
      this.isPlaying = false
      this.mode = null
      this.wordList = []
      this.currentWordIndex = 0
      this.wordCards = []
      this.wordErrors = []
      this.articleContent = ''
      this.articleLines = []
      this.articleLineInputs = []
      this.currentLineIndex = 0
      this.currentArticlePart = 1
      this.totalArticleParts = 1
      this.articlePartsList = []
      this.stats = {
        completed: 0, total: 0, correctChars: 0, accuracy: 1, efficiency: 0,
        timeRemaining: 0, startTime: null, endTime: null, errorCount: 0
      }
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    }
  }
})