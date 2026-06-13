<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="confirm-overlay" @click.self="cancel">
        <div class="confirm-container">
          <div class="confirm-header">
            <span class="confirm-icon" :class="type">{{ icon }}</span>
            <h3>{{ title }}</h3>
          </div>
          <div class="confirm-body"><p>{{ message }}</p></div>
          <div class="confirm-footer">
            <button class="confirm-btn cancel" @click="cancel">{{ cancelText }}</button>
            <button class="confirm-btn confirm" :class="type" @click="confirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'

const visible = ref(false)
const title = ref('提示')
const message = ref('')
const type = ref('info')
const confirmText = ref('确定')
const cancelText = ref('取消')
let resolvePromise = null

const icon = computed(() => {
  switch (type.value) {
    case 'warning': return '⚠️'
    case 'error': return '❌'
    case 'success': return '✅'
    default: return '❓'
  }
})

const show = (options) => {
  return new Promise((resolve) => {
    title.value = options.title || '提示'
    message.value = options.message || '确定要执行此操作吗？'
    type.value = options.type || 'info'
    confirmText.value = options.confirmText || '确定'
    cancelText.value = options.cancelText || '取消'
    visible.value = true
    resolvePromise = resolve
  })
}

const confirm = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(true)
}

const cancel = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(false)
}

defineExpose({ show })
</script>

<style scoped>
.confirm-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 3000; }
.confirm-container { background: var(--bg-primary); border-radius: 12px; width: 400px; max-width: 90%; box-shadow: var(--shadow); }
.confirm-header { display: flex; align-items: center; gap: 12px; padding: 20px 24px; border-bottom: 1px solid var(--border-color); }
.confirm-icon { font-size: 24px; }
.confirm-header h3 { margin: 0; font-size: 18px; }
.confirm-body { padding: 24px; }
.confirm-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid var(--border-color); }
.confirm-btn { padding: 8px 20px; border: none; border-radius: 6px; cursor: pointer; }
.confirm-btn.cancel { background: var(--bg-secondary); border: 1px solid var(--border-color); }
.confirm-btn.confirm { background: var(--primary-color); color: white; }
.confirm-btn.confirm.warning { background: #ff9800; }
.confirm-btn.confirm.error { background: #f44336; }
</style>