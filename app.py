"""
Information Security Awareness Measurement System for Students and Teachers
Flask Full-Stack Application Entry Point
"""

import io
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
)
import pandas as pd

from config import Config
from models.database import (
    init_db, get_questions, save_assessment, get_respondent_with_result,
    get_all_respondents, load_demo_data, clear_all_data, get_db_connection
)
from services.scoring import (
    classify_awareness_level, get_focus_area_explanation
)
from services.recommendations import (
    generate_recommendations, get_institutional_recommendations_catalog
)
from services.statistics import get_dashboard_statistics
from services.validation import perform_validity_and_reliability_analysis
from services.report_generator import generate_pdf_report

app = Flask(__name__)
app.config.from_object(Config)

# Inject Config into Jinja context globally
@app.context_processor
def inject_config():
    return dict(config=Config)

@app.route('/')
def index():
    """Home page with hero banner, 3 focus area cards, and methodology flow"""
    return render_template('index.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    """5-point Likert scale questionnaire submission"""
    if request.method == 'POST':
        # 1. Extract and validate respondent profile
        name = request.form.get('name', '').strip()
        respondent_type = request.form.get('respondent_type', '').strip()
        age_str = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()
        school = request.form.get('school', '').strip()
        
        if not (name and respondent_type and age_str and gender and school):
            flash("All respondent profile fields are mandatory.", "error")
            return redirect(url_for('questionnaire'))
            
        try:
            age = int(age_str)
        except ValueError:
            flash("Age must be a valid integer.", "error")
            return redirect(url_for('questionnaire'))
            
        if respondent_type == 'Student' and not (10 <= age <= 25):
            flash("Please enter an age appropriate for a high school student (12–19 years recommended).", "error")
            return redirect(url_for('questionnaire'))
        elif respondent_type == 'Teacher' and not (20 <= age <= 85):
            flash("Please enter an age appropriate for an adult educator (20–80 years).", "error")
            return redirect(url_for('questionnaire'))
            
        # 2. Extract answers for the 9 mandatory questions
        question_codes = ['ISBP1', 'ISBP2', 'ISBP3', 'ISBS1', 'ISBS2', 'ISBS3', 'ISBE1', 'ISBE2', 'ISBE3']
        answers_dict = {}
        missing_questions = []
        
        for code in question_codes:
            ans = request.form.get(code)
            if not ans:
                missing_questions.append(code)
            else:
                try:
                    val = int(ans)
                    if not (1 <= val <= 5):
                        raise ValueError()
                    answers_dict[code] = val
                except ValueError:
                    flash(f"Invalid answer value for question {code}.", "error")
                    return redirect(url_for('questionnaire'))
                    
        if missing_questions:
            flash(f"All questions are mandatory. Please answer: {', '.join(missing_questions)}", "error")
            return redirect(url_for('questionnaire'))
            
        # 3. Save to database & compute results
        try:
            respondent_data = {
                'name': name,
                'respondent_type': respondent_type,
                'age': age,
                'gender': gender,
                'school': school
            }
            resp_id = save_assessment(respondent_data, answers_dict)
            flash("Assessment submitted and evaluated successfully!", "success")
            return redirect(url_for('result', respondent_id=resp_id))
        except Exception as e:
            flash(f"An error occurred while saving assessment: {str(e)}", "error")
            return redirect(url_for('questionnaire'))

    # GET request: load questions from DB
    questions = get_questions()
    return render_template('questionnaire.html', questions=questions)

@app.route('/result/<int:respondent_id>')
def result(respondent_id):
    """Individual scorecard and personalized recommendations page"""
    data = get_respondent_with_result(respondent_id)
    if not data:
        flash(f"Assessment record #{respondent_id} not found.", "error")
        return redirect(url_for('respondents'))
        
    scores = {
        'password_score': data['password_score'],
        'password_level': classify_awareness_level(data['password_score']),
        'social_media_score': data['social_media_score'],
        'social_media_level': classify_awareness_level(data['social_media_score']),
        'email_score': data['email_score'],
        'email_level': classify_awareness_level(data['email_score']),
        'overall_score': data['overall_score'],
        'awareness_level': data['awareness_level']
    }
    
    explanations = {
        'Password Management': get_focus_area_explanation('Password Management', scores['password_level']),
        'Social Media Use': get_focus_area_explanation('Social Media Use', scores['social_media_level']),
        'Email Use': get_focus_area_explanation('Email Use', scores['email_level'])
    }
    
    recs = generate_recommendations(scores, respondent_type=data['respondent_type'])
    
    return render_template(
        'result.html',
        respondent=data,
        scores=scores,
        explanations=explanations,
        recommendations=recs
    )

@app.route('/dashboard')
def dashboard():
    """Admin dashboard with aggregated stats, 6 charts, and reference contrast"""
    stats = get_dashboard_statistics()
    return render_template('dashboard.html', stats=stats)

@app.route('/respondents')
def respondents():
    """Searchable, filterable directory of all respondents and scores"""
    filter_type = request.args.get('type', '').strip() or None
    filter_level = request.args.get('level', '').strip() or None
    search_query = request.args.get('q', '').strip() or None
    
    records = get_all_respondents(
        filter_type=filter_type,
        filter_level=filter_level,
        search_query=search_query
    )
    
    return render_template(
        'respondents.html',
        respondents=records,
        filter_type=filter_type,
        filter_level=filter_level,
        search_query=search_query or ''
    )

@app.route('/validation')
def validation():
    """Statistical validity (Pearson r, critical r) and reliability (Cronbach's alpha)"""
    analysis = perform_validity_and_reliability_analysis()
    return render_template('validation.html', analysis=analysis)

@app.route('/recommendations')
def recommendations():
    """Actionable recommendations catalog and live empirical guidance"""
    stats = get_dashboard_statistics()
    catalog = get_institutional_recommendations_catalog()
    return render_template('recommendations.html', stats=stats, catalog=catalog)

@app.route('/about')
def about():
    """Academic background, survey methodology, formulas, and attribution"""
    return render_template('about.html')

@app.route('/report/pdf')
def download_pdf_report():
    """Generate and stream comprehensive PDF report using ReportLab"""
    try:
        pdf_stream = generate_pdf_report()
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Information_Security_Awareness_Report.pdf'
        )
    except Exception as e:
        flash(f"Error generating PDF report: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/export/csv')
def export_csv():
    """Export respondents profile and computed awareness results to CSV"""
    records = get_all_respondents()
    if not records:
        flash("No respondent records available to export.", "warning")
        return redirect(url_for('respondents'))
        
    df = pd.DataFrame(records)
    # Reorder columns for clean presentation
    display_cols = [
        'id', 'name', 'respondent_type', 'age', 'gender', 'school',
        'password_score', 'social_media_score', 'email_score', 'overall_score',
        'awareness_level', 'created_at'
    ]
    existing_cols = [c for c in display_cols if c in df.columns]
    df = df[existing_cols]
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='IS_Awareness_Respondents.csv'
    )

