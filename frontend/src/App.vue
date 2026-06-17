<template>
  <div class="app" :data-theme="currentTheme">
    <Sidebar ref="sidebarRef" />
    
    <main class="main-content">
      <TypingArea v-if="isPlaying" />
      <div v-else class="welcome">
        <h1>打字游戏</h1>
        <p>请从左侧菜单选择模式开始</p>
        <div class="shortcuts">
          <span>单词模式</span>
          <span>文章模式</span>
          <span>自定义设置</span>
        </div>
      </div>
    </main>
    
    <VocabularyTable v-model="showVocabulary" />
    <MistakeTable v-model="showMistake" />
    <SettingsPanel v-model="showSettings" />
    
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/Sidebar/Sidebar.vue'
import TypingArea from '@/components/Typing/TypingArea.vue'
import VocabularyTable from '@/components/Dialogs/VocabularyTable.vue'
import MistakeTable from '@/components/Dialogs/MistakeTable.vue'
import SettingsPanel from '@/components/Dialogs/SettingsPanel.vue'
import Toast from '@/components/Common/Toast.vue'

const sidebarRef = ref(null)
const showVocabulary = ref(false)
const showMistake = ref(false)
const showSettings = ref(false)
const toastRef = ref(null)
const isPlaying = ref(false)
const currentTheme = ref('light')

// 模拟接收开始游戏事件
const handleStartGame = () => {
  isPlaying.value = true
  if (sidebarRef.value) {
    sidebarRef.value.closeSidebar()
  }
}

// 暴露给子组件使用（通过 provide 或 eventBus 简化，这里直接挂载到 window 用于演示）
window.__APP__ = {
  startGame: handleStartGame,
  openVocabulary: () => { showVocabulary.value = true },
  openMistake: () => { showMistake.value = true },
  openSettings: () => { showSettings.value = true },
  showToast: (msg, type) => { toastRef.value?.show(msg, 2000, type) }
}
</script>

<style>
@import './assets/styles/main.css';

.app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome {
  text-align: center;
  animation: fadeIn 0.5s ease;
}

.welcome h1 {
  font-size: 48px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, var(--primary-color), #4caf50);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.welcome p {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.shortcuts {
  display: flex;
  gap: 24px;
  justify-content: center;
}

.shortcuts span {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-radius: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>