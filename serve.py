# -*- coding: utf-8 -*-

import sys
import os
import signal
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.serving import make_server

# 获取资源基础路径（兼容 PyInstaller 打包）
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from impl.gameControllerImpl import GameControllerImpl
from tool.loggerTool import logger
from config import initialize_data, DATA_DIR

# ==================== 全局变量 ====================
server = None
server_thread = None
should_exit = False

# ==================== 信号处理 ====================

def shutdown_server():
    """关闭服务器"""
    global server, should_exit
    should_exit = True
    if server:
        logger.info("正在关闭 Flask 服务器...")
        server.shutdown()
        logger.info("Flask 服务器已关闭")
    else:
        logger.info("服务器未运行，直接退出")

def handle_exit(signum, frame):
    """处理退出信号，确保资源释放"""
    logger.info(f"收到退出信号: {signum}，正在清理...")
    shutdown_server()
    # 给服务器一点时间关闭
    time.sleep(0.5)
    logger.info("退出完成")
    os._exit(0)  # 强制退出

# 注册信号处理
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Windows 控制台关闭事件
if sys.platform == 'win32':
    try:
        import win32api
        import win32con
        def console_handler(ctrl_type):
            if ctrl_type == 0:  # CTRL_C_EVENT
                logger.info("收到 Ctrl+C，正在退出...")
                shutdown_server()
                os._exit(0)
                return True
            elif ctrl_type == 2:  # CTRL_CLOSE_EVENT
                logger.info("收到关闭事件，正在退出...")
                shutdown_server()
                os._exit(0)
                return True
            return False
        win32api.SetConsoleCtrlHandler(console_handler, True)
    except ImportError:
        logger.warning("win32api 未安装，无法注册控制台事件处理")
    except Exception as e:
        logger.warning(f"注册控制台事件处理失败: {e}")

# ==================== Flask 应用 ====================

app = Flask(__name__)
CORS(app)

# 将相对路径转换为绝对路径（支持打包后运行）
absolute_data_dir = os.path.abspath(DATA_DIR)

# 配置静态文件服务（提供 data 目录下的资源访问）
app.static_folder = absolute_data_dir
app.static_url_path = '/static'

# 初始化控制器
controller = GameControllerImpl()

# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    result = controller.health_check()
    return jsonify(result), result.get('code', 200)

# ==================== 玩家信息 ====================

@app.route('/api/gamer', methods=['GET'])
def get_gamer():
    result = controller.get_gamer()
    return jsonify(result), result.get('code', 200)

@app.route('/api/gamer', methods=['PUT'])
def update_gamer():
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400
    result = controller.update_gamer(data)
    return jsonify(result), result.get('code', 200)

# ==================== 单词表 ====================

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    letter = request.args.get('letter', None)
    result = controller.get_vocabulary(page, page_size, letter)
    return jsonify(result), result.get('code', 200)

@app.route('/api/vocabulary/search', methods=['GET'])
def search_vocabulary():
    keyword = request.args.get('keyword', '')
    case_sensitive = request.args.get('caseSensitive', 'false').lower() == 'true'
    if not keyword:
        return jsonify({"code": 400, "message": "关键词不能为空", "data": None}), 400
    result = controller.search_vocabulary(keyword, case_sensitive)
    return jsonify(result), result.get('code', 200)

@app.route('/api/vocabulary', methods=['POST'])
def add_vocabulary():
    data = request.get_json()
    if not data or 'word' not in data:
        return jsonify({"code": 400, "message": "缺少word字段", "data": None}), 400
    word = data['word'].strip()
    note = data.get('note', '').strip()
    if not word:
        return jsonify({"code": 400, "message": "单词不能为空", "data": None}), 400
    result = controller.add_vocabulary(word, note)
    return jsonify(result), result.get('code', 200)

@app.route('/api/vocabulary/<path:word>', methods=['DELETE'])
def delete_vocabulary(word):
    result = controller.delete_vocabulary(word)
    return jsonify(result), result.get('code', 200)

