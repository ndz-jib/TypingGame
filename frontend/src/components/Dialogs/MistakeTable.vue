<template>
  <Modal v-model="visible" title="错词表" width="800px">
    <div class="mistake-table">
      <div class="toolbar">
        <div class="sort-buttons">
          <button 
            :class="{ active: sortBy === 'time' }"
            @click="changeSort('time')"
          >
            按时间排序
          </button>
          <button 
            :class="{ active: sortBy === 'count' }"
            @click="changeSort('count')"
          >
            按错误次数排序
          </button>
        </div>
        
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            placeholder="搜索错词..."
            @input="onSearch"
            @keyup.enter="fetchMistakes"
          >
          <button class="search-btn" @click="fetchMistakes">🔍</button>
        </div>
        
        <button @click="clearAll" class="clear-btn">清空错词表</button>
      </div>
      
      <div class="mistake-list">
        <div class="mistake-header">
          <div class="col-word">单词</div>
          <div class="col-count">错误次数</div>
          <div class="col-last">最后错误时间</div>
          <div class="col-action">操作</div>
        </div>
        
        <div v-if="loading" class="loading">
          <span class="spinner"></span> 加载中...
        </div>
        
        <div v-else-if="mistakeList.length === 0" class="empty">
          暂无错词，继续加油！
        </div>
        
        <div v-else class="mistake-rows">
          <div v-for="mistake in mistakeList" :key="mistake.word" class="mistake-row">
            <div class="col-word">{{ mistake.word }}</div>
            <div class="col-count">
              <span class="badge" :class="{ 'high': mistake.errorCount >= 5, 'medium': mistake.errorCount >= 3 }">
                {{ mistake.errorCount }}
              </span>
            </div>
            <div class="col-last">{{ formatTime(mistake.lastErrorTime) }}</div>
            <div class="col-action">
              <button @click="deleteMistake(mistake.word)" class="delete-btn">删除</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <span class="total-count">共 {{ total }} 个错词</span>
        <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '@/services/api'
import Modal from '@/components/Common/Modal.vue'

const visible = defineModel()

const loading = ref(false)
const searchKeyword = ref('')
const sortBy = ref('time') // 'time' or 'count'
const currentPage = ref(1)
const pageSize = 20

const total = ref(0)
const mistakeList = ref([])

// 总页数
const totalPages = computed(() => Math.ceil(total.value / pageSize))

// 获取错词表
const fetchMistakes = async () => {
  loading.value = true
  
  try {
    if (searchKeyword.value) {
      // 使用搜索接口
      const searchRes = await api.get('/mistake/search', {
        keyword: searchKeyword.value,
        caseSensitive: false
      })
      
      if (searchRes.code === 200) {
        total.value = searchRes.data.total
        mistakeList.value = searchRes.data.list
      }
    } else {
      // 使用分页接口
      const params = new URLSearchParams()
      params.append('sortBy', sortBy.value)
      params.append('page', currentPage.value)
      params.append('pageSize', pageSize)
      
      const res = await api.get(`/mistake?${params.toString()}`)
      
      if (res.code === 200) {
        total.value = res.data.total
        mistakeList.value = res.data.list
      }
    }
  } catch (error) {
    console.error('获取错词表失败:', error)
  } finally {
    loading.value = false
  }
}

// 切换排序
const changeSort = (type) => {
  sortBy.value = type
  currentPage.value = 1
  searchKeyword.value = ''
  fetchMistakes()
}

// 搜索
const onSearch = () => {
  currentPage.value = 1
  fetchMistakes()
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchMistakes()
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchMistakes()
  }
}

// 删除错词
const deleteMistake = async (word) => {
  if (confirm(`确定要从错词表中删除 "${word}" 吗？`)) {
    const res = await api.delete(`/mistake/${encodeURIComponent(word)}`)
    if (res.code === 200) {
      // 刷新当前页
      if (mistakeList.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      await fetchMistakes()
    } else {
      alert('删除失败：' + res.message)
    }
  }
}

// 清空所有错词
const clearAll = async () => {
  if (confirm('确定要清空所有错词记录吗？此操作不可恢复。')) {
    const res = await api.delete('/mistake')
    if (res.code === 200) {
      currentPage.value = 1
      await fetchMistakes()
    } else {
      alert('清空失败：' + res.message)
    }
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '未知'
  // 处理格式：2026-04-15 14:30:25
  const parts = timeStr.split(' ')
  if (parts.length === 2) {
    const date = parts[0].split('-')
    const time = parts[1].split(':')
    return `${date[1]}/${date[2]} ${time[0]}:${time[1]}`
  }
  return timeStr
}

// 监听 visible 变化，重新加载数据
watch(visible, (newVal) => {
  if (newVal) {
    currentPage.value = 1
    searchKeyword.value = ''
    fetchMistakes()
  }
})

onMounted(() => {
  fetchMistakes()
})
</script>

<style scoped>
.mistake-table {
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

.sort-buttons {
  display: flex;
  gap: 8px;
}

.sort-buttons button {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.sort-buttons button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
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

.clear-btn {
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.clear-btn:hover {
  opacity: 0.9;
}

.mistake-list {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: auto;
  max-height: 350px;
}

.mistake-header, .mistake-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr 1fr;
  padding: 12px;
}

.mistake-header {
  background: var(--bg-secondary);
  font-weight: bold;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
}

.mistake-row {
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.mistake-row:hover {
  background: var(--card-hover);
}

.mistake-row:last-child {
  border-bottom: none;
}

.col-word {
  font-weight: 500;
  word-break: break-word;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #ff9800;
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  min-width: 28px;
  text-align: center;
}

.badge.high {
  background: #f44336;
}

.badge.medium {
  background: #ff9800;
}

.col-last {
  font-size: 13px;
  color: var(--text-secondary);
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