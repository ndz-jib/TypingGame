<template>
  <div class="settings-entry" @click="openSettings">
    <div class="entry-icon">⚙️</div>
    <div class="entry-info">
      <div class="entry-title">设置</div>
      <div class="entry-desc">主题、音效、数据管理</div>
    </div>
    <div class="entry-arrow">›</div>
  </div>
</template>

<script setup>
const openSettings = () => {
  if (window.__APP__) window.__APP__.openSettings()
}
</script>

<style scoped>
.settings-entry {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color);
}
.settings-entry:hover {
  background: var(--card-hover);
}
.entry-icon {
  font-size: 24px;
  margin-right: 12px;
}
.entry-info {
  flex: 1;
}
.entry-title {
  font-size: 16px;
  font-weight: 500;
}
.entry-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
</style>