import { api } from './api'

class FileService {
  /**
   * 读取本地文件内容
   * @param {File} file - 文件对象
   * @returns {Promise<string>} 文件内容
   */
  async readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = (e) => reject(e)
      reader.readAsText(file, 'UTF-8')
    })
  }

  /**
   * 上传头像
   * @param {File} file - 图片文件
   * @returns {Promise} 上传结果
   */
  async uploadAvatar(file) {
    const formData = new FormData()
    formData.append('file', file)
    return await api.uploadFile('/upload/avatar', file)
  }

  /**
   * 上传字体
   * @param {File} file - 字体文件 (.ttf)
   * @returns {Promise} 上传结果
   */
  async uploadFont(file) {
    if (!file.name.endsWith('.ttf')) {
      throw new Error('请上传 .ttf 格式的字体文件')
    }
    return await api.uploadFile('/upload/font', file)
  }

  /**
   * 上传音效
   * @param {string} type - 音效类型 (keypress, error, complete)
   * @param {File} file - 音频文件 (.mp3)
   * @returns {Promise} 上传结果
   */
  async uploadSound(type, file) {
    if (!file.name.endsWith('.mp3')) {
      throw new Error('请上传 .mp3 格式的音频文件')
    }
    
    const endpoints = {
      keypress: '/upload/voice/keypress',
      error: '/upload/voice/error',
      complete: '/upload/voice/complete'
    }
    
    const endpoint = endpoints[type]
    if (!endpoint) {
      throw new Error('无效的音效类型')
    }
    
    return await api.uploadFile(endpoint, file)
  }

  /**
   * 导入单词表 TXT
   * @param {File} file - TXT 文件
   * @returns {Promise} 导入结果
   */
  async importVocabulary(file) {
    const content = await this.readFile(file)
    return await api.post('/import/vocabulary', {
      content,
      filename: file.name
    })
  }

  /**
   * 导入文章 TXT
   * @param {File} file - TXT 文件
   * @param {Object} options - 选项
   * @returns {Promise} 导入结果
   */
  async importArticle(file, options = { autoSplit: true, maxChars: 1500 }) {
    const content = await this.readFile(file)
    return await api.post('/import/article', {
      content,
      filename: file.name,
      autoSplit: options.autoSplit,
      maxChars: options.maxChars
    })
  }

  /**
   * 导出数据
   * @returns {Promise} 导出结果
   */
  async exportData() {
    return await api.post('/export/data')
  }

  /**
   * 导入数据存档
   * @param {File} file - ZIP 文件
   * @returns {Promise} 导入结果
   */
  async importData(file) {
    return await api.uploadFile('/import/data', file)
  }

  /**
   * 下载文件
   * @param {string} url - 文件 URL
   * @param {string} filename - 保存文件名
   */
  async downloadFile(url, filename) {
    const response = await fetch(url)
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  }

  /**
   * 选择文件
   * @param {Object} options - 选项
   * @returns {Promise<File>} 选择的文件
   */
  selectFile(options = { accept: '*/*' }) {
    return new Promise((resolve, reject) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = options.accept
      
      input.onchange = (e) => {
        const file = e.target.files[0]
        if (file) {
          resolve(file)
        } else {
          reject(new Error('未选择文件'))
        }
      }
      
      input.click()
    })
  }

  /**
   * 选择多个文件
   * @param {Object} options - 选项
   * @returns {Promise<FileList>} 选择的文件列表
   */
  selectMultipleFiles(options = { accept: '*/*' }) {
    return new Promise((resolve, reject) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = options.accept
      input.multiple = true
      
      input.onchange = (e) => {
        const files = e.target.files
        if (files && files.length > 0) {
          resolve(files)
        } else {
          reject(new Error('未选择文件'))
        }
      }
      
      input.click()
    })
  }
}

export const fileService = new FileService()