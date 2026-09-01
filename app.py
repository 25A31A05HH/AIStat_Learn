import uuid
import re
import streamlit as st
import pandas as pd

from mcq_generator import generate_mcqs

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AIStat Learn",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.step-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.day-card {
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #ddd;
    margin-bottom: 20px;
}

.concept-box {
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin: 6px 0;
}

.success-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ccc;
}

.small-text {
    color: #666;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

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
    "material_saved": False,
    "last_uploaded_file": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SUPABASE CONNECTION
# ============================================================

supabase = None

try:
    from supabase import create_client

    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

except Exception as e:
    supabase = None


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def save_material_to_db(text, name):
    """Save uploaded learning material."""

    if supabase is None:
        return False

    try:
        data = {
            "user_id": st.session_state.user_id,
            "material_name": name,
            "content": text
        }

        supabase.table("learning_materials").insert(data).execute()
        return True

    except Exception as e:
        st.warning(f"Could not save material to database: {e}")
        return False


def save_quiz_to_db(questions):
    """Save generated quiz."""

    if supabase is None:
        return None

    try:
        quiz_id = str(uuid.uuid4())

        data = {
            "id": quiz_id,
            "user_id": st.session_state.user_id,
            "material_name": st.session_state.material_name,
            "questions": questions
        }

        supabase.table("quizzes").insert(data).execute()

        return quiz_id

    except Exception as e:
        st.warning(f"Database could not save the quiz: {e}")
        return None


def save_attempt_to_db(score, total):
    """Save assessment attempt."""

    if supabase is None:
        return False

    try:
        percentage = (score / total * 100) if total else 0

        data = {
            "user_id": st.session_state.user_id,
            "quiz_id": st.session_state.quiz_id,
            "score": score,
            "total_questions": total,
            "percentage": percentage
        }

        supabase.table("attempts").insert(data).execute()

        return True

    except Exception as e:
        st.warning(f"Could not save assessment: {e}")
        return False


def load_quiz_history():
    """Load previous attempts."""

    if supabase is None:
        return []

    try:
        response = (
            supabase
            .table("attempts")
            .select("*")
            .eq("user_id", st.session_state.user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception:
        return []


# ============================================================
# QUESTION HELPERS
# ============================================================

def get_question_text(question):
    """Get question text from different possible key names."""

    if not isinstance(question, dict):
        return str(question)

    for key in ["question", "question_text", "text"]:
        if key in question:
            return str(question[key])

    return ""


def get_options(question):
    """Get options from a question."""

    if not isinstance(question, dict):
        return []

    options = (
        question.get("options")
        or question.get("choices")
        or question.get("answers")
        or []
    )

    if isinstance(options, dict):
        result = []

        for key in ["A", "B", "C", "D"]:
            if key in options:
                result.append(options[key])

        if result:
            return result

        return list(options.values())

    return list(options)


def get_correct_option(question):
    """Get correct answer."""

    if not isinstance(question, dict):
        return None

    correct = (
        question.get("correct_answer")
        or question.get("correct_option")
        or question.get("answer")
        or question.get("correct")
    )

    options = get_options(question)

    if correct is None:
        return None

    correct = str(correct).strip()

    # A / B / C / D
    if len(correct) == 1 and correct.upper() in "ABCD":
        index = ord(correct.upper()) - 65

        if index < len(options):
            return options[index]

    # "A. answer"
    match = re.match(r"^([A-D])[\.\)]\s*", correct, re.IGNORECASE)

    if match:
        index = ord(match.group(1).upper()) - 65

        if index < len(options):
            return options[index]

    # Exact answer text
    for option in options:
        if str(option).strip().lower() == correct.lower():
            return option

    return correct


def get_topic(question):
    """Get topic from question."""

    if not isinstance(question, dict):
        return "General"

    topic = (
        question.get("topic")
        or question.get("subject")
        or question.get("category")
    )

    if topic:
        return str(topic).strip()

    return "General"


def get_concept(question):
    """Get concept from question."""

    if not isinstance(question, dict):
        return None

    concept = (
        question.get("concept")
        or question.get("subtopic")
        or question.get("skill")
    )

    if concept:
        return str(concept).strip()

    return None


# ============================================================
# CONCEPT EXTRACTION
# ============================================================

def extract_concepts_from_questions(questions):
    """
    Extract unique concepts from generated MCQs.
    Prefer concept field, otherwise use topic.
    """

    concepts = []

    for question in questions:

        concept = get_concept(question)

        if not concept:
            concept = get_topic(question)

        if concept:
            concept = concept.strip()

            if concept and concept.lower() not in [
                x.lower() for x in concepts
            ]:
                concepts.append(concept)

    return concepts


def extract_concepts_from_material(text):
    """
    Try to identify useful concepts directly from learning material.
    This provides additional concepts when MCQs have limited topic data.
    """

    if not text:
        return []

    concepts = []

    # Common programming/data science concepts
    known_concepts = [
        "Python",
        "Variables",
        "Data Types",
        "Operators",
        "Conditional Statements",
        "Loops",
        "Functions",
        "Lists",
        "Tuples",
        "Sets",
        "Dictionaries",
        "Strings",
        "Arrays",
        "Linked Lists",
        "Stacks",
        "Queues",
        "Trees",
        "Graphs",
        "Sorting",
        "Searching",
        "Recursion",
        "Object Oriented Programming",
        "Classes",
        "Objects",
        "Inheritance",
        "Polymorphism",
        "Encapsulation",
        "Abstraction",
        "SQL",
        "Databases",
        "Machine Learning",
        "Artificial Intelligence",
        "Data Science",
        "Statistics",
        "Probability",
        "Regression",
        "Classification",
        "Clustering",
        "Data Visualization",
        "Cloud Computing",
        "Networking",
        "Cyber Security",
        "Algorithms",
        "Data Structures",
    ]

    text_lower = text.lower()

    for concept in known_concepts:

        if concept.lower() in text_lower:

            if concept.lower() not in [
                x.lower() for x in concepts
            ]:
                concepts.append(concept)

    return concepts


def build_five_day_plan(questions, material_text):
    """
    Create a 5-day plan with different concepts on each day.
    """

    question_concepts = extract_concepts_from_questions(questions)

    material_concepts = extract_concepts_from_material(material_text)

    all_concepts = []

    # First use concepts from questions
    for concept in question_concepts:

        if concept.lower() not in [
            x.lower() for x in all_concepts
        ]:
            all_concepts.append(concept)

    # Then add concepts found in material
    for concept in material_concepts:

        if concept.lower() not in [
            x.lower() for x in all_concepts
        ]:
            all_concepts.append(concept)

    # If no concepts were found
    if not all_concepts:

        all_concepts = [
            "Introduction and Fundamentals",
            "Core Concepts",
            "Important Definitions",
            "Applications",
            "Revision and Practice"
        ]

    # --------------------------------------------------------
    # Find weak topics
    # --------------------------------------------------------

    weak_topics = []

    if st.session_state.quiz_submitted:

        topic_total = {}
        topic_correct = {}

        for i, question in enumerate(questions):

            topic = get_topic(question)

            topic_total[topic] = topic_total.get(topic, 0) + 1

            correct_answer = get_correct_option(question)
            user_answer = st.session_state.assessment_answers.get(i)

            if (
                user_answer is not None
                and correct_answer is not None
                and str(user_answer).strip().lower()
                == str(correct_answer).strip().lower()
            ):
                topic_correct[topic] = topic_correct.get(topic, 0) + 1

        topic_scores = []

        for topic, total in topic_total.items():

            correct = topic_correct.get(topic, 0)

            percentage = (correct / total) * 100 if total else 0

            topic_scores.append(
                (topic, percentage)
            )

        topic_scores.sort(key=lambda x: x[1])

        weak_topics = [
            topic
            for topic, percentage in topic_scores
            if percentage < 70
        ]

    # --------------------------------------------------------
    # Put weak topics first
    # --------------------------------------------------------

    ordered_concepts = []

    for topic in weak_topics:

        for concept in all_concepts:

            if (
                topic.lower() in concept.lower()
                or concept.lower() in topic.lower()
            ):
                if concept not in ordered_concepts:
                    ordered_concepts.append(concept)

    for concept in all_concepts:

        if concept not in ordered_concepts:
            ordered_concepts.append(concept)

    # --------------------------------------------------------
    # Create exactly 5 days
    # --------------------------------------------------------

    days = [
        {
            "day": "Day 1",
            "title": "Foundation",
            "goal": "Build a strong understanding of the basics.",
            "concepts": []
        },
        {
            "day": "Day 2",
            "title": "Core Concepts",
            "goal": "Learn the main concepts and how they work.",
            "concepts": []
        },
        {
            "day": "Day 3",
            "title": "Application",
            "goal": "Understand how the concepts are used in practice.",
            "concepts": []
        },
        {
            "day": "Day 4",
            "title": "Problem Solving",
            "goal": "Practice questions and strengthen weak areas.",
            "concepts": []
        },
        {
            "day": "Day 5",
            "title": "Revision & Assessment",
            "goal": "Revise everything and test your understanding.",
            "concepts": []
        }
    ]

    # --------------------------------------------------------
    # Distribute concepts without repeating them
    # --------------------------------------------------------

    for index, concept in enumerate(ordered_concepts):

        day_index = index % 5

        days[day_index]["concepts"].append(concept)

    return days


# ============================================================
# EXPLANATIONS
# ============================================================

def explain_concept(concept):
    """Return simple explanation for common concepts."""

    explanations = {

        "Queue":
            "A Queue follows FIFO (First In, First Out). "
            "The element inserted first is removed first.",

        "Stack":
            "A Stack follows LIFO (Last In, First Out). "
            "The last element inserted is removed first.",

        "Array":
            "An Array stores elements in an indexed sequence. "
            "It provides fast access using an index.",

        "Linked List":
            "A Linked List consists of nodes connected using links or pointers.",

        "Python":
            "Python is a high-level programming language used for "
            "software development, automation, data science and AI.",

        "Functions":
            "Functions are reusable blocks of code designed to perform "
            "a specific task.",

        "Variables":
            "Variables are names used to store values in a program.",

        "Data Types":
            "Data types define what kind of value a variable can store.",

        "Loops":
            "Loops allow a block of code to execute repeatedly.",

        "Conditional Statements":
            "Conditional statements execute different code depending "
            "on whether a condition is true or false.",

        "Lists":
            "Lists are ordered and changeable collections in Python.",

        "Tuples":
            "Tuples are ordered collections that cannot normally be changed "
            "after creation.",

        "Dictionaries":
            "Dictionaries store data using key-value pairs.",

        "Object Oriented Programming":
            "Object-oriented programming organizes software using classes "
            "and objects.",

        "Machine Learning":
            "Machine learning enables computers to learn patterns from data "
            "and make predictions or decisions.",

        "Artificial Intelligence":
            "Artificial Intelligence focuses on creating systems capable "
            "of performing tasks that normally require human intelligence.",

        "Data Structures":
            "Data structures organize and store data efficiently so that "
            "operations can be performed effectively.",

        "Algorithms":
            "Algorithms are step-by-step procedures used to solve problems.",

    }

    # Exact match
    if concept in explanations:
        return explanations[concept]

    # Partial match
    for key, explanation in explanations.items():

        if key.lower() in concept.lower():
            return explanation

    return (
        f"Study the definition, working principle, important properties, "
        f"examples and practical applications of {concept}."
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 AIStat Learn")

st.sidebar.markdown("---")

navigation = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📚 Learning Material",
        "📝 Generate Questions",
        "✍️ Take Assessment",
        "📊 Progress",
        "📅 Learning Plan",
        "🔧 System Check"
    ]
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎓 AIStat Learn</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-Powered Personalized Learning Platform</div>',
    unsafe_allow_html=True
)


# ============================================================
# HOME
# ============================================================

if navigation == "🏠 Home":

    st.header("Welcome to AIStat Learn 👋")

    st.write(
        "AIStat Learn helps students learn from their own study material "
        "using AI-generated questions, assessments, progress tracking "
        "and personalized learning plans."
    )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Questions", len(st.session_state.questions))

    with col2:
        if st.session_state.quiz_submitted:
            st.metric(
                "Score",
                f"{st.session_state.score}/{st.session_state.total_questions}"
            )
        else:
            st.metric("Score", "Not attempted")

    with col3:
        if st.session_state.quiz_submitted:
            st.metric(
                "Percentage",
                f"{st.session_state.percentage:.1f}%"
            )
        else:
            st.metric("Percentage", "0%")

    with col4:
        st.metric(
            "Learning Days",
            "5"
        )

    st.markdown("---")

    st.subheader("How AIStat Learn Works")

    steps = [
        ("1️⃣", "Upload Material",
         "Upload your PDF learning material."),

        ("2️⃣", "Generate Questions",
         "Generate MCQs from your study material."),

        ("3️⃣", "Take Assessment",
         "Answer the generated questions."),

        ("4️⃣", "Analyze Progress",
         "Identify your strengths and weak topics."),

        ("5️⃣", "Follow Learning Plan",
         "Get a personalized 5-day learning plan.")
    ]

    for icon, title, description in steps:

        st.markdown(
            f"""
            <div class="step-card">
                <h3>{icon} {title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# LEARNING MATERIAL
# ============================================================

elif navigation == "📚 Learning Material":

    st.header("📚 Learning Material")

    st.write(
        "Upload your study material as a PDF."
    )

    uploaded_file = st.file_uploader(
        "Choose your learning material",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.session_state.last_uploaded_file != uploaded_file.name:

            st.session_state.last_uploaded_file = uploaded_file.name

            try:

                from PyPDF2 import PdfReader

                reader = PdfReader(uploaded_file)

                extracted_text = ""

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        extracted_text += page_text + "\n"

                if extracted_text.strip():

                    st.session_state.material_text = extracted_text
                    st.session_state.material_name = uploaded_file.name

                    st.success(
                        "✅ Learning material extracted successfully!"
                    )

                    st.info(
                        f"📄 File: {uploaded_file.name}\n\n"
                        f"📝 Characters extracted: {len(extracted_text)}"
                    )

                    if not st.session_state.material_saved:

                        saved = save_material_to_db(
                            extracted_text,
                            uploaded_file.name
                        )

                        if saved:
                            st.session_state.material_saved = True

                else:

                    st.warning(
                        "⚠️ No text could be extracted from this PDF. "
                        "It may be a scanned PDF."
                    )

                    st.text_area(
                        "Paste your learning material here:",
                        key="manual_material",
                        height=250
                    )

            except ImportError:

                st.error(
                    "PyPDF2 is not installed. Run:\n\n"
                    "pip install PyPDF2"
                )

            except Exception as e:

                st.error(
                    f"Error reading file: {e}"
                )

    # Show current material

    if st.session_state.material_text:

        st.markdown("---")

        st.subheader("📖 Current Learning Material")

        st.info(
            f"Material: {st.session_state.material_name}"
        )

        with st.expander("View extracted text"):

            st.text(
                st.session_state.material_text[:10000]
            )

        if st.button("🗑️ Clear Material"):

            st.session_state.material_text = ""
            st.session_state.material_name = ""
            st.session_state.questions = []
            st.session_state.material_saved = False
            st.session_state.last_uploaded_file = None

            st.rerun()


# ============================================================
# GENERATE QUESTIONS
# ============================================================

elif navigation == "📝 Generate Questions":

    st.header("📝 Generate Questions")

    if not st.session_state.material_text:

        st.warning(
            "⚠️ Please upload learning material first."
        )

        st.info(
            "Go to 📚 Learning Material from the sidebar."
        )

    else:

        st.success(
            f"📖 Material loaded: "
            f"{st.session_state.material_name}"
        )

        st.markdown("---")

        question_count = st.number_input(
            "🔢 Number of Questions",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )

        if st.button(
            "🤖 Generate Questions",
            type="primary"
        ):

            with st.spinner(
                "AI is generating questions..."
            ):

                try:

                    questions = generate_mcqs(
                        st.session_state.material_text,
                        int(question_count)
                    )

                    st.session_state.questions = questions

                    st.session_state.quiz_id = save_quiz_to_db(
                        questions
                    )

                    st.session_state.assessment_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.score = 0
                    st.session_state.total_questions = len(questions)
                    st.session_state.percentage = 0

                except Exception as e:

                    st.error(
                        f"❌ Error generating questions: {e}"
                    )

        if st.session_state.questions:

            generated_count = len(
                st.session_state.questions
            )

            st.success(
                f"✅ {generated_count} questions generated!"
            )

            if generated_count < int(question_count):

                st.warning(
                    f"Requested {int(question_count)}, "
                    f"but only {generated_count} questions were generated."
                )

            st.markdown("---")

            for i, question in enumerate(
                st.session_state.questions
            ):

                st.markdown(
                    f"### Question {i + 1}"
                )

                st.write(
                    get_question_text(question)
                )

                options = get_options(question)

                for j, option in enumerate(options):

                    letter = chr(65 + j)

                    st.write(
                        f"**{letter}.** {option}"
                    )

                st.caption(
                    f"Topic: {get_topic(question)}"
                )

                concept = get_concept(question)

                if concept:

                    st.caption(
                        f"Concept: {concept}"
                    )

                st.markdown("---")


# ============================================================
# TAKE ASSESSMENT
# ============================================================

elif navigation == "✍️ Take Assessment":

    st.header("✍️ Take Assessment")

    if not st.session_state.questions:

        st.warning(
            "⚠️ No questions available."
        )

        st.info(
            "Generate questions first from 📝 Generate Questions."
        )

    else:

        st.write(
            f"Answer all {len(st.session_state.questions)} questions."
        )

        st.markdown("---")

        for i, question in enumerate(
            st.session_state.questions
        ):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(
                get_question_text(question)
            )

            options = get_options(question)

            display_options = []

            for j, option in enumerate(options):

                letter = chr(65 + j)

                display_options.append(
                    f"{letter}. {option}"
                )

            selected = st.radio(
                "Select one answer:",
                display_options,
                key=f"question_answer_{i}",
                index=None
            )

            if selected:

                selected_index = (
                    display_options.index(selected)
                )

                st.session_state.assessment_answers[i] = (
                    options[selected_index]
                )

            st.markdown("---")

        if st.button(
            "✅ Submit Assessment",
            type="primary"
        ):

            unanswered = []

            for i in range(
                len(st.session_state.questions)
            ):

                if i not in st.session_state.assessment_answers:

                    unanswered.append(i + 1)

            if unanswered:

                st.error(
                    "Please answer all questions before submitting.\n\n"
                    f"Unanswered questions: {unanswered}"
                )

            else:

                score = 0

                for i, question in enumerate(
                    st.session_state.questions
                ):

                    user_answer = (
                        st.session_state.assessment_answers
                        .get(i)
                    )

                    correct_answer = (
                        get_correct_option(question)
                    )

                    if (
                        user_answer is not None
                        and correct_answer is not None
                        and str(user_answer).strip().lower()
                        == str(correct_answer).strip().lower()
                    ):

                        score += 1

                total = len(
                    st.session_state.questions
                )

                percentage = (
                    score / total * 100
                    if total
                    else 0
                )

                st.session_state.score = score
                st.session_state.total_questions = total
                st.session_state.percentage = percentage
                st.session_state.quiz_submitted = True

                save_attempt_to_db(
                    score,
                    total
                )

                st.success(
                    "🎉 Assessment submitted successfully!"
                )

                st.rerun()


# ============================================================
# ASSESSMENT RESULTS
# ============================================================

if (
    navigation == "✍️ Take Assessment"
    and st.session_state.quiz_submitted
):

    st.markdown("---")

    st.header("📊 Assessment Results")

    score = st.session_state.score
    total = st.session_state.total_questions
    percentage = st.session_state.percentage

    col1, col2, col3 = st.columns(3)

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

        if percentage >= 80:
            result = "Excellent 🎉"

        elif percentage >= 60:
            result = "Good 👍"

        elif percentage >= 40:
            result = "Needs Practice 📚"

        else:
            result = "Needs Improvement 💪"

        st.metric(
            "Performance",
            result
        )

    # --------------------------------------------------------
    # Question Review
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("🔍 Detailed Review")

    for i, question in enumerate(
        st.session_state.questions
    ):

        user_answer = (
            st.session_state.assessment_answers.get(i)
        )

        correct_answer = (
            get_correct_option(question)
        )

        is_correct = (
            str(user_answer).strip().lower()
            == str(correct_answer).strip().lower()
            if user_answer is not None
            and correct_answer is not None
            else False
        )

        if is_correct:

            st.success(
                f"Question {i + 1}: Correct ✅"
            )

        else:

            st.error(
                f"Question {i + 1}: Incorrect ❌"
            )

        st.write(
            get_question_text(question)
        )

        st.write(
            f"**Your answer:** {user_answer}"
        )

        st.write(
            f"**Correct answer:** {correct_answer}"
        )

        concept = (
            get_concept(question)
            or get_topic(question)
        )

        st.info(
            f"**Why this is correct:** "
            f"{explain_concept(concept)}"
        )

        if not is_correct:

            st.warning(
                "Review this concept again in your learning plan."
            )

        st.markdown("---")


# ============================================================
# PROGRESS
# ============================================================

elif navigation == "📊 Progress":

    st.header("📊 Progress")

    if not st.session_state.quiz_submitted:

        st.info(
            "Complete an assessment to see your progress."
        )

    else:

        score = st.session_state.score
        total = st.session_state.total_questions
        percentage = st.session_state.percentage

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Questions Attempted",
                total
            )

        with col2:

            st.metric(
                "Correct Answers",
                score
            )

        with col3:

            st.metric(
                "Accuracy",
                f"{percentage:.1f}%"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # Topic-wise performance
        # ----------------------------------------------------

        st.subheader("📚 Topic-wise Performance")

        topic_total = {}
        topic_correct = {}

        for i, question in enumerate(
            st.session_state.questions
        ):

            topic = get_topic(question)

            topic_total[topic] = (
                topic_total.get(topic, 0) + 1
            )

            user_answer = (
                st.session_state.assessment_answers.get(i)
            )

            correct_answer = (
                get_correct_option(question)
            )

            if (
                user_answer is not None
                and correct_answer is not None
                and str(user_answer).strip().lower()
                == str(correct_answer).strip().lower()
            ):

                topic_correct[topic] = (
                    topic_correct.get(topic, 0) + 1
                )

        progress_data = []

        for topic, total_questions in topic_total.items():

            correct = topic_correct.get(
                topic,
                0
            )

            accuracy = (
                correct / total_questions * 100
                if total_questions
                else 0
            )

            progress_data.append(
                {
                    "Topic": topic,
                    "Correct": correct,
                    "Total": total_questions,
                    "Accuracy": round(
                        accuracy,
                        1
                    )
                }
            )

        if progress_data:

            df = pd.DataFrame(
                progress_data
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            st.bar_chart(
                df.set_index("Topic")["Accuracy"]
            )

        # ----------------------------------------------------
        # Weak topics
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader("⚠️ Topics to Improve")

        weak_topics = []

        for row in progress_data:

            if row["Accuracy"] < 70:

                weak_topics.append(
                    row["Topic"]
                )

        if weak_topics:

            for topic in weak_topics:

                st.warning(
                    f"📌 {topic} — needs more practice"
                )

        else:

            st.success(
                "🎉 Great! No major weak topics detected."
            )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader("💡 Recommendations")

        if percentage >= 80:

            st.success(
                "Excellent performance! Focus on advanced concepts "
                "and practical problem solving."
            )

        elif percentage >= 60:

            st.info(
                "Good performance. Review weak topics and solve "
                "more practice questions."
            )

        else:

            st.warning(
                "Spend more time on the fundamentals and revise "
                "the weak topics before attempting another assessment."
            )


# ============================================================
# 5-DAY LEARNING PLAN
# ============================================================

elif navigation == "📅 Learning Plan":

    st.header("📅 Personalized 5-Day Learning Plan")

    if not st.session_state.questions:

        st.warning(
            "⚠️ Please generate questions first."
        )

        st.info(
            "The learning plan uses your learning material "
            "and generated question concepts."
        )

    else:

        st.write(
            "Your plan is divided into **5 days**, with different "
            "concepts assigned to each day."
        )

        st.markdown("---")

        five_day_plan = build_five_day_plan(
            st.session_state.questions,
            st.session_state.material_text
        )

        # ----------------------------------------------------
        # Display each day
        # ----------------------------------------------------

        for day in five_day_plan:

            st.markdown(
                f"""
                <div class="day-card">
                    <h2>📅 {day["day"]} — {day["title"]}</h2>
                    <p><b>Goal:</b> {day["goal"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if day["concepts"]:

                st.subheader(
                    "📚 Concepts to Learn"
                )

                for concept in day["concepts"]:

                    st.markdown(
                        f"""
                        <div class="concept-box">
                            <b>🔹 {concept}</b>
                            <br>
                            <span class="small-text">
                                {explain_concept(concept)}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.info(
                    "Use this day for revision and practice."
                )

            st.markdown("#### 📝 Tasks")

            if day["day"] == "Day 1":

                tasks = [
                    "Read the basic concepts carefully.",
                    "Understand important definitions.",
                    "Write short notes in your own words.",
                    "Solve 5 easy practice questions."
                ]

            elif day["day"] == "Day 2":

                tasks = [
                    "Study the core concepts.",
                    "Understand how each concept works.",
                    "Review examples.",
                    "Solve 5–10 practice questions."
                ]

            elif day["day"] == "Day 3":

                tasks = [
                    "Study practical applications.",
                    "Work through examples.",
                    "Try small coding/problem-solving exercises.",
                    "Identify areas that are difficult."
                ]

            elif day["day"] == "Day 4":

                tasks = [
                    "Focus on difficult concepts.",
                    "Practice MCQs and problems.",
                    "Review mistakes from previous questions.",
                    "Spend extra time on weak topics."
                ]

            else:

                tasks = [
                    "Revise all concepts learned during the week.",
                    "Review important definitions and formulas.",
                    "Take a self-test without looking at notes.",
                    "Prepare for the next assessment."
                ]

            for task in tasks:

                st.write(
                    f"☐ {task}"
                )

            st.markdown("---")

        # ----------------------------------------------------
        # Daily timetable
        # ----------------------------------------------------

        st.header("⏰ Suggested Daily Routine")

        routine = pd.DataFrame(
            {
                "Activity": [
                    "Concept Learning",
                    "Notes / Revision",
                    "Practice Questions",
                    "Self-Test"
                ],
                "Time": [
                    "45 minutes",
                    "20 minutes",
                    "30 minutes",
                    "15 minutes"
                ]
            }
        )

        st.table(routine)

        # ----------------------------------------------------
        # Weak topic message
        # ----------------------------------------------------

        if st.session_state.quiz_submitted:

            topic_total = {}
            topic_correct = {}

            for i, question in enumerate(
                st.session_state.questions
            ):

                topic = get_topic(question)

                topic_total[topic] = (
                    topic_total.get(topic, 0) + 1
                )

                user_answer = (
                    st.session_state.assessment_answers.get(i)
                )

                correct_answer = (
                    get_correct_option(question)
                )

                if (
                    user_answer is not None
                    and correct_answer is not None
                    and str(user_answer).strip().lower()
                    == str(correct_answer).strip().lower()
                ):

                    topic_correct[topic] = (
                        topic_correct.get(topic, 0) + 1
                    )

            weak_topics = []

            for topic, total_questions in topic_total.items():

                correct = topic_correct.get(
                    topic,
                    0
                )

                accuracy = (
                    correct / total_questions * 100
                    if total_questions
                    else 0
                )

                if accuracy < 70:

                    weak_topics.append(
                        topic
                    )

            if weak_topics:

                st.markdown("---")

                st.subheader(
                    "🎯 Your Weak Areas"
                )

                for topic in weak_topics:

                    st.warning(
                        f"Spend extra time on **{topic}**."
                    )

        st.markdown("---")

        st.success(
            "🌟 Follow the plan for 5 days, practice regularly, "
            "and then take another assessment to measure your improvement!"
        )


# ============================================================
# SYSTEM CHECK
# ============================================================

elif navigation == "🔧 System Check":

    st.header("🔧 System Check")

    st.subheader("Python Environment")

    import sys

    st.write(
        f"Python version: `{sys.version}`"
    )

    st.subheader("Required Packages")

    packages = [
        "streamlit",
        "pandas",
        "PyPDF2",
        "supabase"
    ]

    for package in packages:

        try:

            if package == "PyPDF2":

                import PyPDF2

                version = PyPDF2.__version__

            elif package == "streamlit":

                version = st.__version__

            elif package == "pandas":

                version = pd.__version__

            elif package == "supabase":

                import supabase

                version = getattr(
                    supabase,
                    "__version__",
                    "Installed"
                )

            st.success(
                f"✅ {package}: {version}"
            )

        except Exception:

            st.error(
                f"❌ {package}: Not available"
            )

    st.subheader("Supabase")

    if supabase:

        st.success(
            "🗄️ Database Connected"
        )

    else:

        st.warning(
            "⚠️ Supabase is not connected."
        )

    st.subheader("Learning Material")

    if st.session_state.material_text:

        st.success(
            f"✅ Material loaded: "
            f"{st.session_state.material_name}"
        )

        st.write(
            f"Characters: {len(st.session_state.material_text)}"
        )

    else:

        st.info(
            "No learning material loaded."
        )

    st.subheader("Questions")

    st.write(
        f"Generated questions: "
        f"{len(st.session_state.questions)}"
    )

    st.subheader("Assessment")

    if st.session_state.quiz_submitted:

        st.success(
            f"Assessment completed — "
            f"{st.session_state.score}/"
            f"{st.session_state.total_questions}"
        )

    else:

        st.info(
            "Assessment not completed."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🎓 AIStat Learn | AI-Powered Personalized Learning Platform"
)
