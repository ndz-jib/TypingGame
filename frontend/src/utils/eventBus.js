const listeners = new Map()

export const eventBus = {
  on(event, callback) {
    if (!listeners.has(event)) {
      listeners.set(event, [])
    }
    listeners.get(event).push(callback)
  },

  off(event, callback) {
    if (!listeners.has(event)) return
    const callbacks = listeners.get(event)
    const index = callbacks.indexOf(callback)
    if (index !== -1) callbacks.splice(index, 1)
  },

  emit(event, data) {
    if (!listeners.has(event)) return
    listeners.get(event).forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`事件 ${event} 执行错误:`, error)
      }
    })
  },

  once(event, callback) {
    const wrapper = (data) => {
      callback(data)
      this.off(event, wrapper)
    }
    this.on(event, wrapper)
  },

  clear() {
    listeners.clear()
  }
}