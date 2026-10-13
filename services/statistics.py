"""
Statistical Analysis and Dashboard Metrics Aggregator
Calculates empirical statistics from the SQLite database.
Handles cases with zero respondents, only students, or only teachers gracefully.
"""

from config import Config
from models.database import get_db_connection
from services.scoring import classify_awareness_level

def get_dashboard_statistics(db_path=None):
    """
    Computes all aggregated metrics required for the admin dashboard and reporting.
    Returns a dictionary of raw numbers, averages, distributions, and chart payloads.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    # 1. Total respondents count
    cur.execute("SELECT COUNT(*) FROM respondents;")
    total_respondents = cur.fetchone()[0]
    
    # 2. Student count and Teacher count
    cur.execute("SELECT COUNT(*) FROM respondents WHERE respondent_type = 'Student';")
    total_students = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM respondents WHERE respondent_type = 'Teacher';")
    total_teachers = cur.fetchone()[0]
    
    # Defaults for empty database
    stats = {
        'total_respondents': total_respondents,
        'total_students': total_students,
        'total_teachers': total_teachers,
        
        'overall_average': 0.0,
        'overall_level': 'N/A',
        'student_average': 0.0,
        'student_level': 'N/A',
        'teacher_average': 0.0,
        'teacher_level': 'N/A',
        
        'password_avg': 0.0,
        'password_level': 'N/A',
        'social_media_avg': 0.0,
        'social_media_level': 'N/A',
        'email_avg': 0.0,
        'email_level': 'N/A',
        
        'student_password_avg': 0.0,
        'student_social_media_avg': 0.0,
        'student_email_avg': 0.0,
        
        'teacher_password_avg': 0.0,
        'teacher_social_media_avg': 0.0,
        'teacher_email_avg': 0.0,
        
        'good_count': 0,
        'average_count': 0,
        'poor_count': 0,
        
        'student_distribution': {'Good': 0, 'Average': 0, 'Poor': 0},
        'teacher_distribution': {'Good': 0, 'Average': 0, 'Poor': 0},
        
        'has_data': total_respondents > 0,
        'has_students': total_students > 0,
        'has_teachers': total_teachers > 0,
        
        # Paper Reference results attached for side-by-side comparison
        'reference_data': Config.REFERENCE_PAPER_RESULTS,
        
        'chart_data': {}
    }
    
    if total_respondents == 0:
        conn.close()
        # Build empty chart structure so frontend renders gracefully
        stats['chart_data'] = build_chart_payloads(stats)
        return stats
        
    # 3. Overall Averages
    cur.execute('''
        SELECT 
            AVG(password_score) as avg_pw,
            AVG(social_media_score) as avg_sm,
            AVG(email_score) as avg_em,
            AVG(overall_score) as avg_ov
        FROM results;
    ''')
    ov_row = cur.fetchone()
    if ov_row and ov_row['avg_ov'] is not None:
        stats['password_avg'] = round(float(ov_row['avg_pw']), 1)
        stats['social_media_avg'] = round(float(ov_row['avg_sm']), 1)
        stats['email_avg'] = round(float(ov_row['avg_em']), 1)
        stats['overall_average'] = round(float(ov_row['avg_ov']), 1)
        
        stats['password_level'] = classify_awareness_level(stats['password_avg'])
        stats['social_media_level'] = classify_awareness_level(stats['social_media_avg'])
        stats['email_level'] = classify_awareness_level(stats['email_avg'])
        stats['overall_level'] = classify_awareness_level(stats['overall_average'])

    # 4. Student Averages
    if total_students > 0:
        cur.execute('''
            SELECT 
                AVG(res.password_score) as avg_pw,
                AVG(res.social_media_score) as avg_sm,
                AVG(res.email_score) as avg_em,
                AVG(res.overall_score) as avg_ov
            FROM results res
            JOIN respondents r ON res.respondent_id = r.id
            WHERE r.respondent_type = 'Student';
        ''')
        st_row = cur.fetchone()
        if st_row and st_row['avg_ov'] is not None:
            stats['student_password_avg'] = round(float(st_row['avg_pw']), 1)
            stats['student_social_media_avg'] = round(float(st_row['avg_sm']), 1)
            stats['student_email_avg'] = round(float(st_row['avg_em']), 1)
            stats['student_average'] = round(float(st_row['avg_ov']), 1)
            stats['student_level'] = classify_awareness_level(stats['student_average'])

    # 5. Teacher Averages
    if total_teachers > 0:
        cur.execute('''
            SELECT 
                AVG(res.password_score) as avg_pw,
                AVG(res.social_media_score) as avg_sm,
                AVG(res.email_score) as avg_em,
                AVG(res.overall_score) as avg_ov
            FROM results res
            JOIN respondents r ON res.respondent_id = r.id
            WHERE r.respondent_type = 'Teacher';
        ''')
        tc_row = cur.fetchone()
        if tc_row and tc_row['avg_ov'] is not None:
            stats['teacher_password_avg'] = round(float(tc_row['avg_pw']), 1)
            stats['teacher_social_media_avg'] = round(float(tc_row['avg_sm']), 1)
            stats['teacher_email_avg'] = round(float(tc_row['avg_em']), 1)
            stats['teacher_average'] = round(float(tc_row['avg_ov']), 1)
            stats['teacher_level'] = classify_awareness_level(stats['teacher_average'])

    # 6. Awareness Levels Distribution
    cur.execute("SELECT awareness_level, COUNT(*) FROM results GROUP BY awareness_level;")
    for row in cur.fetchall():
        lvl = row[0]
        cnt = row[1]
        if lvl == 'Good':
            stats['good_count'] = cnt
        elif lvl == 'Average':
            stats['average_count'] = cnt
        elif lvl == 'Poor':
            stats['poor_count'] = cnt

    # 7. Distribution by Respondent Type
    cur.execute('''
        SELECT r.respondent_type, res.awareness_level, COUNT(*)
        FROM results res
        JOIN respondents r ON res.respondent_id = r.id
        GROUP BY r.respondent_type, res.awareness_level;
    ''')
    for row in cur.fetchall():
        r_type = row[0]
        lvl = row[1]
        cnt = row[2]
        if r_type == 'Student' and lvl in stats['student_distribution']:
            stats['student_distribution'][lvl] = cnt
        elif r_type == 'Teacher' and lvl in stats['teacher_distribution']:
            stats['teacher_distribution'][lvl] = cnt

    conn.close()
    
    # 8. Build chart payloads
    stats['chart_data'] = build_chart_payloads(stats)
    return stats

def build_chart_payloads(stats):
    """
    Constructs JSON-ready payloads for Chart.js rendering on the dashboard.
    Covers the 6 required charts:
    1. Student vs Teacher overall awareness comparison
    2. Focus area comparison (Password, Social Media, Email)
    3. Awareness level distribution (Good, Average, Poor)
    4. Password Management score comparison (Student vs Teacher)
    5. Social Media score comparison (Student vs Teacher)
    6. Email score comparison (Student vs Teacher)
    """
    return {
        # Chart 1: Student vs Teacher Overall Awareness Comparison
        'student_vs_teacher': {
            'labels': ['Overall Awareness (%)'],
            'student_val': stats['student_average'],
            'teacher_val': stats['teacher_average'],
            'overall_val': stats['overall_average']
        },
        # Chart 2: Focus Area Comparison (Overall)
        'focus_areas': {
            'labels': ['Password Management', 'Social Media Use', 'Email Use'],
            'data': [stats['password_avg'], stats['social_media_avg'], stats['email_avg']]
        },
        # Chart 3: Awareness Level Distribution (Doughnut)
        'distribution': {
            'labels': ['Good (80-100%)', 'Average (60-79%)', 'Poor (0-59%)'],
            'data': [stats['good_count'], stats['average_count'], stats['poor_count']]
        },
        # Chart 4: Password Management Comparison
        'password_comparison': {
            'labels': ['Students', 'Teachers', 'Overall'],
            'data': [stats['student_password_avg'], stats['teacher_password_avg'], stats['password_avg']]
        },
        # Chart 5: Social Media Comparison
        'social_media_comparison': {
            'labels': ['Students', 'Teachers', 'Overall'],
            'data': [stats['student_social_media_avg'], stats['teacher_social_media_avg'], stats['social_media_avg']]
        },
        # Chart 6: Email Comparison
        'email_comparison': {
            'labels': ['Students', 'Teachers', 'Overall'],
            'data': [stats['student_email_avg'], stats['teacher_email_avg'], stats['email_avg']]
        },
        # Grouped Comparison: Student vs Teacher across all dimensions
        'grouped_comparison': {
            'labels': ['Password Management', 'Social Media Use', 'Email Use', 'Overall Awareness'],
            'students': [
                stats['student_password_avg'],
                stats['student_social_media_avg'],
                stats['student_email_avg'],
                stats['student_average']
            ],
            'teachers': [
                stats['teacher_password_avg'],
                stats['teacher_social_media_avg'],
                stats['teacher_email_avg'],
                stats['teacher_average']
            ]
        }
    }
