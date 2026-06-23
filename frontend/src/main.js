import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'
import './assets/styles/light.css'
import './assets/styles/dark.css'
import { api } from './services/api'

// 加载字体
const loadFont = async () => {
  const fontUrl = api.getStaticUrl('font/default.ttf')
  
  try {
    // 方法1：使用 FontFace API（现代浏览器）
    const font = new FontFace('CustomFont', `url(${fontUrl})`)
    await font.load()
    document.fonts.add(font)
    document.body.style.fontFamily = 'CustomFont, system-ui, -apple-system, sans-serif'
  } catch (error) {
    console.warn('FontFace 加载失败，尝试备用方法:', error)
    // 方法2：使用 CSS @font-face（备用）
    const style = document.createElement('style')
    style.textContent = `
      @font-face {
        font-family: 'CustomFont';
        src: url('${fontUrl}?t=${Date.now()}') format('truetype');
        font-weight: normal;
        font-style: normal;
      }
      body {
        font-family: 'CustomFont', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
      }
    `
    document.head.appendChild(style)
  }
}

// 初始化应用
const init = async () => {
  await loadFont()
  
  const app = createApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  app.use(router)
  app.mount('#app')
}

init()