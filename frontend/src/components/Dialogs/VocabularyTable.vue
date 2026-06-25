<template>
  <Modal v-model="visible" title="单词表" width="800px">
    <div class="vocabulary-table">
      <!-- ======== 工具栏 ======== -->
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
          <button @click="importTxt" class="import-btn">
            导入TXT
          </button>
          <button @click="addWord" class="add-btn">
            添加单词
          </button>
        </div>
      </div>
      
      <!-- ======== 单词列表 ======== -->
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
              <button @click="deleteWord(word.word)" class="delete-btn">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- ======== 分页 ======== -->
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">‹ 上一页</button>
        <span class="page-info">第 {{ currentPage }} / {{ totalPages || 1 }} 页</span>
        <span class="total-count">共 {{ total }} 个单词</span>
        <button @click="nextPage" :disabled="currentPage === totalPages || totalPages === 0">下一页 ›</button>
      </div>
    </div>

    <Modal v-model="showAddDialog" title="添加新单词" width="480px">
      <div class="add-dialog">
        <!-- 提示信息 -->
        <div class="dialog-tip">
          <span class="tip-text">输入单词及其注释，注释为选填项</span>
        </div>

        <!-- 单词输入 -->
        <div class="form-group" :class="{ 'has-error': wordError }">
          <label class="form-label">
            单词 <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input 
              v-model="newWord.word" 
              placeholder="请输入单词（必填）" 
              @keyup.enter="confirmAddWord"
              class="dialog-input"
              :class="{ 'input-error': wordError }"
              autofocus
            >
            <span v-if="newWord.word" class="input-clear" @click="newWord.word = ''">✕</span>
          </div>
          <span v-if="wordError" class="error-message">
            <span class="error-icon">⚠️</span> {{ wordError }}
          </span>
        </div>
        
        <!-- 注释输入 -->
        <div class="form-group">
          <label class="form-label">
            注释 <span class="optional">选填</span>
          </label>
          <div class="textarea-wrapper">
            <textarea 
              v-model="newWord.note" 
              placeholder="请输入注释（可选）" 
              rows="3"
              class="dialog-textarea"
              @keydown.ctrl.enter="confirmAddWord"
            ></textarea>
          </div>
          <span class="hint">
            支持中文、英文及标点符号，用于辅助记忆
          </span>
        </div>

        <!-- 预览区域（单词 + 注释预览） -->
        <div v-if="newWord.word || newWord.note" class="preview-section">
          <div class="preview-label">预览</div>
          <div class="preview-card">
            <span class="preview-word">{{ newWord.word || '单词' }}</span>
            <span class="preview-note">{{ newWord.note || '注释' }}</span>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="dialog-actions">
          <button @click="closeAddDialog" class="cancel-btn">
            ✕ 取消
          </button>
          <button @click="confirmAddWord" class="confirm-btn" :disabled="loadingAdd">
            <span v-if="loadingAdd" class="btn-spinner"></span>
            <span v-else>✓ 确定添加</span>
          </button>
        </div>
      </div>
    </Modal>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { api } from '@/services/api'
import Modal from '@/components/Common/Modal.vue'
import { ALPHABETS } from '@/utils/constants'

const visible = defineModel()

const loading = ref(false)
const searchKeyword = ref('')
const currentLetter = ref('')
const currentPage = ref(1)
const pageSize = 20

const total = ref(0)
const wordList = ref([])

const letters = ALPHABETS

// 添加单词相关
const showAddDialog = ref(false)
const loadingAdd = ref(false)
const newWord = ref({
  word: '',
  note: ''
})
const wordError = ref('')

// 总页数
const totalPages = computed(() => Math.ceil(total.value / pageSize))

