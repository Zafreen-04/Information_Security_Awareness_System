# Information Security Awareness Measurement System for Students and Teachers

> **Measuring Information Security Behaviour Using Questionnaire-Based Assessment**  
> *An Academic Full-Stack Software Implementation Inspired by Empirical Research Methodology*

---

## 1. Project Overview

In secondary educational institutions, high school students and teachers interact daily with online services, educational management portals, and social media platforms. However, organizational cyber security cannot depend solely on software controls—human behaviour remains the primary determinant of security posture.

This project implements a complete, self-contained, and interactive web application modeled on the research paper:

> **"Measuring information security behaviour of high school students and teachers"**

The system transitions the paper's theoretical framework into an operational software tool:
1. Captures participant profiles and evaluates **9 mandatory Likert-scale questions** across **3 essential focus areas** (Password Management, Social Media Use, and Email Use).
2. Calculates standardized percentage scores and categorizes awareness into **Good**, **Average**, and **Poor** bands.
3. Automatically computes psychometric validity (**Pearson Item-Total Correlation**) with dynamic sample-size critical values ($r_{\text{crit}}$) and reliability (**Cronbach's Alpha**).
4. Delivers dynamic administrative dashboards with **Chart.js visualizations** and direct side-by-side contrast against published research paper benchmarks.
5. Generates publication-ready **ReportLab PDF reports** and facilitates **CSV / Excel (.xlsx)** dataset exports.
6. Employs a rule-based **Recommendation Engine** addressing both individual weak areas and educator role-model responsibilities.

---

## 2. Main Objectives

- **Empirical Measurement:** Systematically quantify the security habits of High School Students versus High School Teachers.
- **Three Critical Focus Areas:**
  - **Password Management:** Credential uniqueness, anti-sharing discipline, and complexity.
  - **Social Media Use:** Application privacy audit, risk deliberation before sharing, and content filtering.
  - **Email Use:** Suspicious link avoidance, anti-phishing scrutiny, and unknown attachment isolation.
- **Psychometric Rigor:** Reproduce SPSS-grade statistical routines using open-source Python (`SciPy`, `NumPy`, `pandas`).
- **Actionable Remediation:** Provide prioritized, role-specific guidelines to cultivate institutional cyber resilience.

---

## 3. Technology Stack

This application was engineered with a clear, reliable, and lightweight tech stack optimized for B.Tech / academic project reviews:

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ / Flask | High clarity, modular design, easy college demonstration. |
| **Database** | SQLite 3 | Embedded, zero-configuration, ACID-compliant file database. |
| **Frontend** | HTML5, CSS3, JavaScript | Pure standards-compliant clientside code with no heavy Node.js runtimes. |
| **UI Framework** | Bootstrap 5.3 + Font Awesome | Responsive, clean academic cyber-security visual styling. |
| **Charts** | Chart.js 4 | Interactive client-side bar, doughnut, and grouped comparative charts. |
| **Statistics** | pandas, NumPy, SciPy | Automated Pearson correlation ($r$), $p$-values, Student's $t$ critical values, and Cronbach's $\alpha$. |
| **PDF Reporting**| ReportLab | Programmatic vector PDF compilation with dynamic two-pass page numbering. |
| **Data Export** | openpyxl & pandas | Native Excel (.xlsx) and CSV spreadsheet generation. |
| **Testing** | pytest | Automated test suite verifying math, classifications, and persistence. |

---

## 4. Project Folder Structure

```text
Information_Security_Awareness_System/
│
├── app.py                      # Flask main application entry point and HTTP route handlers
├── config.py                   # Configuration, score thresholds, and paper reference metadata
├── requirements.txt            # Python dependencies (Flask, pandas, scipy, reportlab, etc.)
├── README.md                   # Comprehensive academic documentation and setup guide
├── run.bat                     # Windows Command Prompt 1-click execution launcher
├── run.ps1                     # Windows PowerShell launcher script
├── database.db                 # Auto-generated SQLite database file (created on initial launch)
│
├── data/
│   ├── questionnaire.json      # Survey specification with the 9 research items and Likert scale
│   └── sample_responses.csv    # 45 realistic demonstration records (Students & Teachers)
│
├── models/
│   └── database.py             # SQLite schema, foreign-key constraints, queries, and demo loader
│
├── services/
│   ├── scoring.py              # Percentage normalization, focus area averages, and classification
│   ├── statistics.py           # Dashboard statistics aggregation and Chart.js payloads
│   ├── validation.py           # Item-total Pearson correlation (r), critical r, and Cronbach's Alpha
│   ├── recommendations.py      # Rule-based recommendation engine and teacher role-model catalog
│   └── report_generator.py     # ReportLab PDF report generation engine
│
├── templates/
│   ├── base.html               # Base layout template with navbar, footer, and flash alerts
│   ├── index.html              # Home page with hero banner and methodology workflow diagram
│   ├── questionnaire.html      # 5-point Likert assessment form with validation and progress tracker
│   ├── result.html             # Individual scorecard with priorities and personalized advice
│   ├── dashboard.html          # Admin analytics dashboard with 6 charts and benchmark comparison
│   ├── respondents.html        # Searchable and filterable respondent submissions directory
│   ├── validation.html         # Statistical validity and reliability psychometric report page
│   ├── recommendations.html    # Actionable security guidelines and educator role-model program
│   └── about.html              # Detailed academic documentation and methodology explanation
│
├── static/
│   ├── css/
│   │   └── style.css           # Academic cybersecurity theme, custom badges, and responsiveness
│   ├── js/
│   │   └── main.js             # Client-side input validation, dynamic age range, and table filters
│   └── images/                 # Image assets directory
│
├── reports/                    # Generated PDF reports storage folder
│
└── tests/
    ├── test_scoring.py         # Unit tests for scoring logic, classification, and priorities
    └── test_validation.py      # Unit tests for Pearson validity, Cronbach's alpha, and DB stats
```

---

## 5. Questionnaire Structure & Focus Areas

The system utilizes the 9 standardized statements formulated in the reference study, scored on a **5-point Likert Scale**:
- `1` = Strongly Disagree
- `2` = Disagree
- `3` = Neutral
- `4` = Agree
- `5` = Strongly Agree

### Focus Area 1: Password Management
- **ISBP1:** *"I always use different passwords for each of my accounts."*
- **ISBP2:** *"I never share my passwords with my friends or family."*
- **ISBP3:** *"I always use a combination of numbers, letters and symbols to make a password."*

### Focus Area 2: Social Media Use
- **ISBS1:** *"I always read the privacy settings of my social media or applications."*
- **ISBS2:** *"I always think about the negative effect that might happen before posting something on my social media."*
- **ISBS3:** *"I always filter what I would post on social media."*

### Focus Area 3: Email Use
- **ISBE1:** *"I never click on suspicious links even if they are from people that I know."*
- **ISBE2:** *"I never open a file that has been sent to me by people that I don't know."*
- **ISBE3:** *"I never click on links that are sent to me from people that I don't know."*

---

## 6. Mathematical & Scoring Methodology

### 6.1 Individual Question Normalization
Each Likert response $x_i \in \{1, 2, 3, 4, 5\}$ is converted into a standardized percentage:
$$\text{Percentage}(x_i) = \left(\frac{x_i}{5}\right) \times 100$$

### 6.2 Focus Area Calculation
For each focus area comprising 3 questions:
$$\text{Score}_{\text{Focus Area}} = \frac{1}{3} \sum_{i=1}^{3} \text{Percentage}(x_i)$$

### 6.3 Composite Overall Awareness Score
$$\text{Score}_{\text{Overall}} = \frac{1}{9} \sum_{i=1}^{9} \text{Percentage}(x_i)$$

### 6.4 Awareness Classification Rubric
Based directly on the reference research methodology:
- **Good (80.0% – 100.0%):** High security discipline. No immediate remediation required.
- **Average (60.0% – 79.9%):** Moderate awareness. Secondary educational intervention recommended.
- **Poor (0.0% – 59.9%):** Low awareness, critical behavioral exposure. Immediate remediation required.

### 6.5 Priority Mapping
- **Poor** $\rightarrow$ **High priority**
- **Average** $\rightarrow$ **Moderate priority**
- **Good** $\rightarrow$ **No immediate action required**

---

## 7. Statistical Validity & Reliability

### 7.1 Questionnaire Validity (Pearson Item-Total Correlation)
Item validity is determined by calculating the Pearson correlation coefficient ($r$) between the score of each individual item and the sum of all 9 items across respondents:
$$r = \frac{\sum (X - \bar{X})(Y - \bar{Y})}{\sqrt{\sum (X - \bar{X})^2 \sum (Y - \bar{Y})^2}}$$

#### Dynamic Critical Value Calculation ($r_{\text{crit}}$)
Rather than hard-coding static tables, this system computes the two-tailed critical correlation value adaptively for any sample size $N$ using Student's $t$ distribution:
$$df = N - 2, \quad \alpha = 0.05$$
$$r_{\text{crit}} = \frac{t_{\text{crit}}}{\sqrt{df + t_{\text{crit}}^2}}$$

- **Decision Criterion:** If $r > r_{\text{crit}}$ and $p < 0.05$, the questionnaire item is statistically **Valid**.
- In the published study, $r_{\text{table}} \approx 0.142$ was reported for the author's specific sample size.

### 7.2 Questionnaire Reliability (Cronbach's Alpha)
Internal consistency is measured across all 9 items, and independently for each 3-item focus area:
$$\alpha = \frac{k}{k - 1} \left( 1 - \frac{\sum_{i=1}^{k} \sigma_i^2}{\sigma_{\text{total}}^2} \right)$$
where $k$ is the number of items, $\sigma_i^2$ is individual item variance, and $\sigma_{\text{total}}^2$ is variance of the total score.

#### Psychometric Reliability Interpretation:
- $\alpha \ge 0.90$: **Excellent**
- $0.80 \le \alpha < 0.89$: **Good**
- $0.70 \le \alpha < 0.79$: **Acceptable**
- $0.60 \le \alpha < 0.69$: **Questionable**
- $\alpha < 0.60$: **Poor**

---

## 8. Benchmark Reference Results vs. Live Project Data

To ensure complete academic transparency, the dashboard contrasts live database findings with the published results from the reference paper:

| Cohort / Dimension | Reference Paper Result | Live Database Result |
| :--- | :--- | :--- |
| **All Respondents** | **67.2% (Average)** | *Dynamically aggregated* |
| **Students (Overall)** | **86.0% (Good)** | *Dynamically aggregated* |
| — Password Management | 81.7% (Good) | *Dynamically aggregated* |
| — Social Media Use | 87.4% (Good) | *Dynamically aggregated* |
| — Email Use | 88.9% (Good) | *Dynamically aggregated* |
| **Teachers (Overall)** | **46.3% (Poor)** | *Dynamically aggregated* |
| — Password Management | 35.9% (Poor) | *Dynamically aggregated* |
| — Social Media Use | 59.4% (Average) | *Dynamically aggregated* |
| — Email Use | 43.6% (Poor) | *Dynamically aggregated* |

*Reference Paper Reliability: Password $\alpha = 0.877$, Social Media $\alpha = 0.823$, Email $\alpha = 0.955$.*

---

## 9. Installation & Running Instructions

### Note on Desktop Path Detection
On Windows machines, the Desktop path is typically located at:
- `C:\Users\<username>\Desktop`  
or (when Microsoft OneDrive folder protection is enabled):
- `C:\Users\<username>\OneDrive\Desktop`

This project resides in your actual Desktop path at:
```text
C:\Users\<username>\OneDrive\Desktop\Information_Security_Awareness_System
```

---

### Option A: 1-Click Launch (Recommended)

Simply double-click the included batch script:
```text
run.bat
```
This script automatically:
1. Detects your Python installation.
2. Creates the isolated virtual environment (`venv`).
3. Installs all required packages from `requirements.txt`.
4. Initializes the SQLite schema and survey questions.
5. Launches the Flask server and opens `http://127.0.0.1:5000` in your default browser.

---

### Option B: Windows Command Prompt (cmd.exe)

1. Open Command Prompt and navigate to the project directory:
   ```cmd
   cd "C:\Users\%USERNAME%\OneDrive\Desktop\Information_Security_Awareness_System"
   ```
   *(If your Desktop is not on OneDrive, use `cd "C:\Users\%USERNAME%\Desktop\Information_Security_Awareness_System"`)*

2. Create and activate a Python virtual environment:
   ```cmd
   python -m venv venv
   call venv\Scripts\activate.bat
   ```

3. Install requirements:
   ```cmd
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```cmd
   python -c "from models.database import init_db; init_db()"
   ```

5. Run the web server:
   ```cmd
   python app.py
   ```

6. Open your web browser at:
   ```text
   http://127.0.0.1:5000
   ```

---

### Option C: Windows PowerShell

1. Open PowerShell and navigate to the project folder:
   ```powershell
   cd "$HOME\OneDrive\Desktop\Information_Security_Awareness_System"
   ```

2. Execute the PowerShell launcher script:
   ```powershell
   .\run.ps1
   ```
   *(If script execution is disabled on your system, execute: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

Or manually:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

---

### Option D: Visual Studio Code (VS Code)

1. Open VS Code.
2. Select **File $\rightarrow$ Open Folder...** and choose `Information_Security_Awareness_System`.
3. Open the integrated terminal (`Ctrl + ~`).
4. Select the Python interpreter:
   - Press `Ctrl + Shift + P` $\rightarrow$ type `Python: Select Interpreter` $\rightarrow$ pick `./venv/Scripts/python.exe`.
5. In the terminal, run:
   ```bash
   python app.py
   ```

---

## 10. How to Use & Demonstrate the System

### 10.1 Load Demo Data (Immediate Demonstration)
1. Open `http://127.0.0.1:5000/dashboard`.
2. Click the **"Load Demo Data"** button in the top right.
3. The system will load 45 realistic student and teacher responses from `data/sample_responses.csv`.
4. All 6 charts, student vs. teacher tables, and distribution widgets will populate instantly.

### 10.2 Take an Assessment
1. Click **"Take Assessment"** in the navigation bar.
2. Enter your Name, Role (Student or Teacher), Age (validates appropriate high school age for students, adult educator age for teachers), Gender, and School.
3. Answer all 9 Likert statements (1 to 5).
4. Click **"Submit Assessment & Calculate Scores"**.
5. View your individual scorecard, priority flags (High / Moderate / None), and tailored recommendations.

### 10.3 Inspect Validity & Reliability
1. Navigate to **"Validity & Reliability"** (`/validation`).
2. Examine the Pearson correlation coefficients ($r$), $p$-values, item means, and the dynamically calculated critical threshold $r_{\text{crit}}$.
3. Review the Cronbach's Alpha ($\alpha$) internal consistency results for Password, Social Media, Email, and Overall scales.

### 10.4 Generate Academic PDF Report
1. On the Dashboard or Respondents page, click **"Download PDF Report"**.
2. A formal research summary PDF is dynamically compiled using ReportLab with headers, footers, tables, and recommendations.

### 10.5 Export Datasets
1. Click **"Export CSV"** or **"Export Excel (.xlsx)"** from the Dashboard or Respondents directory.
2. Open the downloaded file in Microsoft Excel or Google Sheets.

---

## 11. Automated Test Suite

To run the automated verification test suite:
```cmd
pytest
```
The test suite verifies:
- Likert conversion to percentage
- Exact threshold boundaries (80% Good, 60% Average, <60% Poor)
- Arithmetic mean calculations
- Cronbach's Alpha computation & interpretation
- Pearson item-total correlation and dynamic critical value calculation
- SQLite persistence and statistics calculations

---

## 12. Troubleshooting

| Issue | Resolution |
| :--- | :--- |
| `python : The term 'python' is not recognized` | Install Python from python.org and check the box **"Add python.exe to PATH"**. |
| `ImportError: No module named 'flask'` | Ensure your virtual environment is activated (`venv\Scripts\activate`) before installing `requirements.txt`. |
| Port 5000 is already in use | Run on an alternate port: edit the last line of `app.py` to `app.run(port=5050)`. |
| PowerShell Execution Policy error | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window. |

---

## 13. Academic Attribution

This software application was built as an academic full-stack computer science project inspired by the methodology described in:
- *"Measuring information security behaviour of high school students and teachers"*

All statistical models, questionnaires, scoring rubrics, and comparison structures reflect the methodologies established in the reference literature.
