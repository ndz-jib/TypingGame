<template>
  <div class="typing-area">
    <div class="exit-btn" @click="exitGame">
      <span>✕</span> 退出
    </div>
    
    <WordMode v-if="mode === 'word'" :layout="'4'" />
    <ArticleMode v-else-if="mode === 'article'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import WordMode from './WordMode.vue'
import ArticleMode from './ArticleMode.vue'

const mode = ref('word')  // 可通过 props 或全局状态控制

const exitGame = () => {
  if (window.__APP__) window.__APP__.isPlaying = false
}
</script>

<style scoped>
.typing-area { width: 100%; height: 100%; position: relative; }
.exit-btn { position: absolute; top: 20px; right: 20px; padding: 8px 16px; background: var(--error-color); color: white; border-radius: 8px; cursor: pointer; z-index: 100; display: flex; align-items: center; gap: 6px; }
</style>