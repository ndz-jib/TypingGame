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
        <!-- 新增：显示单词表实际数量 -->
        <div class="hint" v-if="totalVocabCount > 0">
          单词表共有 <strong>{{ totalVocabCount }}</strong> 个单词
          <span v-if="localSettings.count > totalVocabCount" class="warning">
            ⚠️ 请求数量超过单词表总数，将使用全部 {{ totalVocabCount }} 个单词
          </span>
        </div>
        <div class="hint" v-else>
          <span class="warning">⚠️ 单词表为空，请先添加单词</span>
        </div>
      </div>
      
      <div class="setting-group">
        <label>卡片布局</label>
        <div class="layout-grid">
          <button 
            v-for="(layout, key) in WORD_LAYOUTS" 
            :key="key"
            class="layout-btn"
            :class="{ 
              active: localSettings.layout === key,
              'layout-disabled': !isLayoutAvailable(key)
            }"
            @click="selectLayout(key)"
            :disabled="!isLayoutAvailable(key)"
          >
            <div class="layout-preview" :data-layout="key">
              <span v-for="i in layout.cardCount" :key="i" class="preview-card"></span>
            </div>
            <span class="layout-name">{{ layout.name }}</span>
            <span class="layout-required">需 {{ layout.cardCount }} 词</span>
          </button>
        </div>
        <div class="hint" v-if="selectedLayoutRequires > effectiveWordCount">
          <span class="warning">
            当前布局需要 {{ selectedLayoutRequires }} 张卡片，但只有 {{ effectiveWordCount }} 个单词可用
          </span>
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
        <button 
          class="confirm-btn" 
          @click="confirm" 
          :disabled="!isValid"
        >
          开始游戏 ({{ effectiveWordCount }} 词)
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import { useVocabularyStore } from '@/stores/vocabularyStore'

// ==================== 常量定义 ====================

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

// ==================== Store ====================

const vocabularyStore = useVocabularyStore()

// ==================== Props & Emits ====================

const visible = defineModel()
const emit = defineEmits(['start'])

// ==================== 本地状态 ====================

const localSettings = ref({
  count: 10,
  layout: '4',
  timer: {
    enabled: false,
    duration: TIMER_OPTIONS.default
  }
})

// ==================== 计算属性 ====================

// 单词表总数量
const totalVocabCount = computed(() => vocabularyStore.totalCount)

// 有效单词数量（取用户请求和实际数量的较小值）
const effectiveWordCount = computed(() => {
  if (totalVocabCount.value === 0) return 0
  return Math.min(localSettings.value.count, totalVocabCount.value)
})

// 当前布局需要的卡片数量
const selectedLayoutRequires = computed(() => {
  const layout = WORD_LAYOUTS[localSettings.value.layout]
  return layout ? layout.cardCount : 0
})

// 检查布局是否可用（单词数 >= 布局所需卡片数）
const isLayoutAvailable = (layoutKey) => {
  const layout = WORD_LAYOUTS[layoutKey]
  if (!layout) return false
  // 如果单词表为空，所有布局都不可用
  if (totalVocabCount.value === 0) return false
  // 需要至少能凑够一次展示的卡片数
  return effectiveWordCount.value >= layout.cardCount
}

// 选择布局（带验证）
const selectLayout = (key) => {
  if (isLayoutAvailable(key)) {
    localSettings.value.layout = key
  }
}

// 整体有效性验证
const isValid = computed(() => {
  // 1. 单词表不能为空
  if (totalVocabCount.value === 0) return false
  
  // 2. 有效单词数量必须 >= 1
  if (effectiveWordCount.value < 1) return false
  
  // 3. 当前布局必须可用
  if (!isLayoutAvailable(localSettings.value.layout)) return false
  
  return true
})

// 单词数量是否有效
const isWordCountValid = computed(() => {
  return localSettings.value.count >= MIN_WORD_COUNT && 
         localSettings.value.count <= MAX_WORD_COUNT &&
         totalVocabCount.value > 0
})

// ==================== 方法 ====================

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const confirm = () => {
  if (!isValid.value) {
    if (totalVocabCount.value === 0) {
      alert('单词表为空，请先添加单词！')
      return
    }
    if (effectiveWordCount.value < selectedLayoutRequires.value) {
      alert(`当前布局需要 ${selectedLayoutRequires.value} 张卡片，但只有 ${effectiveWordCount.value} 个单词可用。\n请减少单词数量或选择更小的布局。`)
      return
    }
    alert('设置无效，请检查配置')
    return
  }
  
  // 传递有效单词数量（实际可用数量）
  const settings = {
    ...localSettings.value,
    count: effectiveWordCount.value  // 使用实际可用数量
  }
  
  emit('start', settings)
  visible.value = false
}

const cancel = () => {
  visible.value = false
}

// ==================== 监听 ====================

// 当单词表数量变化时，自动调整设置
watch(totalVocabCount, (newCount) => {
  if (newCount === 0) {
    // 单词表为空，禁用所有
    return
  }
  
  // 如果用户请求的数量超过实际数量，自动调整
  if (localSettings.value.count > newCount) {
    localSettings.value.count = newCount
  }
  
  // 检查当前布局是否可用，如果不可用则自动切换到最小可用布局
  if (!isLayoutAvailable(localSettings.value.layout)) {
    // 找到第一个可用的布局
    for (const [key, layout] of Object.entries(WORD_LAYOUTS)) {
      if (layout.cardCount <= newCount) {
        localSettings.value.layout = key
        break
      }
    }
  }
}, { immediate: true })

// 当用户调整单词数量时，检查布局是否仍然可用
watch(() => localSettings.value.count, (newCount) => {
  if (totalVocabCount.value === 0) return
  
  const effective = Math.min(newCount, totalVocabCount.value)
  if (!isLayoutAvailable(localSettings.value.layout)) {
    // 当前布局不可用，自动调整
    for (const [key, layout] of Object.entries(WORD_LAYOUTS)) {
      if (layout.cardCount <= effective) {
        localSettings.value.layout = key
        break
      }
    }
  }
})

// 弹窗打开时刷新单词表数据
watch(visible, (newVal) => {
  if (newVal) {
    vocabularyStore.fetchVocabulary()
  }
})
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

.hint {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 4px 0;
}

.hint strong {
  color: var(--text-primary);
}

.hint .warning {
  color: #ff9800;
  display: block;
  margin-top: 2px;
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
  gap: 4px;
  padding: 8px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.layout-btn.active {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.1);
}

.layout-btn.layout-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.8);
}

.layout-btn:hover:not(.layout-disabled) {
  border-color: var(--primary-color);
}

.layout-btn:disabled {
  cursor: not-allowed;
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

.layout-required {
  font-size: 9px;
  color: var(--text-secondary);
  opacity: 0.7;
}

.layout-btn.active .layout-required {
  color: var(--primary-color);
  opacity: 1;
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