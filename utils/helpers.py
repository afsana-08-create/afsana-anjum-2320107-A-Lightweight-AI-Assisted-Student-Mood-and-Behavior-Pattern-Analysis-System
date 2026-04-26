"""
Helper utilities for the application
"""
from datetime import datetime, date

def format_date(date_obj):
    """Format date for display"""
    if isinstance(date_obj, date):
        return date_obj.strftime('%B %d, %Y')
    return str(date_obj)

def get_mood_emoji(mood_level):
    """Get emoji for mood level"""
    emojis = {
        1: '😢',
        2: '😕',
        3: '😐',
        4: '🙂',
        5: '😊'
    }
    return emojis.get(mood_level, '😐')

def get_mood_label(mood_level):
    """Get label for mood level"""
    labels = {
        1: 'Very Sad',
        2: 'Bad',
        3: 'Neutral',
        4: 'Good',
        5: 'Happy'
    }
    return labels.get(mood_level, 'Unknown')

def calculate_average(values):
    """Calculate average of a list"""
    if not values:
        return 0
    return sum(values) / len(values)

def get_date_range(days=7):
    """Get date range for last N days"""
    from datetime import timedelta
    today = datetime.now().date()
    start_date = today - timedelta(days=days-1)
    return start_date, today

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ''
    # Remove leading/trailing whitespace
    text = text.strip()
    # Limit length
    return text[:1000]