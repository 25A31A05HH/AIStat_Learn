# 🎓 AIStat Learn

## AI-Powered Adaptive Learning and Student Assessment Platform

> **Learn smarter. Assess yourself. Identify your gaps. Improve continuously.**

**AIStat Learn** is a Python and Streamlit-based adaptive learning platform designed to provide students with a personalized learning experience.

The platform transforms ordinary study material into an interactive learning journey by allowing students to **upload learning material, generate MCQs, take assessments, analyze their performance, identify competency gaps, track progress, and receive personalized learning recommendations and learning plans.**

---

## 🌟 Project Vision

Traditional learning often follows:

**Study → Write Exam → Get Marks**

AIStat Learn transforms this into:

**Study → Practice → Assess → Analyze → Identify Gaps → Personalized Learning → Improve → Reassess**

The goal is to help students understand **not only what they know, but also what they need to learn next.**

---

# 🚀 Complete Project Workflow

The complete AIStat Learn process is:

```text
                🎓 AIStat Learn
                       │
                       ▼
              🏠 Open Application
                       │
                       ▼
          📚 Upload Learning Material
                       │
                       ▼
              📄 Extract PDF Text
                       │
                       ▼
             🤖 Generate MCQs
                       │
                       ▼
             ✍️ Take Assessment
                       │
                       ▼
          📊 Calculate Performance
                       │
                       ▼
          🎯 Identify Competency Gaps
                       │
                       ▼
             📈 Track Progress
                       │
                       ▼
       🧠 Generate Recommendations
                       │
                       ▼
          📅 Personalized Learning Plan
                       │
                       ▼
               🔄 Learn & Improve
```

---

# 🖥️ Application Walkthrough

## 1️⃣ 🏠 Open AIStat Learn

The journey begins with the AIStat Learn home page.

The application provides a simple navigation system that guides the student through every stage of the learning process.

### Main Navigation

* 🏠 Home
* 📚 Learning Material
* 📝 Generate Questions
* ✍️ Take Assessment
* 📊 Progress
* 📅 Learning Plan
* 🔧 System Check

### 📸 Application Screenshot

Add your Home screen screenshot here:

```text
docs/screenshots/01-home.png
```

---

# 2️⃣ 📚 Upload Learning Material

The student begins by uploading their study material in PDF format.

AIStat Learn reads the uploaded document and extracts the available text so that it can be used for question generation and learning analysis.

### Process

```text
PDF Learning Material
        ↓
      Upload
        ↓
   PDF Processing
        ↓
   Text Extraction
        ↓
 Learning Material Ready
```

### Key Functionality

* PDF upload
* PDF text extraction
* Learning material storage
* Material preview
* Preparation for MCQ generation

### 📸 Screenshot

```text
docs/screenshots/02-learning-material.png
```

---

# 3️⃣ 🤖 Generate MCQs

Once the learning material is available, the student can choose the number of questions they want to practice.

AIStat Learn generates multiple-choice questions based on the uploaded learning material.

### Process

```text
Learning Material
       ↓
   Text Processing
       ↓
Concept Identification
       ↓
 Question Generation
       ↓
MCQs + Multiple Options
```

### Features

* Custom number of questions
* Multiple-choice options
* Topic-based questions
* Concept information
* Automated question generation
* Practice-ready assessment

### 📸 Screenshot

```text
docs/screenshots/03-generate-questions.png
```

---

# 4️⃣ ✍️ Take Assessment

The generated MCQs are presented to the student as an interactive assessment.

Students can select their answers using clickable options and submit the assessment after answering all questions.

### Assessment Flow

```text
Generated Questions
        ↓
   Select Answers
        ↓
 Answer All Questions
        ↓
 Submit Assessment
```

### 📸 Screenshot

```text
docs/screenshots/04-assessment.png
```

---

# 5️⃣ 📊 Assessment Results

After submitting the assessment, AIStat Learn evaluates the student's performance.

The platform calculates:

* Total questions
* Correct answers
* Incorrect answers
* Score
* Percentage
* Overall performance
* Topic-wise performance

