# AIStat_Learn

**AI-Powered Adaptive Learning and Student Assessment Platform**

AIStat_Learn is a Python and Streamlit-based adaptive learning platform designed to help students assess their knowledge, track their academic progress, identify competency gaps, and receive personalized learning recommendations.

## 🚀 Features

* 📚 **Adaptive Recommendations**
  Provides personalized learning recommendations based on student performance.

* 📝 **MCQ Generation**
  Generates multiple-choice questions for assessment and practice.

* 📊 **Assessment Comparison**
  Compares assessment performance and identifies changes in student results.

* 🎯 **Competency Analysis**
  Analyzes student competencies and identifies areas that require improvement.

* 📈 **Progress Tracking**
  Tracks student learning progress and assessment results.

* 🧠 **Personalized Learning Plans**
  Creates learning plans based on student performance and competency gaps.

* 👨‍🎓 **Student Management**
  Manages student information and progress records.

* 📄 **PDF Support**
  Supports reading and processing PDF-based learning material.

* 🌐 **Streamlit Interface**
  Provides an interactive and user-friendly web interface.

## 🛠️ Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-learn
* PyPDF2

## 📂 Project Structure

```text
AIStat_Learn/
│
├── adaptive_recommendations.py
├── app.py
├── assessment_comparator.py
├── competency_analyzer.py
├── learning_plan.py
├── mcq_generator.py
├── progress_manager.py
├── progress_taker.py
├── student_manager.py
├── student_progress.json
├── style.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AIStat_Learn.git
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Open the project folder

```bash
cd AIStat_Learn
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 💻 Running the Application

After starting Streamlit, you should see a local address similar to:

```text
http://localhost:8501
```

Open this address in your browser to use AIStat_Learn.

## 📌 Main Modules

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

## 🎯 Objective

The main objective of AIStat_Learn is to support personalized education by using student assessment data to identify learning gaps and provide suitable learning recommendations.

## 🔮 Future Enhancements

* AI-based question generation
* Advanced student performance analytics
* Learning dashboards and visualizations
* Integration with cloud databases
* User authentication
* More advanced recommendation algorithms
* Deployment as a cloud-based application

## 👩‍💻 Author

**S. Venkata Tejaswi**

Computer Science Engineering Student

---

⭐ If you find this project useful, consider giving the repository a star!
