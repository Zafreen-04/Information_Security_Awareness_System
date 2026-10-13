"""
Unit tests for scoring, percentage conversion, awareness classification, and recommendations.
"""

import pytest
from services.scoring import (
    calculate_percentage,
    classify_awareness_level,
    get_priority_level,
    calculate_focus_area_score,
    calculate_overall_score,
    calculate_all_scores
)
from services.recommendations import generate_recommendations

def test_calculate_percentage():
    """Verify Likert 1-5 conversion to standardized 0-100 percentage"""
    assert calculate_percentage(1) == 20.0
    assert calculate_percentage(2) == 40.0
    assert calculate_percentage(3) == 60.0
    assert calculate_percentage(4) == 80.0
    assert calculate_percentage(5) == 100.0
    
    with pytest.raises(ValueError):
        calculate_percentage(0)
    with pytest.raises(ValueError):
        calculate_percentage(6)
    with pytest.raises(ValueError):
        calculate_percentage(None)

def test_classify_awareness_level():
    """Verify research paper threshold classification: 80-100 Good, 60-79 Average, 0-59 Poor"""
    # Good
    assert classify_awareness_level(100.0) == "Good"
    assert classify_awareness_level(85.5) == "Good"
    assert classify_awareness_level(80.0) == "Good"
    
    # Average
    assert classify_awareness_level(79.9) == "Average"
    assert classify_awareness_level(67.2) == "Average"
    assert classify_awareness_level(60.0) == "Average"
    
    # Poor
    assert classify_awareness_level(59.9) == "Poor"
    assert classify_awareness_level(46.3) == "Poor"
    assert classify_awareness_level(35.9) == "Poor"
    assert classify_awareness_level(0.0) == "Poor"

def test_priority_mapping():
    """Verify action priorities based on awareness classification"""
    assert get_priority_level("Poor") == "High priority"
    assert get_priority_level("Average") == "Moderate priority"
    assert get_priority_level("Good") == "No immediate action required"

def test_calculate_focus_area_and_overall_score():
    """Verify arithmetic mean of percentages for 3-item focus areas and 9-item overall"""
    # 3 answers: 4 (80%), 5 (100%), 4 (80%) -> mean = 260 / 3 = 86.7%
    scores = [4, 5, 4]
    assert calculate_focus_area_score(scores) == 86.7
    
    all_scores = [4, 5, 4, 3, 3, 4, 5, 5, 5]
    # Percentages: 80, 100, 80, 60, 60, 80, 100, 100, 100 = 760 / 9 = 84.4%
    assert calculate_overall_score(all_scores) == 84.4

def test_calculate_all_scores():
    """Verify end-to-end score calculation across all 9 questions"""
    answers = {
        'ISBP1': 5, 'ISBP2': 4, 'ISBP3': 5,  # 100, 80, 100 -> 93.3% (Good)
        'ISBS1': 3, 'ISBS2': 4, 'ISBS3': 3,  # 60, 80, 60 -> 66.7% (Average)
        'ISBE1': 2, 'ISBE2': 2, 'ISBE3': 3   # 40, 40, 60 -> 46.7% (Poor)
    }
    result = calculate_all_scores(answers)
    
    assert result['password_score'] == 93.3
    assert result['password_level'] == "Good"
    assert result['password_priority'] == "No immediate action required"
    
    assert result['social_media_score'] == 66.7
    assert result['social_media_level'] == "Average"
    assert result['social_media_priority'] == "Moderate priority"
    
    assert result['email_score'] == 46.7
    assert result['email_level'] == "Poor"
    assert result['email_priority'] == "High priority"
    
    # Overall: (93.3*3 + 66.7*3 + 46.7*3)/9 = 68.9%
    assert result['overall_score'] == 68.9
    assert result['awareness_level'] == "Average"

def test_generate_recommendations():
    """Verify targeted recommendation synthesis and teacher role-model guidance"""
    scores = {
        'password_score': 50.0,
        'social_media_score': 70.0,
        'email_score': 90.0,
        'overall_score': 70.0
    }
    
    # Student recommendations
    student_recs = generate_recommendations(scores, respondent_type="Student")
    assert "Moderate awareness" in student_recs['overall_summary']
    assert len(student_recs['attention_areas']) == 2  # Password (Poor) and Social Media (Average)
    assert len(student_recs['teacher_specific']) == 0
    
    # Teacher recommendations
    teacher_recs = generate_recommendations(scores, respondent_type="Teacher")
    assert len(teacher_recs['teacher_specific']) > 0
    assert any("Role-Model" in t['title'] for t in teacher_recs['teacher_specific'])
