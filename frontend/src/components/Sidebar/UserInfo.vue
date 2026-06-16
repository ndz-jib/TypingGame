<template>
  <div class="user-info">
    <div class="user-header">
      <div class="avatar" @click="changeAvatar">
        <img :src="avatarUrl" alt="avatar" @error="handleAvatarError">
        <div class="avatar-overlay">📷</div>
      </div>
      <div class="user-details">
        <div class="user-name">{{ userName }}</div>
        <div class="user-points">⭐ {{ points }} 积分</div>
      </div>
    </div>
    
    <div class="theme-toggle" @click="toggleTheme">
      <span class="theme-icon">{{ isDark ? '🌙' : '☀️' }}</span>
      <span>{{ isDark ? '暗色模式' : '亮色模式' }}</span>
    </div>
    
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value">{{ totalPlayTimeFormatted }}</div>
        <div class="stat-label">总游玩时间</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ vocabCount }}</div>
        <div class="stat-label">单词本</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ mistakeCount }}</div>
        <div class="stat-label">错词本</div>
      </div>
    </div>
    
    <div class="mode-stats">
      <div class="mode-stat">
        <div class="mode-name">📝 单词模式</div>
        <div class="mode-data">
          <span>最佳: {{ wordBestWPM }} WPM</span>
          <span>准确: {{ (wordAvgAccuracy * 100).toFixed(1) }}%</span>
        </div>
      </div>
      <div class="mode-stat">
        <div class="mode-name">📖 文章模式</div>
        <div class="mode-data">
          <span>最佳: {{ articleBestWPM }} WPM</span>
          <span>准确: {{ (articleAvgAccuracy * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { useThemeStore } from '@/stores/themeStore'
import { useVocabularyStore } from '@/stores/vocabularyStore'
import { useMistakeStore } from '@/stores/mistakeStore'
import { api } from '@/services/api'

const userStore = useUserStore()
const themeStore = useThemeStore()
const vocabularyStore = useVocabularyStore()
const mistakeStore = useMistakeStore()

// 使用新的静态资源 URL
const avatarUrl = ref(api.getStaticUrlWithTimestamp('picture/avatar.png'))
const userName = computed(() => userStore.name)
const points = computed(() => userStore.points.toFixed(1))
const totalPlayTime = computed(() => userStore.totalPlayTime)
const totalPlayTimeFormatted = computed(() => {
  const hours = Math.floor(totalPlayTime.value / 3600)
  const minutes = Math.floor((totalPlayTime.value % 3600) / 60)
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
})

const vocabCount = computed(() => vocabularyStore.totalCount)
const mistakeCount = computed(() => mistakeStore.totalCount)

const wordBestWPM = computed(() => userStore.wordModeStats.bestWPM)
const wordAvgAccuracy = computed(() => userStore.wordModeStats.avgAccuracy)
const articleBestWPM = computed(() => userStore.articleModeStats.bestWPM)
const articleAvgAccuracy = computed(() => userStore.articleModeStats.avgAccuracy)

const isDark = computed(() => themeStore.theme === 'dark')

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const changeAvatar = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await api.uploadFile('/upload/avatar', file)
    if (res.code === 200) {
      // 刷新头像（添加时间戳强制刷新缓存）
      avatarUrl.value = api.getStaticUrlWithTimestamp('picture/avatar.png')
    }
  }
  input.click()
}

const handleAvatarError = () => {
  // 头像加载失败时显示默认头像（使用 base64 避免网络请求）
  avatarUrl.value = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Ccircle cx="50" cy="50" r="50" fill="%23333"/%3E%3Ctext x="50" y="67" text-anchor="middle" fill="%23fff" font-size="40"%3E?%3C/text%3E%3C/svg%3E'
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  await vocabularyStore.fetchVocabulary()
  await mistakeStore.fetchMistakeList()
})
</script>

<style scoped>
/* 样式保持不变 */
.user-info {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 20px;
}

.avatar:hover .avatar-overlay {
  opacity: 1;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
}

.user-points {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 16px;
  transition: background 0.2s;
}

.theme-toggle:hover {
  background: var(--card-hover);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.mode-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mode-stat {
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.mode-name {
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 6px;
}

.mode-data {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>