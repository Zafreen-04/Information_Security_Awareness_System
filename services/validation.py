"""
Questionnaire Statistical Validity and Reliability Analysis Service
Implements Pearson Product-Moment Item-Total Correlation and Cronbach's Alpha.
Calculates sample-size-adaptive critical r values using the Student's t distribution.
"""

import numpy as np
import pandas as pd
from scipy import stats
from config import Config
from models.database import get_db_connection

def calculate_critical_r(sample_size, alpha=0.05):
    """
    Calculate the two-tailed critical correlation coefficient (r-table value)
    for a given sample size N at significance level alpha.
    Degrees of freedom: df = N - 2
    Formula: r_crit = t_crit / sqrt(df + t_crit^2)
    """
    if sample_size < 3:
        return None
    df = sample_size - 2
    # Two-tailed t-critical value
    t_crit = stats.t.ppf(1.0 - (alpha / 2.0), df)
    r_crit = float(t_crit / np.sqrt(df + (t_crit ** 2)))
    return round(r_crit, 3)

def interpret_cronbach_alpha(alpha):
    """
    Standard psychometric interpretation for Cronbach's Alpha:
    >= 0.90: Excellent
    0.80 - 0.89: Good
    0.70 - 0.79: Acceptable
    0.60 - 0.69: Questionable
    < 0.60: Poor
    """
    if alpha is None:
        return "Insufficient Data"
    if alpha >= 0.90:
        return "Excellent"
    elif alpha >= 0.80:
        return "Good"
    elif alpha >= 0.70:
        return "Acceptable"
    elif alpha >= 0.60:
        return "Questionable"
    else:
        return "Poor"

def compute_cronbach_alpha(data_matrix):
    """
    Calculate Cronbach's Alpha from a 2D array or DataFrame of item scores (rows: respondents, cols: items).
    Formula: alpha = (k / (k - 1)) * (1 - sum(var_i) / var_total)
    """
    df = pd.DataFrame(data_matrix)
    n_respondents, k_items = df.shape
    
    if n_respondents < 2 or k_items < 2:
        return None
        
    item_variances = df.var(axis=0, ddof=1)
    sum_item_variances = item_variances.sum()
    
    total_scores = df.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    
    if total_variance == 0 or np.isnan(total_variance):
        return 0.0
        
    alpha = (k_items / (k_items - 1.0)) * (1.0 - (sum_item_variances / total_variance))
    return round(float(alpha), 3)