The student can also review their answers and compare them with the correct answers.

### Example Performance Levels

```text
80% – 100%   → Excellent 🎉
60% – 79%    → Good 👍
40% – 59%    → Needs Practice 📚
Below 40%    → Needs Improvement 💪
```

### 📸 Screenshot

```text
docs/screenshots/05-results.png
```

---

# 6️⃣ 🎯 Competency & Weak Topic Analysis

AIStat Learn goes beyond calculating a score.

It analyzes the student's performance to identify:

### 🟢 Strong Areas

Concepts where the student demonstrates good understanding.

### 🟡 Areas That Need Practice

Topics where the student has moderate performance.

### 🔴 Weak Areas

Concepts where the student needs focused revision and additional practice.

This helps transform assessment results into **actionable learning recommendations**.

### 📸 Screenshot

```text
docs/screenshots/06-competency-analysis.png
```

---

# 7️⃣ 📈 Progress Tracking

The platform tracks student performance and provides a clear view of learning progress.

Students can understand:

* How many questions they attempted
* How many they answered correctly
* Their accuracy
* Topic-wise performance
* Weak areas
* Improvement areas

### Progress Cycle

```text
Assessment
    ↓
Performance Data
    ↓
Topic Analysis
    ↓
Progress Tracking
    ↓
Improvement Recommendations
```

### 📸 Screenshot

```text
docs/screenshots/07-progress.png
```

---

# 8️⃣ 🧠 Adaptive Recommendations

The recommendation system uses assessment performance and competency information to guide the student toward areas that need additional attention.

Instead of giving the same learning advice to every student, AIStat Learn aims to provide recommendations based on individual performance.

### Example

```text
Low performance in Topic A
          ↓
Recommend Topic A revision
          ↓
Practice Topic A questions
          ↓
Reassess
          ↓
Measure improvement
```

---

# 9️⃣ 📅 Personalized Learning Plan

The final stage of the learning journey is the **Personalized Learning Plan**.

The learning plan connects the student's learning material with their assessment performance and identified learning gaps.

The student receives structured guidance on what to study, revise, and practice.

### Personalized Learning Cycle

```text
Learning Material
       +
Assessment Performance
       +
Weak Topics
       ↓
Personalized Learning Plan
       ↓
Targeted Study
       ↓
Practice
       ↓
Reassessment
```

### 📸 Screenshot

```text
docs/screenshots/08-learning-plan.png
```

---

# 🔄 Complete Adaptive Learning Cycle

AIStat Learn is designed around a continuous improvement loop:

```text
       📚 LEARN
          ↓
      🤖 PRACTICE
          ↓
      ✍️ ASSESS
          ↓
      📊 ANALYZE
          ↓
   🎯 IDENTIFY GAPS
          ↓
      🧠 RECOMMEND
          ↓
       📅 PLAN
          ↓
      📚 LEARN AGAIN
          ↺
```

This creates a continuous:

> **Learn → Practice → Assess → Analyze → Improve**

learning cycle.

---

# 🏗️ System Architecture

```text
                         👨‍🎓 Student
                              │
                              ▼
                    🖥️ Streamlit Interface
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
 📚 Learning Material   🤖 MCQ Generator     ✍️ Assessment
        │                     │                     │
        ▼                     ▼                     ▼
    📄 PyPDF2             📝 Questions       📊 Results
                              │                     │
                              └─────────┬───────────┘
                                        ▼
                              🎯 Competency Analysis
                                        │
                                        ▼
                                📈 Progress Tracking
                                        │
                                        ▼
                             🧠 Recommendations
                                        │
                                        ▼
                              📅 Learning Plan
                                        │
                                        ▼
                                  👨‍🎓 Student
```

---

# ✨ Key Features

## 📚 Adaptive Recommendations

Provides learning recommendations based on student performance and identified learning gaps.

## 📝 MCQ Generation

Generates multiple-choice questions from learning material for practice and assessment.

## 📊 Assessment Comparison