@app.route('/export/excel')
def export_excel():
    """Export respondents profile and computed awareness results to Excel (.xlsx)"""
    records = get_all_respondents()
    if not records:
        flash("No respondent records available to export.", "warning")
        return redirect(url_for('respondents'))
        
    df = pd.DataFrame(records)
    display_cols = [
        'id', 'name', 'respondent_type', 'age', 'gender', 'school',
        'password_score', 'social_media_score', 'email_score', 'overall_score',
        'awareness_level', 'created_at'
    ]
    existing_cols = [c for c in display_cols if c in df.columns]
    df = df[existing_cols]
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Respondents_Results')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='IS_Awareness_Respondents.xlsx'
    )

@app.route('/admin/load-demo-data', methods=['POST'])
def load_demo_data_route():
    """Load sample/demo response dataset into the database"""
    try:
        count = load_demo_data()
        flash(f"Successfully loaded {count} realistic demonstration respondent records!", "success")
    except Exception as e:
        flash(f"Failed to load demo data: {str(e)}", "error")
    return redirect(url_for('dashboard'))

@app.route('/admin/clear-data', methods=['POST'])
def clear_data_route():
    """Clear survey submissions from database (retains questions)"""
    try:
        clear_all_data()
        flash("All survey submissions and results cleared successfully.", "info")
    except Exception as e:
        flash(f"Failed to clear data: {str(e)}", "error")
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="<div class='container py-5 text-center'><h3>Page Not Found (404)</h3><p>The requested page could not be located.</p><a href='/' class='btn btn-primary'>Go Home</a></div>"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', content="<div class='container py-5 text-center'><h3>Server Error (500)</h3><p>An unexpected internal error occurred.</p><a href='/' class='btn btn-primary'>Go Home</a></div>"), 500

if __name__ == '__main__':
    # Initialize SQLite database and question structure on first run
    init_db()
    print("=" * 70)
    print("Information Security Awareness Measurement System")
    print("Measuring Information Security Behaviour Using Questionnaire-Based Assessment")
    print(f"Database: {Config.DATABASE_PATH}")
    print("Server starting at http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=True)
