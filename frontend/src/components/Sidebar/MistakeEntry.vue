<template>
  <div class="mistake-entry" @click="openMistakeTable">
    <div class="entry-icon">⚠️</div>
    <div class="entry-info">
      <div class="entry-title">错词表</div>
      <div class="entry-count">{{ mistakeCount }} 个错词</div>
    </div>
    <div class="entry-arrow">›</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMistakeStore } from '@/stores/mistakeStore'
import { eventBus } from '@/utils/eventBus'

const mistakeStore = useMistakeStore()
const mistakeCount = computed(() => mistakeStore.totalCount)

const openMistakeTable = () => {
  eventBus.emit('open-dialog', 'mistake')
}
</script>

<style scoped>
.mistake-entry {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color);
}

.mistake-entry:hover {
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

.entry-count {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
</style>