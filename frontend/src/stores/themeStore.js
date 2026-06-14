import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light' // 'light' or 'dark'
  }),
  
  actions: {
    // 初始化主题
    initTheme() {
      const savedTheme = localStorage.getItem('typing_theme')
      if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
        this.theme = savedTheme
      } else {
        // 检测系统主题
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        this.theme = prefersDark ? 'dark' : 'light'
      }
      this.applyTheme()
    },
    
    // 切换主题
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('typing_theme', this.theme)
      this.applyTheme()
    },
    
    // 应用主题到 DOM
    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.theme)
      
      // 动态加载对应的主题 CSS
      const linkId = 'theme-style'
      let link = document.getElementById(linkId)
      
      if (!link) {
        link = document.createElement('link')
        link.id = linkId
        link.rel = 'stylesheet'
        document.head.appendChild(link)
      }
      
      // 根据主题加载不同的 CSS 文件
      // 注意：实际加载已在 main.js 中通过 import 完成
      // 这里只需要设置 data-theme 属性即可
    },
    
    // 设置主题
    setTheme(theme) {
      if (theme === 'light' || theme === 'dark') {
        this.theme = theme
        localStorage.setItem('typing_theme', this.theme)
        this.applyTheme()
      }
    }
  },
  
  getters: {
    isDark: (state) => state.theme === 'dark',
    isLight: (state) => state.theme === 'light'
  }
})