@app.route('/api/vocabulary', methods=['DELETE'])
def clear_vocabulary():
    result = controller.clear_vocabulary()
    return jsonify(result), result.get('code', 200)

@app.route('/api/vocabulary/<path:word>/note', methods=['PUT'])
def update_word_note(word):
    data = request.get_json()
    if not data or 'note' not in data:
        return jsonify({"code": 400, "message": "缺少note字段", "data": None}), 400
    result = controller.update_word_note(word, data['note'])
    return jsonify(result), result.get('code', 200)

# ==================== 错词表 ====================

@app.route('/api/mistake', methods=['GET'])
def get_mistake():
    sort_by = request.args.get('sortBy', 'time')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    result = controller.get_mistake_list(sort_by, page, page_size)
    return jsonify(result), result.get('code', 200)

@app.route('/api/mistake/search', methods=['GET'])
def search_mistake():
    keyword = request.args.get('keyword', '')
    case_sensitive = request.args.get('caseSensitive', 'false').lower() == 'true'
    if not keyword:
        return jsonify({"code": 400, "message": "关键词不能为空", "data": None}), 400
    result = controller.search_mistake(keyword, case_sensitive)
    return jsonify(result), result.get('code', 200)

@app.route('/api/mistake/record', methods=['POST'])
def record_mistake():
    """记录错词"""
    data = request.get_json()
    if not data or 'word' not in data:
        return jsonify({"code": 400, "message": "缺少word字段", "data": None}), 400
    word = data['word'].strip()
    if not word:
        return jsonify({"code": 400, "message": "单词不能为空", "data": None}), 400
    result = controller.record_mistake(word)
    return jsonify(result), result.get('code', 200)

@app.route('/api/mistake/<path:word>', methods=['DELETE'])
def delete_mistake(word):
    result = controller.delete_mistake(word)
    return jsonify(result), result.get('code', 200)

@app.route('/api/mistake', methods=['DELETE'])
def clear_mistake():
    result = controller.clear_mistake()
    return jsonify(result), result.get('code', 200)

# ==================== 配置 ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    result = controller.get_config()
    return jsonify(result), result.get('code', 200)

@app.route('/api/config', methods=['PUT'])
def update_config():
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400
    result = controller.update_config(data)
    return jsonify(result), result.get('code', 200)

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    result = controller.reset_config()
    return jsonify(result), result.get('code', 200)

# ==================== 文章管理 ====================

@app.route('/api/articles', methods=['GET'])
def get_article_list():
    """获取文章列表"""
    result = controller.get_article_list()
    return jsonify(result), result.get('code', 200)

@app.route('/api/articles/<path:filename>', methods=['GET'])
def get_article_content(filename):
    """获取文章内容"""
    result = controller.get_article_content(filename)
    return jsonify(result), result.get('code', 200)

@app.route('/api/import/article', methods=['POST'])
def import_article():
    """导入文章"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"code": 400, "message": "缺少content字段", "data": None}), 400
    content = data['content']
    filename = data.get('filename', f"imported_{len(content)}.txt")
    auto_split = data.get('autoSplit', True)
    result = controller.import_article(content, filename, auto_split)
    return jsonify(result), result.get('code', 200)

@app.route('/api/article/process', methods=['POST'])
def process_article():
    """处理文章为行数组（用于游戏显示）"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"code": 400, "message": "缺少content字段", "data": None}), 400
    
    content = data['content']
    line_width = data.get('lineWidth', 40)
    
    result = controller.process_article_to_lines(content, line_width)
    return jsonify(result), result.get('code', 200)

# ==================== 随机单词 ====================

@app.route('/api/random/words', methods=['GET'])
def get_random_words():
    count = request.args.get('count', 10, type=int)
    count = max(1, min(100, count))
    result = controller.get_random_words(count)
    return jsonify(result), result.get('code', 200)

# ==================== 数据导入导出 ====================

@app.route('/api/export/data', methods=['POST'])
def export_data():
    result = controller.export_data()
    return jsonify(result), result.get('code', 200)

