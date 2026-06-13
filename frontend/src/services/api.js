const BASE_URL = 'http://localhost:5000/api'
const STATIC_BASE = 'http://localhost:5000/static'

class ApiService {
  async request(url, options = {}) {
    const response = await fetch(`${BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    
    return response.json()
  }
  
  get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const fullUrl = queryString ? `${url}?${queryString}` : url
    return this.request(fullUrl, { method: 'GET' })
  }
  
  post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
  
  put(url, data) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }
  
  delete(url) {
    return this.request(url, { method: 'DELETE' })
  }
  
  // 文件上传
  async uploadFile(url, file, fieldName = 'file') {
    const formData = new FormData()
    formData.append(fieldName, file)
    
    const response = await fetch(`${BASE_URL}${url}`, {
      method: 'POST',
      body: formData
    })
    
    return response.json()
  }
  
  // 获取静态资源 URL
  getStaticUrl(relativePath) {
    // relativePath 示例: 'picture/avatar.png', 'font/default.ttf', 'voice/keypress.mp3'
    return `${STATIC_BASE}/${relativePath}`
  }

  // 添加时间戳刷新资源
  getStaticUrlWithTimestamp(relativePath) {
    return `${STATIC_BASE}/${relativePath}?t=${Date.now()}`
  }
}

export const api = new ApiService()