Compares assessment performance and helps identify changes in student results.

## 🎯 Competency Analysis

Analyzes student competencies and identifies areas requiring improvement.

## 📈 Progress Tracking

Tracks assessment results and student learning progress.

## 🧠 Personalized Learning Plans

Creates structured learning guidance based on performance and competency gaps.

## 👨‍🎓 Student Management

Manages student information and progress records.

## 📄 PDF Support

Allows students to use PDF-based learning material.

## 🌐 Interactive Streamlit Interface

Provides a simple, interactive and user-friendly web interface.

## 🗄️ Database Integration

Supports persistent storage of learning materials, quizzes and assessment information through Supabase.

---

# 🛠️ Technologies Used

| Technology         | Purpose                                |
| ------------------ | -------------------------------------- |
| 🐍 Python          | Core programming and application logic |
| 🎈 Streamlit       | Interactive web application            |
| 🐼 Pandas          | Data processing and analysis           |
| 🔢 NumPy           | Numerical operations                   |
| 🤖 Scikit-learn    | Machine learning functionality         |
| 📄 PyPDF2          | PDF text extraction                    |
| 🗄️ Supabase       | Cloud database                         |
| 🐙 GitHub          | Version control and project hosting    |
| 🚀 Streamlit Cloud | Application deployment                 |

---

# 📂 Project Structure

```text
AIStat_Learn/
│
├── adaptive_recommendations.py
│
├── app.py
│
├── assessment_comparator.py
│
├── competency_analyzer.py
│
├── learning_plan.py
│
├── mcq_generator.py
│
├── progress_manager.py
│
├── progress_taker.py
│
├── student_manager.py
│
├── student_progress.json
│
├── style.py
│
├── requirements.txt
│
├── README.md
│
└── docs/
    │
    ├── screenshots/
    │   ├── 01-home.png
    │   ├── 02-learning-material.png
    │   ├── 03-generate-questions.png
    │   ├── 04-assessment.png
    │   ├── 05-results.png
    │   ├── 06-competency-analysis.png
    │   ├── 07-progress.png
    │   └── 08-learning-plan.png
    │
    └── demo/
        └── aistat-learn-demo.mp4
```

---

# 📌 Main Modules

| File                          | Purpose                                     |
| ----------------------------- | ------------------------------------------- |
| `app.py`                      | Main Streamlit application                  |
| `adaptive_recommendations.py` | Generates adaptive learning recommendations |
| `assessment_comparator.py`    | Compares assessment results                 |
| `competency_analyzer.py`      | Analyzes student competencies               |
| `learning_plan.py`            | Creates personalized learning plans         |
| `mcq_generator.py`            | Generates MCQ assessments                   |
| `progress_manager.py`         | Manages student progress                    |
| `progress_taker.py`           | Handles progress-taking functionality       |
| `student_manager.py`          | Manages student information                 |
| `student_progress.json`       | Stores student progress data                |
| `style.py`                    | Application styling                         |

---

# 🎯 Problem Statement

Students often study large amounts of academic material without knowing exactly which concepts they understand and which concepts require additional attention.

Traditional assessment systems mainly provide a score after an examination.

However, a score alone does not answer important questions such as:

* Which topics are weak?
* What should the student revise?
* What should the student practice next?
* Is the student's performance improving?
* How can learning be personalized?

AIStat Learn addresses this gap by connecting **learning material, assessment, performance analysis and personalized recommendations** in a single platform.

---

# 💡 Proposed Solution

AIStat Learn provides an integrated adaptive learning environment.

```text
                    STUDENT
                       │
                       ▼
              Upload Study Material
                       │
                       ▼
               Generate Questions
                       │
                       ▼
                 Take Assessment
                       │
                       ▼
              Analyze Performance
                       │
                       ▼
             Identify Learning Gaps
                       │
                       ▼
            Generate Recommendations
                       │
                       ▼
             Personalized Learning Plan
                       │
                       ▼
                Improve Knowledge
                       │
                       └───────────────↺
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

## 2. Open the Project Folder

```bash
cd AIStat_Learn
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 5. Install Required Packages