@app.route('/api/import/data', methods=['POST'])
def import_data():
    """导入数据包（接收 ZIP 文件上传）"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "缺少文件", "data": None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "未选择文件", "data": None}), 400
    
    if not file.filename.lower().endswith('.zip'):
        return jsonify({"code": 400, "message": "仅支持 ZIP 格式", "data": None}), 400
    
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f'import_{file.filename}')
    file.save(temp_path)
    
    result = controller.import_data(temp_path)
    
    try:
        os.remove(temp_path)
    except Exception:
        pass
    
    return jsonify(result), result.get('code', 200)

# ==================== 文件上传 ====================

@app.route('/api/upload/avatar', methods=['POST'])
def upload_avatar():
    """上传头像"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "缺少文件", "data": None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "未选择文件", "data": None}), 400
    
    file_data = file.read()
    result = controller.upload_avatar(file_data, file.filename)
    return jsonify(result), result.get('code', 200)

@app.route('/api/upload/font', methods=['POST'])
def upload_font():
    """上传字体"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "缺少文件", "data": None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "未选择文件", "data": None}), 400
    
    file_data = file.read()
    result = controller.upload_font(file_data, file.filename)
    return jsonify(result), result.get('code', 200)

@app.route('/api/upload/voice/<string:voice_type>', methods=['POST'])
def upload_voice(voice_type):
    """上传音效"""
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "缺少文件", "data": None}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "未选择文件", "data": None}), 400
    
    file_data = file.read()
    result = controller.upload_voice(voice_type, file_data, file.filename)
    return jsonify(result), result.get('code', 200)

@app.route('/api/import/vocabulary', methods=['POST'])
def import_vocabulary():
    """从 TXT 导入单词表"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"code": 400, "message": "缺少content字段", "data": None}), 400
    
    content = data['content']
    filename = data.get('filename', 'imported_vocabulary.txt')
    result = controller.import_vocabulary(content, filename)
    return jsonify(result), result.get('code', 200)

# ==================== 游戏结果记录 ====================

@app.route('/api/gamer/word-record', methods=['POST'])
def record_word_mode_result():
    """记录单词模式游玩结果"""
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400
    
    wpm = data.get('wpm', 0)
    accuracy = data.get('accuracy', 0)
    play_time = data.get('playTime', 0)
    correct_chars = data.get('correctChars', 0)  
    wrong_chars = data.get('wrongChars', 0)      
    
    result = controller.record_word_mode_result(wpm, accuracy, play_time, correct_chars, wrong_chars)
    return jsonify(result), result.get('code', 200)


@app.route('/api/gamer/article-record', methods=['POST'])
def record_article_mode_result():
    """记录文章模式游玩结果"""
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400
    
    wpm = data.get('wpm', 0)
    accuracy = data.get('accuracy', 0)
    play_time = data.get('playTime', 0)
    correct_chars = data.get('correctChars', 0)  
    wrong_chars = data.get('wrongChars', 0)      
    
    result = controller.record_article_mode_result(wpm, accuracy, play_time, correct_chars, wrong_chars)
    return jsonify(result), result.get('code', 200)

# ==================== 启动前初始化 ====================

def before_start():
    """启动前执行初始化和健康检查"""
    logger.info("正在执行启动前初始化...")
    initialize_data()
    logger.info("初始化完成，服务启动中...")

# ==================== 启动应用 ====================

def run_server():
    """在独立线程中运行服务器"""
    global server
    port = int(os.environ.get('TYPING_GAME_PORT', 5000))
    
    # 使用 Werkzeug 服务器，支持 shutdown()
    server = make_server('127.0.0.1', port, app, threaded=True)
    logger.info(f"Flask后端服务启动在 http://localhost:{port}")
    logger.info(f"进程 PID: {os.getpid()}")
    
    try:
        server.serve_forever()
    except Exception as e:
        logger.error(f"服务器异常: {e}")
    finally:
        logger.info("Flask 服务器线程已结束")

if __name__ == '__main__':
    before_start()
    
    # 在主线程中运行服务器
    run_server()
    
    logger.info("Flask 服务已完全停止")