"""
Scoring and Awareness Classification Service
Implements the 5-point Likert scale calculation methodology from the research paper.
"""

from config import Config

def calculate_percentage(answer_value):
    """
    Convert a 1-5 Likert scale answer into a percentage.
    Formula: percentage = (answer / 5) * 100
    """
    if answer_value is None or not (1 <= int(answer_value) <= 5):
        raise ValueError(f"Invalid Likert scale value: {answer_value}. Must be between 1 and 5.")
    return (int(answer_value) / 5.0) * 100.0

def classify_awareness_level(score):
    """
    Classify an awareness percentage according to the research paper's rubric:
    80 - 100: Good
    60 - 79:  Average
    0  - 59:  Poor
    """
    if score is None:
        return "Unknown"
    val = round(float(score), 2)
    if val >= Config.SCORE_THRESHOLDS['GOOD']:
        return "Good"
    elif val >= Config.SCORE_THRESHOLDS['AVERAGE']:
        return "Average"
    else:
        return "Poor"

def get_priority_level(awareness_level):
    """
    Map awareness level to action priority:
    Poor    -> High priority
    Average -> Moderate priority
    Good    -> No immediate action required
    """
    return Config.PRIORITY_MAPPING.get(awareness_level, 'Moderate priority')

def calculate_focus_area_score(answers_list):
    """
    Calculate average percentage for questions in a focus area.
    answers_list contains 1-5 integers.
    """
    if not answers_list:
        return 0.0
    percentages = [calculate_percentage(a) for a in answers_list]
    return round(sum(percentages) / len(percentages), 1)

def calculate_overall_score(all_answers_list):
    """
    Calculate overall awareness score across all 9 Likert responses.
    """
    if not all_answers_list:
        return 0.0
    percentages = [calculate_percentage(a) for a in all_answers_list]
    return round(sum(percentages) / len(percentages), 1)

def calculate_all_scores(answers_dict):
    """
    Compute focus area scores, overall score, awareness levels, and priorities.
    answers_dict maps question codes (ISBP1..3, ISBS1..3, ISBE1..3) to Likert values (1-5).
    """
    pw_keys = ['ISBP1', 'ISBP2', 'ISBP3']
    sm_keys = ['ISBS1', 'ISBS2', 'ISBS3']
    em_keys = ['ISBE1', 'ISBE2', 'ISBE3']
    
    # Check all 9 questions exist
    all_keys = pw_keys + sm_keys + em_keys
    for k in all_keys:
        if k not in answers_dict:
            raise ValueError(f"Missing response for mandatory question {k}")
            
    pw_vals = [int(answers_dict[k]) for k in pw_keys]
    sm_vals = [int(answers_dict[k]) for k in sm_keys]
    em_vals = [int(answers_dict[k]) for k in em_keys]
    all_vals = pw_vals + sm_vals + em_vals
    
    password_score = calculate_focus_area_score(pw_vals)
    social_media_score = calculate_focus_area_score(sm_vals)
    email_score = calculate_focus_area_score(em_vals)
    overall_score = calculate_overall_score(all_vals)
    
    password_level = classify_awareness_level(password_score)
    social_media_level = classify_awareness_level(social_media_score)
    email_level = classify_awareness_level(email_score)
    overall_level = classify_awareness_level(overall_score)
    
    return {
        'password_score': password_score,
        'password_level': password_level,
        'password_priority': get_priority_level(password_level),
        
        'social_media_score': social_media_score,
        'social_media_level': social_media_level,
        'social_media_priority': get_priority_level(social_media_level),
        
        'email_score': email_score,
        'email_level': email_level,
        'email_priority': get_priority_level(email_level),
        
        'overall_score': overall_score,
        'awareness_level': overall_level,
        'overall_priority': get_priority_level(overall_level)
    }

def get_focus_area_explanation(area_name, level):
    """Provide short analytical explanation for assessment card"""
    explanations = {
        'Password Management': {
            'Good': 'Strong credential discipline demonstrated. Unique passwords and complexity standards are consistently maintained.',
            'Average': 'Moderate password hygiene. Inconsistencies exist in password diversity, complexity, or confidentiality.',
            'Poor': 'Critical vulnerabilities identified. Frequent password reuse, weak combinations, or credential sharing observed.'
        },
        'Social Media Use': {
            'Good': 'Excellent privacy consciousness. Thoughtful content filtering and active privacy configuration practiced.',
            'Average': 'Basic privacy awareness. Sporadic review of app privacy settings and potential oversharing risk.',
            'Poor': 'Elevated exposure risk. Neglected privacy configurations and lack of pre-posting risk assessment.'
        },
        'Email Use': {
            'Good': 'High vigilance against phishing vectors. Suspicious attachments and links are systematically avoided.',
            'Average': 'Moderate email discernment. Caution is exercised but vulnerability to deceptive senders remains.',
            'Poor': 'High susceptibility to social engineering attacks. Unsolicited attachments and links frequently opened.'
        }
    }
    return explanations.get(area_name, {}).get(level, 'Awareness level evaluated.')
