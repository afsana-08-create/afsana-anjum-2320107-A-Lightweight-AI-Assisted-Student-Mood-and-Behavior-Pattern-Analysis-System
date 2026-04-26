"""
Pattern Analyzer - Analyzes behavior and mood patterns to generate insights
"""

from datetime import datetime, timedelta


def analyze_patterns(mood_data, behavior_data):
    """
    Analyze patterns in mood and behavior data
    
    Args:
        mood_data: List of mood entry dictionaries
        behavior_data: List of behavior log dictionaries
    
    Returns:
        Dictionary with pattern analysis results
    """
    if not mood_data or not behavior_data:
        return {
            'message': 'Not enough data to analyze patterns. Please log more entries.',
            'avg_sleep': 0,
            'avg_study': 0,
            'avg_exercise': 0,
            'avg_social': 0,
            'mood_trend': 'N/A',
            'insights': []
        }
    
    try:
        # Calculate averages
        avg_sleep = sum(b['sleep_hours'] for b in behavior_data) / len(behavior_data)
        avg_study = sum(b['study_hours'] for b in behavior_data) / len(behavior_data)
        avg_exercise = sum(b['exercise_minutes'] for b in behavior_data) / len(behavior_data)
        avg_social = sum(b['social_hours'] for b in behavior_data) / len(behavior_data)
        
        # Analyze mood trend
        mood_trend = analyze_mood_trend(mood_data)
        
        # Generate insights
        insights = generate_insights(avg_sleep, avg_study, avg_exercise, avg_social, mood_data, behavior_data)
        
        # Find correlations
        correlations = find_correlations(mood_data, behavior_data)
        
        return {
            'avg_sleep': round(avg_sleep, 1),
            'avg_study': round(avg_study, 1),
            'avg_exercise': round(avg_exercise, 0),
            'avg_social': round(avg_social, 1),
            'mood_trend': mood_trend,
            'insights': insights,
            'correlations': correlations,
            'total_entries': len(mood_data),
            'days_tracked': len(behavior_data)
        }
        
    except Exception as e:
        return {
            'message': f'Analysis error: {str(e)}',
            'insights': []
        }


def analyze_mood_trend(mood_data):
    """Analyze the trend of mood over time"""
    if len(mood_data) < 3:
        return "📊 Not enough data for trend"
    
    moods = [m['mood_level'] for m in mood_data]
    
    # Compare recent mood with earlier mood
    recent_avg = sum(moods[-3:]) / 3
    earlier_avg = sum(moods[:3]) / min(3, len(moods))
    
    diff = recent_avg - earlier_avg
    
    if diff > 0.5:
        return "📈 Improving - Your mood is getting better!"
    elif diff < -0.5:
        return "📉 Declining - Your mood seems to be dropping"
    else:
        return "➡️ Stable - Your mood is consistent"


def generate_insights(avg_sleep, avg_study, avg_exercise, avg_social, mood_data, behavior_data):
    """Generate personalized insights based on patterns"""
    insights = []
    
    # Sleep insights
    if avg_sleep < 6:
        insights.append({
            'type': 'warning',
            'icon': '😴',
            'title': 'Sleep Deprivation',
            'message': f'Your average sleep is {avg_sleep}h. Students need 7-9 hours for optimal mood and focus.'
        })
    elif avg_sleep >= 7:
        insights.append({
            'type': 'success',
            'icon': '✅',
            'title': 'Good Sleep Pattern',
            'message': f'Great! You\'re averaging {avg_sleep}h of sleep which is healthy.'
        })
    
    # Study load insights
    if avg_study > 8:
        insights.append({
            'type': 'warning',
            'icon': '📚',
            'title': 'High Study Load',
            'message': f'You\'re studying {avg_study}h/day on average. Consider taking regular breaks to prevent burnout.'
        })
    
    # Exercise insights
    if avg_exercise < 15:
        insights.append({
            'type': 'tip',
            'icon': '🏃',
            'title': 'Exercise Boost',
            'message': 'Only moderate exercise detected. Regular physical activity can significantly improve mood!'
        })
    elif avg_exercise >= 30:
        insights.append({
            'type': 'success',
            'icon': '💪',
            'title': 'Active Lifestyle',
            'message': f'Great job! {avg_exercise} min of exercise daily helps maintain good mood.'
        })
    
    # Social insights
    if avg_social < 1:
        insights.append({
            'type': 'tip',
            'icon': '👥',
            'title': 'Social Connection',
            'message': 'Low social interaction detected. Connecting with friends can boost your mood.'
        })
    elif avg_social >= 2:
        insights.append({
            'type': 'success',
            'icon': '🤝',
            'title': 'Good Social Life',
            'message': f'You\'re averaging {avg_social}h of social time - great for emotional health!'
        })
    
    # Correlation insights
    if len(mood_data) >= 5 and len(behavior_data) >= 5:
        # Find best day
        best_mood = max(mood_data, key=lambda x: x['mood_level'])
        
        # Find corresponding behavior
        for behavior in behavior_data:
            if behavior['log_date'] == best_mood['entry_date']:
                insights.append({
                    'type': 'inspiration',
                    'icon': '⭐',
                    'title': 'Your Best Day',
                    'message': f'Your best mood was on {best_mood["entry_date"]} with {behavior["sleep_hours"]}h sleep, {behavior["study_hours"]}h study, {behavior["exercise_minutes"]}min exercise.'
                })
                break
    
    # Default insight if none generated
    if not insights:
        insights.append({
            'type': 'info',
            'icon': '📝',
            'title': 'Keep Tracking',
            'message': 'Continue logging your daily mood and activities to get more personalized insights.'
        })
    
    return insights


