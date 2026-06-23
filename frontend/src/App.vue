<template>
  <div class="app" :data-theme="themeStore.theme">
    <Sidebar ref="sidebarRef" />
    
    <main class="main-content">
      <TypingArea v-if="gameStore.isPlaying" />
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Sidebar from '@/components/Sidebar/Sidebar.vue'
import TypingArea from '@/components/Typing/TypingArea.vue'
import VocabularyTable from '@/components/Dialogs/VocabularyTable.vue'
import MistakeTable from '@/components/Dialogs/MistakeTable.vue'
import SettingsPanel from '@/components/Dialogs/SettingsPanel.vue'
import Toast from '@/components/Common/Toast.vue'
import { useThemeStore } from '@/stores/themeStore'
import { useGameStore } from '@/stores/gameStore'
import { useConfigStore } from '@/stores/configStore'
import { useUserStore } from '@/stores/userStore'
import { useVocabularyStore } from '@/stores/vocabularyStore'
import { useMistakeStore } from '@/stores/mistakeStore'
import { eventBus } from '@/utils/eventBus'

const themeStore = useThemeStore()
const gameStore = useGameStore()
const configStore = useConfigStore()
const userStore = useUserStore()
const vocabularyStore = useVocabularyStore()
const mistakeStore = useMistakeStore()

const sidebarRef = ref(null)
const showVocabulary = ref(false)
const showMistake = ref(false)
const showSettings = ref(false)
const toastRef = ref(null)

const handleOpenDialog = (dialogName) => {
  switch (dialogName) {
    case 'vocabulary':
      showVocabulary.value = true
      break
    case 'mistake':
      showMistake.value = true
      break
    case 'settings':
      showSettings.value = true
      break
  }
}

const handleStartGame = ({ mode, settings }) => {
  // 开始游戏时自动收起折叠栏
  if (sidebarRef.value) {
    sidebarRef.value.closeSidebar()
  }
  gameStore.startGame(mode, settings)
}

const handleBeforeUnload = (e) => {
  if (gameStore.isPlaying) {
    gameStore.$reset()
  }
}

onMounted(async () => {
  themeStore.initTheme()
  await configStore.fetchConfig()
  await userStore.fetchUserInfo()
  await vocabularyStore.fetchVocabulary()
  await mistakeStore.fetchMistakeList()
  
  eventBus.on('open-dialog', handleOpenDialog)
  eventBus.on('start-game', handleStartGame)
  
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  eventBus.off('open-dialog', handleOpenDialog)
  eventBus.off('start-game', handleStartGame)
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
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