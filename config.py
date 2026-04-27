import os

class Config:
    """Configuration settings for the application"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'student_mood_analyzer_secret_key_2026')

    # MySQL Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'mood_analysis_db')
    MYSQL_CURSORCLASS = 'DictCursor'