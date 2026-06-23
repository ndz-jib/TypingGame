<template>
  <div class="typing-entry">
    <h3 class="section-title">🎮 打字入口</h3>
    
    <div class="mode-section">
      <div class="mode-header" @click="toggleWordMode">
        <span class="mode-title">📝 单词模式</span>
        <span class="toggle-icon">{{ wordModeExpanded ? '▼' : '▶' }}</span>
      </div>
      <div v-show="wordModeExpanded" class="mode-settings">
        <button class="start-btn" @click="openWordSettings">开始单词模式</button>
      </div>
    </div>
    
    <div class="mode-section">
      <div class="mode-header" @click="toggleArticleMode">
        <span class="mode-title">📖 文章模式</span>
        <span class="toggle-icon">{{ articleModeExpanded ? '▼' : '▶' }}</span>
      </div>
      <div v-show="articleModeExpanded" class="mode-settings">
        <button class="start-btn" @click="openArticleSettings">开始文章模式</button>
      </div>
    </div>
    
    <WordModeSettings v-model="showWordSettings" @start="startWordMode" />
    <ArticleModeSettings v-model="showArticleSettings" @start="startArticleMode" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import { eventBus } from '@/utils/eventBus'
import WordModeSettings from '@/components/Dialogs/WordModeSettings.vue'
import ArticleModeSettings from '@/components/Dialogs/ArticleModeSettings.vue'

const gameStore = useGameStore()

const wordModeExpanded = ref(true)
const articleModeExpanded = ref(false)
const showWordSettings = ref(false)
const showArticleSettings = ref(false)

const openWordSettings = () => showWordSettings.value = true
const openArticleSettings = () => showArticleSettings.value = true

const startWordMode = (settings) => {
  gameStore.startGame('word', settings)
  eventBus.emit('start-game', { mode: 'word', settings })
}

const startArticleMode = (settings) => {
  gameStore.startGame('article', settings)
  eventBus.emit('start-game', { mode: 'article', settings })
}

const toggleWordMode = () => wordModeExpanded.value = !wordModeExpanded.value
const toggleArticleMode = () => articleModeExpanded.value = !articleModeExpanded.value
</script>

<style scoped>
.typing-entry { padding: 16px; border-bottom: 1px solid var(--border-color); }
.section-title { font-size: 16px; margin-bottom: 16px; }
.mode-section { margin-bottom: 16px; }
.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  cursor: pointer;
}
.mode-title { font-size: 15px; font-weight: 500; }
.toggle-icon { color: var(--text-secondary); font-size: 12px; }
.mode-settings { padding: 12px 0; }
.start-btn {
  width: 100%;
  padding: 10px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.start-btn:hover { opacity: 0.9; }
</style>