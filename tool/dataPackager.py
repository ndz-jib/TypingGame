import os
import zipfile
import shutil
from datetime import datetime
from .loggerTool import logger
from config import EXPORTS_DIR, JSON_DIR, TXT_DIR, VOICE_DIR, FONT_DIR

class DataPackager:
    
    @staticmethod
    def export_data():
        """导出数据包（不含 gamerData.json 和 背景图）"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"typing_data_{timestamp}.zip"
        zip_path = os.path.join(EXPORTS_DIR, zip_filename)
        
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 导出单词表
            vocab_path = os.path.join(JSON_DIR, 'vocabularyList.json')
            if os.path.exists(vocab_path):
                zipf.write(vocab_path, 'vocabularyList.json')
            
            # 导出错词表
            mistake_path = os.path.join(JSON_DIR, 'mistakeList.json')
            if os.path.exists(mistake_path):
                zipf.write(mistake_path, 'mistakeList.json')
            
            # 导出配置
            config_path = os.path.join(JSON_DIR, 'config.json')
            if os.path.exists(config_path):
                zipf.write(config_path, 'config.json')
            
            # 导出 txt 目录
            if os.path.exists(TXT_DIR):
                for root, dirs, files in os.walk(TXT_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('txt', file)
                        zipf.write(file_path, arcname)
            
            # 导出 voice 目录（音效文件）
            if os.path.exists(VOICE_DIR):
                for file in os.listdir(VOICE_DIR):
                    if file.endswith('.mp3'):
                        file_path = os.path.join(VOICE_DIR, file)
                        zipf.write(file_path, os.path.join('voice', file))
            
            # 导出 font 目录（字体文件）
            if os.path.exists(FONT_DIR):
                for file in os.listdir(FONT_DIR):
                    if file.endswith('.ttf'):
                        file_path = os.path.join(FONT_DIR, file)
                        zipf.write(file_path, os.path.join('font', file))
            
            # 注意：不导出 picture 目录（头像由前端单独管理，背景图已废弃）
        
        logger.info(f"数据导出成功: {zip_path}")
        return zip_path, zip_filename
    
    @staticmethod
    def import_data(zip_path, target_dir):
        """
        导入数据包
        
        参数:
            zip_path: ZIP 文件路径
            target_dir: 目标目录（data 目录）
        
        返回:
            bool: 是否成功
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # 验证包结构
                required_files = ['vocabularyList.json', 'mistakeList.json', 'config.json']
                zip_contents = zipf.namelist()
                
                for req_file in required_files:
                    if req_file not in zip_contents:
                        logger.error(f"ZIP包缺少必要文件: {req_file}")
                        return False
                
                # 解压文件
                zipf.extractall(target_dir)
            
            logger.info(f"数据导入成功: {zip_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据导入失败: {str(e)}")
            return False
    
    @staticmethod
    def validate_import_package(zip_path):
        """验证导入包的结构合法性"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                contents = zipf.namelist()
                
                # 检查必要文件
                if 'vocabularyList.json' not in contents:
                    return False, "缺少 vocabularyList.json"
                if 'mistakeList.json' not in contents:
                    return False, "缺少 mistakeList.json"
                if 'config.json' not in contents:
                    return False, "缺少 config.json"
                
                return True, "验证通过"
                
        except Exception as e:
            return False, f"ZIP文件损坏: {str(e)}"