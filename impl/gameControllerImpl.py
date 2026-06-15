# -*- coding: utf-8 -*-
# gameControllerImpl.py
# 游戏控制器模拟实现框架（Mock Implementation）
# 用途：提供所有 API 的默认返回值，使应用能够启动并正常运行。
# 后续开发只需将此文件中的模拟数据替换为真实业务逻辑即可。

import os
import shutil
import random
from datetime import datetime
from flask import jsonify
from controller.gameController import GameController
from tool.fileManageTool import FileManageTool
from tool.textSplitter import TextSplitter
from tool.lineSplitter import LineSplitter
from tool.articleSplitter import ArticleSplitter
from tool.scoreCalculator import ScoreCalculator
from tool.dataPackager import DataPackager
from tool.loggerTool import logger
from config import (
    GAMER_DATA_PATH, VOCABULARY_PATH, MISTAKE_PATH, CONFIG_PATH,
    TXT_DIR, PICTURE_DIR, FONT_DIR, VOICE_DIR,
    DEFAULT_GAMER_DATA, DEFAULT_VOCABULARY, DEFAULT_CONFIG,
    BACKUP_DIR, MAX_ARTICLE_CHARS
)


class GameControllerImpl(GameController):
    """
    GameController 的模拟实现。
    所有方法返回符合规范的固定数据，不执行任何真实 IO 操作。
    开发者应在此基础上实现具体的文件读写、数据处理等业务。
    """

    def __init__(self):
        self.file_tool = FileManageTool()
        self.splitter = TextSplitter()
        self.line_splitter = LineSplitter()
        self.article_splitter = ArticleSplitter()
        self.calculator = ScoreCalculator()
        self.packager = DataPackager()

    # ==================== 健康检查 ====================
    def health_check(self):
        from config import ensure_directories
        
        try:
            ensure_directories()
            
            files_ok = True
            if not os.path.exists(GAMER_DATA_PATH):
                self.file_tool.write_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
                files_ok = False
            
            if not os.path.exists(VOCABULARY_PATH):
                self.file_tool.write_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
                files_ok = False
            
            if not os.path.exists(MISTAKE_PATH):
                self.file_tool.write_json(MISTAKE_PATH, {})
                files_ok = False
            
            if not os.path.exists(CONFIG_PATH):
                self.file_tool.write_json(CONFIG_PATH, DEFAULT_CONFIG)
                files_ok = False
            
            for dir_path in [TXT_DIR, VOICE_DIR, FONT_DIR, PICTURE_DIR]:
                os.makedirs(dir_path, exist_ok=True)
            
            logger.info("健康检查完成")
            
            return {
                "code": 200,
                "message": "ok",
                "data": {
                    "status": "healthy",
                    "dataIntegrity": files_ok,
                    "lastCheck": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                "code": 500,
                "message": "健康检查失败",
                "data": {
                    "status": "unhealthy",
                    "error": str(e)
                }
            }

    # ==================== 玩家信息 ====================
    def get_gamer(self):
        data = self.file_tool.read_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
        return {"code": 200, "message": "success", "data": data}
    
    def update_gamer(self, update_data):
        current = self.file_tool.read_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
        
        def deep_update(base, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(current, update_data)
        
        if self.file_tool.write_json(GAMER_DATA_PATH, current):
            return {"code": 200, "message": "更新成功", "data": current}
        return {"code": 500, "message": "更新失败", "data": None}

    # ==================== 单词表 ====================
    def get_vocabulary(self, page=1, page_size=20, letter=None):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        
        all_words = []
        for l, words in data.items():
            if letter is None or l == letter:
                for word, note in words:
                    all_words.append({
                        "word": word,
                        "note": note,
                        "firstLetter": l
                    })
        
        total = len(all_words)
        start = (page - 1) * page_size
        end = start + page_size
        page_list = all_words[start:end]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "list": page_list
            }
        }

    def search_vocabulary(self, keyword, case_sensitive=False):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        
        results = []
        search_key = keyword if case_sensitive else keyword.lower()
        
        for letter, words in data.items():
            for word, note in words:
                compare_word = word if case_sensitive else word.lower()
                if search_key in compare_word:
                    results.append({
                        "word": word,
                        "note": note,
                        "firstLetter": letter
                    })
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": len(results),
                "page": 1,
                "pageSize": len(results),
                "list": results
            }
        }

    def add_vocabulary(self, word, note):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        
        first_letter = word[0].upper()
        if first_letter not in data:
            data[first_letter] = []
        
        found = False
        for i, (w, n) in enumerate(data[first_letter]):
            if w == word:
                if note and note.strip():
                    data[first_letter][i][1] = note
                found = True
                break
        
        if not found:
            data[first_letter].append([word, note or ""])
            data[first_letter].sort(key=lambda x: x[0].lower())
        
        if self.file_tool.write_json(VOCABULARY_PATH, data):
            return {"code": 200, "message": "添加成功", "data": {"word": word, "note": note}}
        return {"code": 500, "message": "添加失败", "data": None}

    def delete_vocabulary(self, word):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        first_letter = word[0].upper()
        
        if first_letter in data:
            data[first_letter] = [item for item in data[first_letter] if item[0] != word]
            if not data[first_letter]:
                del data[first_letter]
            
            if self.file_tool.write_json(VOCABULARY_PATH, data):
                self._remove_from_mistake(word)
                return {"code": 200, "message": "删除成功", "data": None}
        
        return {"code": 404, "message": "单词不存在", "data": None}

    def clear_vocabulary(self):
        if self.file_tool.write_json(VOCABULARY_PATH, {}):
            return {"code": 200, "message": "单词表已清空", "data": None}
        return {"code": 500, "message": "清空失败", "data": None}

    def update_word_note(self, word, note):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        first_letter = word[0].upper()
        
        if first_letter in data:
            for i, (w, n) in enumerate(data[first_letter]):
                if w == word:
                    data[first_letter][i][1] = note
                    if self.file_tool.write_json(VOCABULARY_PATH, data):
                        return {"code": 200, "message": "更新成功", "data": {"word": word, "note": note}}
                    break
        
        return {"code": 404, "message": "单词不存在", "data": None}

    # ==================== 错词表 ====================
    def record_mistake(self, word):
        """
        记录错词（对外 API）
        如果单词不在单词表中，自动添加（注释为空）
        """
        # 检查单词是否在单词表中
        vocab_data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        first_letter = word[0].upper()
        word_exists = False
        
        if first_letter in vocab_data:
            for w, n in vocab_data[first_letter]:
                if w == word:
                    word_exists = True
                    break
        
        # 如果不存在，添加到单词表
        if not word_exists:
            logger.info(f"错词 {word} 不在单词表中，自动添加")
            self.add_vocabulary(word, "")
        
        # 记录错词
        self._add_to_mistake(word)
        
        return {"code": 200, "message": "错词记录成功", "data": None}

    def get_mistake_list(self, sort_by="time", page=1, page_size=20):
        data = self.file_tool.read_json(MISTAKE_PATH, {})
        
        all_words = []
        for letter, words in data.items():
            for word, count, error_time in words:
                all_words.append({
                    "word": word,
                    "errorCount": count,
                    "lastErrorTime": error_time,
                    "firstLetter": letter
                })
        
        if sort_by == "count":
            all_words.sort(key=lambda x: x["errorCount"], reverse=True)
        else:
            all_words.sort(key=lambda x: x["lastErrorTime"], reverse=True)
        
        total = len(all_words)
        start = (page - 1) * page_size
        end = start + page_size
        page_list = all_words[start:end]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "list": page_list
            }
        }

    def search_mistake(self, keyword, case_sensitive=False):
        data = self.file_tool.read_json(MISTAKE_PATH, {})
        
        results = []
        search_key = keyword if case_sensitive else keyword.lower()
        
        for letter, words in data.items():
            for word, count, error_time in words:
                compare_word = word if case_sensitive else word.lower()
                if search_key in compare_word:
                    results.append({
                        "word": word,
                        "errorCount": count,
                        "lastErrorTime": error_time,
                        "firstLetter": letter
                    })
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": len(results),
                "page": 1,
                "pageSize": len(results),
                "list": results
            }
        }

    def delete_mistake(self, word):
        data = self.file_tool.read_json(MISTAKE_PATH, {})
        first_letter = word[0].upper()
        
        if first_letter in data:
            data[first_letter] = [item for item in data[first_letter] if item[0] != word]
            if not data[first_letter]:
                del data[first_letter]
            
            if self.file_tool.write_json(MISTAKE_PATH, data):
                return {"code": 200, "message": "删除成功", "data": None}
        
        return {"code": 404, "message": "错词不存在", "data": None}

    def clear_mistake(self):
        if self.file_tool.write_json(MISTAKE_PATH, {}):
            return {"code": 200, "message": "错词表已清空", "data": None}
        return {"code": 500, "message": "清空失败", "data": None}

    # ==================== 配置 ====================
    def get_config(self):
        # 模拟返回一个默认配置
        return {
            "code": 200,
            "message": "success",
            "data": {
                "customSettings": {
                    "fontSize": 16,
                    "theme": "light",
                    "avatarPath": "./data/picture/avatar.png",
                    "fontPath": "./data/font/default.ttf"
                }
            }
        }

    def update_config(self, update_data):
        # 模拟：直接返回传入的更新数据
        return {"code": 200, "message": "更新成功", "data": update_data}

    def reset_config(self):
        # 模拟：重置成功
        return {"code": 200, "message": "已恢复默认设置", "data": None}

    # ==================== 文章管理 ====================
    def get_article_list(self):
        # 模拟返回文章列表（空列表）
        return {"code": 200, "message": "success", "data": []}

    def get_article_content(self, filename):
        # 模拟返回一篇文章内容
        return {
            "code": 200,
            "message": "success",
            "data": {
                "filename": filename,
                "content": "This is a mock article content for testing."
            }
        }

    def import_article(self, content, filename, auto_split=True):
        # 模拟导入成功，返回固定统计信息
        return {
            "code": 200,
            "message": "文章导入成功",
            "data": {
                "filename": filename,
                "split": False,
                "totalWords": len(content.split()),
                "newWordsAdded": 0,
                "wordList": content.split()[:10]
            }
        }

    def import_vocabulary(self, content, filename):
        # 模拟从文本导入单词表成功
        return {
            "code": 200,
            "message": "单词表导入成功",
            "data": {
                "totalWords": 0,
                "newWordsAdded": 0,
                "existingWordsSkipped": 0,
                "wordList": []
            }
        }

    # ==================== 随机单词 ====================
    def get_random_words(self, count=10):
        # 模拟返回固定数量的随机单词
        mock_words = [{"word": f"word{i}", "note": ""} for i in range(min(count, 5))]
        return {"code": 200, "message": "success", "data": {"words": mock_words}}

    # ==================== 数据导入导出 ====================
    def export_data(self):
        # 模拟导出成功，返回一个虚假的压缩包路径
        return {
            "code": 200,
            "message": "导出包生成成功",
            "data": {
                "filePath": "./backup/mock_export.zip",
                "fileName": "mock_export.zip"
            }
        }

    def import_data(self, file_path):
        # 模拟导入成功
        return {
            "code": 200,
            "message": "数据导入成功，请重启应用",
            "data": {"backupPath": "./backup/before_import.zip"}
        }

    # ==================== 文件上传 ====================
    def upload_avatar(self, file_data, filename):
        # 模拟头像上传成功
        return {
            "code": 200,
            "message": "头像上传成功",
            "data": {"avatarPath": "./data/picture/avatar.png"}
        }

    def upload_font(self, file_data, filename):
        # 模拟字体上传成功
        return {
            "code": 200,
            "message": "字体上传成功",
            "data": {"fontPath": "./data/font/default.ttf"}
        }

    def upload_voice(self, voice_type, file_data, filename):
        # 模拟音效上传成功
        valid_types = ['keypress', 'error', 'complete']
        if voice_type not in valid_types:
            return {"code": 400, "message": f"无效的音效类型", "data": None}
        return {
            "code": 200,
            "message": f"{voice_type} 音效上传成功",
            "data": {"voicePath": f"./data/voice/{voice_type}.mp3"}
        }

    # ==================== 游戏结果记录 ====================
    def record_word_mode_result(self, wpm, accuracy, play_time):
        # 模拟记录成功，返回空统计（实际应更新玩家数据）
        return {
            "code": 200,
            "message": "记录成功",
            "data": {"games": 0, "bestWPM": 0, "avgAccuracy": 1.0}
        }

    def record_article_mode_result(self, wpm, accuracy, play_time):
        # 模拟记录成功
        return {
            "code": 200,
            "message": "记录成功",
            "data": {"games": 0, "bestWPM": 0, "avgAccuracy": 1.0}
        }

    # ==================== 文章行切分 ====================
    def process_article_to_lines(self, content, line_width):
        # 模拟行切分：简单按空格分割成行（仅用于演示）
        words = content.split()
        lines = [' '.join(words[i:i+5]) for i in range(0, len(words), 5)]
        return {
            "code": 200,
            "message": "success",
            "data": {
                "lines": lines,
                "totalChars": len(content),
                "totalLines": len(lines),
                "lineWidth": line_width
            }
        }

    # ==================== 内部辅助方法 ====================
    def _remove_from_mistake(self, word):
        """从错词表中删除单词"""
        mistake_data = self.file_tool.read_json(MISTAKE_PATH, {})
        first_letter = word[0].upper()
        
        if first_letter in mistake_data:
            mistake_data[first_letter] = [item for item in mistake_data[first_letter] if item[0] != word]
            if not mistake_data[first_letter]:
                del mistake_data[first_letter]
            self.file_tool.write_json(MISTAKE_PATH, mistake_data)

    def _add_to_mistake(self, word):
        """添加或更新错词记录（内部方法）"""
        mistake_data = self.file_tool.read_json(MISTAKE_PATH, {})
        first_letter = word[0].upper()
        
        if first_letter not in mistake_data:
            mistake_data[first_letter] = []
        
        found = False
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for i, (w, count, time) in enumerate(mistake_data[first_letter]):
            if w == word:
                mistake_data[first_letter][i][1] = count + 1
                mistake_data[first_letter][i][2] = current_time
                found = True
                break
        
        if not found:
            mistake_data[first_letter].append([word, 1, current_time])
        
        self.file_tool.write_json(MISTAKE_PATH, mistake_data)
        logger.debug(f"错词记录已更新: {word}")

    def _add_words_to_vocabulary(self, words):
        return []
