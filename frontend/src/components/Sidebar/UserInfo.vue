<template>
  <div class="user-info">
    <div class="user-header">
      <div class="avatar" @click="changeAvatar">
        <img :src="avatarUrl" alt="avatar">
        <div class="avatar-overlay">📷</div>
      </div>
      <div class="user-details">
        <div class="user-name">Demo User</div>
        <div class="user-points">⭐ 1250 积分</div>
      </div>
    </div>
    
    <div class="theme-toggle" @click="toggleTheme">
      <span class="theme-icon">{{ isDark ? '🌙' : '☀️' }}</span>
      <span>{{ isDark ? '暗色模式' : '亮色模式' }}</span>
    </div>
    
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value">2h 30m</div>
        <div class="stat-label">总游玩时间</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">48</div>
        <div class="stat-label">单词本</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">12</div>
        <div class="stat-label">错词本</div>
      </div>
    </div>
    
    <div class="mode-stats">
      <div class="mode-stat">
        <div class="mode-name">📝 单词模式</div>
        <div class="mode-data">
          <span>最佳: 65 WPM</span>
          <span>准确: 94.2%</span>
        </div>
      </div>
      <div class="mode-stat">
        <div class="mode-name">📖 文章模式</div>
        <div class="mode-data">
          <span>最佳: 58 WPM</span>
          <span>准确: 91.5%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const avatarUrl = ref('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Ccircle cx="50" cy="50" r="50" fill="%23333"/%3E%3Ctext x="50" y="67" text-anchor="middle" fill="%23fff" font-size="40"%3E?%3C/text%3E%3C/svg%3E')
const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  if (window.__APP__) window.__APP__.currentTheme = theme
}

const changeAvatar = () => {
  alert('更换头像功能演示')
}
</script>

<style scoped>
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