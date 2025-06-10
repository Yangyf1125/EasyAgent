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
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        
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
    #level=logging.INFO,
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
) 