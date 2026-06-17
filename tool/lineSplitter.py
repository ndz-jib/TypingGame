import re
from .loggerTool import logger

class LineSplitter:
    """文章行切分工具"""
    
    @staticmethod
    def split_to_lines(text, line_width=40):
        """
        将文本按固定宽度切分为行，确保单词不被拆分
        
        参数:
            text: 原始文本
            line_width: 每行最大字符数（默认40）
        
        返回:
            list: 行数组
        """
        if not text:
            return []
        
        # 按空白字符切分为单词
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            
            # 如果当前行已有内容，需要加一个空格
            if current_line and current_length + 1 + word_len <= line_width:
                current_line.append(word)
                current_length += 1 + word_len
            elif word_len <= line_width:
                # 新行
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_len
            else:
                # 单词本身超过行宽，强制拆分（罕见情况）
                if current_line:
                    lines.append(' '.join(current_line))
                
                # 按字符拆解长单词
                for i in range(0, word_len, line_width):
                    chunk = word[i:i+line_width]
                    lines.append(chunk)
                
                current_line = []
                current_length = 0
        
        # 添加最后一行
        if current_line:
            lines.append(' '.join(current_line))
        
        logger.debug(f"文章行切分完成: 总字符数={len(text)}, 行数={len(lines)}, 行宽={line_width}")
        return lines
    
    @staticmethod
    def split_to_lines_preserve_spaces(text, line_width=40):
        """
        将文本按固定宽度切分为行，保留空格和换行符
        
        参数:
            text: 原始文本
            line_width: 每行最大字符数（默认40）
        
        返回:
            list: 行数组（每行包含原文本中的空格）
        """
        if not text:
            return []
        
        # 按行分割，保留换行符作为行分隔
        paragraphs = text.split('\n')
        all_lines = []
        
        for para in paragraphs:
            if not para.strip():
                all_lines.append('')  # 空行
                continue
            
            # 对段落进行切分
            words = para.split(' ')
            current_line = []
            current_length = 0
            
            for word in words:
                word_len = len(word)
                
                if current_line and current_length + 1 + word_len <= line_width:
                    current_line.append(word)
                    current_length += 1 + word_len
                elif word_len <= line_width:
                    if current_line:
                        all_lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_len
                else:
                    if current_line:
                        all_lines.append(' '.join(current_line))
                    for i in range(0, word_len, line_width):
                        all_lines.append(word[i:i+line_width])
                    current_line = []
                    current_length = 0
            
            if current_line:
                all_lines.append(' '.join(current_line))
        
        return all_lines