import os
from abc import ABC, abstractmethod
from datetime import datetime

# 抽象基类：游戏控制器接口
class GameController(ABC):
    """
    游戏控制器抽象基类，定义了所有业务操作的接口。
    具体的业务逻辑由子类实现。
    """

    # ==================== 初始化 ====================
    def __init__(self):
        """
        初始化控制器。
        子类可以在此处加载必要的工具、数据文件等资源。
        """
        pass

    # ==================== 玩家信息 ====================

    @abstractmethod
    def get_gamer(self):
        """
        获取当前玩家信息。
        
        返回:
            dict: 包含玩家数据的标准响应结构
        """
        pass

    @abstractmethod
    def update_gamer(self, update_data):
        """
        更新玩家信息（支持深层字典合并）。
        
        参数:
            update_data (dict): 需要更新的字段
        
        返回:
            dict: 标准响应，包含更新后的完整玩家数据
        """
        pass

    # ==================== 单词表 ====================

    @abstractmethod
    def get_vocabulary(self, page=1, page_size=20, letter=None):
        """
        分页获取单词表，可按首字母过滤。
        
        参数:
            page (int): 页码
            page_size (int): 每页条数
            letter (str, optional): 首字母过滤，None 表示所有
        
        返回:
            dict: 包含 total, page, pageSize, list 等字段的响应
        """
        pass

    @abstractmethod
    def search_vocabulary(self, keyword, case_sensitive=False):
        """
        按关键词搜索单词表。
        
        参数:
            keyword (str): 搜索关键词
            case_sensitive (bool): 是否区分大小写
        
        返回:
            dict: 搜索结果列表及其总数
        """
        pass

    @abstractmethod
    def add_vocabulary(self, word, note):
        """
        添加新单词，若已存在则更新注释。
        
        参数:
            word (str): 单词
            note (str): 注释
        
        返回:
            dict: 操作结果，包含新增或更新的单词信息
        """
        pass

    @abstractmethod
    def delete_vocabulary(self, word):
        """
        删除指定单词，并同步清理错词表中的记录。
        
        参数:
            word (str): 要删除的单词
        
        返回:
            dict: 操作结果
        """
        pass

    @abstractmethod
    def clear_vocabulary(self):
        """
        清空整个单词表。
        
        返回:
            dict: 操作结果
        """
        pass

    @abstractmethod
    def update_word_note(self, word, note):
        """
        单独更新某个单词的注释。
        
        参数:
            word (str): 单词
            note (str): 新的注释内容
        
        返回:
            dict: 操作结果
        """
        pass

    # ==================== 错词表 ====================

    @abstractmethod
    def record_mistake(self, word):
        """
        记录一个错词。若单词不在单词表中，会自动添加（注释为空）。
        
        参数:
            word (str): 出错的单词
        
        返回:
            dict: 操作结果
        """
        pass

    @abstractmethod
    def get_mistake_list(self, sort_by="time", page=1, page_size=20):
        """
        分页获取错词列表，支持按时间或错误次数排序。
        
        参数:
            sort_by (str): 排序方式，"time" 或 "count"
            page (int): 页码
            page_size (int): 每页条数
        
        返回:
            dict: 包含 total, page, pageSize, list 等字段的响应
        """
        pass

    @abstractmethod
    def search_mistake(self, keyword, case_sensitive=False):
        """
        按关键词搜索错词表。
        
        参数:
            keyword (str): 搜索关键词
            case_sensitive (bool): 是否区分大小写
        
        返回:
            dict: 搜索结果列表及其总数
        """
        pass

    @abstractmethod
    def delete_mistake(self, word):
        """
        从错词表中删除指定单词。
        
        参数:
            word (str): 要删除的错词
        
        返回:
            dict: 操作结果
        """
        pass

    @abstractmethod
    def clear_mistake(self):
        """
        清空整个错词表。
        
        返回:
            dict: 操作结果
        """
        pass

    # ==================== 配置 ====================

    @abstractmethod
    def get_config(self):
        """
        获取当前应用配置。
        
        返回:
            dict: 配置数据
        """
        pass

    @abstractmethod
    def update_config(self, update_data):
        """
        更新配置（支持深层字典合并）。
        
        参数:
            update_data (dict): 需要更新的配置字段
        
        返回:
            dict: 更新后的完整配置
        """
        pass

    @abstractmethod
    def reset_config(self):
        """
        重置配置为默认值。
        
        返回:
            dict: 操作结果
        """
        pass

    # ==================== 文章管理 ====================

    @abstractmethod
    def get_article_list(self):
        """
        获取所有已导入文章的文件名列表。
        
        返回:
            dict: 文章列表
        """
        pass

    @abstractmethod
    def get_article_content(self, filename):
        """
        根据文件名获取文章完整内容。
        
        参数:
            filename (str): 文章文件名
        
        返回:
            dict: 文章内容及文件名
        """
        pass

    @abstractmethod
    def import_article(self, content, filename, auto_split=True):
        """
        导入一篇新文章。支持自动拆分超长文章。
        
        参数:
            content (str): 文章文本内容
            filename (str): 存储文件名
            auto_split (bool): 是否自动拆分大文件
        
        返回:
            dict: 导入结果，可能包含拆分信息和新增单词数
        """
        pass

    @abstractmethod
    def import_vocabulary(self, content, filename):
        """
        从文本内容导入单词表（提取唯一单词并去重）。
        
        参数:
            content (str): 包含单词的文本
            filename (str): 来源文件名（用于日志）
        
        返回:
            dict: 导入统计，包含新增、已存在的单词数量
        """
        pass

    # ==================== 随机单词 ====================

    @abstractmethod
    def get_random_words(self, count=10):
        """
        从单词表中随机获取指定数量的单词。
        
        参数:
            count (int): 需要获取的单词数量
        
        返回:
            dict: 随机单词列表
        """
        pass

    # ==================== 数据导入导出 ====================

    @abstractmethod
    def export_data(self):
        """
        导出所有用户数据为压缩包。
        
        返回:
            dict: 压缩包路径和文件名
        """
        pass

    @abstractmethod
    def import_data(self, file_path):
        """
        导入数据压缩包，覆盖当前数据（导入前自动备份）。
        
        参数:
            file_path (str): 压缩包文件路径
        
        返回:
            dict: 操作结果，包含备份路径
        """
        pass

    # ==================== 健康检查 ====================

    @abstractmethod
    def health_check(self):
        """
        检查数据文件和目录的完整性，必要时自动修复缺失文件。
        
        返回:
            dict: 系统状态和数据完整性信息
        """
        pass

    # ==================== 文件上传 ====================

    @abstractmethod
    def upload_avatar(self, file_data, filename):
        """
        上传并更新用户头像（保存为固定文件名，更新配置）。
        
        参数:
            file_data (bytes): 图片二进制数据
            filename (str): 原始文件名（用于类型校验）
        
        返回:
            dict: 操作结果，包含头像访问路径
        """
        pass

    @abstractmethod
    def upload_font(self, file_data, filename):
        """
        上传并更新自定义字体（TTF格式）。
        
        参数:
            file_data (bytes): 字体文件二进制数据
            filename (str): 原始文件名
        
        返回:
            dict: 操作结果，包含字体路径
        """
        pass

    @abstractmethod
    def upload_voice(self, voice_type, file_data, filename):
        """
        上传音效文件（按键音、错误音、完成音）。
        
        参数:
            voice_type (str): 音效类型，'keypress'、'error'、'complete'
            file_data (bytes): MP3 文件二进制数据
            filename (str): 原始文件名
        
        返回:
            dict: 操作结果，包含音效路径
        """
        pass

    # ==================== 游戏结果记录 ====================

    @abstractmethod
    def record_word_mode_result(self, wpm, accuracy, play_time):
        """
        记录一局单词模式的游戏结果，更新玩家统计（WPM、准确率、游戏次数等）。
        
        参数:
            wpm (float): 每分钟输入单词数
            accuracy (float): 准确率（0~1）
            play_time (float): 游玩时长（秒）
        
        返回:
            dict: 更新后的单词模式统计数据
        """
        pass

    @abstractmethod
    def record_article_mode_result(self, wpm, accuracy, play_time):
        """
        记录一局文章模式的游戏结果，更新玩家统计。
        
        参数:
            wpm (float): 每分钟输入单词数
            accuracy (float): 准确率（0~1）
            play_time (float): 游玩时长（秒）
        
        返回:
            dict: 更新后的文章模式统计数据
        """
        pass

    # ==================== 文章行切分 ====================

    @abstractmethod
    def process_article_to_lines(self, content, line_width):
        """
        将文章按指定行宽切分为多行文本数组。
        
        参数:
            content (str): 文章内容
            line_width (int): 每行最大字符数（20~100）
        
        返回:
            dict: 包含行数组、总字符数、总行数等信息的响应
        """
        pass

    # ==================== 内部辅助方法（可选实现） ====================
    
    def _remove_from_mistake(self, word):
        """
        【内部方法】从错词表中删除指定单词（通常在删除单词时调用）。
        子类可按需实现。
        
        参数:
            word (str): 要删除的单词
        """
        pass

    def _add_to_mistake(self, word):
        """
        【内部方法】向错词表添加或更新错误记录（累加错误次数，更新错误时间）。
        子类可按需实现。
        
        参数:
            word (str): 出错的单词
        """
        pass

    def _add_words_to_vocabulary(self, words):
        """
        【内部方法】批量添加新单词到单词表（注释为空），保持按首字母分组并排序。
        返回实际新增的单词列表。
        
        参数:
            words (list[str]): 待添加的单词列表
        
        返回:
            list[str]: 本次新增的单词列表
        """
        pass