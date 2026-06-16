<template>
  <Modal v-model="visible" title="设置" width="600px">
    <div class="settings-panel">
      <!-- 用户信息设置 -->
      <div class="settings-section">
        <h3>用户信息</h3>
        <div class="setting-item">
          <label>用户名称</label>
          <input v-model="localUserName" type="text" placeholder="输入用户名">
          <button @click="updateUserName" class="save-btn">保存</button>
        </div>
        <div class="setting-item">
          <label>头像</label>
          <button @click="changeAvatar" class="upload-btn">更换头像</button>
        </div>
      </div>

      <!-- 字体设置 -->
      <div class="settings-section">
        <h3>字体</h3>
        <div class="setting-item">
          <label>自定义字体</label>
          <button @click="uploadFont" class="upload-btn">上传字体</button>
          <span class="hint">支持 .ttf 格式</span>
        </div>
      </div>

      <!-- 音效设置 -->
      <div class="settings-section">
        <h3>音效</h3>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="localSoundEnabled">
            启用音效
          </label>
        </div>
        <div v-if="localSoundEnabled" class="sound-uploads">
          <div class="sound-item">
            <span>按键音效</span>
            <button @click="uploadSound('keypress')" class="upload-btn-small">上传</button>
            <button @click="testSound('keypress')" class="test-btn">试听前3s</button>
          </div>
          <div class="sound-item">
            <span>错误音效</span>
            <button @click="uploadSound('error')" class="upload-btn-small">上传</button>
            <button @click="testSound('error')" class="test-btn">试听前3s</button>
          </div>
          <div class="sound-item">
            <span>完成音效</span>
            <button @click="uploadSound('complete')" class="upload-btn-small">上传</button>
            <button @click="testSound('complete')" class="test-btn">试听前3s</button>
          </div>
        </div>
      </div>

      <!-- 震动设置 -->
      <div class="settings-section">
        <h3>震动</h3>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="localVibrationEnabled">
            启用错误震动
          </label>
        </div>
      </div>

      <!-- 数据管理 -->
      <div class="settings-section">
        <h3>💾 数据管理</h3>
        <div class="setting-item">
          <button @click="exportData" class="action-btn export">导出存档</button>
          <button @click="importData" class="action-btn import">导入存档</button>
        </div>
      </div>

      <!-- 关于 -->
      <div class="settings-section">
        <h3>ℹ️ 关于</h3>
        <div class="about-info">
          <p>打字游戏 v1.0.0</p>
          <p>基于 Electron + Vue 3 + Flask</p>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useConfigStore } from '@/stores/configStore'
import { useUserStore } from '@/stores/userStore'
import { api } from '@/services/api'
import { audioService } from '@/services/audioService'
import Modal from '@/components/Common/Modal.vue'

const configStore = useConfigStore()
const userStore = useUserStore()

const visible = defineModel()

const localUserName = ref(userStore.name)
const localSoundEnabled = ref(configStore.soundEnabled)
const localVibrationEnabled = ref(configStore.vibrationEnabled)

// 更新用户名
const updateUserName = async () => {
  if (localUserName.value.trim()) {
    await api.put('/gamer', { name: localUserName.value })
    await userStore.fetchUserInfo()
    alert('用户名更新成功')
  }
}

// 更换头像
const changeAvatar = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const res = await api.uploadFile('/upload/avatar', file)
    if (res.code === 200) {
      // 触发头像更新事件，让 UserInfo 组件刷新
      const event = new CustomEvent('avatar-updated')
      window.dispatchEvent(event)
      alert('头像上传成功')
    } else {
      alert('上传失败：' + res.message)
    }
  }
  input.click()
}

// 上传字体
const uploadFont = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.ttf'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const res = await api.uploadFile('/upload/font', file)
    if (res.code === 200) {
      // 重新加载字体（使用静态资源 URL）
      const fontUrl = api.getStaticUrlWithTimestamp('font/default.ttf')
      const style = document.createElement('style')
      style.textContent = `
        @font-face {
          font-family: 'CustomFont';
          src: url('${fontUrl}') format('truetype');
        }
        body {
          font-family: 'CustomFont', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        }
      `
      // 移除旧的字体样式
      const oldStyle = document.querySelector('#dynamic-font-style')
      if (oldStyle) oldStyle.remove()
      style.id = 'dynamic-font-style'
      document.head.appendChild(style)
      alert('字体上传成功')
    } else {
      alert('上传失败：' + res.message)
    }
  }
  input.click()
}

// 上传音效
const uploadSound = async (type) => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.mp3'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const endpoints = {
      keypress: '/upload/voice/keypress',
      error: '/upload/voice/error',
      complete: '/upload/voice/complete'
    }
    
    const res = await api.uploadFile(endpoints[type], file)
    if (res.code === 200) {
      alert('音效上传成功，应用将刷新')
      window.location.reload()  // 强制刷新页面
    } else {
      alert('上传失败：' + res.message)
    }
  }
  input.click()
}

// 试听音效
const testSound = (type) => {
  audioService.preview(type)
}

// 导出数据
const exportData = async () => {
  const res = await api.post('/export/data')
  if (res.code === 200) {
    alert(`数据已导出到: ${res.data.path}`)
  } else {
    alert('导出失败：' + res.message)
  }
}

// 导入数据
const importData = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.zip'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    const res = await api.uploadFile('/import/data', file)
    if (res.code === 200) {
      alert('数据导入成功，应用将重启')
      if (window.electronAPI) {
        window.electronAPI.restartApp()
      } else {
        window.location.reload()
      }
    } else {
      alert('导入失败：' + res.message)
    }
  }
  input.click()
}

// 保存音效开关
watch(localSoundEnabled, async (val) => {
  await configStore.updateConfig({ soundEnabled: val })
  audioService.setEnabled(val)
})

// 保存震动开关
watch(localVibrationEnabled, async (val) => {
  await configStore.updateConfig({ vibrationEnabled: val })
})
</script>

<style scoped>
.settings-panel {
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
}

.settings-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.settings-section h3 {
  margin-bottom: 12px;
  font-size: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.setting-item label {
  min-width: 80px;
}

.setting-item input[type="text"] {
  flex: 1;
  padding: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
}

.hint {
  font-size: 12px;
  color: var(--text-secondary);
}

.save-btn, .upload-btn, .action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background: var(--primary-color);
  color: white;
}

.save-btn:hover {
  opacity: 0.9;
}

.upload-btn {
  background: #4caf50;
  color: white;
}

.upload-btn:hover {
  opacity: 0.9;
}

.upload-btn-small {
  padding: 4px 8px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.upload-btn-small:hover {
  opacity: 0.9;
}

.test-btn {
  padding: 4px 8px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.test-btn:hover {
  opacity: 0.9;
}

.action-btn {
  margin-right: 12px;
}

.action-btn.export {
  background: #2196f3;
  color: white;
}

.action-btn.import {
  background: #ff9800;
  color: white;
}

.action-btn:hover {
  opacity: 0.9;
}

.sound-uploads {
  margin-top: 8px;
  padding-left: 20px;
}

.sound-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.sound-item span {
  width: 80px;
}

.about-info {
  color: var(--text-secondary);
  font-size: 14px;
}
</style>