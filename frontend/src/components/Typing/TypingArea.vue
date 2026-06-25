<template>
  <div class="typing-area">
    <div class="exit-btn" @click="exitGame">
      <span>✕</span> 退出
    </div>
    
    <WordMode 
      v-if="gameStore.mode === 'word'"
      ref="wordModeRef"
      :word-cards="gameStore.wordCards"
      :total-words="gameStore.stats.total"
      :completed-count="gameStore.stats.completed"
      :accuracy="gameStore.stats.accuracy"
      :layout="gameStore.wordSettings?.layout || '4'"
      :timer-enabled="gameStore.timerEnabled"
      :time-remaining="gameStore.stats.timeRemaining"
      @word-complete="onWordComplete"
      @word-error="onWordError"
      @need-next-word="onNeedNextWord"
    />
    
    <ArticleMode 
      v-else-if="gameStore.mode === 'article'"
      ref="articleModeRef"
      :article-lines="gameStore.articleLines"
      :article-line-inputs="gameStore.articleLineInputs"
      :current-line-index="gameStore.currentLineIndex"
      :display-lines="gameStore.displayLines"
      :stats="gameStore.stats"
      :timer-enabled="gameStore.timerEnabled"
      :time-remaining="gameStore.stats.timeRemaining"
      @update-line="onUpdateLine"
      @complete-line="onCompleteLine"
      @force-move="onForceMove"
      @move-to-line="onMoveToLine"
      @word-error="onArticleWordError"
      @char-error="onCharError"
    />
    
    <Modal v-model="showResultModal" title="游戏结束">
      <div class="result-stats">
        <div class="result-item">
          <span>完成进度</span>
          <strong>{{ gameStore.stats.completed }}/{{ gameStore.stats.total }}</strong>
        </div>
        <div class="result-item">
          <span>准确率</span>
          <strong>{{ (gameStore.stats.accuracy * 100).toFixed(1) }}%</strong>
        </div>
        <div class="result-item">
          <span>WPM</span>
          <strong>{{ calculatedWPM }}</strong>
        </div>
        <div class="result-item">
          <span>用时</span>
          <strong>{{ formatTime(elapsedTime) }}</strong>
        </div>
      </div>
      
      <div v-if="gameStore.mode === 'article' && hasNextPart" class="continue-section">
        <button class="continue-btn" @click="continueNextPart">
          继续下一部分 ({{ gameStore.currentArticlePart + 1 }}/{{ gameStore.totalArticleParts }})
        </button>
        <button class="exit-result-btn" @click="closeResult">返回菜单</button>
      </div>
      <button v-else class="close-btn" @click="closeResult">确定</button>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import WordMode from './WordMode.vue'
import ArticleMode from './ArticleMode.vue'
import Modal from '@/components/Common/Modal.vue'

const gameStore = useGameStore()

const showResultModal = ref(false)
const calculatedWPM = ref(0)
const elapsedTime = ref(0)

// 子组件引用
const wordModeRef = ref(null)
const articleModeRef = ref(null)

const hasNextPart = computed(() => {
  return gameStore.mode === 'article' && 
         gameStore.currentArticlePart < gameStore.totalArticleParts
})

// ==================== 单词模式事件 ====================
const onWordComplete = ({ cardId, isCorrect, word, input }) => {
  gameStore.handleWordComplete(cardId, isCorrect, word, input)
}

const onWordError = ({ word }) => {}

const onNeedNextWord = ({ index }) => {
  const card = gameStore.wordCards[index]
  if (card && card.isCompleted) {
    const nextWord = gameStore.getNextWord()
    if (nextWord) {
      gameStore.replaceWordCard(index, nextWord.word, nextWord.note)
    }
  }
}

// ==================== 文章模式事件 ====================
const onUpdateLine = ({ lineIndex, input }) => {
  gameStore.updateArticleLine(lineIndex, input)
}

const onCompleteLine = () => {
  gameStore.completeCurrentLine()
}

const onForceMove = () => {
  gameStore.forceMoveToNextLine()
}

const onMoveToLine = (lineIndex) => {
  gameStore.currentLineIndex = lineIndex
}

