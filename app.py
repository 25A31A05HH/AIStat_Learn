import os
import uuid
import re
import streamlit as st
import pandas as pd

from mcq_generator import generate_mcqs

# =========================================================
# PDF SUPPORT
# =========================================================

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AIStat Learn",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
    }

    .sub-title {
        font-size: 20px;
        color: #666;
    }

    .score-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }

    .correct-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-top: 10px;
    }

    .topic-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "user_id": str(uuid.uuid4()),
    "current_step": 1,

    "material_text": "",
    "material_name": "",

    "questions": [],
    "quiz_id": None,

    "assessment_answers": {},
    "quiz_submitted": False,

    "score": 0,
    "total_questions": 0,
    "percentage": 0,

    "quiz_history": [],
    "topic_progress": {},

    "material_saved": False,
    "pdf_loaded": False,
    "last_uploaded_file": "",

    "show_topic_explanations": True
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SUPABASE CONNECTION
# =========================================================

supabase = None
db_status = "Not Connected"

try:
    from supabase import create_client

    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:

        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        db_status = "Connected"

    else:
        db_status = "Secrets not found"

except Exception as e:
    db_status = f"Connection error: {e}"


# =========================================================
# NAVIGATION FUNCTION
# =========================================================

def go_to_step(step_number):
    st.session_state.current_step = step_number
    st.rerun()


# =========================================================
# TEXT HELPERS
# =========================================================

