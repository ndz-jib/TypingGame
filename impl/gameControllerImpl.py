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
        data = self.file_tool.read_json(CONFIG_PATH, DEFAULT_CONFIG)
        return {"code": 200, "message": "success", "data": data}

    def update_config(self, update_data):
        current = self.file_tool.read_json(CONFIG_PATH, DEFAULT_CONFIG)
        
        def deep_update(base, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(current, update_data)
        
        if self.file_tool.write_json(CONFIG_PATH, current):
            return {"code": 200, "message": "更新成功", "data": current}
        return {"code": 500, "message": "更新失败", "data": None}

    def reset_config(self):
        """重置配置"""
        try:
            self.file_tool.write_json(CONFIG_PATH, DEFAULT_CONFIG)
            logger.info("已重置配置")
            return {"code": 200, "message": "已恢复默认设置", "data": None}
        except Exception as e:
            logger.error(f"重置失败: {str(e)}")
            return {"code": 500, "message": f"重置失败: {str(e)}", "data": None}

    # ==================== 文章管理 ====================
    def get_article_list(self):
        """获取文章列表"""
        try:
            articles = self.article_splitter.get_article_list()
            return {"code": 200, "message": "success", "data": articles}
        except Exception as e:
            logger.error(f"获取文章列表失败: {str(e)}")
            return {"code": 500, "message": f"获取失败: {str(e)}", "data": []}

    def get_article_content(self, filename):
        """获取文章内容"""
        try:
            # 安全检查：防止路径遍历攻击
            if '..' in filename or filename.startswith('/'):
                return {"code": 400, "message": "非法文件名", "data": None}
            
            content = self.article_splitter.get_article_content(filename)
            if content is None:
                return {"code": 404, "message": "文章不存在", "data": None}
            
            return {"code": 200, "message": "success", "data": {"filename": filename, "content": content}}
        except Exception as e:
            logger.error(f"获取文章内容失败: {str(e)}")
            return {"code": 500, "message": f"获取失败: {str(e)}", "data": None}

    def import_article(self, content, filename, auto_split=True):
        """
        导入文章
        
        参数:
            content: 文章内容
            filename: 文件名
            auto_split: 是否自动拆分大文件
        """
        try:
            # 检查是否需要拆分
            is_exceed, message = self.article_splitter.check_size_limit(content)
            
            if is_exceed and auto_split:
                # 拆分文章
                parts = self.article_splitter.split_article(content, filename)
                saved_files = self.article_splitter.save_split_articles(parts)
                
                # 对每个片段进行分词并添加新词
                all_new_words = []
                for part in parts:
                    words = self.splitter.extract_word_cards(part["content"])
                    new_words = self._add_words_to_vocabulary(words)
                    all_new_words.extend(new_words)
                
                return {
                    "code": 200,
                    "message": f"文章已拆分保存，共 {len(parts)} 个片段",
                    "data": {
                        "filename": filename,
                        "split": True,
                        "parts": saved_files,
                        "totalParts": len(parts),
                        "newWordsAdded": len(set(all_new_words)),
                        "warning": message
                    }
                }
            else:
                # 保存原文
                os.makedirs(TXT_DIR, exist_ok=True)
                file_path = os.path.join(TXT_DIR, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 分词并添加新词
                words = self.splitter.extract_word_cards(content)
                new_words = self._add_words_to_vocabulary(words)
                
                return {
                    "code": 200,
                    "message": "文章导入成功",
                    "data": {
                        "filename": filename,
                        "split": False,
                        "totalWords": len(words),
                        "newWordsAdded": len(new_words),
                        "wordList": words[:50]
                    }
                }
                
        except Exception as e:
            logger.error(f"文章导入失败: {str(e)}")
            return {"code": 500, "message": f"导入失败: {str(e)}", "data": None}

    def import_vocabulary(self, content, filename):
        """从 TXT 导入单词表"""
        try:
            # 提取单词
            words = self.splitter.extract_word_cards(content)
            unique_words = list(dict.fromkeys(words))  # 去重保留顺序
            
            vocab_data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
            new_words = []
            existing_words = []
            
            for word in unique_words:
                first_letter = word[0].upper()
                if first_letter not in vocab_data:
                    vocab_data[first_letter] = []
                
                found = False
                for w, n in vocab_data[first_letter]:
                    if w == word:
                        found = True
                        break
                
                if found:
                    existing_words.append(word)
                else:
                    vocab_data[first_letter].append([word, ""])
                    new_words.append(word)
            
            # 保持排序
            for letter in vocab_data:
                vocab_data[letter].sort(key=lambda x: x[0].lower())
            
            self.file_tool.write_json(VOCABULARY_PATH, vocab_data)
            
            logger.info(f"单词表导入完成: {filename}, 新增{len(new_words)}, 已存在{len(existing_words)}")
            
            return {
                "code": 200,
                "message": "单词表导入成功",
                "data": {
                    "totalWords": len(unique_words),
                    "newWordsAdded": len(new_words),
                    "existingWordsSkipped": len(existing_words),
                    "wordList": new_words[:50]  # 最多返回50个
                }
            }
        
        except Exception as e:
            logger.error(f"单词表导入失败: {str(e)}")
            return {"code": 500, "message": f"导入失败: {str(e)}", "data": None}

    # ==================== 随机单词 ====================
    def get_random_words(self, count=10):
        data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        
        all_words = []
        for letter, words in data.items():
            for word, note in words:
                all_words.append({"word": word, "note": note})
        
        if len(all_words) == 0:
            return {"code": 200, "message": "success", "data": {"words": []}}
        
        random_count = min(count, len(all_words))
        selected = random.sample(all_words, random_count)
        
        return {"code": 200, "message": "success", "data": {"words": selected}}

    # ==================== 数据导入导出 ====================
    def export_data(self):
        try:
            zip_path, filename = self.packager.export_data()
            return {
                "code": 200,
                "message": "导出包生成成功",
                "data": {
                    "filePath": zip_path,
                    "fileName": filename
                }
            }
        except Exception as e:
            logger.error(f"导出失败: {str(e)}")
            return {"code": 500, "message": f"导出失败: {str(e)}", "data": None}

    def import_data(self, file_path):
        try:
            valid, msg = self.packager.validate_import_package(file_path)
            if not valid:
                return {"code": 400, "message": msg, "data": None}
            
            backup_path = self.file_tool.backup_data("before_import")
            
            from config import DATA_DIR
            if self.packager.import_data(file_path, DATA_DIR):
                self.health_check()
                
                return {
                    "code": 200,
                    "message": "数据导入成功，请重启应用",
                    "data": {"backupPath": backup_path}
                }
            else:
                return {"code": 500, "message": "导入失败", "data": None}
                
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            return {"code": 500, "message": f"导入失败: {str(e)}", "data": None}

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
        """记录单词模式游玩结果"""
        try:
            current = self.file_tool.read_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
            
            stats = current['playStats']['modeStats']['wordMode']
            
            # 更新游戏次数
            stats['games'] += 1
            
            # 更新最佳 WPM
            if wpm > stats['bestWPM']:
                stats['bestWPM'] = wpm
            
            # 更新平均准确率
            old_avg = stats['avgAccuracy']
            games_count = stats['games']
            new_avg = (old_avg * (games_count - 1) + accuracy) / games_count
            stats['avgAccuracy'] = round(new_avg, 3)
            
            # 更新总游玩时间
            current['playStats']['totalPlayTime'] += play_time
            
            # 更新总游戏次数
            current['playStats']['totalGames'] += 1
            
            self.file_tool.write_json(GAMER_DATA_PATH, current)
            
            logger.info(f"单词模式记录: WPM={wpm}, 准确率={accuracy}, 用时={play_time}s")
            
            return {"code": 200, "message": "记录成功", "data": current['playStats']['modeStats']['wordMode']}
        
        except Exception as e:
            logger.error(f"记录单词模式结果失败: {str(e)}")
            return {"code": 500, "message": f"记录失败: {str(e)}", "data": None}

    def record_article_mode_result(self, wpm, accuracy, play_time):
        """记录文章模式游玩结果"""
        try:
            current = self.file_tool.read_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
            
            stats = current['playStats']['modeStats']['articleMode']
            
            # 更新游戏次数
            stats['games'] += 1
            
            # 更新最佳 WPM
            if wpm > stats['bestWPM']:
                stats['bestWPM'] = wpm
            
            # 更新平均准确率
            old_avg = stats['avgAccuracy']
            games_count = stats['games']
            new_avg = (old_avg * (games_count - 1) + accuracy) / games_count
            stats['avgAccuracy'] = round(new_avg, 3)
            
            # 更新总游玩时间
            current['playStats']['totalPlayTime'] += play_time
            
            # 更新总游戏次数
            current['playStats']['totalGames'] += 1
            
            self.file_tool.write_json(GAMER_DATA_PATH, current)
            
            logger.info(f"文章模式记录: WPM={wpm}, 准确率={accuracy}, 用时={play_time}s")
            
            return {"code": 200, "message": "记录成功", "data": current['playStats']['modeStats']['articleMode']}
        
        except Exception as e:
            logger.error(f"记录文章模式结果失败: {str(e)}")
            return {"code": 500, "message": f"记录失败: {str(e)}", "data": None}

    # ==================== 文章行切分 ====================
    def process_article_to_lines(self, content, line_width):
        """处理文章为行数组"""
        try:
            if not content:
                return {"code": 400, "message": "内容不能为空", "data": None}
            
            # 限制行宽范围
            line_width = max(20, min(100, line_width))
            
            # 切分为行
            lines = self.line_splitter.split_to_lines(content, line_width)
            
            # 计算统计信息
            total_chars = len(content)
            total_lines = len(lines)
            
            logger.info(f"文章行切分完成: 总字符数={total_chars}, 总行数={total_lines}, 行宽={line_width}")
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "lines": lines,
                    "totalChars": total_chars,
                    "totalLines": total_lines,
                    "lineWidth": line_width
                }
            }
        
        except Exception as e:
            logger.error(f"文章行切分失败: {str(e)}")
            return {"code": 500, "message": f"处理失败: {str(e)}", "data": None}

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
        """
        批量添加单词到单词表（注释为空）
        返回新添加的单词列表
        """
        vocab_data = self.file_tool.read_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        new_words = []
        
        for word in words:
            first_letter = word[0].upper()
            if first_letter not in vocab_data:
                vocab_data[first_letter] = []
            
            found = False
            for w, n in vocab_data[first_letter]:
                if w == word:
                    found = True
                    break
            
            if not found:
                vocab_data[first_letter].append([word, ""])
                new_words.append(word)
        
        # 保持排序
        for letter in vocab_data:
            vocab_data[letter].sort(key=lambda x: x[0].lower())
        
        self.file_tool.write_json(VOCABULARY_PATH, vocab_data)
        logger.debug(f"批量添加 {len(new_words)} 个新词到单词表")
        
        return new_words