def get_survey_data_matrix(db_path=None):
    """
    Extracts all respondent item scores as a structured pandas DataFrame.
    Columns: ISBP1, ISBP2, ISBP3, ISBS1, ISBS2, ISBS3, ISBE1, ISBE2, ISBE3
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    cur.execute('''
        SELECT resp.respondent_id, q.question_code, resp.answer
        FROM responses resp
        JOIN questions q ON resp.question_id = q.id
        ORDER BY resp.respondent_id, q.order_number;
    ''')
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        return pd.DataFrame()
        
    records = {}
    for r in rows:
        resp_id = r['respondent_id']
        code = r['question_code']
        ans = r['answer']
        if resp_id not in records:
            records[resp_id] = {}
        records[resp_id][code] = ans
        
    df = pd.DataFrame.from_dict(records, orient='index')
    # Standard column ordering
    expected_cols = ['ISBP1', 'ISBP2', 'ISBP3', 'ISBS1', 'ISBS2', 'ISBS3', 'ISBE1', 'ISBE2', 'ISBE3']
    existing_cols = [c for c in expected_cols if c in df.columns]
    return df[existing_cols]

def perform_validity_and_reliability_analysis(db_path=None, alpha_level=0.05):
    """
    Runs complete statistical assessment:
    1. Pearson item-total correlations and p-values for validity
    2. Dynamic critical r determination based on sample size N
    3. Cronbach's Alpha for overall and each focus area
    4. Reference comparison benchmarks
    """
    df = get_survey_data_matrix(db_path)
    n_respondents = len(df)
    
    analysis = {
        'sample_size': n_respondents,
        'alpha_level': alpha_level,
        'critical_r': None,
        'reference_critical_r': Config.REFERENCE_PAPER_RESULTS.get('r_table_reference', 0.142),
        'validity_items': [],
        'reliability': {},
        'reference_reliability': Config.REFERENCE_PAPER_RESULTS.get('reliability_alpha', {}),
        'can_calculate': n_respondents >= 3,
        'message': ''
    }
    
    # Question metadata
    questions_meta = {
        'ISBP1': {'focus_area': 'Password Management', 'text': 'I always use different passwords for each of my accounts.'},
        'ISBP2': {'focus_area': 'Password Management', 'text': 'I never share my passwords with my friends or family.'},
        'ISBP3': {'focus_area': 'Password Management', 'text': 'I always use a combination of numbers, letters and symbols to make a password.'},
        'ISBS1': {'focus_area': 'Social Media Use', 'text': 'I always read the privacy settings of my social media or applications.'},
        'ISBS2': {'focus_area': 'Social Media Use', 'text': 'I always think about the negative effect that might happen before posting something on my social media.'},
        'ISBS3': {'focus_area': 'Social Media Use', 'text': 'I always filter what I would post on social media.'},
        'ISBE1': {'focus_area': 'Email Use', 'text': 'I never click on suspicious links even if they are from people that I know.'},
        'ISBE2': {'focus_area': 'Email Use', 'text': "I never open a file that has been sent to me by people that I do not know."},
        'ISBE3': {'focus_area': 'Email Use', 'text': "I never click on links that are sent to me from people that I do not know."},
    }
    
    if n_respondents < 3:
        analysis['message'] = f"Insufficient sample size (N={n_respondents}). At least 3 respondents are required to compute correlation and validity statistics (recommended N >= 15)."
        # Populate empty template items for UI display
        for code, meta in questions_meta.items():
            analysis['validity_items'].append({
                'code': code,
                'focus_area': meta['focus_area'],
                'text': meta['text'],
                'mean': 'N/A',
                'correlation': 'N/A',
                'p_value': 'N/A',
                'is_valid': False,
                'status': 'Insufficient Data'
            })
            
        analysis['reliability'] = {
            'overall': {'alpha': None, 'interpretation': 'Insufficient Data', 'k': 9},
            'password': {'alpha': None, 'interpretation': 'Insufficient Data', 'k': 3},
            'social_media': {'alpha': None, 'interpretation': 'Insufficient Data', 'k': 3},
            'email': {'alpha': None, 'interpretation': 'Insufficient Data', 'k': 3}
        }
        return analysis

    # Compute Critical r dynamically based on actual N
    crit_r = calculate_critical_r(n_respondents, alpha_level)
    analysis['critical_r'] = crit_r
    
    # Calculate Total score for each respondent
    df['total_score'] = df.sum(axis=1)
    
    # Item-total Pearson Correlation Analysis
    for code, meta in questions_meta.items():
        if code in df.columns:
            item_vals = df[code].values
            total_vals = df['total_score'].values
            
            mean_val = round(float(np.mean(item_vals)), 2)
            
            # Check for zero variance
            if np.std(item_vals) == 0 or np.std(total_vals) == 0:
                r_val = 0.0
                p_val = 1.0
            else:
                r_val, p_val = stats.pearsonr(item_vals, total_vals)
                r_val = round(float(r_val), 3)
                p_val = round(float(p_val), 4)
                
            # Validity criterion: r_calculated > r_table and p < alpha
            is_valid = bool(r_val > (crit_r if crit_r is not None else 0.142) and p_val < alpha_level)
            status = "Valid" if is_valid else "Invalid / Low Correlation"
            
            analysis['validity_items'].append({
                'code': code,
                'focus_area': meta['focus_area'],
                'text': meta['text'],
                'mean': mean_val,
                'correlation': r_val,
                'p_value': p_val,
                'is_valid': is_valid,
                'status': status
            })

    # Reliability Analysis (Cronbach's Alpha)
    pw_cols = [c for c in ['ISBP1', 'ISBP2', 'ISBP3'] if c in df.columns]
    sm_cols = [c for c in ['ISBS1', 'ISBS2', 'ISBS3'] if c in df.columns]
    em_cols = [c for c in ['ISBE1', 'ISBE2', 'ISBE3'] if c in df.columns]
    all_cols = pw_cols + sm_cols + em_cols
    
    alpha_ov = compute_cronbach_alpha(df[all_cols])
    alpha_pw = compute_cronbach_alpha(df[pw_cols])
    alpha_sm = compute_cronbach_alpha(df[sm_cols])
    alpha_em = compute_cronbach_alpha(df[em_cols])
    
    analysis['reliability'] = {
        'overall': {
            'focus_area': 'Overall Questionnaire (9 items)',
            'alpha': alpha_ov,
            'interpretation': interpret_cronbach_alpha(alpha_ov),
            'k': len(all_cols),
            'ref_value': 'N/A'
        },
        'password': {
            'focus_area': 'Password Management',
            'alpha': alpha_pw,
            'interpretation': interpret_cronbach_alpha(alpha_pw),
            'k': len(pw_cols),
            'ref_value': Config.REFERENCE_PAPER_RESULTS['reliability_alpha']['password']
        },
        'social_media': {
            'focus_area': 'Social Media Use',
            'alpha': alpha_sm,
            'interpretation': interpret_cronbach_alpha(alpha_sm),
            'k': len(sm_cols),
            'ref_value': Config.REFERENCE_PAPER_RESULTS['reliability_alpha']['social_media']
        },
        'email': {
            'focus_area': 'Email Use',
            'alpha': alpha_em,
            'interpretation': interpret_cronbach_alpha(alpha_em),
            'k': len(em_cols),
            'ref_value': Config.REFERENCE_PAPER_RESULTS['reliability_alpha']['email']
        }
    }
    
    return analysis
