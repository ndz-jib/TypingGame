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
      wrongChars: 0,
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
      let wordCount = settings.count || 10
      
      // 获取单词表总数
      const vocabRes = await api.get('/vocabulary', { 
        params: { page: 1, pageSize: 1 } 
      })
      const totalAvailable = vocabRes.data?.total || 0
      
      if (totalAvailable === 0) {
        console.error('单词表为空，无法开始游戏')
        this.isPlaying = false
        this.mode = null
        alert('单词表为空，请先添加单词！')
        return
      }
      
      // 限制单词数量不超过实际可用数量
      if (wordCount > totalAvailable) {
        console.warn(`请求 ${wordCount} 个单词，但单词表只有 ${totalAvailable} 个，将使用全部可用单词`)
        wordCount = totalAvailable
      }
      
      // 检查布局是否可用
      const layout = settings.layout || '4'
      const layoutCardCount = this.getCardCountByLayout(layout)
      if (wordCount < layoutCardCount) {
        console.warn(`单词数量 (${wordCount}) 少于布局所需卡片数 (${layoutCardCount})，将使用最小可用布局`)
        const availableLayouts = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for (const l of availableLayouts) {
          if (this.getCardCountByLayout(l) <= wordCount) {
            this.wordSettings.layout = l
            break
          }
        }
      }
      
      // 调用 API 获取随机单词
      const res = await api.get('/random/words', { params: { count: wordCount } })
      
      if (res.code === 200 && res.data.words && res.data.words.length > 0) {
        this.wordList = res.data.words
        this.stats.total = this.wordList.length
        this.stats.startTime = Date.now()
        this.stats.correctChars = 0
        this.stats.wrongChars = 0
        this.stats.errorCount = 0
        this.stats.completed = 0
        this.stats.accuracy = 1
        this.stats.efficiency = 0
        this.wordErrors = []
        this.initWordCards(this.wordSettings.layout || '4')
        console.log('单词模式初始化成功，共', this.wordList.length, '个单词')
      } else {
        console.error('获取随机单词失败:', res)
        this.isPlaying = false
        this.mode = null
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
        // 正确：累加正确字符数
        this.stats.correctChars += wordText.length
        console.log(`单词 "${wordText}" 正确，+${wordText.length} 正确字符`)
      } else {
        // 错误：记录错词并累加错误字符数
        if (!this.wordErrors.includes(wordText)) {
          this.wordErrors.push(wordText)
          this.stats.wrongChars += wordText.length
          this.stats.errorCount += wordText.length
          console.log(`单词 "${wordText}" 错误，+${wordText.length} 错误字符`)
          api.post('/mistake/record', { word: wordText }).catch(e => console.error(e))
        }
      }
      
      // 重新计算准确率（基于字符数）
      const totalChars = this.stats.correctChars + this.stats.wrongChars
      this.stats.accuracy = totalChars > 0 
        ? this.stats.correctChars / totalChars 
        : 1
      
      console.log(`进度: ${this.stats.completed}/${this.stats.total}, 准确率: ${(this.stats.accuracy * 100).toFixed(1)}%`)
      
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
          this.stats.wrongChars = 0
          this.stats.errorCount = 0
          this.stats.completed = 0
          this.stats.accuracy = 1
          this.currentLineIndex = 0
          this.wordErrors = []
          console.log('文章处理成功，总行数:', this.articleLines.length, '总字符数:', this.stats.total)
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
      const currentInput = input
      
      // 逐字符比对，只统计新增的字符变化
      for (let i = 0; i < currentInput.length; i++) {
        if (i >= originalText.length) break
        
        const isNewChar = i >= prevInput.length
        
        if (currentInput[i] === originalText[i]) {
          // 正确字符：只统计新增的正确字符
          if (isNewChar) {
            this.stats.correctChars++
          }
        } else if (currentInput[i] !== undefined && currentInput[i] !== '') {
          // 错误字符：统计错误字符
          if (isNewChar) {
            this.stats.wrongChars++
            this.stats.errorCount++
          }
          // 记录错词
          const errorWord = this.extractWordAtPosition(originalText, i)
          if (errorWord && !this.wordErrors.includes(errorWord)) {
            this.wordErrors.push(errorWord)
            api.post('/mistake/record', { word: errorWord }).catch(e => console.error(e))
          }
        }
      }
      
      // 如果用户删除了字符，重新计算统计
      if (currentInput.length < prevInput.length) {
        this.recalculateAllStats()
      }
      
      this.articleLineInputs[lineIndex] = input
      this.updateArticleProgress()
      this.updateEfficiency()
    },
    
    // 重新计算所有统计（当用户删除字符时使用）
    recalculateAllStats() {
      let correct = 0
      let wrong = 0
      
      for (let i = 0; i < this.articleLines.length; i++) {
        const text = this.articleLines[i] || ''
        const input = this.articleLineInputs[i] || ''
        const minLen = Math.min(input.length, text.length)
        
        for (let j = 0; j < minLen; j++) {
          if (input[j] === text[j]) {
            correct++
          } else if (input[j] !== undefined && input[j] !== '') {
            wrong++
          }
        }
      }
      
      this.stats.correctChars = correct
      this.stats.wrongChars = wrong
      this.stats.errorCount = wrong
      
      const totalChars = correct + wrong
      this.stats.accuracy = totalChars > 0 ? correct / totalChars : 1
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
      for (let i = 0; i <= this.currentLineIndex && i < this.articleLineInputs.length; i++) {
        completedChars += (this.articleLineInputs[i] || '').length
      }
      this.stats.completed = Math.min(completedChars, this.stats.total || 0)
      
      const totalChars = this.stats.correctChars + this.stats.wrongChars
      this.stats.accuracy = totalChars > 0 
        ? this.stats.correctChars / totalChars 
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
          this.stats.wrongChars = 0
          this.stats.errorCount = 0
          this.stats.completed = 0
          this.stats.accuracy = 1
          this.wordErrors = []
          return true
        }
      }
      return false
    },
    
    async handleWordError(word) {
      if (!this.wordErrors.includes(word)) {
        this.wordErrors.push(word)
        this.stats.wrongChars += word.length
        this.stats.errorCount += word.length
        await api.post('/mistake/record', { word }).catch(e => console.error(e))
      }
    },

    handleCharError(char) {
      this.stats.errorCount++
      this.stats.wrongChars++
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
      // 标准单词长度 = 5 个字符
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
      
      // 获取正确和错误的字符数
      const correctChars = this.stats.correctChars || 0
      const wrongChars = this.stats.wrongChars || 0
      
      console.log('游戏结束统计:', {
        mode: this.mode,
        wpm: wpm,
        correctChars: correctChars,
        wrongChars: wrongChars,
        elapsed: elapsed,
        accuracy: this.stats.accuracy
      })
      
      await this.saveGameRecord(wpm, elapsed, correctChars, wrongChars)
      this.isPlaying = false
    },
    
    async saveGameRecord(wpm, playTime, correctChars, wrongChars) {
      const totalChars = (correctChars || 0) + (wrongChars || 0)
      const accuracy = totalChars > 0 ? (correctChars || 0) / totalChars : 1
      
      const endpoint = this.mode === 'word' ? '/gamer/word-record' : '/gamer/article-record'
      
      const payload = {
        wpm: Math.round(wpm * 10) / 10,
        accuracy: Math.round(accuracy * 1000) / 1000,
        playTime: Math.round(playTime * 100) / 100,
        correctChars: correctChars || 0,
        wrongChars: wrongChars || 0
      }
      
      console.log('发送游戏记录:', endpoint, payload)
      
      try {
        const res = await api.post(endpoint, payload)
        if (res.code === 200) {
          console.log('游戏记录保存成功:', res.data)
          // 刷新用户信息以获取最新积分
          const { useUserStore } = await import('./userStore')
          const userStore = useUserStore()
          await userStore.fetchUserInfo()
          return res
        } else {
          console.error('游戏记录保存失败:', res.message)
          return res
        }
      } catch (error) {
        console.error('保存游戏记录异常:', error)
        throw error
      }
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
        completed: 0,
        total: 0,
        correctChars: 0,
        wrongChars: 0,
        accuracy: 1,
        efficiency: 0,
        timeRemaining: 0,
        startTime: null,
        endTime: null,
        errorCount: 0
      }
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      console.log('游戏状态已重置')
    }
  }
})