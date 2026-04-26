"""
Mood Predictor - AI Model for predicting student mood based on behavior patterns
Uses Random Forest Classifier for mood prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Sample training data for initial model
TRAINING_DATA = {
    'sleep_hours': [8, 6, 5, 7, 4, 6, 8, 7, 5, 6, 9, 4, 7, 6, 5, 8, 6, 7, 5, 6],
    'study_hours': [4, 6, 8, 5, 9, 7, 4, 5, 8, 6, 3, 10, 5, 7, 8, 4, 6, 5, 7, 6],
    'exercise_minutes': [30, 0, 0, 30, 0, 15, 45, 30, 0, 20, 60, 0, 20, 15, 0, 45, 30, 20, 10, 25],
    'social_hours': [2, 1, 0.5, 2, 0.5, 1, 3, 2, 1, 1.5, 3, 0.5, 1.5, 2, 1, 2.5, 2, 1.5, 1, 2],
    'mood': [5, 3, 2, 4, 2, 3, 5, 4, 3, 4, 5, 2, 4, 3, 2, 5, 4, 4, 3, 4]
}

MODEL_FILE = os.path.join(BASE_DIR, 'ml_model.pkl')
SCALER_FILE = os.path.join(BASE_DIR, 'scaler.pkl')


def train_model():
    """Train the Random Forest model with sample data"""
    df = pd.DataFrame(TRAINING_DATA)
    X = df[['sleep_hours', 'study_hours', 'exercise_minutes', 'social_hours']]
    y = df['mood']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        min_samples_split=2
    )
    model.fit(X_scaled, y)
    
    # Save model and scaler
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)
    
    return model, scaler


def load_model():
    """Load trained model and scaler, or train if not exists"""
    if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
        model = joblib.load(MODEL_FILE)
        scaler = joblib.load(SCALER_FILE)
    else:
        model, scaler = train_model()
    return model, scaler


def predict_mood(behavior_data):
    """
    Predict mood based on behavior data
    
    Args:
        behavior_data: List of behavior log dictionaries
    
    Returns:
        Dictionary with predicted mood and recommendation
    """
    if not behavior_data or len(behavior_data) < 1:
        return {
            'predicted_mood': None,
            'recommendation': 'Not enough data to predict mood. Please log your daily activities.'
        }
    
    try:
        model, scaler = load_model()
        
        # Get latest behavior data
        latest = behavior_data[-1]
        features = [[
            float(latest.get('sleep_hours', 7)),
            float(latest.get('study_hours', 5)),
            float(latest.get('exercise_minutes', 0)),
            float(latest.get('social_hours', 1))
        ]]
        
        # Scale and predict
        features_scaled = scaler.transform(features)
        predicted_mood = model.predict(features_scaled)[0]
        
        # Get prediction probability
        probabilities = model.predict_proba(features_scaled)[0]
        confidence = max(probabilities) * 100
        
        # Generate recommendation based on predicted mood
        recommendations = {
            1: "😢 Your mood is predicted to be very low. This might be due to poor sleep, high stress, or lack of social interaction. Consider: talking to a friend, taking a walk, or speaking with a counselor.",
            2: "😕 You're predicted to feel stressed or down. Tips: Try to get 7-8 hours of sleep, take short breaks during study, and engage in light exercise.",
            3: "😐 Your mood is predicted to be neutral. To improve: maintain regular sleep schedule, stay physically active, and connect with friends.",
            4: "🙂 You're predicted to feel good! Keep up your healthy habits: good sleep, regular exercise, and social connections.",
            5: "😊 Great mood predicted! You're on the right track. Continue your healthy routines and share your positivity with others!"
        }
        
        return {
            'predicted_mood': int(predicted_mood),
            'confidence': round(confidence, 1),
            'recommendation': recommendations.get(predicted_mood, "Keep tracking your habits!"),
            'factors': analyze_factors(latest)
        }
        
    except Exception as e:
        return {
            'predicted_mood': None,
            'recommendation': f'Prediction error: {str(e)}'
        }


def analyze_factors(behavior):
    """Analyze which factors most influence the mood"""
    factors = []
    
    sleep = behavior.get('sleep_hours', 0)
    study = behavior.get('study_hours', 0)
    exercise = behavior.get('exercise_minutes', 0)
    social = behavior.get('social_hours', 0)
    
    if sleep < 6:
        factors.append('⚠️ Low sleep is affecting your mood')
    elif sleep >= 7:
        factors.append('✅ Good sleep pattern')
    
    if study > 8:
        factors.append('⚠️ High study load may cause stress')
    
    if exercise < 15:
        factors.append('💡 More exercise can boost your mood')
    elif exercise >= 30:
        factors.append('✅ Regular exercise helps mood')
    
    if social < 1:
        factors.append('💡 More social interaction may help')
    elif social >= 2:
        factors.append('✅ Good social connection')
    
    return factors


def retrain_with_user_data(behavior_data, mood_data):
    """
    Retrain model with user-specific data
    This improves prediction accuracy over time
    """
    if len(behavior_data) < 5:
        return False
    
    try:
        # Combine behavior and mood data
        X_data = []
        y_data = []
        
        for i in range(len(behavior_data)):
            # Try to match behavior with mood on same date
            for mood in mood_data:
                if mood.get('entry_date') == behavior_data[i].get('log_date'):
                    X_data.append([
                        behavior_data[i].get('sleep_hours', 7),
                        behavior_data[i].get('study_hours', 5),
                        behavior_data[i].get('exercise_minutes', 0),
                        behavior_data[i].get('social_hours', 1)
                    ])
                    y_data.append(mood.get('mood_level', 3))
                    break
        
        if len(X_data) >= 5:
            # Add original training data
            for i, row in enumerate(TRAINING_DATA['sleep_hours']):
                X_data.append([
                    TRAINING_DATA['sleep_hours'][i],
                    TRAINING_DATA['study_hours'][i],
                    TRAINING_DATA['exercise_minutes'][i],
                    TRAINING_DATA['social_hours'][i]
                ])
                y_data.append(TRAINING_DATA['mood'][i])
            
            # Retrain
            X = np.array(X_data)
            y = np.array(y_data)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)
            
            joblib.dump(model, MODEL_FILE)
            joblib.dump(scaler, SCALER_FILE)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"Retrain error: {e}")
        return False


if __name__ == '__main__':
    # Test the model
    test_data = [{
        'sleep_hours': 6,
        'study_hours': 7,
        'exercise_minutes': 30,
        'social_hours': 2
    }]
    
    result = predict_mood(test_data)
    print("Test Prediction:", result)