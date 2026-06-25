<template>
  <div class="word-mode">
    <div v-if="wordCards.length === 0" class="empty-state">
      <div class="empty-text">没有足够的单词</div>
      <div class="empty-hint">请返回设置调整单词数量或布局</div>
    </div>
    
    <div v-else class="cards-grid" :class="gridClass">
      <WordCard
        v-for="(card, idx) in wordCards"
        :key="card.id"
        :word="card.word"
        :note="card.note"
        :is-active="idx === activeCardIndex && !card.isCompleted"
        :is-completed="card.isCompleted"
        @complete="(result) => onCardComplete(card.id, idx, result)"
        @error="(info) => onCardError(info)"
      />
    </div>
    
    <div class="stats-bar">
      <div>进度: {{ completedCount }}/{{ totalWords }}</div>
      <div>提交准确率: {{ (accuracy * 100).toFixed(1) }}%</div>
      <div v-if="timerEnabled">剩余: {{ formatTime(timeRemaining) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import WordCard from './WordCard.vue'
import { audioService } from '@/services/audioService'
import { useConfigStore } from '@/stores/configStore'

const props = defineProps({
  wordCards: { type: Array, required: true },
  totalWords: { type: Number, required: true },
  completedCount: { type: Number, required: true },
  accuracy: { type: Number, default: 1 },
  layout: { type: String, default: '4' },
  timerEnabled: { type: Boolean, default: false },
  timeRemaining: { type: Number, default: 0 }
})

const emit = defineEmits(['word-complete', 'word-error', 'need-next-word'])

const configStore = useConfigStore()
const activeCardIndex = ref(0)

const gridClass = computed(() => {
  const layouts = {
    '1': 'grid-1x1', '2': 'grid-2x1', '3': 'grid-3x1',
    '4': 'grid-2x2', '5': 'grid-2x2-plus-1', '6': 'grid-2x3',
    '7': 'grid-3-plus-4', '8': 'grid-2x4', '9': 'grid-3x3'
  }
  return layouts[props.layout] || 'grid-2x2'
})

const onCardComplete = (cardId, index, result) => {
  if (result.isCorrect && configStore.soundEnabled) {
    audioService.playComplete()
  }
  
  emit('word-complete', { cardId, ...result })
  emit('need-next-word', { index })
  
  const nextIndex = findNextActiveIndex()
  activeCardIndex.value = nextIndex
}

const onCardError = (info) => {
  emit('word-error', info)
}

const findNextActiveIndex = () => {
  for (let i = activeCardIndex.value + 1; i < props.wordCards.length; i++) {
    if (!props.wordCards[i].isCompleted) return i
  }
  for (let i = 0; i < activeCardIndex.value; i++) {
    if (!props.wordCards[i].isCompleted) return i
  }
  return -1
}

// 聚焦第一个输入框的方法
const focusFirstInput = () => {
  nextTick(() => {
    // 方法1：通过 DOM 查询
    const input = document.querySelector('.word-card.active input') ||
                  document.querySelector('.word-card:not(.completed) input')
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 监听 wordCards 变化，更新活动索引
watch(() => props.wordCards, (newCards) => {
  if (newCards.length === 0) return
  
  if (newCards[activeCardIndex.value]?.isCompleted) {
    const nextIndex = findNextActiveIndex()
    activeCardIndex.value = nextIndex >= 0 ? nextIndex : 0
  }
  
  const allCompleted = newCards.every(c => c.isCompleted)
  if (allCompleted) {
    activeCardIndex.value = -1
  }
}, { deep: true, immediate: true })

// 暴露方法给父组件
defineExpose({
  focusFirstInput
})
</script>

<style scoped>
.word-mode {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 40px;
}

.cards-grid {
  flex: 1;
  display: grid;
  gap: 20px;
  place-items: center;
}

.grid-1x1 { grid-template-columns: 1fr; place-items: center; }
.grid-1x1 .word-card { width: 300px; }
.grid-2x1 { grid-template-columns: repeat(2, 1fr); }
.grid-2x1 .word-card { width: 250px; }
.grid-3x1 { grid-template-columns: repeat(3, 1fr); }
.grid-3x1 .word-card { width: 200px; }
.grid-2x2 { grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, auto); }
.grid-2x2-plus-1 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto auto;
}
.grid-2x2-plus-1 .word-card:last-child {
  grid-column: span 2;
  justify-self: center;
  width: 250px;
}
.grid-2x3 { grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(2, auto); }
.grid-3-plus-4 {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto;
}
.grid-3-plus-4 .word-card:nth-child(1),
.grid-3-plus-4 .word-card:nth-child(2),
.grid-3-plus-4 .word-card:nth-child(3) { grid-row: 1; }
.grid-3-plus-4 .word-card:nth-child(4),
.grid-3-plus-4 .word-card:nth-child(5),
.grid-3-plus-4 .word-card:nth-child(6),
.grid-3-plus-4 .word-card:nth-child(7) { grid-row: 2; }
.grid-2x4 { grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(2, auto); }
.grid-3x3 { grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, auto); }

.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  margin-top: 20px;
  font-size: 14px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.6;
}

.empty-text {
  font-size: 18px;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 14px;
  color: var(--text-secondary);
  opacity: 0.7;
}
</style>