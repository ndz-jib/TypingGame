import re
from .loggerTool import logger

class TextSplitter:
    
    @staticmethod
    def split_words(text):
        """将文本分词为单词列表"""
        raw_words = text.split()
        result = []
        
        for word in raw_words:
            cleaned = TextSplitter._clean_word(word)
            if cleaned and TextSplitter._is_valid_word(cleaned):
                result.append(cleaned)
        
        logger.debug(f"分词完成: 原文{len(raw_words)}词 -> 有效{len(result)}词")
        return result
    
    @staticmethod
    def extract_word_cards(text):
        """
        提取单词卡（用于单词表导入）
        与 split_words 逻辑一致，但保留原始大小写
        """
        raw_words = text.split()
        result = []
        
        for word in raw_words:
            cleaned = TextSplitter._clean_word_raw(word)
            if cleaned and TextSplitter._is_valid_word(cleaned):
                result.append(cleaned)
        
        return list(dict.fromkeys(result))  # 去重保留顺序
    
    @staticmethod
    def _clean_word(word):
        """清理单词，应用大小写规则"""
        cleaned = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', word)
        if not cleaned:
            return None
        return TextSplitter._apply_case_rule(cleaned)
    
    @staticmethod
    def _clean_word_raw(word):
        """清理单词，保留原始大小写"""
        cleaned = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', word)
        return cleaned if cleaned else None
    
    @staticmethod
    def _apply_case_rule(word):
        """应用大小写规则"""
        # 如果单词全是字母且全是大写，保持原样
        if word.isalpha() and word.isupper():
            return word
        
        # 如果是单词 "I"，保持大写
        if word == 'I':
            return word
        
        # 其他情况转为小写
        return word.lower()
    
    @staticmethod
    def _is_valid_word(word):
        """检查单词是否有效"""
        # 剔除纯数字
        if word.isdigit():
            return False
        
        # 剔除纯符号
        if not re.search(r'[a-zA-Z]', word):
            return False
        
        # 允许的字符：字母、数字、连字符、&、撇号
        if re.match(r'^[a-zA-Z0-9\-\&\']+$', word):
            return True
        
        return False
    
    @staticmethod
    def extract_unique_words(text):
        """提取文本中的唯一单词列表"""
        words = TextSplitter.split_words(text)
        return list(dict.fromkeys(words))