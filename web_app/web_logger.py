import logging
from datetime import datetime
import streamlit as st

class WebLogger:
    def __init__(self, log_file='web_execution_log.txt'):
        self.log_file = log_file
        self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('web_execution_logger')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器，指定UTF-8编码
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
    def log(self, message, message_type="info"):
        """记录日志信息并显示在网页上"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {message}"
        self.logger.info(log_message)
        
        # 根据消息类型选择不同的显示样式
        if message_type == "info":
            st.info(message)
        elif message_type == "success":
            st.success(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "error":
            st.error(message)
        else:
            st.write(message)

# 初始化全局网页日志记录器
web_logger = WebLogger() 