import { api } from './api'

class AudioService {
  constructor() {
    this.enabled = true
    this.audios = {
      keypress: null,
      error: null,
      complete: null
    }
    this.isPlaying = false
    this.stopTimer = null
    this.previewTimer = null  // 试听定时器
    this.init()
  }

  async init() {
    const keypressUrl = api.getStaticUrlWithTimestamp('voice/keypress.mp3')
    const errorUrl = api.getStaticUrlWithTimestamp('voice/error.mp3')
    const completeUrl = api.getStaticUrlWithTimestamp('voice/complete.mp3')
    
    this.audios.keypress = new Audio(keypressUrl)
    this.audios.error = new Audio(errorUrl)
    this.audios.complete = new Audio(completeUrl)
    
    for (const key of Object.keys(this.audios)) {
      if (this.audios[key]) {
        this.audios[key].volume = 0.5
        if (key === 'keypress') {
          this.audios[key].loop = true
        }
        this.audios[key].load()
      }
    }
    
    console.log('音效服务初始化完成')
  }

  setEnabled(enabled) {
    this.enabled = enabled
  }

  startKeypress() {
    if (!this.enabled) return
    
    if (this.stopTimer) {
      clearTimeout(this.stopTimer)
      this.stopTimer = null
    }
    
    const audio = this.audios.keypress
    if (audio) {
      if (this.isPlaying) {
        audio.pause()
        audio.currentTime = 0
      }
      audio.play().catch(e => console.warn('按键音效播放失败:', e))
      this.isPlaying = true
    }
  }

  stopKeypress() {
    if (!this.enabled) return
    
    if (this.stopTimer) {
      clearTimeout(this.stopTimer)
    }
    this.stopTimer = setTimeout(() => {
      const audio = this.audios.keypress
      if (audio && this.isPlaying) {
        audio.pause()
        audio.currentTime = 0
        this.isPlaying = false
      }
      this.stopTimer = null
    }, 500)
  }

  // 试听音效（限制3秒）
  preview(type) {
    if (!this.enabled) return
    
    // 清除之前的试听定时器
    if (this.previewTimer) {
      clearTimeout(this.previewTimer)
      this.previewTimer = null
    }
    
    // 停止当前播放的按键音效
    this.stopKeypressImmediately()
    
    const audio = this.audios[type]
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(e => console.warn(`${type}音效试听失败:`, e))
      
      // 3秒后自动停止
      this.previewTimer = setTimeout(() => {
        if (audio && !audio.paused) {
          audio.pause()
          audio.currentTime = 0
        }
        this.previewTimer = null
      }, 3000)
    }
  }

  playError() {
    if (!this.enabled) return
    this.stopKeypressImmediately()
    const audio = this.audios.error
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(e => console.warn('错误音效播放失败:', e))
    }
  }

  playComplete() {
    if (!this.enabled) return
    this.stopKeypressImmediately()
    const audio = this.audios.complete
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(e => console.warn('完成音效播放失败:', e))
    }
  }

  stopKeypressImmediately() {
    if (this.stopTimer) {
      clearTimeout(this.stopTimer)
      this.stopTimer = null
    }
    const audio = this.audios.keypress
    if (audio && this.isPlaying) {
      audio.pause()
      audio.currentTime = 0
      this.isPlaying = false
    }
  }

  async reload() {
    this.stopKeypressImmediately()
    
    for (const key of Object.keys(this.audios)) {
      if (this.audios[key]) {
        this.audios[key].pause()
        this.audios[key].src = ''
        this.audios[key] = null
      }
    }
    
    await this.init()
    console.log('音效服务重新加载完成')
  }
}

export const audioService = new AudioService()