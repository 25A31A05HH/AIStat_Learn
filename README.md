# AIStat Learn

## AI-Powered Personalized Learning & Competency Assessment Platform

AIStat Learn is an AI-powered personalized learning platform designed to help learners study from their own learning materials, assess their knowledge, identify competency gaps, receive personalized recommendations, and track their learning progress.

The project was developed as a **solo project** for the **SkillUp Hackathon in collaboration with IBM SkillsBuild**.

---

## Problem Statement

Students often depend on multiple platforms for studying, practicing assessments, identifying weak areas, and monitoring their progress. Traditional learning systems generally follow a one-size-fits-all approach and may not provide learners with personalized feedback based on their individual performance.

Students also have learning materials in formats such as PDF documents and personal notes, but converting this material into useful assessments can be time-consuming.

---

## Solution

AIStat Learn brings learning material processing, assessment generation, competency analysis, personalized recommendations, learning planning, and progress tracking into a single platform.

The system allows learners to use their own study material and transform it into an interactive learning and assessment experience.

### Core Workflow

```text
Learning Material
       ↓
Content Processing
       ↓
MCQ Generation
       ↓
Assessment
       ↓
Performance Analysis
       ↓
Competency Gap Identification
       ↓
Personalized Recommendations
       ↓
Learning Plan
       ↓
Progress Tracking
       ↓
Continuous Improvement
```

---

## Key Features

### 📚 Learning Material Processing

Learners can provide study material using supported document formats and use the content as the basis for their learning and assessment.

### 📝 AI-Assisted MCQ Generation

The platform generates multiple-choice questions from the provided learning content, helping learners test their understanding.

### 🎯 Competency Assessment

Assessment results are analyzed to understand the learner's performance and identify areas that require improvement.

### 📊 Progress Tracking

Learners can monitor their performance and observe their progress across different learning areas.

### 🧠 Personalized Recommendations

Based on assessment performance, the system provides recommendations that help learners focus on areas where additional practice is needed.

### 📅 Learning Plan

The platform supports a structured learning workflow to help learners organize their learning activities and continue improving.

---

## Technology Stack

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **PyPDF2**
* **python-docx**
* **Supabase**
* **IBM Bob**

---

## Project Structure

```text
AIStat_Learn/
│
├── app.py
├── adaptive_recommendations.py
├── assessment_comparator.py
├── competency_analyzer.py
├── learning_plan.py
├── mcq_generator.py
├── progress_manager.py
├── progress_tracker.py
├── student_manager.py
├── student_progress.json
├── style.css
│
├── requirements.txt
├── README.md
└── IBM_BOB_USAGE.md
```

---

## Description of Main Modules

| File                          | Purpose                               |
| ----------------------------- | ------------------------------------- |
| `app.py`                      | Main Streamlit application            |
| `adaptive_recommendations.py` | Personalized learning recommendations |
| `assessment_comparator.py`    | Assessment performance comparison     |
| `competency_analyzer.py`      | Learner competency analysis           |
| `learning_plan.py`            | Learning-plan functionality           |
| `mcq_generator.py`            | MCQ generation functionality          |
| `progress_manager.py`         | Progress management                   |
| `progress_tracker.py`         | Learning progress tracking            |
| `student_manager.py`          | Student-related data management       |
| `student_progress.json`       | Local progress data                   |
| `style.css`                   | Application styling                   |

---

## IBM Bob Usage

IBM Bob was used as an AI-powered development partner during the development of AIStat Learn.

It assisted with activities such as:

* Project planning
* Code development
* Code modification
* Debugging
* Feature refinement
* Code understanding
* Refactoring
* Documentation support

The development workflow involved using IBM Bob assistance, reviewing the suggested changes, testing the application, identifying issues, and refining the implementation.

Detailed information about IBM Bob's role in the project is available in:

**`IBM_BOB_USAGE.md`**

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/25A31A05HH/AIStat_Learn.git
```

### 2. Open the Project Folder

```bash
cd AIStat_Learn
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in the browser through the Streamlit local server.

---

## Requirements

The project dependencies are listed in:

```text
requirements.txt
```

Current dependencies include:

```text
streamlit
pandas
numpy
scikit-learn
PyPDF2
python-docx
supabase
```

---

## Future Improvements

Possible future enhancements include:

* More advanced AI-based competency prediction
* Improved personalization using learner history
* More detailed analytics dashboards
* Enhanced learning-plan recommendations
* Additional document formats
* Cloud-based persistent learner profiles
* Improved assessment security
* Deployment as a scalable web application

---

## Project Objective

The objective of AIStat Learn is to make learning:

* **Personalized**
* **Interactive**
* **Measurable**
* **Data-driven**
* **Continuous**

The platform aims to help learners follow a cycle of:

> **Learn → Assess → Identify Gaps → Practice → Track → Improve**

---

## Developer

**Surimalla Venkata Tejaswi**

Computer Science and Engineering
Pragati Engineering College

---

## Hackathon

**SkillUp Hackathon in collaboration with IBM SkillsBuild**

### Project

**AIStat Learn – AI-Powered Personalized Learning & Competency Assessment Platform**

---

## Repository

**GitHub:**
https://github.com/25A31A05HH/AIStat_Learn

---

## Conclusion

AIStat Learn demonstrates how artificial intelligence and modern software-development tools can be used to create a personalized learning experience.

By connecting learning materials, assessments, competency analysis, recommendations, learning plans, and progress tracking, the platform provides learners with a structured approach to continuous improvement.

**AIStat Learn — Learn. Assess. Identify Gaps. Improve.**
