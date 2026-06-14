import os
import re
from .loggerTool import logger
from config import MAX_ARTICLE_CHARS, TXT_DIR

class ArticleSplitter:
    """文章拆分工具"""
    
    @staticmethod
    def split_article(content, filename, max_chars=None):
        """
        拆分文章
        
        参数:
            content: 文章内容
            filename: 原文件名
            max_chars: 最大字符数限制，默认使用配置值
        
        返回:
            list: 拆分后的文件信息列表 [{"filename": "xxx_part1.txt", "content": "..."}, ...]
        """
        if max_chars is None:
            max_chars = MAX_ARTICLE_CHARS
        
        if len(content) <= max_chars:
            # 无需拆分
            return [{"filename": filename, "content": content}]
        
        # 需要拆分
        logger.info(f"文章 {filename} 长度 {len(content)} 超过限制 {max_chars}，开始拆分")
        
        parts = []
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        
        remaining = content
        part_num = 1
        
        while remaining:
            if len(remaining) <= max_chars:
                # 最后一部分
                parts.append({
                    "filename": f"{base_name}_part{part_num}{ext}",
                    "content": remaining
                })
                break
            
            # 在 max_chars 范围内向前寻找最后一个空格
            split_pos = max_chars
            while split_pos > 0 and remaining[split_pos] != ' ':
                split_pos -= 1
            
            # 如果找不到空格，就在 max_chars 处强制切割
            if split_pos == 0:
                split_pos = max_chars
            
            part_content = remaining[:split_pos].strip()
            parts.append({
                "filename": f"{base_name}_part{part_num}{ext}",
                "content": part_content
            })
            
            remaining = remaining[split_pos:].strip()
            part_num += 1
        
        logger.info(f"文章 {filename} 拆分为 {len(parts)} 部分")
        return parts
    
    @staticmethod
    def save_split_articles(parts, target_dir=None):
        """
        保存拆分后的文章到文件
        
        参数:
            parts: split_article 返回的列表
            target_dir: 目标目录，默认使用 TXT_DIR
        
        返回:
            list: 保存的文件名列表
        """
        if target_dir is None:
            target_dir = TXT_DIR
        
        os.makedirs(target_dir, exist_ok=True)
        saved_files = []
        
        for part in parts:
            filepath = os.path.join(target_dir, part["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(part["content"])
            saved_files.append(part["filename"])
            logger.debug(f"已保存文章片段: {part['filename']}")
        
        return saved_files
    
    @staticmethod
    def get_article_list():
        """获取文章列表"""
        if not os.path.exists(TXT_DIR):
            return []
        
        articles = []
        for filename in os.listdir(TXT_DIR):
            if filename.endswith('.txt'):
                filepath = os.path.join(TXT_DIR, filename)
                stat = os.stat(filepath)
                articles.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "chars": ArticleSplitter._count_chars(filepath)
                })
        
        # 按修改时间倒序排序
        articles.sort(key=lambda x: x["modified"], reverse=True)
        return articles
    
    @staticmethod
    def get_article_content(filename):
        """获取文章内容"""
        filepath = os.path.join(TXT_DIR, filename)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _count_chars(filepath):
        """统计文件字符数（不含换行符）"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 去除换行符后统计
                return len(content.replace('\n', '').replace('\r', ''))
        except Exception:
            return 0
    
    @staticmethod
    def check_size_limit(content, max_chars=None):
        """
        检查文章是否超过字数限制
        
        返回:
            (is_exceed, message)
        """
        if max_chars is None:
            max_chars = MAX_ARTICLE_CHARS
        
        if len(content) <= max_chars:
            return False, f"文章长度 {len(content)} 字符，在限制 {max_chars} 字符以内"
        else:
            return True, f"文章长度 {len(content)} 字符，超过限制 {max_chars} 字符，将被拆分"