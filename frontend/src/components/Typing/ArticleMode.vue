<template>
  <div class="article-mode">
    <div class="article-container" ref="containerRef">
      <div class="lines-wrapper">
        <div
          v-for="line in visibleLines"
          :key="`line_${line.index}`"
          class="line-item"
          :class="{
            completed: line.type === 'completed',
            pending: line.type === 'pending',
            current: line.type === 'current',
            new: line.type === 'new'
          }"
          :data-line-index="line.index"
        >
          <div class="line-number">{{ line.index + 1 }}</div>
          
          <div class="line-content-area">
            <div class="line-text">
              <span 
                v-for="(unit, unitIdx) in parseUnits(line.text, line.userInput || '')"
                :key="`unit_${unitIdx}`"
                :class="getUnitClass(unit)"
              >
                <template v-if="unit.type === 'word'">
                  <span 
                    v-for="(char, charIdx) in unit.text.split('')" 
                    :key="`char_${unitIdx}_${charIdx}`"
                    class="word-char"
                    :class="getWordCharClass(unit, charIdx)"
                  >
                    {{ char }}
                  </span>
                </template>
                <template v-else>
                  {{ unit.displayChar }}
                </template>
              </span>
            </div>
            
            <div v-if="line.type === 'pending' || line.type === 'current'" class="line-input-area">
              <input
                v-if="line.type === 'current'"
                :ref="el => setCurrentInputRef(el)"
                v-model="currentInputValue"
                type="text"
                class="line-input"
                :class="{ error: hasCurrentError }"
                :placeholder="'在此输入...'"
                @input="onCurrentInput"
                @keydown="onKeyDown"
                @keyup="onKeyUp"
                @keydown.up="onMoveUp"
                @keydown.down="onMoveDown"
              >
              <input
                v-else
                :ref="el => setPendingInputRef(el)"
                v-model="pendingInputValue"
                type="text"
                class="line-input pending-input"
                :class="{ error: hasPendingError }"
                :placeholder="'修改后按下方向键返回...'"
                @input="onPendingInput"
                @keydown.up="onMoveUpFromPending"
                @keydown.down="onMoveDownFromPending"
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="stats-bar">
      <div>进度: {{ stats.completed || 0 }}/{{ stats.total || 0 }} 字符</div>
      <div>准确率: {{ ((stats.accuracy || 0) * 100).toFixed(1) }}%</div>
      <div>效率: {{ (stats.efficiency || 0).toFixed(1) }} 字符/10s</div>
      <div v-if="timerEnabled">剩余: {{ formatTime(timeRemaining) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { audioService } from '@/services/audioService'
import { useConfigStore } from '@/stores/configStore'

const SPECIAL_CHARS = { space: '·', newline: '¶' }

const props = defineProps({
  articleLines: { type: Array, default: () => [] },
  articleLineInputs: { type: Array, default: () => [] },
  currentLineIndex: { type: Number, default: 0 },
  displayLines: { type: Number, default: 4 },
  stats: { type: Object, default: () => ({}) },
  timerEnabled: { type: Boolean, default: false },
  timeRemaining: { type: Number, default: 0 }
})

const emit = defineEmits(['update-line', 'complete-line', 'force-move', 'move-to-line', 'word-error', 'char-error'])

const configStore = useConfigStore()
const containerRef = ref(null)
let currentInputRef = null
let pendingInputRef = null

// 用户主动设置的待完成行索引（按上方向键时设置）
const userPendingLineIndex = ref(-1)

const setCurrentInputRef = (el) => {
  currentInputRef = el
}

const setPendingInputRef = (el) => {
  pendingInputRef = el
}

const currentInputValue = ref('')
const hasCurrentError = ref(false)

const pendingInputValue = ref('')
const hasPendingError = ref(false)

// 判断一行是否为待完成栏（不匹配的输入）
const isLinePending = (index) => {
  if (index >= props.currentLineIndex) return false
  const input = props.articleLineInputs[index] || ''
  const text = props.articleLines[index] || ''
  if (input.length === 0) return false
  return input.length === text.length && input !== text
}

// 计算可见行
const visibleLines = computed(() => {
  if (!props.articleLines || !Array.isArray(props.articleLines) || props.articleLines.length === 0) {
    return []
  }
  
  const lines = []
  const currentIdx = props.currentLineIndex
  const userPendingIdx = userPendingLineIndex.value
  
  // 找到当前应该显示的待完成栏索引（最多一个）
  let activePendingIdx = -1
  if (userPendingIdx >= 0) {
    activePendingIdx = userPendingIdx
  } else {
    // 没有用户主动设置的待完成行时，查找当前行上方最近的一个不匹配行
    for (let i = currentIdx - 1; i >= 0; i--) {
      if (isLinePending(i)) {
        activePendingIdx = i
        break
      }
    }
  }
  
  const half = Math.floor(props.displayLines / 2)
  let start = Math.max(0, currentIdx - half)
  let end = Math.min(props.articleLines.length, start + props.displayLines)
  
  if (end - start < props.displayLines && start > 0) {
    start = Math.max(0, end - props.displayLines)
  }
  
  for (let i = start; i < end; i++) {
    let type = 'new'
    let userInput = ''
    
    if (i === currentIdx) {
      type = 'current'
      userInput = currentInputValue.value
    } else if (i === activePendingIdx && activePendingIdx >= 0) {
      type = 'pending'
      userInput = i === userPendingIdx ? pendingInputValue.value : (props.articleLineInputs[i] || '')
    } else if (i < currentIdx) {
      type = 'completed'
      userInput = props.articleLineInputs[i] || ''
    } else {
      type = 'new'
      userInput = ''
    }
    
    lines.push({
      index: i,
      text: props.articleLines[i] || '',
      userInput,
      type
    })
  }
  
  return lines
})

// 解析文本为单元
const parseUnits = (text, input) => {
  const units = []
  let i = 0
  let currentWord = ''
  
  while (i < text.length) {
    const char = text[i]
    const isLetter = /[a-zA-Z]/.test(char)
    
    if (isLetter) {
      currentWord += char
    } else {
      if (currentWord) {
        units.push({ type: 'word', text: currentWord, userInput: '', isCompleted: false, hasError: false, errorTriggered: false })
        currentWord = ''
      }
      let displayChar = char
      if (char === ' ') displayChar = SPECIAL_CHARS.space
      if (char === '\n') displayChar = SPECIAL_CHARS.newline
      units.push({ type: 'char', text: char, displayChar, userInput: '', isCompleted: false, hasError: false })
    }
    i++
  }
  
  if (currentWord) {
    units.push({ type: 'word', text: currentWord, userInput: '', isCompleted: false, hasError: false, errorTriggered: false })
  }
  
  let inputOffset = 0
  for (const unit of units) {
    if (unit.type === 'word') {
      const wordInput = input.slice(inputOffset, inputOffset + unit.text.length)
      unit.userInput = wordInput
      unit.isCompleted = wordInput === unit.text
      
      unit.hasError = false
      if (!unit.isCompleted && wordInput.length > 0) {
        for (let j = 0; j < wordInput.length; j++) {
          if (wordInput[j] !== unit.text[j]) {
            unit.hasError = true
            break
          }
        }
      }
      inputOffset += unit.text.length
    } else {
      const charInput = input[inputOffset]
      unit.userInput = charInput || ''
      unit.isCompleted = charInput === unit.text
      unit.hasError = !unit.isCompleted && charInput !== undefined && charInput !== ''
      inputOffset += 1
    }
  }
  
  return units
}

const getUnitClass = (unit) => {
  if (unit.type === 'word') {
    if (unit.isCompleted) return 'word-unit word-completed'
    if (unit.hasError) return 'word-unit word-error'
    return 'word-unit'
  } else {
    if (unit.isCompleted) return 'char-unit char-correct'
    if (unit.hasError) return 'char-unit char-error'
    return 'char-unit'
  }
}

const getWordCharClass = (unit, charIdx) => {
  if (unit.isCompleted) return 'correct'
  if (unit.userInput.length > charIdx) {
    if (unit.userInput[charIdx] === unit.text[charIdx]) return 'correct'
    return 'incorrect'
  }
  return ''
}

const hasMismatch = (input, target) => {
  if (input.length === 0) return false
  for (let i = 0; i < input.length; i++) {
    if (i >= target.length || input[i] !== target[i]) return true
  }
  return false
}

const focusCurrentInput = () => {
  nextTick(() => {
    if (currentInputRef && typeof currentInputRef.focus === 'function') {
      currentInputRef.focus()
      currentInputRef.setSelectionRange(currentInputValue.value.length, currentInputValue.value.length)
    }
  })
}

const focusPendingInput = () => {
  nextTick(() => {
    if (pendingInputRef && typeof pendingInputRef.focus === 'function') {
      pendingInputRef.focus()
      pendingInputRef.setSelectionRange(pendingInputValue.value.length, pendingInputValue.value.length)
    }
  })
}

const clearUserPendingState = () => {
  userPendingLineIndex.value = -1
  pendingInputValue.value = ''
  hasPendingError.value = false
}

// ==================== 按键音效 ====================
const onKeyDown = () => {
  if (configStore.soundEnabled) {
    audioService.startKeypress()
  }
}

const onKeyUp = () => {
  if (configStore.soundEnabled) {
    audioService.stopKeypress()
  }
}

// ==================== 当前行输入 ====================
const onCurrentInput = () => {
  const currentText = props.articleLines[props.currentLineIndex]
  if (!currentText) return
  
  if (currentInputValue.value.length > currentText.length) {
    currentInputValue.value = currentInputValue.value.slice(0, currentText.length)
  }
  
  const hasMismatchError = hasMismatch(currentInputValue.value, currentText)
  hasCurrentError.value = hasMismatchError
  
  if (hasMismatchError && currentInputValue.value.length > 0) {
    for (let i = 0; i < currentInputValue.value.length; i++) {
      if (i >= currentText.length || currentInputValue.value[i] !== currentText[i]) {
        if (configStore.soundEnabled) {
          audioService.playError()
        }
        emit('char-error', { char: currentInputValue.value[i] || '?', input: currentInputValue.value })
        break
      }
    }
  }
  
  emit('update-line', { lineIndex: props.currentLineIndex, input: currentInputValue.value })
  
  // 输入长度等于目标长度时，强制换行
  if (currentInputValue.value.length === currentText.length) {
    // 停止按键音效
    audioService.stopKeypressImmediately()
    
    if (currentInputValue.value === currentText) {
      // 完全匹配：直接变成完成栏
      if (configStore.soundEnabled) {
        audioService.playComplete()
      }
      emit('complete-line')
    } else {
      // 不匹配：当前行变成待完成栏，移动到下一行
      if (configStore.soundEnabled) {
        audioService.playComplete()
      }
      emit('force-move')
    }
  }
}

// ==================== 待完成行输入（禁用自动换行） ====================
const onPendingInput = () => {
  const pendingIdx = userPendingLineIndex.value
  if (pendingIdx < 0) return
  
  const pendingText = props.articleLines[pendingIdx]
  if (!pendingText) return
  
  if (pendingInputValue.value.length > pendingText.length) {
    pendingInputValue.value = pendingInputValue.value.slice(0, pendingText.length)
  }
  
  const hasMismatchError = hasMismatch(pendingInputValue.value, pendingText)
  hasPendingError.value = hasMismatchError
  
  emit('update-line', { lineIndex: pendingIdx, input: pendingInputValue.value })
}

// ==================== 键盘导航 ====================
const onMoveUp = () => {
  // 查找当前行上方最近的一个待完成栏
  let targetLine = -1
  for (let i = props.currentLineIndex - 1; i >= 0; i--) {
    if (isLinePending(i)) {
      targetLine = i
      break
    }
  }
  
  if (targetLine >= 0 && userPendingLineIndex.value === -1) {
    clearUserPendingState()
    userPendingLineIndex.value = targetLine
    pendingInputValue.value = props.articleLineInputs[targetLine] || ''
    hasPendingError.value = true
    setTimeout(() => focusPendingInput(), 50)
    scrollToCurrentLine()
  }
}

const onMoveDown = () => {}

const onMoveUpFromPending = () => {}

const onMoveDownFromPending = () => {
  if (userPendingLineIndex.value >= 0) {
    clearUserPendingState()
    setTimeout(() => focusCurrentInput(), 50)
    scrollToCurrentLine()
  }
}

const scrollToCurrentLine = async () => {
  await nextTick()
  const container = containerRef.value
  if (!container) return
  
  const currentLine = container.querySelector('.line-item.current')
  if (currentLine) {
    const containerRect = container.getBoundingClientRect()
    const elementRect = currentLine.getBoundingClientRect()
    const offset = elementRect.top - containerRect.top - (containerRect.height / 2) + (elementRect.height / 2)
    
    container.scrollBy({
      top: offset,
      behavior: 'smooth'
    })
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 监听当前行变化
watch(() => props.currentLineIndex, (newIndex) => {
  clearUserPendingState()
  currentInputValue.value = props.articleLineInputs[newIndex] || ''
  hasCurrentError.value = false
  scrollToCurrentLine()
  setTimeout(() => focusCurrentInput(), 100)
}, { immediate: true })

// 监听 articleLineInputs 变化
watch(() => props.articleLineInputs, (newInputs) => {
  const pendingIdx = userPendingLineIndex.value
  if (pendingIdx >= 0 && newInputs[pendingIdx] !== pendingInputValue.value) {
    pendingInputValue.value = newInputs[pendingIdx] || ''
  }
}, { deep: true })

onMounted(() => {
  // 如果文章内容已经存在，则聚焦
  if (props.articleLines && props.articleLines.length > 0) {
    setTimeout(() => {
      focusCurrentInput()
      scrollToCurrentLine()
    }, 200)
  }
})

watch(() => props.articleLines, (newLines) => {
  if (newLines && newLines.length > 0 && props.currentLineIndex >= 0) {
    // 文章内容加载完成，延迟聚焦
    setTimeout(() => {
      focusCurrentInput()
      scrollToCurrentLine()
    }, 100)
  }
}, { immediate: true })

// 暴露方法给父组件
defineExpose({ focusCurrentInput })
</script>

<style scoped>
/* 样式保持不变 */
.article-mode {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.article-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.lines-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  justify-content: center;
  min-height: 100%;
}

.line-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.line-item.completed {
  opacity: 0;
  transform: translateY(-10px);
  pointer-events: none;
  height: 0;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

.line-item.pending {
  background: rgba(255, 193, 7, 0.1);
  border-left: 3px solid #ff9800;
  animation: fadeInUp 0.3s ease;
}

.line-item.current {
  background: rgba(33, 150, 243, 0.15);
  border-left: 3px solid var(--primary-color);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
  animation: fadeInUp 0.3s ease;
}

.line-item.new {
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.line-number {
  width: 50px;
  font-size: 14px;
  color: var(--text-secondary);
  font-family: monospace;
  flex-shrink: 0;
  text-align: center;
  margin-right: 20px;
}

.line-content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.line-text {
  font-family: 'Courier New', monospace;
  font-size: 18px;
  line-height: 1.5;
  letter-spacing: 1px;
  text-align: center;
  word-break: break-word;
  padding: 4px 0;
}

.line-input-area {
  width: 100%;
  display: flex;
  justify-content: center;
}

.line-input {
  width: 80%;
  max-width: 500px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
  font-size: 16px;
  outline: none;
  transition: all 0.2s;
  text-align: center;
  box-sizing: border-box;
}

.line-input:focus {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
}

.line-input.error {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.08);
}

.line-input.pending-input {
  border-color: #ff9800;
}

.line-input.pending-input:focus {
  box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.3);
}

.word-unit {
  display: inline-block;
  background: var(--card-bg);
  border-radius: 6px;
  padding: 2px 6px;
  margin: 0 2px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.word-unit.word-completed {
  background: #e8f5e9;
  border-color: #4caf50;
}

.word-unit.word-error {
  background: #ffebee;
  border-color: #f44336;
  animation: shake 0.3s ease-in-out;
}

.word-char {
  display: inline-block;
  transition: all 0.1s;
}

.word-char.correct { 
  color: #2e7d32;
  font-weight: 500;
}

.word-char.incorrect { 
  color: #c62828;
  text-decoration: underline;
  background: rgba(244, 67, 54, 0.15);
  border-radius: 2px;
}

.char-unit {
  display: inline-block;
  transition: all 0.1s;
  min-width: 1.2em;
  text-align: center;
}

.char-unit.char-correct { 
  color: #2e7d32;
  font-weight: 500;
}

.char-unit.char-error {
  color: #c62828;
  text-decoration: underline;
  background: rgba(244, 67, 54, 0.15);
  border-radius: 2px;
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-3px); }
  40% { transform: translateX(3px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 12px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  font-size: 14px;
  flex-shrink: 0;
}
</style>