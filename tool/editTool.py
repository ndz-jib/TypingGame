import json
import os
import shutil
from datetime import datetime
from .loggerTool import logger

class EditTool:
    
    @staticmethod
    def validate_and_repair_json(file_path, default_data=None):
        """验证并修复JSON文件"""
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            if default_data is not None:
                EditTool._create_default_json(file_path, default_data)
                return True
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            logger.debug(f"JSON文件验证通过: {file_path}")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误 {file_path}: {str(e)}")
            
            # 备份损坏的文件
            backup_path = f"{file_path}.broken.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(file_path, backup_path)
            logger.info(f"已备份损坏文件: {backup_path}")
            
            # 重建文件
            if default_data is not None:
                EditTool._create_default_json(file_path, default_data)
                logger.info(f"已重建文件: {file_path}")
                return True
            return False
    
    @staticmethod
    def _create_default_json(file_path, default_data):
        """创建默认JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        logger.info(f"已创建默认文件: {file_path}")
    
    @staticmethod
    def safe_read_json(file_path, default_data=None):
        """安全读取JSON文件"""
        if EditTool.validate_and_repair_json(file_path, default_data):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {str(e)}")
        return default_data if default_data is not None else {}
    
    @staticmethod
    def safe_write_json(file_path, data):
        """安全写入JSON文件"""
        try:
            # 先写入临时文件
            temp_path = f"{file_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 验证临时文件
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # 替换原文件
            shutil.move(temp_path, file_path)
            logger.debug(f"成功写入文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {str(e)}")
            return False