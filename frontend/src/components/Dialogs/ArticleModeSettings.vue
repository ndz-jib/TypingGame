<template>
  <Modal v-model="visible" title="文章模式设置" width="500px">
    <div class="article-settings">
      <div class="setting-group">
        <label>选择文章</label>
        <div class="article-select">
          <select v-model="localSettings.selectedArticle" :disabled="articleList.length === 0">
            <option v-if="articleList.length === 0" disabled value="">暂无文章，请先上传</option>
            <option v-for="article in articleList" :key="article.filename" :value="article.filename">
              {{ article.filename }} ({{ article.chars || article.size }} 字符)
            </option>
          </select>
          <button @click="uploadArticle" class="upload-btn">上传TXT</button>
        </div>
        <div v-if="articleList.length === 0" class="empty-hint">
          暂无文章，请点击"上传TXT"导入文章
        </div>
      </div>
      
      <div class="setting-group">
        <label>展示行数 ({{ localSettings.displayLines }})</label>
        <div class="setting-control">
          <input 
            type="range" 
            v-model.number="localSettings.displayLines"
            :min="MIN_DISPLAY_LINES"
            :max="MAX_DISPLAY_LINES"
            step="1"
          >
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
      
      <div v-if="splitInfo.show" class="split-warning">
        <span class="warning-icon">⚠️</span>
        <span>{{ splitInfo.message }}</span>
      </div>
      
      <div class="dialog-actions">
        <button class="cancel-btn" @click="cancel">取消</button>
        <button class="confirm-btn" @click="confirm" :disabled="articleList.length === 0">
          开始游戏
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import { api } from '@/services/api'
import { ARTICLE_CONFIG, TIMER_OPTIONS } from '@/utils/constants'

const visible = defineModel()
const emit = defineEmits(['start'])

const MIN_DISPLAY_LINES = ARTICLE_CONFIG.minDisplayLines
const MAX_DISPLAY_LINES = ARTICLE_CONFIG.maxDisplayLines

const articleList = ref([])
const splitInfo = ref({ show: false, message: '' })

const localSettings = ref({
  selectedArticle: '',
  displayLines: ARTICLE_CONFIG.defaultDisplayLines,
  timer: {
    enabled: false,
    duration: TIMER_OPTIONS.default
  }
})

// 加载文章列表
const loadArticles = async () => {
  try {
    const res = await api.get('/articles')
    if (res.code === 200 && res.data && res.data.length > 0) {
      articleList.value = res.data
      localSettings.value.selectedArticle = articleList.value[0].filename
    } else {
      articleList.value = []
      localSettings.value.selectedArticle = ''
      // 显示提示信息（通过模板中的 empty-hint 和 disabled 状态）
      console.log('文章列表为空，请先上传文章')
    }
  } catch (error) {
    console.error('加载文章列表失败:', error)
    articleList.value = []
  }
}

// 上传文章
const uploadArticle = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.txt'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    const content = await file.text()
    
    const res = await api.post('/import/article', {
      content,
      filename: file.name,
      autoSplit: true,
      maxChars: ARTICLE_CONFIG.maxCharsPerArticle
    })
    
    if (res.code === 200) {
      if (res.data.split) {
        splitInfo.value = {
          show: true,
          message: `文件过大，已拆分为 ${res.data.totalParts} 个部分，请逐个选择加载。`
        }
        setTimeout(() => {
          splitInfo.value.show = false
        }, 3000)
      }
      await loadArticles()
      // 自动选择第一个拆分后的文件
      if (res.data.parts && res.data.parts.length) {
        localSettings.value.selectedArticle = res.data.parts[0]
      }
    }
  }
  input.click()
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const confirm = () => {
  if (articleList.value.length === 0) {
    alert('请先上传文章')
    return
  }
  if (!localSettings.value.selectedArticle) {
    alert('请选择一篇文章')
    return
  }
  emit('start', { ...localSettings.value })
  visible.value = false
}

const cancel = () => {
  visible.value = false
}

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.article-settings {
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

.article-select {
  display: flex;
  gap: 12px;
}

.article-select select {
  flex: 1;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
}

.upload-btn {
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-control input[type="range"] {
  flex: 1;
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

.value {
  min-width: 50px;
  text-align: center;
  color: var(--primary-color);
  font-weight: bold;
}

.split-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 152, 0, 0.15);
  border-radius: 6px;
  font-size: 13px;
  color: #ff9800;
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

.empty-hint {
  font-size: 12px;
  color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 8px;
  text-align: center;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>