def find_correlations(mood_data, behavior_data):
    """Find correlations between behavior factors and mood"""
    correlations = []
    
    if len(mood_data) < 3 or len(behavior_data) < 3:
        return correlations
    
    # Match mood with behavior by date
    paired_data = []
    for mood in mood_data:
        for behavior in behavior_data:
            if mood['entry_date'] == behavior['log_date']:
                paired_data.append({
                    'mood': mood['mood_level'],
                    'sleep': behavior['sleep_hours'],
                    'study': behavior['study_hours'],
                    'exercise': behavior['exercise_minutes'],
                    'social': behavior['social_hours']
                })
                break
    
    if len(paired_data) < 3:
        return correlations
    
    # Simple correlation analysis
    moods = [p['mood'] for p in paired_data]
    sleeps = [p['sleep'] for p in paired_data]
    studies = [p['study'] for p in paired_data]
    exercises = [p['exercise'] for p in paired_data]
    socials = [p['social'] for p in paired_data]
    
    # Calculate simple correlations
    sleep_corr = calculate_correlation(sleeps, moods)
    study_corr = calculate_correlation(studies, moods)
    exercise_corr = calculate_correlation(exercises, moods)
    social_corr = calculate_correlation(socials, moods)
    
    if sleep_corr > 0.3:
        correlations.append(f'🛏️ Better sleep → Higher mood (correlation: {sleep_corr:.2f})')
    elif sleep_corr < -0.3:
        correlations.append(f'🛏️ More sleep → Lower mood (correlation: {sleep_corr:.2f})')
    
    if study_corr > 0.3:
        correlations.append(f'📚 More study → Higher mood')
    elif study_corr < -0.3:
        correlations.append(f'📚 More study → Lower mood (possible stress)')
    
    if exercise_corr > 0.3:
        correlations.append(f'🏃 Exercise → Better mood')
    
    if social_corr > 0.3:
        correlations.append(f'👥 Social time → Better mood')
    
    return correlations


def calculate_correlation(x, y):
    """Calculate simple correlation coefficient"""
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_y2 = sum(yi ** 2 for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def get_weekly_summary(mood_data, behavior_data):
    """Get weekly summary of mood and behavior"""
    if not mood_data or not behavior_data:
        return None
    
    # Get last 7 days
    recent_moods = mood_data[-7:] if len(mood_data) >= 7 else mood_data
    recent_behaviors = behavior_data[-7:] if len(behavior_data) >= 7 else behavior_data
    
    if not recent_moods or not recent_behaviors:
        return None
    
    avg_mood = sum(m['mood_level'] for m in recent_moods) / len(recent_moods)
    avg_sleep = sum(b['sleep_hours'] for b in recent_behaviors) / len(recent_behaviors)
    avg_exercise = sum(b['exercise_minutes'] for b in recent_behaviors) / len(recent_behaviors)
    
    return {
        'avg_mood': round(avg_mood, 1),
        'avg_sleep': round(avg_sleep, 1),
        'avg_exercise': round(avg_exercise, 0),
        'mood_emoji': get_mood_emoji(avg_mood)
    }


def get_mood_emoji(mood_level):
    """Get emoji for mood level"""
    emojis = {
        1: '😢',
        2: '😕',
        3: '😐',
        4: '🙂',
        5: '😊'
    }
    return emojis.get(int(round(mood_level)), '😐')


if __name__ == '__main__':
    # Test
    test_mood = [
        {'mood_level': 3, 'entry_date': '2026-04-15'},
        {'mood_level': 4, 'entry_date': '2026-04-16'},
        {'mood_level': 4, 'entry_date': '2026-04-17'},
        {'mood_level': 5, 'entry_date': '2026-04-18'},
    ]
    test_behavior = [
        {'sleep_hours': 6, 'study_hours': 7, 'exercise_minutes': 30, 'social_hours': 2, 'log_date': '2026-04-15'},
        {'sleep_hours': 7, 'study_hours': 6, 'exercise_minutes': 45, 'social_hours': 2, 'log_date': '2026-04-16'},
        {'sleep_hours': 7, 'study_hours': 5, 'exercise_minutes': 30, 'social_hours': 3, 'log_date': '2026-04-17'},
        {'sleep_hours': 8, 'study_hours': 4, 'exercise_minutes': 60, 'social_hours': 2, 'log_date': '2026-04-18'},
    ]
    
    result = analyze_patterns(test_mood, test_behavior)
    print(result)