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
  
  // 文件上传（独立实现，不依赖 request）
  async uploadFile(url, file, fieldName = 'file') {
    const formData = new FormData()
    formData.append(fieldName, file)
    
    const response = await fetch(`${BASE_URL}${url}`, {
      method: 'POST',
      body: formData
      // 不要设置 Content-Type，浏览器自动设置 multipart/form-data
    })
    
    // 处理响应
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return response.json()
    } else {
      // 如果是 HTML 错误页面，抛出友好错误
      const text = await response.text()
      throw new Error(`服务器返回错误 (${response.status})`)
    }
  }
  
  // 带时间戳的静态资源 URL
  getStaticUrl(relativePath) {
    return `${STATIC_BASE}/${relativePath}`
  }

  getStaticUrlWithTimestamp(relativePath) {
    return `${STATIC_BASE}/${relativePath}?t=${Date.now()}`
  }
}

export const api = new ApiService()