```bash
pip install -r requirements.txt
```

## 6. Run the Application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

# 💻 Running the Application

After starting Streamlit, the application will normally be available at:

```text
http://localhost:8501
```

Open the address in your browser to use AIStat Learn.

---

# 🗄️ Database

AIStat Learn can use **Supabase** for cloud-based data storage.

The database can be used for storing information such as:

* Learning materials
* Generated quizzes
* Assessment attempts
* Student progress

### 🔐 Security

Database credentials and application secrets should **never be committed to GitHub**.

For example:

```text
.streamlit/
└── secrets.toml
```

`secrets.toml` should remain private and should be included in `.gitignore`.

---

# 🌐 Live Application

🚀 **AIStat Learn Live Demo**

> Add your deployed Streamlit application link here.

---

# 📸 Application Screenshots

The GitHub repository should present the application journey in this order:

### 01 — Home

```text
docs/screenshots/01-home.png
```

### 02 — Learning Material

```text
docs/screenshots/02-learning-material.png
```

### 03 — Generate Questions

```text
docs/screenshots/03-generate-questions.png
```

### 04 — Assessment

```text
docs/screenshots/04-assessment.png
```

### 05 — Results

```text
docs/screenshots/05-results.png
```

### 06 — Competency Analysis

```text
docs/screenshots/06-competency-analysis.png
```

### 07 — Progress

```text
docs/screenshots/07-progress.png
```

### 08 — Learning Plan

```text
docs/screenshots/08-learning-plan.png
```

---

# 🎥 Project Demonstration

A complete walkthrough demonstrates the entire AIStat Learn process:

```text
🏠 Open Application
      ↓
📚 Upload PDF
      ↓
🤖 Generate MCQs
      ↓
✍️ Answer Questions
      ↓
📊 View Results
      ↓
🎯 Identify Weak Areas
      ↓
📈 Track Progress
      ↓
📅 Follow Learning Plan
```

Add the project demonstration video to:

```text
docs/demo/aistat-learn-demo.mp4
```

For a large video file, use a hosted video link instead of committing the video directly to the repository.

---

# 🏆 What Makes AIStat Learn Different?

AIStat Learn does not stop after generating questions.

The platform connects multiple stages of the student's learning journey:

```text
Learning Material
       +
Question Generation
       +
Assessment
       +
Performance Analysis
       +
Competency Analysis
       +
Progress Tracking
       +
Adaptive Recommendations
       +
Personalized Learning Plan
```

This makes the project more than a simple quiz application.

It is designed as an **adaptive learning and student assessment platform**.

---

# 🔮 Future Enhancements

The platform can be extended with:

* 🤖 More advanced AI-based question generation
* 🧠 Advanced personalized recommendation algorithms
* 📊 Advanced student analytics
* 📈 Interactive learning dashboards
* 🗄️ Expanded cloud database integration
* 🔐 User authentication
* 👨‍🏫 Teacher and student dashboards
* 🏆 Gamification and achievement badges
* 📱 Mobile application
* 🎙️ Voice-based learning assistant
* 🌍 Multi-language learning support
* 🔔 Personalized study reminders
* 📚 Support for additional document formats

---

# 🎯 Project Objective

The main objective of **AIStat Learn** is to support personalized education by using student assessment data to identify learning gaps, track progress and provide suitable learning recommendations.

The project aims to make learning:

**Personalized • Measurable • Adaptive • Actionable**

---

# 👩‍💻 Author

## S. Venkata Tejaswi

**Computer Science & Engineering Student**
**Pragati Engineering College**

### GitHub

`25A31A05HH`

### LeetCode

`venkata_tejaswi`

---

# ⭐ Support the Project

If you find **AIStat Learn** useful or interesting, consider giving the repository a ⭐ star.

---

## 🚀 AIStat Learn

> **From learning material to personalized improvement — AIStat Learn connects every step of the student's learning journey.**

**Learn → Practice → Assess → Analyze → Improve**
