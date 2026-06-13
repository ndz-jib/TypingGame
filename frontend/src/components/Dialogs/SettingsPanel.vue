<template>
  <Modal v-model="visible" title="设置" width="600px">
    <div class="settings-panel">
      <div class="settings-section">
        <h3>👤 用户信息</h3>
        <div class="setting-item">
          <label>用户名称</label>
          <input v-model="userName" type="text" placeholder="输入用户名">
          <button class="save-btn">保存</button>
        </div>
        <div class="setting-item">
          <label>头像</label>
          <button class="upload-btn">更换头像</button>
        </div>
      </div>

      <div class="settings-section">
        <h3>🔤 字体</h3>
        <div class="setting-item">
          <label>自定义字体</label>
          <button class="upload-btn">上传字体</button>
          <span class="hint">支持 .ttf 格式</span>
        </div>
      </div>

      <div class="settings-section">
        <h3>🔊 音效</h3>
        <div class="setting-item">
          <label><input type="checkbox" v-model="soundEnabled"> 启用音效</label>
        </div>
      </div>

      <div class="settings-section">
        <h3>📳 震动</h3>
        <div class="setting-item">
          <label><input type="checkbox" v-model="vibrationEnabled"> 启用错误震动</label>
        </div>
      </div>

      <div class="settings-section">
        <h3>💾 数据管理</h3>
        <div class="setting-item">
          <button class="action-btn export">导出存档</button>
          <button class="action-btn import">导入存档</button>
        </div>
      </div>

      <div class="settings-section">
        <h3>ℹ️ 关于</h3>
        <div class="about-info">
          <p>打字游戏 v1.0.0</p>
          <p>基于 Electron + Vue 3</p>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref } from 'vue'
import Modal from '@/components/Common/Modal.vue'

const visible = defineModel()
const userName = ref('Demo User')
const soundEnabled = ref(true)
const vibrationEnabled = ref(true)
</script>

<style scoped>
.settings-panel { max-height: 500px; overflow-y: auto; padding: 4px; }
.settings-section { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
.settings-section h3 { margin-bottom: 12px; font-size: 16px; }
.setting-item { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.setting-item label { min-width: 80px; }
.setting-item input[type="text"] { flex: 1; padding: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); }
.hint { font-size: 12px; color: var(--text-secondary); }
.save-btn, .upload-btn, .action-btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; }
.save-btn { background: var(--primary-color); color: white; }
.upload-btn { background: #4caf50; color: white; }
.action-btn.export { background: #2196f3; color: white; margin-right: 12px; }
.action-btn.import { background: #ff9800; color: white; }
.about-info { color: var(--text-secondary); font-size: 14px; }
</style>