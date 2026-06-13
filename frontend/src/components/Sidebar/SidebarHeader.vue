<template>
  <div class="sidebar-header">
    <div class="logo">
      <span class="logo-icon">⌨️</span>
      <span class="logo-text">打字游戏</span>
    </div>
    <div class="close-btn" @click="closeSidebar">
      <span>✕</span>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['close'])

const closeSidebar = () => {
  emit('close')
}
</script>

<style scoped>
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-sidebar);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, var(--primary-color), #4caf50);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--card-hover);
}

.close-btn span {
  font-size: 18px;
  color: var(--text-secondary);
}
</style>