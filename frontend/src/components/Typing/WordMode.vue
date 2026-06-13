<template>
  <div class="word-mode">
    <div class="cards-grid" :class="gridClass">
      <div v-for="(card, idx) in demoWords" :key="idx" class="word-card" :class="{ active: idx === 0 }">
        <div class="word-display">{{ card.word }}</div>
        <div class="word-note">📝 {{ card.note }}</div>
        <input type="text" class="word-input" :placeholder="`输入 ${card.word}...`">
      </div>
    </div>
    <div class="stats-bar">
      <div>进度: 0/{{ demoWords.length }}</div>
      <div>准确率: 100%</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  layout: { type: String, default: '4' }
})

const demoWords = ref([
  { word: 'apple', note: '苹果' },
  { word: 'banana', note: '香蕉' },
  { word: 'cherry', note: '樱桃' },
  { word: 'date', note: '枣' }
])

const gridClass = computed(() => {
  const layouts = { '1': 'grid-1x1', '2': 'grid-2x1', '3': 'grid-3x1', '4': 'grid-2x2' }
  return layouts[props.layout] || 'grid-2x2'
})
</script>

<style scoped>
.word-mode { width: 100%; height: 100%; display: flex; flex-direction: column; padding: 40px; }
.cards-grid { flex: 1; display: grid; gap: 20px; place-items: center; }
.grid-1x1 { grid-template-columns: 1fr; }
.grid-2x1 { grid-template-columns: repeat(2, 1fr); }
.grid-3x1 { grid-template-columns: repeat(3, 1fr); }
.grid-2x2 { grid-template-columns: repeat(2, 1fr); }
.word-card { background: var(--card-bg); border-radius: 12px; padding: 16px; text-align: center; min-width: 180px; }
.word-card.active { border: 2px solid var(--primary-color); transform: scale(1.02); }
.word-display { font-size: 20px; font-weight: bold; font-family: monospace; margin-bottom: 8px; }
.word-note { font-size: 11px; color: var(--text-secondary); margin-bottom: 12px; }
.word-input { width: 100%; padding: 10px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; text-align: center; }
.stats-bar { display: flex; justify-content: space-around; padding: 16px; background: var(--bg-secondary); border-radius: 12px; margin-top: 20px; }
</style>