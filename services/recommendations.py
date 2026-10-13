"""
Recommendation Engine Service
Generates targeted and role-specific recommendations based on assessment scores and focus area outcomes.
"""

def generate_recommendations(scores, respondent_type="Student"):
    """
    Generate personalized recommendations for an individual assessment.
    scores is a dict containing password_score, social_media_score, email_score, overall_score.
    """
    recs = {
        'overall_summary': '',
        'focus_area_recommendations': [],
        'attention_areas': [],
        'teacher_specific': []
    }
    
    overall = scores['overall_score']
    if overall >= 80:
        recs['overall_summary'] = "Good performance. Continue following secure information-security practices."
    elif overall >= 60:
        recs['overall_summary'] = "Moderate awareness. Additional awareness training is recommended."
    else:
        recs['overall_summary'] = "Low awareness. Immediate awareness training and policy guidance are recommended."
        
    # Password Management recommendations
    pw = scores['password_score']
    if pw < 60:
        pw_rec = {
            'area': 'Password Management',
            'score': pw,
            'level': 'Poor',
            'priority': 'High priority',
            'badge_class': 'danger',
            'action': "Improve password management by using unique passwords, stronger password combinations, and avoiding password sharing.",
            'details': [
                "Deploy a reputable password manager to generate and store 16+ character passphrases.",
                "Immediately stop sharing credentials with colleagues, friends, or family members.",
                "Enforce multi-factor authentication (MFA) across all email and administrative accounts."
            ]
        }
        recs['attention_areas'].append(pw_rec)
    elif pw < 80:
        pw_rec = {
            'area': 'Password Management',
            'score': pw,
            'level': 'Average',
            'priority': 'Moderate priority',
            'badge_class': 'warning',
            'action': "Strengthen password practices by adopting password managers, avoiding reuse across services, and enabling multi-factor authentication.",
            'details': [
                "Audit stored passwords to eliminate repeated credentials across accounts.",
                "Ensure passwords incorporate numbers, symbols, and mixed casing.",
                "Enable biometric authentication or security keys where supported."
            ]
        }
        recs['attention_areas'].append(pw_rec)
    else:
        pw_rec = {
            'area': 'Password Management',
            'score': pw,
            'level': 'Good',
            'priority': 'No immediate action required',
            'badge_class': 'success',
            'action': "Maintain exemplary credential discipline and regularly review active sessions.",
            'details': [
                "Conduct periodic password audits every 6 to 12 months.",
                "Keep account recovery information up to date."
            ]
        }
    recs['focus_area_recommendations'].append(pw_rec)

    # Social Media recommendations
    sm = scores['social_media_score']
    if sm < 60:
        sm_rec = {
            'area': 'Social Media Use',
            'score': sm,
            'level': 'Poor',
            'priority': 'High priority',
            'badge_class': 'danger',
            'action': "Review privacy settings and think carefully before sharing information on social media.",
            'details': [
                "Audit all social profile privacy settings to ensure posts are restricted to confirmed connections.",
                "Avoid sharing personally identifiable information (birthdays, home address, real-time location).",
                "Disable third-party application permissions connected to social accounts."
            ]
        }
        recs['attention_areas'].append(sm_rec)
    elif sm < 80:
        sm_rec = {
            'area': 'Social Media Use',
            'score': sm,
            'level': 'Average',
            'priority': 'Moderate priority',
            'badge_class': 'warning',
            'action': "Periodically audit social media privacy permissions and exercise discretion when posting personal or location data.",
            'details': [
                "Practice digital foot-printing awareness before sharing media or opinions online.",
                "Review friend lists and revoke access from unfamiliar acquaintances.",
                "Beware of social engineering tactics where attackers glean answers to security questions."
            ]
        }
        recs['attention_areas'].append(sm_rec)
    else:
        sm_rec = {
            'area': 'Social Media Use',
            'score': sm,
            'level': 'Good',
            'priority': 'No immediate action required',
            'badge_class': 'success',
            'action': "Continue filtering posts thoughtfully and maintaining stringent social media account privacy configurations.",
            'details': [
                "Stay informed about updates to platform privacy policies.",
                "Encourage peers to maintain secure online sharing habits."
            ]
        }
    recs['focus_area_recommendations'].append(sm_rec)

    # Email Use recommendations
    em = scores['email_score']
    if em < 60:
        em_rec = {
            'area': 'Email Use',
            'score': em,
            'level': 'Poor',
            'priority': 'High priority',
            'badge_class': 'danger',
            'action': "Be cautious with unknown links, attachments, and suspicious email messages.",
            'details': [
                "Never click on hyperlinks inside unverified emails without checking the full URL domain.",
                "Never open or download attachments (especially .zip, .exe, .scr, or macro-enabled docs) from unfamiliar senders.",
                "Report suspicious messages to school IT administrators or mark them as phishing."
            ]
        }
        recs['attention_areas'].append(em_rec)
    elif em < 80:
        em_rec = {
            'area': 'Email Use',
            'score': em,
            'level': 'Average',
            'priority': 'Moderate priority',
            'badge_class': 'warning',
            'action': "Enhance phishing detection skills, verify sender email addresses, and inspect URLs before clicking.",
            'details': [
                "Inspect the true email header and sender domain, not just the display name.",
                "Look out for urgent language, artificial deadlines, and unusual requests for sensitive data.",
                "Verify legitimate-looking requests through a separate trusted communication channel."
            ]
        }
        recs['attention_areas'].append(em_rec)
    else:
        em_rec = {
            'area': 'Email Use',
            'score': em,
            'level': 'Good',
            'priority': 'No immediate action required',
            'badge_class': 'success',
            'action': "Maintain high vigilance against spear-phishing tactics and keep email filtering rules active.",
            'details': [
                "Stay vigilant against sophisticated spoofing and business email compromise tactics.",
                "Continue adhering to institutional communication channels."
            ]
        }
    recs['focus_area_recommendations'].append(em_rec)

    # Teacher specific role-model recommendations
    if respondent_type == 'Teacher':
        recs['teacher_specific'] = [
            {
                'title': "Cybersecurity Role-Model Responsibility",
                'description': "As highlighted in the research paper, teachers serve as direct role models for high school students. Demonstrating rigorous cybersecurity habits directly influences students' perception of safe digital practices."
            },
            {
                'title': "Workstation & Classroom Lab Security",
                'description': "Never leave grading systems, classroom projectors, or shared computer lab terminals logged in. Lock screens whenever stepping away from faculty desks."
            },
            {
                'title': "Student Data Privacy & Institutional Records",
                'description': "Ensure sensitive student grades, attendance, and identity records are transmitted strictly through encrypted institutional systems rather than personal email or unverified cloud drives."
            },
            {
                'title': "Separation of Personal and Academic Profiles",
                'description': "Maintain a clear boundary between personal social media presence and institutional student communications to prevent social engineering and impersonation."
            }
        ]
        
    return recs

