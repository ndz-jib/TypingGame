import { createPinia } from 'pinia'

// 创建 Pinia 实例
const pinia = createPinia()

// 导出所有 store
export { default as useThemeStore } from './themeStore'
export { default as useGameStore } from './gameStore'
export { default as useUserStore } from './userStore'
export { default as useVocabularyStore } from './vocabularyStore'
export { default as useMistakeStore } from './mistakeStore'
export { default as useConfigStore } from './configStore'

// 默认导出 pinia 实例
export default pinia