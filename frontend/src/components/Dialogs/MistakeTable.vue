<template>
  <Modal v-model="visible" title="错词表" width="800px">
    <div class="mistake-table">
      <div class="toolbar">
        <div class="sort-buttons">
          <button :class="{ active: sortBy === 'time' }" @click="sortBy = 'time'">
            ⏰ 按时间排序
          </button>
          <button :class="{ active: sortBy === 'count' }" @click="sortBy = 'count'">
            🔥 按错误次数排序
          </button>
        </div>
        <div class="search-box">
          <input v-model="searchKeyword" placeholder="搜索错词...">
          <button class="search-btn">🔍</button>
        </div>
        <button class="clear-btn">🗑️ 清空错词表</button>
      </div>
      
      <div class="mistake-list">
        <div class="mistake-header">
          <div class="col-word">单词</div>
          <div class="col-count">错误次数</div>
          <div class="col-last">最后错误时间</div>
          <div class="col-action">操作</div>
        </div>
        <div class="mistake-rows">
          <div v-for="mistake in demoMistakes" :key="mistake.word" class="mistake-row">
            <div class="col-word">{{ mistake.word }}</div>
            <div class="col-count"><span class="badge">{{ mistake.errorCount }}</span></div>
            <div class="col-last">{{ mistake.lastErrorTime }}</div>
            <div class="col-action"><button class="delete-btn">删除</button></div>
          </div>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref } from 'vue'
import Modal from '@/components/Common/Modal.vue'

const visible = defineModel()
const sortBy = ref('time')
const searchKeyword = ref('')
const demoMistakes = ref([
  { word: 'necessary', errorCount: 5, lastErrorTime: '2024-01-15 14:30' },
  { word: 'accommodate', errorCount: 3, lastErrorTime: '2024-01-14 09:20' },
  { word: 'separate', errorCount: 2, lastErrorTime: '2024-01-13 16:45' }
])
</script>

<style scoped>
.mistake-table { display: flex; flex-direction: column; gap: 16px; max-height: 500px; }
.toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.sort-buttons { display: flex; gap: 8px; }
.sort-buttons button { padding: 6px 12px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; font-size: 13px; }
.sort-buttons button.active { background: var(--primary-color); color: white; border-color: var(--primary-color); }
.search-box { display: flex; gap: 4px; flex: 1; min-width: 180px; }
.search-box input { flex: 1; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); }
.search-btn { padding: 8px 12px; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer; }
.clear-btn { padding: 8px 16px; background: var(--error-color); color: white; border: none; border-radius: 6px; cursor: pointer; }
.mistake-list { border: 1px solid var(--border-color); border-radius: 8px; overflow: auto; max-height: 350px; }
.mistake-header, .mistake-row { display: grid; grid-template-columns: 2fr 1fr 2fr 1fr; padding: 12px; }
.mistake-header { background: var(--bg-secondary); font-weight: bold; border-bottom: 1px solid var(--border-color); }
.mistake-row { border-bottom: 1px solid var(--border-color); }
.badge { display: inline-block; padding: 2px 8px; background: #ff9800; color: white; border-radius: 20px; font-size: 12px; font-weight: bold; }
.delete-btn { padding: 4px 12px; background: var(--error-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
</style>