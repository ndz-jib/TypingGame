<template>
  <div class="vocabulary-entry" @click="openVocabularyTable">
    <div class="entry-icon">📚</div>
    <div class="entry-info">
      <div class="entry-title">单词表</div>
      <div class="entry-count">{{ vocabCount }} 个单词</div>
    </div>
    <div class="entry-arrow">›</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useVocabularyStore } from '@/stores/vocabularyStore'
import { eventBus } from '@/utils/eventBus'

const vocabularyStore = useVocabularyStore()
const vocabCount = computed(() => vocabularyStore.totalCount)

const openVocabularyTable = () => {
  eventBus.emit('open-dialog', 'vocabulary')
}
</script>

<style scoped>
.vocabulary-entry {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color);
}

.vocabulary-entry:hover {
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

.entry-arrow {
  font-size: 20px;
  color: var(--text-secondary);
}
</style>