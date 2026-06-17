// API 基础配置
export const API_BASE_URL = 'http://localhost:5000/api'

// 单词模式布局配置
export const WORD_LAYOUTS = {
  '1': { name: '1x1', cols: 1, rows: 1, cardCount: 1 },
  '2': { name: '2x1', cols: 2, rows: 1, cardCount: 2 },
  '3': { name: '3x1', cols: 3, rows: 1, cardCount: 3 },
  '4': { name: '2x2', cols: 2, rows: 2, cardCount: 4 },
  '5': { name: '2x2+1', cols: 2, rows: 3, cardCount: 5, specialLayout: 'last-centered' },
  '6': { name: '2x3', cols: 3, rows: 2, cardCount: 6 },
  '7': { name: '3+4', cols: 4, rows: 2, cardCount: 7, specialLayout: 'first-row-3' },
  '8': { name: '2x4', cols: 4, rows: 2, cardCount: 8 },
  '9': { name: '3x3', cols: 3, rows: 3, cardCount: 9 }
}

// 倒计时选项（秒）
export const TIMER_OPTIONS = {
  min: 30,
  max: 300,
  step: 30,
  default: 120
}

// 文章模式配置
export const ARTICLE_CONFIG = {
  defaultDisplayLines: 4,
  minDisplayLines: 2,
  maxDisplayLines: 6,
  maxCharsPerArticle: 1500,  // 单篇最大字符数
  bufferLines: 2              // 缓冲区行数
}

// 单词模式配置
export const WORD_CONFIG = {
  defaultWordCount: 10,
  minWordCount: 1,
  maxWordCount: 100
}

// 特殊字符占位（固定，不可配置）
export const SPECIAL_CHARS = {
  space: '·',      // 空格占位符
  newline: '¶'     // 换行符占位符
}

// 音效类型
export const SOUND_TYPES = {
  KEYPRESS: 'keypress',
  ERROR: 'error',
  COMPLETE: 'complete'
}

// 音效文件路径（本地）
export const SOUND_PATHS = {
  [SOUND_TYPES.KEYPRESS]: './data/voice/keypress.mp3',
  [SOUND_TYPES.ERROR]: './data/voice/error.mp3',
  [SOUND_TYPES.COMPLETE]: './data/voice/complete.mp3'
}

// 静态资源路径
export const ASSETS = {
  avatar: './data/picture/avatar.png',
  font: './data/font/default.ttf'
}

// 本地存储 Key
export const STORAGE_KEYS = {
  THEME: 'typing_theme',
  GAME_STATE: 'typing_game_state',
  USER_SETTINGS: 'typing_user_settings'
}

// 字母表
export const ALPHABETS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// 错误码
export const ERROR_CODES = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
}

// 消息提示
export const MESSAGES = {
  // 成功
  IMPORT_SUCCESS: '导入成功',
  SAVE_SUCCESS: '保存成功',
  DELETE_SUCCESS: '删除成功',
  
  // 错误
  IMPORT_FAILED: '导入失败',
  SAVE_FAILED: '保存失败',
  NETWORK_ERROR: '网络连接失败',
  
  // 确认
  CONFIRM_DELETE: '确定要删除吗？',
  CONFIRM_CLEAR: '确定要清空吗？此操作不可恢复。',
  CONFIRM_EXIT: '确定要退出吗？未保存的进度将丢失。',
  
  // 警告
  FILE_TOO_LARGE: '文件过大，将被拆分',
  NO_WORDS_FOUND: '未检测到有效单词'
}

// 正则表达式
export const REGEX = {
  // 单词匹配（字母开头，可包含连字符和撇号）
  WORD: /[a-zA-Z]+(?:[-'][a-zA-Z]+)*/g,
  // 中文匹配
  CHINESE: /[\u4e00-\u9fa5]/g,
  // 标点符号
  PUNCTUATION: /[，。！？；：""''《》【】（）,.!?;:"'`~@#$%^&*()_+={}[\]|\\<>]/g
}