// 获取单词表
const fetchVocabulary = async () => {
  loading.value = true
  
  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('pageSize', pageSize)
    
    if (currentLetter.value) {
      params.append('letter', currentLetter.value)
    }
    
    if (searchKeyword.value) {
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

// 添加单词（打开对话框）
const addWord = () => {
  newWord.value = {
    word: '',
    note: ''
  }
  wordError.value = ''
  showAddDialog.value = true
  // 延迟聚焦输入框
  nextTick(() => {
    const input = document.querySelector('.dialog-input')
    if (input) input.focus()
  })
}

// 关闭添加对话框
const closeAddDialog = () => {
  showAddDialog.value = false
  newWord.value = {
    word: '',
    note: ''
  }
  wordError.value = ''
}

// 确认添加单词
const confirmAddWord = async () => {
  const word = newWord.value.word.trim()
  
  if (!word) {
    wordError.value = '请输入单词'
    return
  }
  
  if (!/^[a-zA-Z\s\-']+$/.test(word)) {
    wordError.value = '单词只能包含字母、空格、连字符和撇号'
    return
  }
  
  wordError.value = ''
  loadingAdd.value = true
  
  try {
    const note = newWord.value.note.trim() || ''
    await api.post('/vocabulary', { word, note })
    
    closeAddDialog()
    await fetchVocabulary()
    
  } catch (err) {
    if (err.response && err.response.status === 409) {
      wordError.value = `单词 "${word}" 已存在`
    } else {
      alert('添加失败：' + (err.message || '未知错误'))
    }
  } finally {
    loadingAdd.value = false
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
/* ============================================================ */
/*                   主表格样式（保持不变）                        */
/* ============================================================ */
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
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.15);
}

.search-btn {
  padding: 8px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.search-btn:hover { opacity: 0.9; }

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
  transition: all 0.2s;
  font-weight: 500;
}

.letter-filter button:hover {
  background: var(--card-hover);
  transform: scale(1.05);
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
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.import-btn {
  background: #4caf50;
  color: white;
}

.import-btn:hover {
  background: #43a047;
  transform: scale(1.02);
}

.add-btn {
  background: var(--primary-color);
  color: white;
}

.add-btn:hover {
  background: #1976d2;
  transform: scale(1.02);
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
  padding: 12px 16px;
  align-items: center;
}

.word-header {
  background: var(--bg-secondary);
  font-weight: bold;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 1;
}

.word-row {
  border-bottom: 1px solid var(--border-color);
  transition: background 0.15s;
}

.word-row:hover {
  background: var(--card-hover);
}

.word-row:last-child { border-bottom: none; }

.col-word {
  font-weight: 500;
  word-break: break-word;
  font-size: 15px;
}

.col-note input {
  width: 100%;
  padding: 6px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  transition: all 0.2s;
}

.col-note input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.delete-btn {
  padding: 4px 10px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  opacity: 0.5;
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.15);
  opacity: 1;
  transform: scale(1.1);
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
  padding: 6px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:not(:disabled):hover {
  background: var(--card-hover);
  transform: scale(1.02);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--text-primary);
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
  to { transform: rotate(360deg); }
}

.add-dialog {
  padding: 4px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---- 提示信息 ---- */
.dialog-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(33, 150, 243, 0.08);
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.tip-icon {
  font-size: 18px;
}

.tip-text {
  font-size: 13px;
  color: var(--text-secondary);
}

/* ---- 表单组 ---- */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group.has-error .dialog-input {
  border-color: #f44336;
  box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.12);
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: #f44336;
  font-weight: 700;
}

.optional {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 0 8px;
  border-radius: 10px;
}

/* ---- 输入框 ---- */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  color: var(--text-secondary);
  pointer-events: none;
}

.dialog-input {
  width: 100%;
  padding: 10px 14px 10px 40px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 15px;
  transition: all 0.25s;
}

.dialog-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.12);
  background: var(--bg-primary);
}

.dialog-input.input-error {
  border-color: #f44336;
}

.input-clear {
  position: absolute;
  right: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
  opacity: 0.5;
}

.input-clear:hover {
  background: var(--card-hover);
  opacity: 1;
  transform: scale(1.1);
}

/* ---- 错误信息 ---- */
.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #f44336;
  padding: 4px 0;
}

.error-icon {
  font-size: 14px;
}

/* ---- 文本域 ---- */
.textarea-wrapper {
  position: relative;
}

.textarea-icon {
  position: absolute;
  left: 12px;
  top: 12px;
  font-size: 16px;
  color: var(--text-secondary);
  pointer-events: none;
}

.dialog-textarea {
  width: 100%;
  padding: 10px 14px 10px 40px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 70px;
  transition: all 0.25s;
}

.dialog-textarea:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.12);
  background: var(--bg-primary);
}

/* ---- 辅助提示 ---- */
.hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 4px 0;
}

.hint-icon {
  font-size: 13px;
}

/* ---- 预览区域 ---- */
.preview-section {
  padding: 12px 14px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px dashed var(--border-color);
}

.preview-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-word {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
}

.preview-note {
  font-size: 14px;
  color: var(--text-secondary);
  padding-left: 12px;
  border-left: 2px solid var(--border-color);
}

.preview-note:empty::before {
  content: '无注释';
  color: var(--text-secondary);
  opacity: 0.5;
}

/* ---- 对话框操作按钮 ---- */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.cancel-btn {
  padding: 10px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--card-hover);
  transform: scale(1.02);
}

.confirm-btn {
  padding: 10px 28px;
  background: linear-gradient(135deg, var(--primary-color), #1976d2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.confirm-btn:hover:not(:disabled) {
  transform: scale(1.03);
  box-shadow: 0 4px 16px rgba(33, 150, 243, 0.35);
}

.confirm-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* ---- 按钮加载状态 ---- */
.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
</style>