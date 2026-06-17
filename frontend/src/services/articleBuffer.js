/**
 * 文章缓冲区服务
 * 用于大文件分块加载，避免一次性加载过多内容
 */

class ArticleBuffer {
  constructor(content, chunkSize = 5000) {
    this.content = content
    this.chunkSize = chunkSize
    this.chunks = this.splitIntoChunks(content)
    this.loadedChunks = new Set()
    this.bufferSize = 2 // 前后各缓冲2个块
  }

  splitIntoChunks(content) {
    const chunks = []
    for (let i = 0; i < content.length; i += this.chunkSize) {
      chunks.push(content.slice(i, i + this.chunkSize))
    }
    return chunks
  }

  getCharPosition(globalIndex) {
    let offset = 0
    for (let i = 0; i < this.chunks.length; i++) {
      const chunkLen = this.chunks[i].length
      if (globalIndex < offset + chunkLen) {
        return { chunkIndex: i, localIndex: globalIndex - offset }
      }
      offset += chunkLen
    }
    return null
  }

  getChar(globalIndex) {
    const pos = this.getCharPosition(globalIndex)
    if (pos) {
      return this.chunks[pos.chunkIndex][pos.localIndex]
    }
    return null
  }

  loadChunk(chunkIndex) {
    if (chunkIndex < 0 || chunkIndex >= this.chunks.length) return
    if (this.loadedChunks.has(chunkIndex)) return

    this.loadedChunks.add(chunkIndex)
    return {
      chunkIndex,
      content: this.chunks[chunkIndex],
      startOffset: this.getChunkStartOffset(chunkIndex)
    }
  }

  loadChunksAround(globalIndex) {
    const pos = this.getCharPosition(globalIndex)
    if (!pos) return []

    const loaded = []
    const startChunk = Math.max(0, pos.chunkIndex - this.bufferSize)
    const endChunk = Math.min(this.chunks.length - 1, pos.chunkIndex + this.bufferSize)

    for (let i = startChunk; i <= endChunk; i++) {
      const result = this.loadChunk(i)
      if (result) loaded.push(result)
    }
    return loaded
  }

  getChunkStartOffset(chunkIndex) {
    let offset = 0
    for (let i = 0; i < chunkIndex; i++) {
      offset += this.chunks[i].length
    }
    return offset
  }

  isLoaded(globalIndex) {
    const pos = this.getCharPosition(globalIndex)
    return pos ? this.loadedChunks.has(pos.chunkIndex) : false
  }

  get totalChars() {
    return this.content.length
  }

  // 获取指定范围的文本（确保范围内已加载）
  getTextRange(start, end) {
    if (!this.isLoaded(start) || !this.isLoaded(end)) {
      this.loadChunksAround(start)
      this.loadChunksAround(end)
    }
    return this.content.slice(start, end)
  }
}

export default ArticleBuffer