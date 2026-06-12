# -*- coding: utf-8 -*-
# gameControllerImpl.py
# 游戏控制器模拟实现框架（Mock Implementation）
# 用途：提供所有 API 的默认返回值，使应用能够启动并正常运行。
# 后续开发只需将此文件中的模拟数据替换为真实业务逻辑即可。

from datetime import datetime
from controller.gameController import GameController


class GameControllerImpl(GameController):
    """
    GameController 的模拟实现。
    所有方法返回符合规范的固定数据，不执行任何真实 IO 操作。
    开发者应在此基础上实现具体的文件读写、数据处理等业务。
    """

    def __init__(self):
        # 可在此处初始化真正的工具类，如 FileManageTool 等
        # 目前为模拟状态，无需任何初始化
        super().__init__()

    # ==================== 健康检查 ====================
    def health_check(self):
        # 模拟：总是返回健康状态
        return {
            "code": 200,
            "message": "ok",
            "data": {
                "status": "healthy",
                "dataIntegrity": True,
                "lastCheck": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    # ==================== 玩家信息 ====================
    def get_gamer(self):
        # 模拟返回一个预定义的玩家档案
        return {
            "code": 200,
            "message": "success",
            "data": {
                "nickname": "Player",
                "level": 1,
                "playStats": {
                    "totalGames": 0,
                    "totalPlayTime": 0,
                    "modeStats": {
                        "wordMode": {"games": 0, "bestWPM": 0, "avgAccuracy": 1.0},
                        "articleMode": {"games": 0, "bestWPM": 0, "avgAccuracy": 1.0}
                    }
                }
            }
        }

    def update_gamer(self, update_data):
        # 模拟：直接返回传入的更新数据，表示更新成功
        return {"code": 200, "message": "更新成功", "data": update_data}

    # ==================== 单词表 ====================
    def get_vocabulary(self, page=1, page_size=20, letter=None):
        # 模拟：返回一个固定的单词列表，忽略分页参数
        mock_words = [
            {"word": "apple", "note": "苹果", "firstLetter": "A"},
            {"word": "banana", "note": "香蕉", "firstLetter": "B"},
            {"word": "cherry", "note": "樱桃", "firstLetter": "C"}
        ]
        # 简单模拟分页（始终返回所有）
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": len(mock_words),
                "page": page,
                "pageSize": page_size,
                "list": mock_words
            }
        }

    def search_vocabulary(self, keyword, case_sensitive=False):
        # 模拟：返回空结果
        return {
            "code": 200,
            "message": "success",
            "data": {"total": 0, "page": 1, "pageSize": 0, "list": []}
        }

    def add_vocabulary(self, word, note):
        # 模拟：添加成功
        return {"code": 200, "message": "添加成功", "data": {"word": word, "note": note}}

    def delete_vocabulary(self, word):
        # 模拟：删除成功
        return {"code": 200, "message": "删除成功", "data": None}

    def clear_vocabulary(self):
        # 模拟：清空成功
        return {"code": 200, "message": "单词表已清空", "data": None}

    def update_word_note(self, word, note):
        # 模拟：更新注释成功
        return {"code": 200, "message": "更新成功", "data": {"word": word, "note": note}}

    # ==================== 错词表 ====================
    def record_mistake(self, word):
        # 模拟：记录成功
        return {"code": 200, "message": "错词记录成功", "data": None}

    def get_mistake_list(self, sort_by="time", page=1, page_size=20):
        # 模拟返回一个固定的错词列表
        mock_mistakes = [
            {"word": "apple", "errorCount": 3, "lastErrorTime": "2025-01-01 12:00:00", "firstLetter": "A"},
            {"word": "banana", "errorCount": 1, "lastErrorTime": "2025-01-02 12:00:00", "firstLetter": "B"}
        ]
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total": len(mock_mistakes),
                "page": page,
                "pageSize": page_size,
                "list": mock_mistakes
            }
        }

    def search_mistake(self, keyword, case_sensitive=False):
        # 模拟：返回空结果
        return {
            "code": 200,
            "message": "success",
            "data": {"total": 0, "page": 1, "pageSize": 0, "list": []}
        }

    def delete_mistake(self, word):
        # 模拟：删除成功
        return {"code": 200, "message": "删除成功", "data": None}

    def clear_mistake(self):
        # 模拟：清空成功
        return {"code": 200, "message": "错词表已清空", "data": None}

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

    # ==================== 内部辅助方法（已由抽象类定义，这里为空实现） ====================
    def _remove_from_mistake(self, word):
        pass

    def _add_to_mistake(self, word):
        pass

    def _add_words_to_vocabulary(self, words):
        return []