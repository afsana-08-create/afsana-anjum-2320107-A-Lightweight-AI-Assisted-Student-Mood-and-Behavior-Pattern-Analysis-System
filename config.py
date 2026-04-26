import os

class Config:
    """Configuration settings for the application"""
    SECRET_KEY = os.urandom(24)
    
    # MySQL Database Configuration (XAMPP)
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'mood_analysis_db'
    MYSQL_CURSORCLASS = 'DictCursor'