def clean_display_text(text):
    if text is None:
        return ""

    text = str(text)

    text = text.replace("\\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_option(option):
    if option is None:
        return ""

    return clean_display_text(option)


def get_question_text(question):
    if isinstance(question, dict):

        for key in [
            "question",
            "question_text",
            "text"
        ]:
            if key in question:
                return clean_display_text(question[key])

    return clean_display_text(question)


def get_question_topic(question):

    if isinstance(question, dict):

        for key in [
            "topic",
            "subject",
            "category"
        ]:
            if key in question:
                return clean_display_text(question[key])

    return "General"


def get_question_concept(question):

    if isinstance(question, dict):

        for key in [
            "concept",
            "subtopic"
        ]:
            if key in question:
                return clean_display_text(question[key])

    return get_question_topic(question)


def get_correct_answer(question):

    if isinstance(question, dict):

        for key in [
            "correct_answer",
            "answer",
            "correct",
            "correct_option"
        ]:

            if key in question:

                value = question[key]

                if isinstance(value, int):
                    return str(value)

                return normalize_option(value)

    return ""


def get_options(question):

    if not isinstance(question, dict):
        return []

    options = question.get("options", [])

    if isinstance(options, dict):
        options = list(options.values())

    if not isinstance(options, list):
        options = []

    return [
        normalize_option(option)
        for option in options
    ]


def get_general_explanation(question):

    if isinstance(question, dict):

        for key in [
            "explanation",
            "answer_explanation",
            "reason"
        ]:

            if key in question:
                return clean_display_text(question[key])

    return ""


# =========================================================
# CORRECT OPTION FINDER
# =========================================================

def find_correct_option(question):

    correct = get_correct_answer(question)
    options = get_options(question)

    if not correct:
        return ""

    # If answer is A/B/C/D
    if correct.upper() in ["A", "B", "C", "D"]:

        index = ord(correct.upper()) - ord("A")

        if index < len(options):
            return options[index]

    # Match exact option text
    for option in options:

        if option.lower() == correct.lower():
            return option

    return correct


# =========================================================
# OPTION FEEDBACK
# =========================================================

def get_option_feedback(question, option):

    if not isinstance(question, dict):
        return ""

    feedback = question.get("option_feedback", {})

    if isinstance(feedback, dict):

        if option in feedback:
            return clean_display_text(feedback[option])

        for key, value in feedback.items():

            if str(key).lower() == str(option).lower():
                return clean_display_text(value)

    return ""


def explain_incorrect_option(question, option):

    question_text = get_question_text(question)
    topic = get_question_topic(question)

    correct_option = find_correct_option(question)

    if option == correct_option:
        return "This is the correct answer."

    option_lower = option.lower()

    # Common conceptual explanations
    if "stack" in option_lower and "queue" in question_text.lower():
        return (
            "A stack follows LIFO (Last In, First Out), "
            "while a queue follows FIFO (First In, First Out)."
        )

    if "queue" in option_lower and "stack" in question_text.lower():
        return (
            "A queue follows FIFO, whereas a stack follows "
            "LIFO. Therefore, this option does not match the question."
        )

    if "tree" in option_lower:
        return (
            "A tree is mainly used to represent hierarchical "
            "relationships. It does not represent the concept "
            "being asked here."
        )

    if "graph" in option_lower:
        return (
            "A graph is generally used to represent relationships "
            "or connections between entities. It is not the correct "
            "concept for this question."
        )

    return (
        f"This option is not correct because it does not match "
        f"the required concept of {topic}. "
        f"The correct answer is '{correct_option}'."
    )


# =========================================================
# TOPIC EXPLANATION
# =========================================================

def create_topic_explanation(topic):

    topic_lower = topic.lower()

    if "queue" in topic_lower:

        return """
### 📚 Queue

A **Queue** is a linear data structure that follows the **FIFO
(First In, First Out)** principle.

Think about people standing in a ticket line:

- The person who enters first gets served first.
- A new person joins at the back.
- The person at the front leaves first.

#### Main Queue Operations

- **Enqueue** → Add an element
- **Dequeue** → Remove an element
- **Front/Peek** → View the first element

💡 **Remember:** Queue = FIFO
"""

    if "stack" in topic_lower:

        return """
### 📚 Stack

A **Stack** is a linear data structure that follows the
**LIFO (Last In, First Out)** principle.

Think about a stack of plates:

- You place a new plate on top.
- You remove the top plate first.

#### Main Stack Operations

- **Push** → Add an element
- **Pop** → Remove the top element
- **Peek** → View the top element

💡 **Remember:** Stack = LIFO
"""

    if "array" in topic_lower:

        return """
### 📚 Array

An **Array** stores multiple elements of the same type in
contiguous memory locations.

Each element can be accessed using an index.

For example:

Array = [10, 20, 30, 40]

The first element is accessed using index 0.

💡 **Remember:** Array = indexed collection of elements.
"""

    if "linked list" in topic_lower:

        return """
### 📚 Linked List

A **Linked List** is a linear data structure made up of nodes.

Each node generally contains:

- Data
- A link/reference to the next node

Unlike arrays, linked-list elements do not need to be stored
in contiguous memory.

💡 **Remember:** Linked List = Nodes connected using links.
"""

    if "python" in topic_lower:

        return """
### 📚 Python

Python is a high-level, interpreted programming language.

It is widely used for:

- Web development
- Data analysis
- Artificial intelligence
- Machine learning
- Automation

Python is popular because its syntax is simple and readable.

💡 **Remember:** Python = Simple syntax + powerful libraries.
"""

    if "data structure" in topic_lower:

        return """
### 📚 Data Structures

A data structure is a way of organizing and storing data so
that it can be accessed and modified efficiently.

Common data structures include:

- Arrays
- Linked Lists
- Stacks
- Queues
- Trees
- Graphs

Different data structures are suitable for different problems.

💡 **Remember:** Choose a data structure based on the operations
your problem requires.
"""

    return f"""
### 📚 {topic}

This question belongs to the **{topic}** topic.

The main idea is to understand the fundamental concepts,
definitions, operations and applications related to this topic.

Review your learning material for this topic and focus on the
concept tested by the question.
"""


# =========================================================
# PERFORMANCE
# =========================================================

def calculate_performance(percentage):

    if percentage >= 90:
        return "Excellent 🌟"

    elif percentage >= 75:
        return "Very Good 👍"

    elif percentage >= 60:
        return "Good 🙂"

    elif percentage >= 40:
        return "Needs Improvement 📚"

    return "Needs More Practice 💪"


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def save_material_to_db(material_name, material_text):

    if supabase is None:
        return None

    try:

        data = {
            "user_id": st.session_state.user_id,
            "material_name": material_name,
            "content": material_text
        }

        result = supabase.table("learning_materials").insert(
            data
        ).execute()

        if result.data:
            return result.data[0].get("id")

    except Exception as e:

        st.warning(
            f"Material could not be saved to database: {e}"
        )

    return None


def save_quiz_to_db(questions):

    if supabase is None:
        return None

    try:

        quiz_data = {
            "user_id": st.session_state.user_id,
            "question_count": len(questions)
        }

        result = supabase.table("quizzes").insert(
            quiz_data
        ).execute()

        if result.data:
            return result.data[0].get("id")

    except Exception as e:

        st.warning(
            f"Quiz could not be saved to database: {e}"
        )

    return None


def save_attempt_to_db(
    quiz_id,
    score,
    total_questions,
    percentage
):

    if supabase is None:
        return

    try:

        data = {
            "user_id": st.session_state.user_id,
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage
        }

        supabase.table("quiz_attempts").insert(
            data
        ).execute()

    except Exception as e:

        st.warning(
            f"Attempt could not be saved to database: {e}"
        )


def load_quiz_history():

    if supabase is None:
        return []

    try:

        result = (
            supabase
            .table("quiz_attempts")
            .select("*")
            .eq(
                "user_id",
                st.session_state.user_id
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        return result.data or []

    except Exception:
        return []


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎓 AIStat Learn")

st.sidebar.caption(
    "AI-Powered Personalized Learning Platform"
)

st.sidebar.divider()

st.sidebar.subheader("📌 Learning Progress")

step_names = [
    "1️⃣ Learning Material",
    "2️⃣ Generate Questions",
    "3️⃣ Take Assessment",
    "4️⃣ Progress",
    "5️⃣ Learning Plan"
]

current_step = st.session_state.current_step

for i, step_name in enumerate(step_names, start=1):

    if i < current_step:
        st.sidebar.success(step_name)

    elif i == current_step:
        st.sidebar.info(step_name)

    else:
        st.sidebar.write(step_name)

st.sidebar.divider()

st.sidebar.subheader("Navigation")

navigation_pages = [
    "🏠 Home",
    "📚 Learning Material",
    "📝 Generate Questions",
    "✍️ Take Assessment",
    "📊 Progress",
    "📅 Learning Plan",
    "🔧 System Check"
]

if current_step == 1:
    default_page = "📚 Learning Material"

elif current_step == 2:
    default_page = "📝 Generate Questions"

elif current_step == 3:
    default_page = "✍️ Take Assessment"

elif current_step == 4:
    default_page = "📊 Progress"

elif current_step == 5:
    default_page = "📅 Learning Plan"

else:
    default_page = "🏠 Home"

sidebar_page = st.sidebar.radio(
    "Go to",
    navigation_pages,
    index=navigation_pages.index(default_page)
)

st.sidebar.divider()

if db_status == "Connected":
    st.sidebar.success("🗄️ Database Connected")
else:
    st.sidebar.warning(
        f"🗄️ Database: {db_status}"
    )


# =========================================================
# HOME
# =========================================================

if sidebar_page == "🏠 Home":

    st.markdown(
        '<div class="main-title">🎓 AIStat Learn</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'AI-Powered Personalized Learning Platform'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.write(
        """
        Welcome to **AIStat Learn**! 🚀

        This platform helps students:

        📚 Upload or enter learning material

        🤖 Generate AI-powered practice questions

        📝 Take assessments

        💡 Understand why answers are correct or incorrect

        📊 Track learning progress

        📅 Get personalized learning recommendations
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Questions Generated",
            len(st.session_state.questions)
        )

    with col2:
        st.metric(
            "Latest Score",
            f"{st.session_state.percentage:.1f}%"
        )

    with col3:
        st.metric(
            "Current Step",
            f"{st.session_state.current_step}/5"
        )

    st.divider()

    if st.button(
        "🚀 Start Learning",
        use_container_width=True
    ):
        go_to_step(1)


# =========================================================
# STEP 1 — LEARNING MATERIAL
# =========================================================

elif sidebar_page == "📚 Learning Material":

    st.title("📚 Step 1 — Learning Material")

    st.write(
        "Upload a PDF or enter your learning material manually."
    )

    # -----------------------------------------------------
    # PDF UPLOAD
    # -----------------------------------------------------

    st.subheader("📤 Upload Learning Material")

    uploaded_file = st.file_uploader(
        "Upload your learning material as a PDF",
        type=["pdf"],
        help="Upload a text-based PDF for automatic text extraction."
    )

    if uploaded_file is not None:

        if PdfReader is None:

            st.error(
                "❌ PyPDF2 is not installed."
            )

            st.code(
                "pip install PyPDF2",
                language="bash"
            )

        else:

            if (
                st.session_state.last_uploaded_file
                != uploaded_file.name
            ):

                try:

                    reader = PdfReader(uploaded_file)

                    extracted_text = ""

                    for page in reader.pages:

                        page_text = page.extract_text()

                        if page_text:
                            extracted_text += (
                                page_text + "\n"
                            )

                    if extracted_text.strip():

                        st.session_state.material_text = (
                            extracted_text.strip()
                        )

                        st.session_state.material_name = (
                            uploaded_file.name.rsplit(
                                ".",
                                1
                            )[0]
                        )

                        st.session_state.pdf_loaded = True

                        st.session_state.last_uploaded_file = (
                            uploaded_file.name
                        )

                        st.success(
                            f"✅ PDF loaded successfully: "
                            f"{uploaded_file.name}"
                        )

                    else:

                        st.error(
                            "❌ Could not extract text from this PDF."
                        )

                        st.info(
                            "This may be a scanned/image-only PDF. "
                            "Try a text-based PDF or paste the text manually."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Error reading PDF: {e}"
                    )

    # -----------------------------------------------------
    # MANUAL INPUT
    # -----------------------------------------------------

    st.divider()

    st.subheader("✍️ Enter / Edit Learning Material")

    material_name = st.text_input(
        "Material Name",
        value=st.session_state.material_name,
        placeholder="Example: Python Basics"
    )

    material_text = st.text_area(
        "Learning Material",
        value=st.session_state.material_text,
        height=350,
        placeholder=(
            "Paste your learning material here..."
        )
    )

    # -----------------------------------------------------
    # SAVE MATERIAL
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Material",
            use_container_width=True
        ):

            if not material_text.strip():

                st.error(
                    "Please upload a PDF or enter learning material."
                )

            elif len(material_text.split()) < 5:

                st.error(
                    "Please provide more learning material "
                    "so questions can be generated."
                )

            else:

                st.session_state.material_text = (
                    material_text.strip()
                )

                st.session_state.material_name = (
                    material_name.strip()
                    if material_name.strip()
                    else "Learning Material"
                )

                st.session_state.material_saved = True

                material_id = save_material_to_db(
                    st.session_state.material_name,
                    st.session_state.material_text
                )

                st.success(
                    "✅ Learning material saved successfully!"
                )

                if material_id:
                    st.caption(
                        f"Material ID: {material_id}"
                    )

    with col2:

        if st.button(
            "➡️ NEXT: Generate Questions",
            use_container_width=True
        ):

            if not material_text.strip():

                st.error(
                    "Please upload a PDF or enter learning material first."
                )

            elif len(material_text.split()) < 5:

                st.error(
                    "Please provide more learning material."
                )

            else:

                st.session_state.material_text = (
                    material_text.strip()
                )

                st.session_state.material_name = (
                    material_name.strip()
                    if material_name.strip()
                    else "Learning Material"
                )

                go_to_step(2)


# =========================================================
# STEP 2 — GENERATE QUESTIONS
# =========================================================

elif sidebar_page == "📝 Generate Questions":

    st.title("📝 Step 2 — Generate Questions")

    if not st.session_state.material_text:

        st.warning(
            "⚠️ Please upload or enter learning material first."
        )

        if st.button("📚 Go to Learning Material"):
            go_to_step(1)

    else:

        st.success(
            f"📚 Material: "
            f"{st.session_state.material_name}"
        )

        word_count = len(
            st.session_state.material_text.split()
        )

        st.caption(
            f"Material contains approximately "
            f"{word_count} words."
        )

        st.divider()

        question_count = st.slider(
            "How many questions do you want?",
            min_value=1,
            max_value=20,
            value=5
        )

        if st.button(
            "🤖 Generate Questions",
            use_container_width=True
        ):

            with st.spinner(
                "Generating questions..."
            ):

                try:

                    questions = generate_mcqs(
                        st.session_state.material_text,
                        question_count
                    )

                    if questions:

                        st.session_state.questions = questions

                        st.session_state.total_questions = (
                            len(questions)
                        )

                        st.session_state.assessment_answers = {}

                        st.session_state.quiz_submitted = False

                        quiz_id = save_quiz_to_db(
                            questions
                        )

                        st.session_state.quiz_id = quiz_id

                        st.success(
                            f"✅ {len(questions)} questions generated!"
                        )

                    else:

                        st.error(
                            "❌ No questions could be generated. "
                            "Please provide more detailed learning material."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Error generating questions: {e}"
                    )

        # -------------------------------------------------
        # QUESTION PREVIEW
        # -------------------------------------------------

        if st.session_state.questions:

            st.divider()

            st.subheader("👀 Question Preview")

            for i, question in enumerate(
                st.session_state.questions,
                start=1
            ):

                st.markdown(
                    f"### Question {i}"
                )

                st.write(
                    get_question_text(question)
                )

                options = get_options(question)

                for j, option in enumerate(
                    options
                ):

                    st.write(
                        f"{chr(65+j)}. {option}"
                    )

                st.divider()

            if st.button(
                "➡️ NEXT: Take Assessment",
                use_container_width=True
            ):

                go_to_step(3)


# =========================================================
# STEP 3 — TAKE ASSESSMENT
# =========================================================

elif sidebar_page == "✍️ Take Assessment":

    st.title("✍️ Step 3 — Take Assessment")

    if not st.session_state.questions:

        st.warning(
            "⚠️ Please generate questions first."
        )

        if st.button("📝 Go to Generate Questions"):
            go_to_step(2)

    else:

        if not st.session_state.quiz_submitted:

            st.info(
                f"Answer all "
                f"{len(st.session_state.questions)} questions."
            )

            st.divider()

            for i, question in enumerate(
                st.session_state.questions
            ):

                q_text = get_question_text(question)

                options = get_options(question)

                st.markdown(
                    f"### Q{i+1}. {q_text}"
                )

                if not options:

                    st.warning(
                        "No options found for this question."
                    )

                    continue

                answer = st.radio(
                    "Select your answer:",
                    options,
                    key=f"question_{i}",
                    index=None
                )

                st.session_state.assessment_answers[
                    i
                ] = answer

                st.divider()

            if st.button(
                "✅ Submit Assessment",
                use_container_width=True
            ):

                unanswered = []

                for i in range(
                    len(st.session_state.questions)
                ):

                    answer = st.session_state.assessment_answers.get(
                        i
                    )

                    if not answer:
                        unanswered.append(i + 1)

                if unanswered:

                    st.error(
                        "Please answer all questions before submitting."
                    )

                    st.write(
                        "Unanswered questions:",
                        ", ".join(
                            map(str, unanswered)
                        )
                    )

                else:

                    score = 0

                    for i, question in enumerate(
                        st.session_state.questions
                    ):

                        user_answer = (
                            st.session_state.assessment_answers.get(
                                i,
                                ""
                            )
                        )

                        correct_answer = (
                            find_correct_option(question)
                        )

                        if (
                            user_answer.strip().lower()
                            ==
                            correct_answer.strip().lower()
                        ):

                            score += 1

                    total = len(
                        st.session_state.questions
                    )

                    percentage = (
                        score / total * 100
                        if total > 0
                        else 0
                    )

                    st.session_state.score = score

                    st.session_state.total_questions = total

                    st.session_state.percentage = percentage

                    st.session_state.quiz_submitted = True

                    save_attempt_to_db(
                        st.session_state.quiz_id,
                        score,
                        total,
                        percentage
                    )

                    st.rerun()

        # =================================================
        # RESULTS + EXPLANATIONS
        # =================================================

        else:

            st.success(
                "🎉 Assessment Submitted Successfully!"
            )

            score = st.session_state.score

            total = st.session_state.total_questions

            percentage = st.session_state.percentage

            performance = calculate_performance(
                percentage
            )

            st.divider()

            st.subheader("📊 Your Result")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Score",
                    f"{score}/{total}"
                )

            with col2:
                st.metric(
                    "Percentage",
                    f"{percentage:.1f}%"
                )

            with col3:

                correct = score

                incorrect = total - score

                st.metric(
                    "Correct",
                    correct
                )

            with col4:

                st.metric(
                    "Incorrect",
                    incorrect
                )

            st.info(
                f"Performance: **{performance}**"
            )

            st.divider()

            # =============================================
            # DETAILED QUESTION REVIEW
            # =============================================

            st.subheader(
                "💡 Detailed Question Explanations"
            )

            topic_results = {}

            for i, question in enumerate(
                st.session_state.questions
            ):

                q_text = get_question_text(
                    question
                )

                topic = get_question_topic(
                    question
                )

                concept = get_question_concept(
                    question
                )

                options = get_options(
                    question
                )

                correct_answer = find_correct_option(
                    question
                )

                user_answer = (
                    st.session_state.assessment_answers.get(
                        i,
                        "Not answered"
                    )
                )

                is_correct = (
                    user_answer.strip().lower()
                    ==
                    correct_answer.strip().lower()
                )

                # Topic result
                if topic not in topic_results:
                    topic_results[topic] = {
                        "correct": 0,
                        "total": 0
                    }

                topic_results[topic]["total"] += 1

                if is_correct:
                    topic_results[topic]["correct"] += 1

                # Question header
                if is_correct:

                    st.success(
                        f"### Q{i+1}. ✅ Correct"
                    )

                else:

                    st.error(
                        f"### Q{i+1}. ❌ Incorrect"
                    )

                st.write(
                    f"**Question:** {q_text}"
                )

                st.write(
                    f"**Topic:** {topic}"
                )

                st.write(
                    f"**Concept:** {concept}"
                )

                st.write(
                    f"**Your Answer:** "
                    f"{user_answer}"
                )

                st.write(
                    f"**Correct Answer:** "
                    f"{correct_answer}"
                )

                # -----------------------------------------
                # WHY CORRECT?
                # -----------------------------------------

                st.markdown(
                    "#### ✅ Why is this answer correct?"
                )

                explanation = get_general_explanation(
                    question
                )

                if explanation:

                    st.info(
                        explanation
                    )

                else:

                    st.info(
                        f"**{correct_answer}** is correct "
                        f"because it matches the fundamental "
                        f"concept being tested in **{topic}**."
                    )

                # -----------------------------------------
                # WHY OTHER OPTIONS ARE WRONG?
                # -----------------------------------------

                st.markdown(
                    "#### ❌ Why are the other options incorrect?"
                )

                for option in options:

                    if (
                        option.strip().lower()
                        ==
                        correct_answer.strip().lower()
                    ):
                        continue

                    option_feedback = get_option_feedback(
                        question,
                        option
                    )

                    if option_feedback:

                        st.write(
                            f"❌ **{option}** — "
                            f"{option_feedback}"
                        )

                    else:

                        feedback = explain_incorrect_option(
                            question,
                            option
                        )

                        st.write(
                            f"❌ **{option}** — "
                            f"{feedback}"
                        )

                # -----------------------------------------
                # TOPIC EXPLANATION
                # -----------------------------------------

                if st.session_state.show_topic_explanations:

                    with st.expander(
                        f"📚 Learn More About: {topic}"
                    ):

                        st.markdown(
                            create_topic_explanation(
                                topic
                            )
                        )

                st.divider()

            # =============================================
            # WEAK TOPICS
            # =============================================

            st.subheader(
                "📌 Topic-wise Performance"
            )

            topic_rows = []

            for topic, result in topic_results.items():

                topic_total = result["total"]

                topic_correct = result["correct"]

                topic_percentage = (
                    topic_correct
                    / topic_total
                    * 100
                    if topic_total
                    else 0
                )

                topic_rows.append(
                    {
                        "Topic": topic,
                        "Correct": topic_correct,
                        "Total": topic_total,
                        "Performance":
                            f"{topic_percentage:.1f}%"
                    }
                )

            if topic_rows:

                df = pd.DataFrame(
                    topic_rows
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            # =============================================
            # RECOMMENDATIONS
            # =============================================

            st.subheader(
                "🤖 Personalized Recommendation"
            )

            weak_topics = []

            for topic, result in topic_results.items():

                topic_percentage = (
                    result["correct"]
                    / result["total"]
                    * 100
                    if result["total"]
                    else 0
                )

                if topic_percentage < 60:

                    weak_topics.append(
                        topic
                    )

            if weak_topics:

                st.warning(
                    "You need more practice in: "
                    + ", ".join(weak_topics)
                )

                for topic in weak_topics:

                    st.write(
                        f"📚 Revise **{topic}** and "
                        f"practice more questions on this topic."
                    )

            else:

                st.success(
                    "🌟 Great job! You are performing well "
                    "across the tested topics."
                )

            st.divider()

            # =============================================
            # NEXT ACTIONS
            # =============================================

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "🔄 Retake Assessment",
                    use_container_width=True
                ):

                    st.session_state.assessment_answers = {}

                    st.session_state.quiz_submitted = False

                    go_to_step(3)

            with col2:

                if st.button(
                    "➡️ Go to Progress",
                    use_container_width=True
                ):

                    st.session_state.quiz_history = (
                        load_quiz_history()
                    )

                    go_to_step(4)


# =========================================================
# STEP 4 — PROGRESS
# =========================================================

elif sidebar_page == "📊 Progress":

    st.title("📊 Step 4 — Progress")

    st.subheader(
        "📈 Your Learning Progress"
    )

    if st.session_state.total_questions > 0:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Latest Score",
                f"{st.session_state.score}/"
                f"{st.session_state.total_questions}"
            )

        with col2:
            st.metric(
                "Percentage",
                f"{st.session_state.percentage:.1f}%"
            )

        with col3:
            st.metric(
                "Performance",
                calculate_performance(
                    st.session_state.percentage
                )
            )

    else:

        st.info(
            "Take an assessment to see your progress."
        )

    st.divider()

    # Load history
    history = load_quiz_history()

    if history:

        st.subheader(
            "📚 Assessment History"
        )

        rows = []

        for item in history:

            rows.append(
                {
                    "Score":
                        item.get("score", "-"),

                    "Total":
                        item.get(
                            "total_questions",
                            item.get(
                                "total",
                                "-"
                            )
                        ),

                    "Percentage":
                        item.get(
                            "percentage",
                            "-"
                        ),

                    "Date":
                        item.get(
                            "created_at",
                            "-"
                        )
                }
            )

        if rows:

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "No previous assessment attempts found."
        )

    st.divider()

    if st.button(
        "➡️ Go to Learning Plan",
        use_container_width=True
    ):

        go_to_step(5)


# =========================================================
# STEP 5 — LEARNING PLAN
# =========================================================

elif sidebar_page == "📅 Learning Plan":

    st.title("📅 Step 5 — Personalized Learning Plan")

    st.write(
        "Your learning plan is based on your assessment performance."
    )

    percentage = st.session_state.percentage

    if percentage >= 80:

        st.success(
            """
            🌟 **Strong Performance**

            Recommended plan:

            1. Review the concepts briefly.
            2. Solve advanced questions.
            3. Start the next topic.
            4. Take another assessment to confirm mastery.
            """
        )

    elif percentage >= 60:

        st.info(
            """
            👍 **Good Progress**

            Recommended plan:

            1. Review concepts where you made mistakes.
            2. Practice medium-level questions.
            3. Revise important definitions and examples.
            4. Retake the assessment.
            """
        )

    else:

        st.warning(
            """
            📚 **More Practice Recommended**

            Recommended plan:

            1. Re-read the learning material.
            2. Focus on weak concepts.
            3. Practice basic questions.
            4. Review explanations after every question.
            5. Retake the assessment.
            """
        )

    st.divider()

    if st.session_state.questions:

        st.subheader(
            "📌 Topics from Your Assessment"
        )

        topics = []

        for question in st.session_state.questions:

            topic = get_question_topic(
                question
            )

            if topic not in topics:
                topics.append(topic)

        for topic in topics:

            st.write(
                f"📖 **{topic}**"
            )

    st.divider()

    if st.button(
        "📚 Go to Learning Material",
        use_container_width=True
    ):

        go_to_step(1)


# =========================================================
# SYSTEM CHECK
# =========================================================

elif sidebar_page == "🔧 System Check":

    st.title("🔧 System Check")

    st.subheader(
        "Application Components"
    )

    # Streamlit
    st.success(
        "✅ Streamlit is running"
    )

    # MCQ generator
    try:

        test_questions = generate_mcqs(
            "Python is a programming language. "
            "Python supports variables, loops, functions and lists.",
            2
        )

        if test_questions:

            st.success(
                "✅ MCQ Generator is working"
            )

            st.write(
                f"Generated {len(test_questions)} test questions."
            )

        else:

            st.error(
                "❌ MCQ Generator returned no questions"
            )

    except Exception as e:

        st.error(
            f"❌ MCQ Generator error: {e}"
        )

    # PDF
    if PdfReader is not None:

        st.success(
            "✅ PyPDF2 is installed"
        )

    else:

        st.error(
            "❌ PyPDF2 is not installed"
        )

        st.code(
            "pip install PyPDF2",
            language="bash"
        )

    # Supabase
    if supabase is not None:

        st.success(
            "✅ Supabase connection initialized"
        )

    else:

        st.warning(
            "⚠️ Supabase is not connected"
        )

    st.divider()

    st.subheader(
        "📁 Project Information"
    )

    st.write(
        f"**User ID:** {st.session_state.user_id}"
    )

    st.write(
        f"**Material:** "
        f"{st.session_state.material_name or 'None'}"
    )

    st.write(
        f"**Questions:** "
        f"{len(st.session_state.questions)}"
    )

    st.write(
        f"**Current Step:** "
        f"{st.session_state.current_step}"
    )

    st.write(
        f"**Database:** "
        f"{db_status}"
    )

    st.write(
        f"**PDF Support:** "
        f"{'Available' if PdfReader else 'Not Available'}"
    )
