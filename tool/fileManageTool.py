import os
import shutil
from datetime import datetime
from .editTool import EditTool
from .loggerTool import logger
from config import BACKUP_DIR

class FileManageTool:
    
    def __init__(self):
        self.edit_tool = EditTool()
    
    def read_json(self, file_path, default_data=None):
        """读取JSON文件"""
        return self.edit_tool.safe_read_json(file_path, default_data)
    
    def write_json(self, file_path, data):
        """写入JSON文件"""
        return self.edit_tool.safe_write_json(file_path, data)
    
    def backup_data(self, description=""):
        """备份当前所有数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}_{description}")
        
        # 备份JSON目录
        json_backup = os.path.join(backup_path, 'json')
        txt_backup = os.path.join(backup_path, 'txt')
        
        os.makedirs(json_backup, exist_ok=True)
        os.makedirs(txt_backup, exist_ok=True)
        
        # 复制JSON文件
        from config import JSON_DIR, TXT_DIR
        for filename in os.listdir(JSON_DIR):
            src = os.path.join(JSON_DIR, filename)
            dst = os.path.join(json_backup, filename)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
        
        # 复制TXT文件
        if os.path.exists(TXT_DIR):
            for filename in os.listdir(TXT_DIR):
                src = os.path.join(TXT_DIR, filename)
                dst = os.path.join(txt_backup, filename)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        logger.info(f"数据已备份到: {backup_path}")
        return backup_path
    
    def restore_from_backup(self, backup_path):
        """从备份恢复数据"""
        from config import JSON_DIR, TXT_DIR
        
        json_backup = os.path.join(backup_path, 'json')
        txt_backup = os.path.join(backup_path, 'txt')
        
        # 恢复JSON文件
        if os.path.exists(json_backup):
            for filename in os.listdir(json_backup):
                src = os.path.join(json_backup, filename)
                dst = os.path.join(JSON_DIR, filename)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        # 恢复TXT文件
        if os.path.exists(txt_backup):
            for filename in os.listdir(txt_backup):
                src = os.path.join(txt_backup, filename)
                dst = os.path.join(TXT_DIR, filename)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        logger.info(f"已从备份恢复: {backup_path}")