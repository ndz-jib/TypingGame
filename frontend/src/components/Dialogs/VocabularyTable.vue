<template>
  <Modal v-model="visible" title="单词表" width="800px">
    <div class="vocabulary-table">
      <div class="toolbar">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            placeholder="搜索单词..."
            @input="onSearch"
            @keyup.enter="fetchVocabulary"
          >
          <button class="search-btn" @click="fetchVocabulary">🔍</button>
        </div>
        
        <div class="letter-filter">
          <button 
            v-for="letter in letters" 
            :key="letter"
            :class="{ active: currentLetter === letter }"
            @click="filterByLetter(letter)"
          >
            {{ letter }}
          </button>
          <button 
            :class="{ active: currentLetter === '' }"
            @click="filterByLetter('')"
          >
            全部
          </button>
        </div>
        
        <div class="actions">
          <button @click="importTxt" class="import-btn">导入TXT</button>
          <button @click="addWord" class="add-btn">+ 添加单词</button>
        </div>
      </div>
      
      <div class="word-list">
        <div class="word-header">
          <div class="col-word">单词</div>
          <div class="col-note">注释</div>
          <div class="col-action">操作</div>
        </div>
        
        <div v-if="loading" class="loading">
          <span class="spinner"></span> 加载中...
        </div>
        
        <div v-else-if="wordList.length === 0" class="empty">
          暂无单词，点击上方按钮添加
        </div>
        
        <div v-else class="word-rows">
          <div v-for="word in wordList" :key="word.word" class="word-row">
            <div class="col-word">{{ word.word }}</div>
            <div class="col-note">
              <input 
                v-model="word.note" 
                placeholder="添加注释..."
                @blur="updateNote(word)"
              >
            </div>
            <div class="col-action">
              <button @click="deleteWord(word.word)" class="delete-btn">删除</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <span class="total-count">共 {{ total }} 个单词</span>
        <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '@/services/api'
import Modal from '@/components/Common/Modal.vue'
import { ALPHABETS, MESSAGES } from '@/utils/constants'

const visible = defineModel()

const loading = ref(false)
const searchKeyword = ref('')
const currentLetter = ref('')
const currentPage = ref(1)
const pageSize = 20

const total = ref(0)
const wordList = ref([])

const letters = ALPHABETS

// 总页数
const totalPages = computed(() => Math.ceil(total.value / pageSize))

// 获取单词表
const fetchVocabulary = async () => {
  loading.value = true
  
  try {
    let url = '/vocabulary'
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('pageSize', pageSize)
    
    if (currentLetter.value) {
      params.append('letter', currentLetter.value)
    }
    
    if (searchKeyword.value) {
      // 使用搜索接口
      const searchRes = await api.get('/vocabulary/search', {
        keyword: searchKeyword.value,
        caseSensitive: false
      })
      
      if (searchRes.code === 200) {
        total.value = searchRes.data.total
        wordList.value = searchRes.data.list
      }
    } else {
      const res = await api.get(`/vocabulary?${params.toString()}`)
      
      if (res.code === 200) {
        total.value = res.data.total
        wordList.value = res.data.list
      }
    }
  } catch (error) {
    console.error('获取单词表失败:', error)
  } finally {
    loading.value = false
  }
}

// 按字母筛选
const filterByLetter = (letter) => {
  currentLetter.value = letter
  currentPage.value = 1
  fetchVocabulary()
}

// 搜索
const onSearch = () => {
  currentPage.value = 1
  fetchVocabulary()
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchVocabulary()
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchVocabulary()
  }
}

// 导入 TXT
const importTxt = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.txt'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    loading.value = true
    const content = await file.text()
    
    const res = await api.post('/import/vocabulary', {
      content,
      filename: file.name
    })
    
    loading.value = false
    
    if (res.code === 200) {
      alert(`导入成功！新增 ${res.data.newWordsAdded} 个单词，跳过 ${res.data.existingWordsSkipped} 个重复`)
      currentPage.value = 1
      await fetchVocabulary()
    } else {
      alert('导入失败：' + res.message)
    }
  }
  input.click()
}

// 添加单词
const addWord = () => {
  const word = prompt('请输入单词')
  if (word && word.trim()) {
    api.post('/vocabulary', { word: word.trim(), note: '' })
      .then(async () => {
        await fetchVocabulary()
      })
      .catch(err => {
        alert('添加失败：' + err.message)
      })
  }
}

// 删除单词
const deleteWord = async (word) => {
  if (confirm(`确定要删除单词 "${word}" 吗？`)) {
    const res = await api.delete(`/vocabulary/${encodeURIComponent(word)}`)
    if (res.code === 200) {
      await fetchVocabulary()
    } else {
      alert('删除失败：' + res.message)
    }
  }
}

// 更新注释
const updateNote = async (word) => {
  const res = await api.put(`/vocabulary/${encodeURIComponent(word.word)}/note`, { note: word.note })
  if (res.code !== 200) {
    alert('更新注释失败')
  }
}

// 监听 visible 变化，重新加载数据
watch(visible, (newVal) => {
  if (newVal) {
    currentPage.value = 1
    currentLetter.value = ''
    searchKeyword.value = ''
    fetchVocabulary()
  }
})

onMounted(() => {
  fetchVocabulary()
})
</script>

<style scoped>
.vocabulary-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 500px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 4px;
  flex: 1;
  min-width: 180px;
}

.search-box input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.search-btn {
  padding: 8px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.letter-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 300px;
}

.letter-filter button {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.letter-filter button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.import-btn, .add-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.import-btn {
  background: #4caf50;
  color: white;
}

.add-btn {
  background: var(--primary-color);
  color: white;
}

.word-list {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: auto;
  max-height: 350px;
}

.word-header, .word-row {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr;
  padding: 12px;
}

.word-header {
  background: var(--bg-secondary);
  font-weight: bold;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
}

.word-row {
  border-bottom: 1px solid var(--border-color);
}

.word-row:last-child {
  border-bottom: none;
}

.col-word {
  font-weight: 500;
  word-break: break-word;
}

.col-note input {
  width: 100%;
  padding: 6px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
}

.col-note input:focus {
  border-color: var(--primary-color);
  outline: none;
}

.delete-btn {
  padding: 4px 12px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  opacity: 0.9;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 16px;
  align-items: center;
  padding: 12px;
  border-top: 1px solid var(--border-color);
}

.pagination button {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background: var(--card-hover);
}

.total-count {
  color: var(--text-secondary);
  font-size: 13px;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>