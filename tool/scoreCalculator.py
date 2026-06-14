import math
from .loggerTool import logger

class ScoreCalculator:
    
    @staticmethod
    def calculate_score(correct_chars, wrong_chars, wpm, base_score=0):
        """
        计算积分
        
        参数:
            correct_chars: 正确字符数
            wrong_chars: 错误字符数
            wpm: 当前WPM
            base_score: 基础积分（可选）
        
        返回:
            计算后的积分
        """
        if correct_chars == 0:
            return base_score
        
        total_chars = correct_chars + wrong_chars
        accuracy = correct_chars / total_chars if total_chars > 0 else 0
        
        # 速度系数: min(1, WPM / 60)
        speed_factor = min(1.0, wpm / 60.0)
        
        # 正确率系数: 正确率²
        accuracy_factor = accuracy ** 2
        
        # 积分 = 正确字符数 × 速度系数 × 正确率系数
        calculated_score = correct_chars * speed_factor * accuracy_factor
        
        final_score = base_score + int(calculated_score)
        
        logger.debug(f"积分计算: 正确{correct_chars}, 错误{wrong_chars}, WPM={wpm:.1f}, "
                    f"准确率={accuracy:.2%}, 新积分={final_score}")
        
        return final_score
    
    @staticmethod
    def calculate_wpm(correct_chars, time_seconds):
        """
        计算WPM (每分钟正确单词数)
        假设平均单词长度为5个字符
        
        参数:
            correct_chars: 正确字符数
            time_seconds: 用时（秒）
        
        返回:
            WPM值
        """
        if time_seconds <= 0:
            return 0
        
        minutes = time_seconds / 60.0
        words_typed = correct_chars / 5.0  # 标准单词长度5个字符
        
        wpm = words_typed / minutes if minutes > 0 else 0
        return round(wpm, 1)
    
    @staticmethod
    def update_average_accuracy(old_avg, new_accuracy, games_count):
        """更新平均准确率"""
        if games_count == 0:
            return new_accuracy
        
        new_avg = (old_avg * games_count + new_accuracy) / (games_count + 1)
        return round(new_avg, 3)
    
    @staticmethod
    def update_best_wpm(old_best, new_wpm):
        """更新最佳WPM"""
        return max(old_best, new_wpm)