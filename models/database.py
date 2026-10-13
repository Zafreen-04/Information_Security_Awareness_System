import sqlite3
import json
import csv
from pathlib import Path
from config import Config
from services.scoring import calculate_all_scores

def get_db_path(db_path=None):
    """Resolve database path, defaulting to Config.DATABASE_PATH"""
    if db_path is not None:
        return Path(db_path)
    return Config.DATABASE_PATH

def get_db_connection(db_path=None):
    """Get SQLite database connection with row factory and foreign keys enabled"""
    path = get_db_path(db_path)
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=None):
    """Initialize database schema and populate default questionnaire items"""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    # Create respondents table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS respondents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            respondent_type TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            school TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create questions table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_code TEXT UNIQUE NOT NULL,
            focus_area TEXT NOT NULL,
            question_text TEXT NOT NULL,
            order_number INTEGER NOT NULL
        );
    ''')
    
    # Create responses table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (respondent_id) REFERENCES respondents(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        );
    ''')
    
    # Create results table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER UNIQUE NOT NULL,
            password_score REAL NOT NULL,
            social_media_score REAL NOT NULL,
            email_score REAL NOT NULL,
            overall_score REAL NOT NULL,
            awareness_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (respondent_id) REFERENCES respondents(id) ON DELETE CASCADE
        );
    ''')
    
    # Check if questions already exist
    cur.execute("SELECT COUNT(*) FROM questions;")
    count = cur.fetchone()[0]
    
    if count == 0:
        json_path = Config.DATA_DIR / 'questionnaire.json'
        questions_data = []
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions_data = data.get('questions', [])
        
        # Fallback if json not found
        if not questions_data:
            questions_data = [
                {"code": "ISBP1", "focus_area": "Password Management", "text": "I always use different passwords for each of my accounts.", "order": 1},
                {"code": "ISBP2", "focus_area": "Password Management", "text": "I never share my passwords with my friends or family.", "order": 2},
                {"code": "ISBP3", "focus_area": "Password Management", "text": "I always use a combination of numbers, letters and symbols to make a password.", "order": 3},
                {"code": "ISBS1", "focus_area": "Social Media Use", "text": "I always read the privacy settings of my social media or applications.", "order": 4},
                {"code": "ISBS2", "focus_area": "Social Media Use", "text": "I always think about the negative effect that might happen before posting something on my social media.", "order": 5},
                {"code": "ISBS3", "focus_area": "Social Media Use", "text": "I always filter what I would post on social media.", "order": 6},
                {"code": "ISBE1", "focus_area": "Email Use", "text": "I never click on suspicious links even if they are from people that I know.", "order": 7},
                {"code": "ISBE2", "focus_area": "Email Use", "text": "I never open a file that has been sent to me by people that I don't know.", "order": 8},
                {"code": "ISBE3", "focus_area": "Email Use", "text": "I never click on links that are sent to me from people that I don't know.", "order": 9}
            ]
            
        for q in questions_data:
            cur.execute('''
                INSERT INTO questions (question_code, focus_area, question_text, order_number)
                VALUES (?, ?, ?, ?);
            ''', (q['code'], q['focus_area'], q['text'], q['order']))
            
    conn.commit()
    conn.close()

def get_questions(db_path=None):
    """Retrieve all survey questions ordered by order_number"""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, question_code, focus_area, question_text, order_number FROM questions ORDER BY order_number ASC;")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def save_assessment(respondent_data, answers_dict, db_path=None):
    """
    Save respondent profile, individual Likert answers, and computed awareness results.
    answers_dict maps question_code -> int (1-5) or question_id -> int
    Returns respondent_id
    """
    scores = calculate_all_scores(answers_dict)
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    try:
        # Insert respondent
        cur.execute('''
            INSERT INTO respondents (name, respondent_type, age, gender, school)
            VALUES (?, ?, ?, ?, ?);
        ''', (
            respondent_data['name'].strip(),
            respondent_data['respondent_type'],
            int(respondent_data['age']),
            respondent_data['gender'],
            respondent_data['school'].strip()
        ))
        respondent_id = cur.lastrowid
        
        # Fetch question map: question_code -> question_id
        cur.execute("SELECT id, question_code FROM questions;")
        q_map = {row['question_code']: row['id'] for row in cur.fetchall()}
        
        # Insert individual responses
        for q_code, q_id in q_map.items():
            ans = answers_dict.get(q_code)
            if ans is None and str(q_id) in answers_dict:
                ans = answers_dict[str(q_id)]
            if ans is None:
                raise ValueError(f"Missing response for question {q_code}")
                
            cur.execute('''
                INSERT INTO responses (respondent_id, question_id, answer)
                VALUES (?, ?, ?);
            ''', (respondent_id, q_id, int(ans)))
            
        # Insert computed results
        cur.execute('''
            INSERT INTO results (respondent_id, password_score, social_media_score, email_score, overall_score, awareness_level)
            VALUES (?, ?, ?, ?, ?, ?);
        ''', (
            respondent_id,
            scores['password_score'],
            scores['social_media_score'],
            scores['email_score'],
            scores['overall_score'],
            scores['awareness_level']
        ))
        
        conn.commit()
        return respondent_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_respondent_with_result(respondent_id, db_path=None):
    """Fetch complete assessment profile, results, and item responses for a single respondent"""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    cur.execute('''
        SELECT r.id, r.name, r.respondent_type, r.age, r.gender, r.school, r.created_at,
               res.password_score, res.social_media_score, res.email_score, res.overall_score, res.awareness_level
        FROM respondents r
        LEFT JOIN results res ON r.id = res.respondent_id
        WHERE r.id = ?;
    ''', (respondent_id,))
    resp_row = cur.fetchone()
    
    if not resp_row:
        conn.close()
        return None
        
    respondent = dict(resp_row)
    
    # Fetch responses with question details
    cur.execute('''
        SELECT resp.question_id, resp.answer, q.question_code, q.focus_area, q.question_text, q.order_number
        FROM responses resp
        JOIN questions q ON resp.question_id = q.id
        WHERE resp.respondent_id = ?
        ORDER BY q.order_number ASC;
    ''', (respondent_id,))
    responses = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    respondent['responses'] = responses
    return respondent

def get_all_respondents(filter_type=None, filter_level=None, search_query=None, db_path=None):
    """Retrieve all respondents with results, applying optional filters and search"""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    query = '''
        SELECT r.id, r.name, r.respondent_type, r.age, r.gender, r.school, r.created_at,
               res.password_score, res.social_media_score, res.email_score, res.overall_score, res.awareness_level
        FROM respondents r
        LEFT JOIN results res ON r.id = res.respondent_id
        WHERE 1=1
    '''
    params = []
    
    if filter_type and filter_type in ('Student', 'Teacher'):
        query += " AND r.respondent_type = ?"
        params.append(filter_type)
        
    if filter_level and filter_level in ('Good', 'Average', 'Poor'):
        query += " AND res.awareness_level = ?"
        params.append(filter_level)
        
    if search_query:
        query += " AND (r.name LIKE ? OR r.school LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])
        
    query += " ORDER BY r.id DESC;"
    
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def load_demo_data(csv_path=None, db_path=None):
    """Load sample/demo response dataset from CSV into database"""
    if csv_path is None:
        csv_path = Config.DATA_DIR / 'sample_responses.csv'
    else:
        csv_path = Path(csv_path)
        
    if not csv_path.exists():
        raise FileNotFoundError(f"Sample response file not found at {csv_path}")
        
    init_db(db_path)
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    # Fetch questions map
    cur.execute("SELECT id, question_code FROM questions;")
    q_map = {row['question_code']: row['id'] for row in cur.fetchall()}
    
    loaded_count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            resp_data = {
                'name': row['name'],
                'respondent_type': row['respondent_type'],
                'age': int(row['age']),
                'gender': row['gender'],
                'school': row['school']
            }
            answers_dict = {
                'ISBP1': int(row['ISBP1']),
                'ISBP2': int(row['ISBP2']),
                'ISBP3': int(row['ISBP3']),
                'ISBS1': int(row['ISBS1']),
                'ISBS2': int(row['ISBS2']),
                'ISBS3': int(row['ISBS3']),
                'ISBE1': int(row['ISBE1']),
                'ISBE2': int(row['ISBE2']),
                'ISBE3': int(row['ISBE3'])
            }
            scores = calculate_all_scores(answers_dict)
            
            cur.execute('''
                INSERT INTO respondents (name, respondent_type, age, gender, school)
                VALUES (?, ?, ?, ?, ?);
            ''', (resp_data['name'], resp_data['respondent_type'], resp_data['age'], resp_data['gender'], resp_data['school']))
            resp_id = cur.lastrowid
            
            for code, q_id in q_map.items():
                cur.execute('''
                    INSERT INTO responses (respondent_id, question_id, answer)
                    VALUES (?, ?, ?);
                ''', (resp_id, q_id, answers_dict[code]))
                
            cur.execute('''
                INSERT INTO results (respondent_id, password_score, social_media_score, email_score, overall_score, awareness_level)
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (
                resp_id,
                scores['password_score'],
                scores['social_media_score'],
                scores['email_score'],
                scores['overall_score'],
                scores['awareness_level']
            ))
            loaded_count += 1
            
    conn.commit()
    conn.close()
    return loaded_count

def clear_all_data(db_path=None):
    """Clear respondents, responses, and results from database (retaining questionnaire structure)"""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM results;")
    cur.execute("DELETE FROM responses;")
    cur.execute("DELETE FROM respondents;")
    conn.commit()
    conn.close()
