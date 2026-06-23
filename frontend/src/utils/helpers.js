/**
 * 从文本中提取指定位置的单词
 * 用于文章模式的错词记录
 */
export const extractWordAtPosition = (text, position) => {
  // 找到单词边界（字母范围）
  let start = position
  let end = position
  
  // 向前找单词开头
  while (start > 0 && /[a-zA-Z]/.test(text[start - 1])) {
    start--
  }
  
  // 向后找单词结尾
  while (end < text.length && /[a-zA-Z]/.test(text[end])) {
    end++
  }
  
  // 如果当前位置不是字母，返回null
  if (!/[a-zA-Z]/.test(text[position])) {
    return null
  }
  
  return text.substring(start, end)
}