"""
Unit tests for psychometric validation, Cronbach's Alpha, and database statistics.
"""

import tempfile
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from services.validation import (
    calculate_critical_r,
    compute_cronbach_alpha,
    interpret_cronbach_alpha,
    perform_validity_and_reliability_analysis
)
from services.statistics import get_dashboard_statistics
from models.database import init_db, save_assessment, clear_all_data

def test_critical_r_calculation():
    """Verify Student's t distribution based critical correlation coefficient"""
    # For N < 3, correlation df is <= 0
    assert calculate_critical_r(2) is None
    
    # For large sample, e.g. N = 100, df = 98, critical r at alpha=0.05 is ~0.197
    r_100 = calculate_critical_r(100, alpha=0.05)
    assert 0.19 <= r_100 <= 0.21
    
    # For small sample N = 20, critical r is higher (~0.444)
    r_20 = calculate_critical_r(20, alpha=0.05)
    assert 0.43 <= r_20 <= 0.46

def test_cronbach_alpha_computation():
    """Verify Cronbach's Alpha calculation on sample psychometric matrix"""
    # Perfect internal consistency (all items identical scores across respondents)
    perfect_data = pd.DataFrame({
        'Q1': [1, 2, 3, 4, 5],
        'Q2': [1, 2, 3, 4, 5],
        'Q3': [1, 2, 3, 4, 5]
    })
    alpha = compute_cronbach_alpha(perfect_data)
    assert alpha == 1.0

    # Low sample size edge case
    assert compute_cronbach_alpha(pd.DataFrame({'Q1': [1]})) is None

def test_cronbach_alpha_interpretation():
    """Verify alpha interpretation scale"""
    assert interpret_cronbach_alpha(0.95) == "Excellent"
    assert interpret_cronbach_alpha(0.85) == "Good"
    assert interpret_cronbach_alpha(0.75) == "Acceptable"
    assert interpret_cronbach_alpha(0.65) == "Questionable"
    assert interpret_cronbach_alpha(0.50) == "Poor"
    assert interpret_cronbach_alpha(None) == "Insufficient Data"

def test_empty_database_handling():
    """Ensure system handles empty database gracefully without crashing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
        
    try:
        init_db(db_path)
        stats = get_dashboard_statistics(db_path)
        assert stats['total_respondents'] == 0
        assert stats['overall_average'] == 0.0
        assert stats['has_data'] is False
        
        val = perform_validity_and_reliability_analysis(db_path)
        assert val['can_calculate'] is False
        assert val['sample_size'] == 0
    finally:
        if db_path.exists():
            db_path.unlink()

def test_database_persistence_and_stats():
    """Verify saving responses, computing results, and retrieving live stats"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
        
    try:
        init_db(db_path)
        
        # Save a student
        student_data = {
            'name': 'Student Test',
            'respondent_type': 'Student',
            'age': 16,
            'gender': 'Female',
            'school': 'Test High School'
        }
        student_answers = {
            'ISBP1': 5, 'ISBP2': 5, 'ISBP3': 5,
            'ISBS1': 5, 'ISBS2': 5, 'ISBS3': 5,
            'ISBE1': 5, 'ISBE2': 5, 'ISBE3': 5
        }
        s_id = save_assessment(student_data, student_answers, db_path)
        assert s_id > 0
        
        # Save a teacher
        teacher_data = {
            'name': 'Teacher Test',
            'respondent_type': 'Teacher',
            'age': 45,
            'gender': 'Male',
            'school': 'Test High School'
        }
        teacher_answers = {
            'ISBP1': 1, 'ISBP2': 2, 'ISBP3': 2,
            'ISBS1': 3, 'ISBS2': 3, 'ISBS3': 3,
            'ISBE1': 2, 'ISBE2': 2, 'ISBE3': 2
        }
        t_id = save_assessment(teacher_data, teacher_answers, db_path)
        assert t_id > 0
        
        stats = get_dashboard_statistics(db_path)
        assert stats['total_respondents'] == 2
        assert stats['total_students'] == 1
        assert stats['total_teachers'] == 1
        assert stats['student_average'] == 100.0
        assert stats['student_level'] == "Good"
        assert stats['teacher_average'] < 60.0
        assert stats['teacher_level'] == "Poor"
    finally:
        if db_path.exists():
            db_path.unlink()
