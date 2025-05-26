import logging
from datetime import datetime

class OutputLogger:
    def __init__(self, log_file='execution_log.txt'):
        self.log_file = log_file
        self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('execution_logger')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器，指定UTF-8编码
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
    def log(self, message):
        """记录日志信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {message}"
        self.logger.info(log_message)
        print(log_message)  # 同时输出到控制台

# 初始化全局日志记录器
output_logger = OutputLogger()

# 配置连接日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mcp_connection.log'
) 