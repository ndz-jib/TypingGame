<template>
  <Modal v-model="visible" title="单词表" width="800px">
    <div class="vocabulary-table">
      <div class="toolbar">
        <div class="search-box">
          <input v-model="searchKeyword" placeholder="搜索单词...">
          <button class="search-btn">🔍</button>
        </div>
        <div class="actions">
          <button class="import-btn">📄 导入TXT</button>
          <button class="add-btn">+ 添加单词</button>
        </div>
      </div>
      <div class="word-list">
        <div class="word-header">
          <div class="col-word">单词</div>
          <div class="col-note">注释</div>
          <div class="col-action">操作</div>
        </div>
        <div class="word-rows">
          <div v-for="word in demoWords" :key="word.word" class="word-row">
            <div class="col-word">{{ word.word }}</div>
            <div class="col-note"><input v-model="word.note" placeholder="添加注释..."></div>
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
const searchKeyword = ref('')
const demoWords = ref([
  { word: 'apple', note: '苹果' },
  { word: 'banana', note: '香蕉' },
  { word: 'cherry', note: '樱桃' }
])
</script>

<style scoped>
.vocabulary-table { display: flex; flex-direction: column; gap: 16px; max-height: 500px; }
.toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.search-box { display: flex; gap: 4px; flex: 1; min-width: 180px; }
.search-box input { flex: 1; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); }
.search-btn { padding: 8px 12px; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer; }
.actions { display: flex; gap: 8px; }
.import-btn, .add-btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; }
.import-btn { background: #4caf50; color: white; }
.add-btn { background: var(--primary-color); color: white; }
.word-list { border: 1px solid var(--border-color); border-radius: 8px; overflow: auto; max-height: 350px; }
.word-header, .word-row { display: grid; grid-template-columns: 2fr 3fr 1fr; padding: 12px; }
.word-header { background: var(--bg-secondary); font-weight: bold; border-bottom: 1px solid var(--border-color); }
.word-row { border-bottom: 1px solid var(--border-color); }
.col-note input { width: 100%; padding: 6px 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); }
.delete-btn { padding: 4px 12px; background: var(--error-color); color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>