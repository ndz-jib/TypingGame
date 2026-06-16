<template>
  <div 
    class="word-card" 
    :class="{ 
      active: isActive,
      completed: isCompleted,
      'has-error': hasError && !isCompleted
    }"
  >
    <div class="word-display">
      <span 
        v-for="(char, idx) in wordChars" 
        :key="idx"
        :class="getCharClass(idx)"
      >
        {{ char }}
      </span>
    </div>
    
    <div v-if="note && !isCompleted" class="word-note">
      📝 {{ note }}
    </div>
    
    <input 
      v-if="isActive && !isCompleted"
      ref="inputRef"
      type="text"
      v-model="inputValue"
      @input="onInput"
      @keydown="onKeyDown"
      @keyup="onKeyUp"
      @keydown.enter.prevent="onSubmit"
      class="word-input"
      :placeholder="`输入 ${word}...`"
    >
    
    <div v-if="isCompleted" class="completed-mark">
      ✅ 完成
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { audioService } from '@/services/audioService'
import { useConfigStore } from '@/stores/configStore'

const props = defineProps({
  word: { type: String, required: true },
  note: { type: String, default: '' },
  isActive: { type: Boolean, default: false },
  isCompleted: { type: Boolean, default: false }
})

const emit = defineEmits(['complete', 'error'])

const configStore = useConfigStore()
const inputValue = ref('')
const hasError = ref(false)
const errorTriggered = ref(false)
const inputRef = ref(null)

const wordChars = computed(() => props.word?.split('') || [])
const wordLength = computed(() => props.word?.length || 0)

const getCharClass = (index) => {
  if (props.isCompleted) return ''
  if (index >= inputValue.value.length) return ''
  
  const inputChar = inputValue.value[index]
  const targetChar = props.word[index]
  
  if (inputChar === targetChar) return 'correct'
  return 'incorrect'
}

// 按键按下：开始播放按键音效
const onKeyDown = () => {
  if (configStore.soundEnabled) {
    audioService.startKeypress()
  }
}

// 按键抬起：停止播放按键音效（延迟停止）
const onKeyUp = () => {
  if (configStore.soundEnabled) {
    audioService.stopKeypress()
  }
}

const triggerError = () => {
  if (errorTriggered.value) return
  errorTriggered.value = true
  hasError.value = true
  
  // 播放错误音效
  if (configStore.soundEnabled) {
    audioService.playError()
  }
  
  emit('error', { word: props.word, input: inputValue.value })
}

const onInput = () => {
  if (props.isCompleted) return
  
  if (inputValue.value.length > wordLength.value) {
    inputValue.value = inputValue.value.slice(0, wordLength.value)
  }
  
  // 检查错误
  let hasMismatch = false
  for (let i = 0; i < inputValue.value.length; i++) {
    if (inputValue.value[i] !== props.word[i]) {
      hasMismatch = true
      break
    }
  }
  
  if (hasMismatch && !hasError.value) {
    triggerError()
  } else if (!hasMismatch) {
    hasError.value = false
    errorTriggered.value = false
  }
  
  // 自动提交
  if (inputValue.value.length === wordLength.value) {
    onSubmit()
  }
}

const onSubmit = () => {
  if (props.isCompleted) return
  
  // 停止按键音效
  audioService.stopKeypressImmediately()
  
  const isCorrect = (inputValue.value === props.word)
  
  if (!isCorrect && !hasError.value) {
    triggerError()
  }
  
  emit('complete', {
    word: props.word,
    input: inputValue.value,
    isCorrect
  })
}

const focus = () => {
  nextTick(() => {
    if (inputRef.value && !props.isCompleted) {
      inputRef.value.focus()
      inputRef.value.select()
    }
  })
}

const reset = () => {
  inputValue.value = ''
  hasError.value = false
  errorTriggered.value = false
}

watch(() => props.isActive, (active) => {
  if (active && !props.isCompleted) focus()
})

defineExpose({ focus, reset })
</script>

<style scoped>
/* 样式保持不变 */
.word-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  box-shadow: var(--shadow);
  transition: all 0.3s;
  min-width: 180px;
}

.word-card.active {
  border: 2px solid var(--primary-color);
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.word-card.completed {
  opacity: 0.6;
  transform: scale(0.98);
}

.word-card.has-error {
  border-color: var(--error-color);
  animation: shake 0.4s ease-in-out;
}

.word-display {
  font-size: 20px;
  font-weight: bold;
  font-family: monospace;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.word-note {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  background: var(--bg-secondary);
  padding: 4px 8px;
  border-radius: 16px;
  display: inline-block;
}

.correct {
  color: var(--correct-color);
}

.incorrect {
  color: var(--error-color);
  text-decoration: underline;
  background: rgba(244, 67, 54, 0.15);
}

.word-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  outline: none;
}

.word-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.completed-mark {
  margin-top: 10px;
  font-size: 12px;
  color: var(--correct-color);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-5px); }
  40% { transform: translateX(5px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
}
</style>