def get_institutional_recommendations_catalog():
    """
    Returns the comprehensive catalog of 11 institutional recommendations
    for display on the /recommendations page.
    """
    return [
        {
            "id": 1,
            "category": "Password Management",
            "title": "Password Management Training",
            "icon": "fa-key",
            "color": "primary",
            "description": "Conduct structured interactive workshops demonstrating how brute-force tools and dictionary attacks exploit weak passwords in seconds.",
            "target": "Students & Teachers",
            "frequency": "Semester Induction"
        },
        {
            "id": 2,
            "category": "Password Management",
            "title": "Strong Password Practices",
            "icon": "fa-shield-halved",
            "color": "primary",
            "description": "Establish policy mandates for 12+ character passphrases combining uppercase, lowercase, numbers, and special symbols rather than predictable words.",
            "target": "All Users",
            "frequency": "Continuous Policy"
        },
        {
            "id": 3,
            "category": "Password Management",
            "title": "Zero Password Sharing Policy",
            "icon": "fa-user-lock",
            "color": "primary",
            "description": "Strictly prohibit sharing login credentials with friends, relatives, or faculty assistants. Reinforce that individual accounts ensure accountability.",
            "target": "Students & Staff",
            "frequency": "Mandatory Rule"
        },
        {
            "id": 4,
            "category": "Password Management",
            "title": "Regular Password Updates & Management Tools",
            "icon": "fa-rotate",
            "color": "primary",
            "description": "Promote open-source or institutional password managers and automated breach alert notifications (e.g., HaveIBeenPwned API integration).",
            "target": "Staff & Senior Students",
            "frequency": "Quarterly Check"
        },
        {
            "id": 5,
            "category": "Social Media Use",
            "title": "Social Media Privacy Configuration",
            "icon": "fa-user-shield",
            "color": "info",
            "description": "Step-by-step guidance on locking down Instagram, Facebook, TikTok, and X privacy settings, auditing app permissions, and disabling location tags.",
            "target": "Students & Teachers",
            "frequency": "Annual Audit"
        },
        {
            "id": 6,
            "category": "Social Media Use",
            "title": "Careful Information Sharing & Digital Footprint",
            "icon": "fa-share-nodes",
            "color": "info",
            "description": "Education on social engineering, oversharing dangers, geolocation risks in photos, and how personal posts can compromise password reset questions.",
            "target": "High School Students",
            "frequency": "Curriculum Topic"
        },
        {
            "id": 7,
            "category": "Email Use",
            "title": "Phishing Awareness & Simulation",
            "icon": "fa-envelope-open-text",
            "color": "warning",
            "description": "Regular controlled phishing simulation exercises to train users to identify forged sender addresses, urgent baiting, and domain typosquatting.",
            "target": "Teachers & Administrators",
            "frequency": "Bi-monthly Drill"
        },
        {
            "id": 8,
            "category": "Email Use",
            "title": "Suspicious-Link Detection",
            "icon": "fa-link-slash",
            "color": "warning",
            "description": "Train users to inspect hyperlinked destinations by hovering before clicking, utilizing URL sandbox scanners, and verifying shortened links.",
            "target": "All Users",
            "frequency": "Continuous Habit"
        },
        {
            "id": 9,
            "category": "Email Use",
            "title": "Suspicious Attachment Isolation",
            "icon": "fa-file-shield",
            "color": "warning",
            "description": "Implement automated email gateway scanning and instruct users never to open unexpected attachments or enable office document macros.",
            "target": "Faculty & Staff",
            "frequency": "IT Security Protocol"
        },
        {
            "id": 10,
            "category": "Institutional Role Models",
            "title": "Teacher Cybersecurity Training Program",
            "icon": "fa-chalkboard-user",
            "color": "danger",
            "description": "Dedicated cyber defense upskilling tailored for educators, emphasizing their role as trusted mentors and guardians of student educational records.",
            "target": "High School Teachers",
            "frequency": "Professional Development Day"
        },
        {
            "id": 11,
            "category": "Governance",
            "title": "Periodic Security Behaviour Re-evaluation",
            "icon": "fa-chart-line",
            "color": "success",
            "description": "Administer this 9-item questionnaire bi-annually to track empirical awareness growth and adapt institutional educational interventions.",
            "target": "Entire School Community",
            "frequency": "Bi-annual Measurement"
        }
    ]
