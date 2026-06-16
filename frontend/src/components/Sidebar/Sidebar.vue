<template>
  <div>
    <div class="sidebar-toggle" @click="toggleSidebar">
      <span class="toggle-icon">{{ isOpen ? '✕' : '☰' }}</span>
    </div>
    
    <transition name="fade">
      <div v-if="isOpen" class="sidebar-mask" @click="closeSidebar"></div>
    </transition>
    
    <transition name="slide">
      <aside v-if="isOpen" class="sidebar">
        <SidebarHeader @close="closeSidebar" />
        <div class="sidebar-content">
          <TypingEntry />
          <UserInfo />
          <VocabularyEntry />
          <MistakeEntry />
          <SettingsEntry />
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SidebarHeader from './SidebarHeader.vue'
import TypingEntry from './TypingEntry.vue'
import UserInfo from './UserInfo.vue'
import VocabularyEntry from './VocabularyEntry.vue'
import MistakeEntry from './MistakeEntry.vue'
import SettingsEntry from './SettingsEntry.vue'

const isOpen = ref(false)

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const closeSidebar = () => {
  isOpen.value = false
}

// 暴露方法给父组件
defineExpose({ closeSidebar })
</script>

<style scoped>
.sidebar-toggle {
  position: fixed;
  left: 20px;
  top: 20px;
  width: 40px;
  height: 40px;
  background: var(--bg-secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1001;
  box-shadow: var(--shadow);
}

.sidebar-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 320px;
  height: 100vh;
  background: var(--bg-sidebar);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow);
  z-index: 1001;
  overflow-y: auto;
}

.sidebar-content {
  padding: 0 0 20px 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}
</style>