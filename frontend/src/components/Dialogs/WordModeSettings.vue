<template>
  <Modal v-model="visible" title="单词模式设置" width="450px">
    <div class="word-settings">
      <div class="setting-group">
        <label>单词数量</label>
        <div class="setting-control">
          <input 
            type="range" 
            v-model.number="localSettings.count"
            :min="MIN_WORD_COUNT"
            :max="MAX_WORD_COUNT"
            step="1"
          >
          <span class="value">{{ localSettings.count }}</span>
        </div>
      </div>
      
      <div class="setting-group">
        <label>卡片布局</label>
        <div class="layout-grid">
          <button 
            v-for="(layout, key) in WORD_LAYOUTS" 
            :key="key"
            class="layout-btn"
            :class="{ active: localSettings.layout === key }"
            @click="localSettings.layout = key"
          >
            <div class="layout-preview" :data-layout="key">
              <span v-for="i in layout.cardCount" :key="i" class="preview-card"></span>
            </div>
            <span class="layout-name">{{ layout.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="setting-group">
        <label>
          <input type="checkbox" v-model="localSettings.timer.enabled">
          启用倒计时
        </label>
        <div v-if="localSettings.timer.enabled" class="timer-setting">
          <input 
            type="range" 
            v-model.number="localSettings.timer.duration"
            :min="TIMER_OPTIONS.min"
            :max="TIMER_OPTIONS.max"
            :step="TIMER_OPTIONS.step"
          >
          <span class="value">{{ formatTime(localSettings.timer.duration) }}</span>
        </div>
      </div>
      
      <div class="dialog-actions">
        <button class="cancel-btn" @click="cancel">取消</button>
        <button class="confirm-btn" @click="confirm" :disabled="!isWordCountValid">
          开始游戏
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue'
import Modal from '@/components/Common/Modal.vue'

// 常量定义
const WORD_LAYOUTS = {
  '1': { name: '1x1', cardCount: 1 },
  '2': { name: '2x1', cardCount: 2 },
  '3': { name: '3x1', cardCount: 3 },
  '4': { name: '2x2', cardCount: 4 },
  '5': { name: '2x2+1', cardCount: 5 },
  '6': { name: '2x3', cardCount: 6 },
  '7': { name: '3+4', cardCount: 7 },
  '8': { name: '2x4', cardCount: 8 },
  '9': { name: '3x3', cardCount: 9 }
}

const TIMER_OPTIONS = {
  min: 30,
  max: 300,
  step: 30,
  default: 120
}

const MIN_WORD_COUNT = 1
const MAX_WORD_COUNT = 100

// 使用 defineModel 需要 Vue 3.3+
// 如果不支持，改用 props + emit
const visible = defineModel()

const emit = defineEmits(['start'])

const localSettings = ref({
  count: 10,
  layout: '4',
  timer: {
    enabled: false,
    duration: TIMER_OPTIONS.default
  }
})

// 计算属性：单词数量是否有效
const isWordCountValid = computed(() => {
  return localSettings.value.count >= MIN_WORD_COUNT && localSettings.value.count <= MAX_WORD_COUNT
})

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const confirm = () => {
  if (!isWordCountValid.value) {
    alert(`单词数量必须在 ${MIN_WORD_COUNT} 到 ${MAX_WORD_COUNT} 之间`)
    return
  }
  emit('start', { ...localSettings.value })
  visible.value = false
}

const cancel = () => {
  visible.value = false
}
</script>

<style scoped>
.word-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-control input[type="range"] {
  flex: 1;
}

.value {
  min-width: 40px;
  text-align: center;
  color: var(--primary-color);
  font-weight: bold;
}

.layout-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.layout-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.layout-btn.active {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.1);
}

.layout-preview {
  display: grid;
  gap: 3px;
  background: var(--card-bg);
  padding: 6px;
  border-radius: 4px;
  width: 60px;
  height: 45px;
}

.layout-preview[data-layout="1"] {
  grid-template-columns: 1fr;
  place-items: center;
}
.layout-preview[data-layout="1"] .preview-card {
  width: 30px;
}

.layout-preview[data-layout="2"],
.layout-preview[data-layout="3"] {
  grid-template-columns: repeat(2, 1fr);
}
.layout-preview[data-layout="3"] {
  grid-template-columns: repeat(3, 1fr);
}
.layout-preview[data-layout="4"],
.layout-preview[data-layout="5"],
.layout-preview[data-layout="6"] {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
}
.layout-preview[data-layout="6"] {
  grid-template-columns: repeat(3, 1fr);
}
.layout-preview[data-layout="7"] {
  grid-template-columns: repeat(4, 1fr);
}
.layout-preview[data-layout="8"] {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 1fr);
}
.layout-preview[data-layout="9"] {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
}

.preview-card {
  background: var(--primary-color);
  border-radius: 2px;
  opacity: 0.6;
}

.layout-btn.active .preview-card {
  opacity: 1;
}

.layout-name {
  font-size: 11px;
  color: var(--text-secondary);
}

.timer-setting {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  padding-left: 20px;
}

.timer-setting input {
  flex: 1;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.cancel-btn {
  padding: 8px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>