const onArticleWordError = ({ word, input }) => {
  gameStore.handleWordError(word)
}

const onCharError = ({ char, input }) => {
  gameStore.handleCharError(char)
}

// ==================== 通用方法 ====================
const exitGame = () => {
  gameStore.reset()
}

const continueNextPart = async () => {
  const success = await gameStore.loadNextArticlePart()
  if (success) {
    showResultModal.value = false
    gameStore.startTimer()
  }
}

const closeResult = () => {
  showResultModal.value = false
  gameStore.reset()
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const checkGameEnd = () => {
  if (!gameStore.isPlaying && gameStore.stats.endTime) {
    calculatedWPM.value = gameStore.calculateWPM()
    elapsedTime.value = (gameStore.stats.endTime - gameStore.stats.startTime) / 1000
    showResultModal.value = true
  }
}

// ==================== 聚焦方法（兼容两种模式） ====================

/**
 * 聚焦当前模式的输入框
 * - 单词模式：聚焦到第一个未完成的单词卡片输入框
 * - 文章模式：聚焦到当前行的输入框
 */
const focusCurrentMode = async () => {
  await nextTick()
  
  if (gameStore.mode === 'word') {
    // ✅ 单词模式：使用 WordMode 组件暴露的方法
    if (wordModeRef.value && typeof wordModeRef.value.focusFirstInput === 'function') {
      wordModeRef.value.focusFirstInput()
    } else {
      // 备用方案：直接 DOM 查询
      const input = document.querySelector('.word-card.active input') ||
                    document.querySelector('.word-card:not(.completed) input')
      if (input) {
        input.focus()
        input.select()
      }
    }
  } else if (gameStore.mode === 'article') {
    // ✅ 文章模式：使用 ArticleMode 组件暴露的方法
    if (articleModeRef.value && typeof articleModeRef.value.focusCurrentInput === 'function') {
      articleModeRef.value.focusCurrentInput()
    }
  }
}

// ==================== 监听器 ====================

// 监听游戏开始，自动聚焦
watch(() => gameStore.isPlaying, (playing, wasPlaying) => {
  if (playing && !wasPlaying) {
    // 检查是否有有效内容
    if (gameStore.mode === 'word' && (!gameStore.wordList || gameStore.wordList.length === 0)) {
      console.warn('单词列表为空，游戏无法开始')
      gameStore.reset()
      return
    }
    if (gameStore.mode === 'article' && (!gameStore.articleLines || gameStore.articleLines.length === 0)) {
      console.warn('文章内容为空，游戏无法开始')
      gameStore.reset()
      return
    }
    
    // 延迟等待 DOM 渲染完成后聚焦
    setTimeout(() => {
      focusCurrentMode()
    }, 500)
  } else if (wasPlaying && !playing) {
    checkGameEnd()
  }
})

// 监听单词卡片变化，确保聚焦
watch(() => gameStore.wordCards, () => {
  if (gameStore.mode === 'word' && gameStore.isPlaying) {
    setTimeout(() => {
      focusCurrentMode()
    }, 50)
  }
}, { deep: true })

// 监听文章行变化，确保聚焦
watch(() => gameStore.articleLines, (newLines) => {
  if (gameStore.mode === 'article' && gameStore.isPlaying && newLines && newLines.length > 0) {
    setTimeout(() => {
      focusCurrentMode()
    }, 300)
  }
}, { immediate: true })

// 监听当前行索引变化，重新聚焦
watch(() => gameStore.currentLineIndex, () => {
  if (gameStore.mode === 'article' && gameStore.isPlaying) {
    setTimeout(() => {
      focusCurrentMode()
    }, 100)
  }
})

onUnmounted(() => {
  if (gameStore.timer) clearInterval(gameStore.timer)
})
</script>

<style scoped>
.typing-area {
  width: 100%;
  height: 100%;
  position: relative;
}

.exit-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}
.exit-btn:hover { opacity: 0.9; }

.result-stats { padding: 20px; }
.result-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}
.result-item strong { font-size: 18px; color: var(--primary-color); }

.continue-section {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}
.continue-btn {
  flex: 1;
  padding: 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.exit-result-btn {
  flex: 1;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
}
.close-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 8px;
}
</style>