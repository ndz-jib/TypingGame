<template>
  <div class="article-mode">
    <div class="article-container">
      <div class="lines-wrapper">
        <div v-for="(line, idx) in demoLines" :key="idx" class="line-item" :class="{ current: idx === 0 }">
          <div class="line-number">{{ idx + 1 }}</div>
          <div class="line-content-area">
            <div class="line-text">{{ line.text }}</div>
            <div class="line-input-area">
              <input type="text" class="line-input" placeholder="在此输入...">
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="stats-bar">
      <div>进度: 0/{{ totalChars }}</div>
      <div>准确率: 100%</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const demoLines = ref([
  { text: 'The quick brown fox jumps over the lazy dog.' },
  { text: 'Typing games help improve your typing speed.' },
  { text: 'Practice makes perfect.' }
])

const totalChars = computed(() => {
  return demoLines.value.reduce((sum, line) => sum + line.text.length, 0)
})
</script>

<style scoped>
.article-mode { width: 100%; height: 100%; display: flex; flex-direction: column; background: var(--bg-primary); }
.article-container { flex: 1; overflow-y: auto; padding: 20px; }
.lines-wrapper { display: flex; flex-direction: column; gap: 20px; align-items: center; min-height: 100%; }
.line-item { display: flex; align-items: center; width: 100%; max-width: 900px; margin: 0 auto; padding: 16px 20px; border-radius: 12px; }
.line-item.current { background: rgba(33, 150, 243, 0.15); border-left: 3px solid var(--primary-color); }
.line-number { width: 50px; font-size: 14px; color: var(--text-secondary); font-family: monospace; text-align: center; margin-right: 20px; }
.line-content-area { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.line-text { font-family: 'Courier New', monospace; font-size: 18px; line-height: 1.5; text-align: center; }
.line-input { width: 80%; max-width: 500px; padding: 10px 16px; background: var(--bg-secondary); border: 2px solid var(--primary-color); border-radius: 10px; text-align: center; }
.stats-bar { display: flex; justify-content: space-around; padding: 12px; background: var(--bg-secondary); border-top: 1px solid var(--border-color); }
</style>