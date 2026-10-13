import os
from pathlib import Path

# Base Directory of the Project (Relative and dynamic)
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Application Configuration Settings"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cyber-security-awareness-assessment-secret-key-2026')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Paths
    DATABASE_PATH = BASE_DIR / 'database.db'
    DATA_DIR = BASE_DIR / 'data'
    REPORTS_DIR = BASE_DIR / 'reports'
    
    # Application Titles
    PROJECT_TITLE = "Information Security Awareness Measurement System for Students and Teachers"
    PROJECT_SUBTITLE = "Measuring Information Security Behaviour Using Questionnaire-Based Assessment"
    
    # Awareness Classification Thresholds based on reference methodology:
    # 80 - 100: Good
    # 60 - 79:  Average
    #  0 - 59:  Poor
    SCORE_THRESHOLDS = {
        'GOOD': 80.0,
        'AVERAGE': 60.0,
        'POOR': 0.0
    }
    
    # Priority Mapping
    PRIORITY_MAPPING = {
        'Poor': 'High priority',
        'Average': 'Moderate priority',
        'Good': 'No immediate action required'
    }

    # Reference Study Results (from original research paper for comparative benchmarking)
    REFERENCE_PAPER_RESULTS = {
        'all': {
            'overall_score': 67.2,
            'awareness_level': 'Average'
        },
        'students': {
            'overall_score': 86.0,
            'awareness_level': 'Good',
            'password_score': 81.7,
            'password_level': 'Good',
            'social_media_score': 87.4,
            'social_media_level': 'Good',
            'email_score': 88.9,
            'email_level': 'Good'
        },
        'teachers': {
            'overall_score': 46.3,
            'awareness_level': 'Poor',
            'password_score': 35.9,
            'password_level': 'Poor',
            'social_media_score': 59.4,
            'social_media_level': 'Average',
            'email_score': 43.6,
            'email_level': 'Poor'
        },
        'reliability_alpha': {
            'password': 0.877,
            'social_media': 0.823,
            'email': 0.955
        },
        'r_table_reference': 0.142
    }
