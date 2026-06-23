import os
import shutil
from datetime import datetime
import sys

# ==================== 路径配置 ====================

def get_base_dir():
    """获取程序所在目录（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，可执行文件所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, 'data')
JSON_DIR = os.path.join(DATA_DIR, 'json')
TXT_DIR = os.path.join(DATA_DIR, 'txt')
VOICE_DIR = os.path.join(DATA_DIR, 'voice')
FONT_DIR = os.path.join(DATA_DIR, 'font')
PICTURE_DIR = os.path.join(DATA_DIR, 'picture')
LOG_DIR = os.path.join(BASE_DIR, 'log')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
BACKUP_DIR = os.path.join(DATA_DIR, 'backup')

# ==================== 默认数据（保持不变）====================

DEFAULT_GAMER_DATA = {
    "name": "User",
    "avatarUrl": "./data/picture/avatar.png",
    "score": 0,
    "playStats": {
        "totalPlayTime": 0,
        "totalGames": 0,
        "totalCorrectChars": 0,
        "totalWrongChars": 0,
        "modeStats": {
            "wordMode": {
                "games": 0,
                "bestWPM": 0,
                "avgAccuracy": 0
            },
            "articleMode": {
                "games": 0,
                "bestWPM": 0,
                "avgAccuracy": 0
            }
        }
    }
}

DEFAULT_VOCABULARY = {
    "A": [
        ["Apple", "苹果 (水果，公司名)"],
        ["aerial", "空中的，航空的"],
        ["Analyze", "分析 (美式拼写)"]
    ],
    "B": [
        ["Banana", "香蕉"],
        ["B&O", "Bang & Olufsen 音响品牌"],
        ["benevolent", "仁慈的，乐善好施的"]
    ],
    "C": [
        ["China", "中国 (国家)"],
        ["china", "瓷器 (小写有不同含义)"],
        ["C&A", "服装零售品牌 C&A"]
    ],
    "D": [
        ["D&G", "Dolce & Gabbana 奢侈品牌"],
        ["diligent", "勤奋的，勤勉的"],
        ["December", "十二月"]
    ],
    "E": [
        ["E-mail", "电子邮件"],
        ["eloquent", "雄辩的，有口才的"],
        ["Enterprise", "企业，进取心"]
    ],
    "F": [
        ["Facebook", "脸书社交平台"],
        ["fabulous", "极好的，难以置信的"],
        ["F&B", "Food and Beverage 餐饮"]
    ],
    "G": [
        ["Google", "谷歌搜索引擎"],
        ["gratitude", "感激，感恩"],
        ["G-shock", "卡西欧G-Shock手表品牌"]
    ],
    "H": [
        ["H&M", "Hennes & Mauritz 服装品牌"],
        ["happiness", "幸福，快乐"],
        ["Huawei", "华为公司"]
    ],
    "I": [
        ["I", "我 (第一人称代词，必须大写)"],
        ["iPhone", "苹果手机"],
        ["incredible", "难以置信的"]
    ],
    "J": [
        ["J&J", "Johnson & Johnson 强生公司"],
        ["jellyfish", "水母"],
        ["Jupiter", "木星"]
    ],
    "K": [
        ["KFC", "肯德基快餐"],
        ["knowledge", "知识，学问"],
        ["K-pop", "韩国流行音乐"]
    ],
    "L": [
        ["L'Oréal", "欧莱雅化妆品品牌"],
        ["laboratory", "实验室"],
        ["LinkedIn", "领英职场社交平台"]
    ],
    "M": [
        ["McDonald's", "麦当劳快餐"],
        ["magnificent", "宏伟的，壮丽的"],
        ["M&M's", "M&M巧克力豆"]
    ],
    "N": [
        ["Netflix", "奈飞流媒体平台"],
        ["nutrition", "营养，营养学"],
        ["NATO", "北大西洋公约组织"]
    ],
    "O": [
        ["O'Reilly", "奥莱利 (姓氏/品牌)"],
        ["opportunity", "机会，机遇"],
        ["O2O", "Online to Offline 线上线下模式"]
    ],
    "P": [
        ["P&G", "Procter & Gamble 宝洁公司"],
        ["persevere", "坚持不懈"],
        ["PlayStation", "索尼游戏主机"]
    ],
    "Q": [
        ["Q&A", "Question and Answer 问答"],
        ["quintessential", "典型的，精髓的"],
        ["QR code", "二维码"]
    ],
    "R": [
        ["R&B", "Rhythm and Blues 节奏布鲁斯音乐"],
        ["restaurant", "餐厅，饭店"],
        ["R2-D2", "星球大战机器人R2-D2"]
    ],
    "S": [
        ["S&P", "Standard & Poor's 标准普尔"],
        ["sophisticated", "复杂的，精致的"],
        ["Samsung", "三星电子"]
    ],
    "T": [
        ["T-shirt", "T恤衫"],
        ["technology", "技术，科技"],
        ["TikTok", "抖音短视频平台"]
    ],
    "U": [
        ["U.S.A.", "美利坚合众国"],
        ["ubiquitous", "无处不在的"],
        ["U-turn", "掉头，U型转弯"]
    ],
    "V": [
        ["V8", "V8发动机"],
        ["vocabulary", "词汇，词汇量"],
        ["V-shaped", "V字形的"]
    ],
    "W": [
        ["W3C", "万维网联盟"],
        ["whatsoever", "无论什么，丝毫"],
        ["WWE", "世界摔角娱乐"]
    ],
    "X": [
        ["X-ray", "X射线，X光"],
        ["xenophobia", "仇外心理"],
        ["Xbox", "微软游戏主机"]
    ],
    "Y": [
        ["Y2K", "2000年千年虫问题"],
        ["yesterday", "昨天"],
        ["YouTube", "油管视频平台"]
    ],
    "Z": [
        ["ZARA", "飒拉服装品牌"],
        ["zenith", "顶峰，顶点"],
        ["Z-score", "Z分数 (统计学)"]
    ]
}

DEFAULT_CONFIG = {
    "gameSettings": {
        "autoSaveOnExit": True
    },
    "customSettings": {
        "fontPath": "./data/font/default.ttf",
        "avatarPath": "./data/picture/avatar.png",
        "soundEnabled": True,
        "vibrationEnabled": True
    }
}

# 文章最大字符数（普通人5分钟平均打字字数）
MAX_ARTICLE_CHARS = 1500

# ==================== 文件路径 ====================

GAMER_DATA_PATH = os.path.join(JSON_DIR, 'gamerData.json')
VOCABULARY_PATH = os.path.join(JSON_DIR, 'vocabularyList.json')
MISTAKE_PATH = os.path.join(JSON_DIR, 'mistakeList.json')
CONFIG_PATH = os.path.join(JSON_DIR, 'config.json')

# ==================== 占位资源生成（保持不变）====================

def _ensure_directories():
    """确保所有目录存在"""
    for dir_path in [DATA_DIR, JSON_DIR, TXT_DIR, VOICE_DIR, FONT_DIR, PICTURE_DIR, LOG_DIR, EXPORTS_DIR, BACKUP_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def _generate_blank_mp3(filepath, duration_ms=100):
    """生成空白 MP3 文件（静音）"""
    import struct
    
    blank_mp3 = bytes([
        0xFF, 0xFB, 0x90, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]) * 4
    
    with open(filepath, 'wb') as f:
        f.write(blank_mp3)
    
    print(f"已生成空白音效: {filepath}")


def _generate_blank_png(filepath, width=200, height=200):
    """生成空白 PNG 图片（透明/灰色）"""
    blank_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    
    with open(filepath, 'wb') as f:
        f.write(blank_png)
    
    print(f"已生成空白图片: {filepath}")


def _generate_blank_ttf(filepath):
    """生成占位字体文件（复制系统默认字体或创建最小 TTF）"""
    import sys
    
    possible_fonts = [
        "/System/Library/Fonts/Helvetica.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    font_copied = False
    for font_path in possible_fonts:
        if os.path.exists(font_path):
            shutil.copy2(font_path, filepath)
            print(f"已复制系统字体到: {filepath}")
            font_copied = True
            break
    
    if not font_copied:
        with open(filepath, 'w') as f:
            f.write("Placeholder font file. Please replace with actual font.")
        print(f"警告: 无法复制系统字体，已创建占位文件: {filepath}")


def _ensure_default_resources():
    """确保默认资源文件存在，不存在则生成占位文件"""
    
    avatar_path = os.path.join(PICTURE_DIR, 'avatar.png')
    if not os.path.exists(avatar_path):
        _generate_blank_png(avatar_path)
    
    keypress_path = os.path.join(VOICE_DIR, 'keypress.mp3')
    error_path = os.path.join(VOICE_DIR, 'error.mp3')
    complete_path = os.path.join(VOICE_DIR, 'complete.mp3')
    
    if not os.path.exists(keypress_path):
        _generate_blank_mp3(keypress_path)
    if not os.path.exists(error_path):
        _generate_blank_mp3(error_path)
    if not os.path.exists(complete_path):
        _generate_blank_mp3(complete_path)
    
    font_path = os.path.join(FONT_DIR, 'default.ttf')
    if not os.path.exists(font_path):
        _generate_blank_ttf(font_path)


def _ensure_json_files():
    """确保 JSON 数据文件存在"""
    from tool.editTool import EditTool
    
    edit_tool = EditTool()
    
    if not os.path.exists(GAMER_DATA_PATH):
        edit_tool.safe_write_json(GAMER_DATA_PATH, DEFAULT_GAMER_DATA)
        print(f"已创建默认玩家数据: {GAMER_DATA_PATH}")
    
    if not os.path.exists(VOCABULARY_PATH):
        edit_tool.safe_write_json(VOCABULARY_PATH, DEFAULT_VOCABULARY)
        print(f"已创建默认单词表: {VOCABULARY_PATH}")
    
    if not os.path.exists(MISTAKE_PATH):
        edit_tool.safe_write_json(MISTAKE_PATH, {})
        print(f"已创建默认错词表: {MISTAKE_PATH}")
    
    if not os.path.exists(CONFIG_PATH):
        edit_tool.safe_write_json(CONFIG_PATH, DEFAULT_CONFIG)
        print(f"已创建默认配置: {CONFIG_PATH}")


def initialize_data():
    """初始化所有数据和资源（在服务启动时调用）"""
    print(f"数据目录: {DATA_DIR}")
    print("正在初始化数据和资源...")
    
    _ensure_directories()
    _ensure_json_files()
    _ensure_default_resources()
    
    print("初始化完成。")


# ==================== 工具函数 ====================

def ensure_directories():
    """对外暴露的目录确保函数"""
    _ensure_directories()