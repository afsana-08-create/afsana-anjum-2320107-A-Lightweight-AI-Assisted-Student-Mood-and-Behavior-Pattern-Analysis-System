# AI-Assisted Student Mood & Behavior Pattern Analysis System

A Flask-based web application that uses AI to analyze student mood and behavior patterns.

## Features

- **User Authentication** - Register and login system
- **Mood Tracking** - Log daily mood (1-5 scale) with notes
- **Behavior Logging** - Track sleep, study, exercise, and social activities
- **AI Analytics** - Mood prediction using Random Forest classifier
- **Pattern Analysis** - Behavior-mood correlation detection
- **Visual Charts** - Interactive charts using Chart.js

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask (Python) |
| Database | MySQL (XAMPP) |
| AI/ML | Scikit-learn (Random Forest) |
| Frontend | Bootstrap 5, HTML, CSS |
| Charts | Chart.js |

## Project Structure

```
cse307/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/style.css       # Custom styles
│   └── js/                 # JavaScript files
├── templates/
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── register.html       # Registration
│   ├── index.html          # Dashboard
│   ├── mood_entry.html     # Mood input
│   ├── behavior_log.html   # Behavior input
│   └── analytics.html      # AI analytics
├── models/
│   └── database.py         # Database connection
├── ml/
│   ├── mood_predictor.py   # AI prediction
│   ├── pattern_analyzer.py # Pattern analysis
│   └── datasets/           # Training data
└── utils/
    ├── auth.py             # Auth helpers
    └── helpers.py          # Utilities
```

## Installation

1. **Start XAMPP** and ensure MySQL is running

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Open browser:**
```
http://localhost:5001
```

## Database Schema

- **users** - User accounts
- **mood_entries** - Daily mood logs
- **behavior_logs** - Daily activity logs

## AI Model

- **Algorithm**: Random Forest Classifier
- **Input**: sleep_hours, study_hours, exercise_minutes, social_hours
- **Output**: Predicted mood (1-5)

## Usage

1. Register a new account
2. Login to dashboard
3. Log your daily mood
4. Log your daily activities (sleep, study, exercise, social)
5. View Analytics to see AI predictions and patterns

## License

MIT License