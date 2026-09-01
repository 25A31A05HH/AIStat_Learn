import os
import uuid
import json
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

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .result-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .correct-box {
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        background-color: #f1f8f3;
        margin: 10px 0;
    }

    .wrong-box {
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #c62828;
        background-color: #fff5f5;
        margin: 10px 0;
    }

    .topic-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin: 15px 0;
    }

    .key-point {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        background-color: #f7f7f7;
    }

    .score-number {
        font-size: 42px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)


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

    "quiz_history": [],
    "topic_progress": {},

    "show_topic_explanations": True
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SUPABASE CONNECTION
# ============================================================

supabase = None
database_status = "Not Connected"

try:
    from supabase import create_client

    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        database_status = "Connected"

except Exception as e:
    database_status = f"Not Connected: {str(e)}"


# ============================================================
# NAVIGATION
# ============================================================

def go_to_step(step_number):
    st.session_state.current_step = step_number
    st.rerun()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_display_text(text):
    """Convert any value into readable text."""
    if text is None:
        return ""

    if isinstance(text, list):
        return ", ".join(str(x) for x in text)

    if isinstance(text, dict):
        if "label" in text:
            return str(text["label"])

        if "text" in text:
            return str(text["text"])

        if "value" in text:
            return str(text["value"])

    return str(text)


def normalize_option(option):
    """
    Supports different option formats from mcq_generator.py.
    """

    if isinstance(option, dict):
        value = (
            option.get("value")
            or option.get("id")
            or option.get("letter")
        )

        label = (
            option.get("label")
            or option.get("text")
            or option.get("answer")
            or option.get("option")
            or option.get("value")
        )

        feedback = (
            option.get("feedback")
            or option.get("explanation")
            or ""
        )

        return {
            "value": str(value) if value is not None else "",
            "label": clean_display_text(label),
            "feedback": clean_display_text(feedback)
        }

    return {
        "value": "",
        "label": clean_display_text(option),
        "feedback": ""
    }


def get_question_text(question):
    return clean_display_text(
        question.get("question")
        or question.get("text")
        or question.get("question_text")
        or ""
    )


def get_question_topic(question):
    return clean_display_text(
        question.get("topic")
        or question.get("subject")
        or "General Topic"
    )


def get_question_concept(question):
    return clean_display_text(
        question.get("concept")
        or question.get("skill")
        or question.get("topic")
        or "Key Concept"
    )


def get_correct_answer(question):
    """
    Supports different correct-answer field names.
    """

    answer = (
        question.get("correct_answer")
        or question.get("correctAnswer")
        or question.get("answer")
        or question.get("correct")
    )

    if answer is not None:
        return clean_display_text(answer)

    correct_values = question.get("correctValues")

    if correct_values:
        if isinstance(correct_values, list):
            return clean_display_text(correct_values[0])
        return clean_display_text(correct_values)

    return ""


def get_options(question):
    raw_options = (
        question.get("options")
        or question.get("choices")
        or []
    )

    return [normalize_option(option) for option in raw_options]


def get_general_explanation(question):
    """
    Gets the explanation generated by mcq_generator.py.
    """

    return clean_display_text(
        question.get("explanation")
        or question.get("answer_explanation")
        or question.get("solution")
        or question.get("reason")
        or ""
    )


def find_correct_option(question):
    """
    Finds the complete correct option object.
    """

    options = get_options(question)
    correct_answer = get_correct_answer(question)

    for option in options:
        if option["label"].strip().lower() == correct_answer.strip().lower():
            return option

        if option["value"].strip().lower() == correct_answer.strip().lower():
            return option

    return None


def get_option_feedback(question, option):
    """
    Uses option-specific feedback if mcq_generator.py provides it.
    """

    if option.get("feedback"):
        return option["feedback"]

    # Some generators may store feedback separately.
    feedback_map = question.get("option_feedback")

    if isinstance(feedback_map, dict):
        label = option["label"]
        value = option["value"]

        if label in feedback_map:
            return clean_display_text(feedback_map[label])

        if value in feedback_map:
            return clean_display_text(feedback_map[value])

    return ""


def explain_incorrect_option(question, option, correct_option):
    """
    Safe fallback explanation when the generator does not provide
    option-specific feedback.
    """

    specific_feedback = get_option_feedback(question, option)

    if specific_feedback:
        return specific_feedback

    correct_label = (
        correct_option["label"]
        if correct_option
        else get_correct_answer(question)
    )

    concept = get_question_concept(question)

    return (
        f"This option does not match the correct concept being tested. "
        f"For this question, the correct answer is '{correct_label}', "
        f"because it best satisfies the question's stated condition. "
        f"The key concept to review is {concept}."
    )


def create_topic_explanation(question):
    """
    Builds a useful topic explanation using information already
    present in the generated question.
    """

    topic = get_question_topic(question)
    concept = get_question_concept(question)

    explanation = get_general_explanation(question)

    source_text = clean_display_text(
        question.get("source_text")
        or question.get("source")
        or ""
    )

    st.markdown(f"### 📚 Topic Explanation: {topic}")

    st.markdown(
        f"""
        <div class="topic-box">
        <h4>🔑 Key Concept: {concept}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    if explanation:
        st.markdown("#### What you should understand")
        st.write(explanation)

    elif source_text:
        st.markdown("#### Topic Overview")

        # Try to show useful source sentences rather than the whole material.
        sentences = re.split(r"(?<=[.!?])\s+", source_text)

        useful_sentences = []

        for sentence in sentences:
            if len(sentence.split()) >= 5:
                useful_sentences.append(sentence.strip())

        if useful_sentences:
            st.write(" ".join(useful_sentences[:4]))
        else:
            st.write(source_text[:800])

    else:
        st.write(
            f"This question tests your understanding of {concept}. "
            f"Review the definition, important characteristics, "
            f"examples, and applications related to this concept."
        )

    st.markdown("#### 💡 Remember")

    st.markdown(
        f"""
        <div class="key-point">
        • Topic: <b>{topic}</b>
        </div>

        <div class="key-point">
        • Concept: <b>{concept}</b>
        </div>

        <div class="key-point">
        • Focus on understanding the concept rather than memorizing only the answer.
        </div>
        """,
        unsafe_allow_html=True
    )


def calculate_performance(percentage):
    if percentage >= 90:
        return "Excellent 🎉", "You have demonstrated excellent understanding."

    if percentage >= 75:
        return "Very Good 👏", "You have a strong understanding of the topic."

    if percentage >= 60:
        return "Good 👍", "You understand many of the important concepts."

    if percentage >= 40:
        return "Needs Improvement 📖", "Review the weak concepts and practice again."

    return "Needs More Practice 💪", "Go through the topic explanation and try another assessment."


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def save_material_to_db(text, material_name="Learning Material"):
    if supabase is None:
        return None

    try:
        response = supabase.table("materials").insert({
            "user_id": st.session_state.user_id,
            "title": material_name,
            "content": text
        }).execute()

        if response.data:
            return response.data[0].get("id")

    except Exception as e:
        st.warning(f"Material could not be saved to database: {e}")

    return None


def save_quiz_to_db(questions, material_id=None):
    if supabase is None:
        return None

    try:
        quiz_data = {
            "user_id": st.session_state.user_id
        }

        if material_id:
            quiz_data["material_id"] = material_id

        response = (
            supabase
            .table("quizzes")
            .insert(quiz_data)
            .execute()
        )

        if not response.data:
            return None

        quiz_id = response.data[0].get("id")

        # Try saving questions individually.
        for index, question in enumerate(questions, start=1):

            options = get_options(question)

            option_labels = [
                option["label"]
                for option in options
            ]

            question_data = {
                "quiz_id": quiz_id,
                "question_number": index,
                "question": get_question_text(question),
                "options": option_labels,
                "correct_answer": get_correct_answer(question),
                "explanation": get_general_explanation(question)
            }

            # Optional fields
            topic = get_question_topic(question)
            concept = get_question_concept(question)

            if topic:
                question_data["topic"] = topic

            if concept:
                question_data["concept"] = concept

            try:
                supabase.table("questions").insert(
                    question_data
                ).execute()

            except Exception:
                # Do not stop the quiz if the optional question table
                # has a different schema.
                pass

        return quiz_id

    except Exception as e:
        st.warning(f"Quiz could not be saved to database: {e}")

    return None


def save_attempt_to_db(score, total, percentage):
    if supabase is None:
        return

    if not st.session_state.quiz_id:
        return

    try:
        supabase.table("attempts").insert({
            "user_id": st.session_state.user_id,
            "quiz_id": st.session_state.quiz_id,
            "score": score,
            "total": total,
            "percentage": percentage
        }).execute()

    except Exception as e:
        st.warning(f"Attempt could not be saved to database: {e}")


def load_quiz_history():
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
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 AIStat Learn")

st.sidebar.markdown("---")

navigation_pages = [
    "🏠 Home",
    "📚 Learning Material",
    "📝 Generate Questions",
    "✍️ Take Assessment",
    "📊 Progress",
    "📅 Learning Plan",
    "🔧 System Check"
]

current_step = st.session_state.current_step

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

st.sidebar.markdown("---")

st.sidebar.write("### Progress")

steps = [
    ("1", "Learning Material"),
    ("2", "Generate Questions"),
    ("3", "Take Assessment"),
    ("4", "Progress"),
    ("5", "Learning Plan")
]

for number, name in steps:
    if int(number) < current_step:
        st.sidebar.success(f"✓ {number}. {name}")
    elif int(number) == current_step:
        st.sidebar.info(f"● {number}. {name}")
    else:
        st.sidebar.write(f"○ {number}. {name}")

st.sidebar.markdown("---")

if database_status == "Connected":
    st.sidebar.success("🗄️ Database Connected")
else:
    st.sidebar.warning("🗄️ Database Offline")


# ============================================================
# HOME
# ============================================================

if sidebar_page == "🏠 Home":

    st.markdown(
        '<div class="main-title">🎓 AIStat Learn</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">AI-powered personalized learning platform</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        AIStat Learn helps students learn from study material,
        practice with automatically generated questions,
        understand their mistakes, and track their progress.
        """
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
            ### 📚 Learn

            Upload or enter your learning material.
            """
        )

    with col2:
        st.info(
            """
            ### 📝 Practice

            Generate personalized MCQs and take an assessment.
            """
        )

    with col3:
        st.info(
            """
            ### 📊 Improve

            Understand mistakes and track weak topics.
            """
        )

    st.markdown("---")

    if st.button("🚀 Start Learning", use_container_width=True):
        go_to_step(1)


# ============================================================
# STEP 1 — LEARNING MATERIAL
# ============================================================

elif sidebar_page == "📚 Learning Material":

    st.title("📚 Step 1 — Learning Material")

    st.write(
        "Enter the study material from which you want AIStat Learn "
        "to generate questions."
    )

    material_name = st.text_input(
        "Material Title",
        value=st.session_state.material_name,
        placeholder="Example: Python Basics"
    )

    material_text = st.text_area(
        "Learning Material",
        value=st.session_state.material_text,
        height=350,
        placeholder=(
            "Paste your study material here...\n\n"
            "Example:\n"
            "Python is a high-level programming language. "
            "It supports variables, loops, functions and lists."
        )
    )

    if st.button("💾 Save Learning Material", use_container_width=True):

        if len(material_text.strip()) < 10:
            st.error("Please enter sufficient learning material.")
        else:

            st.session_state.material_text = material_text
            st.session_state.material_name = (
                material_name.strip()
                if material_name.strip()
                else "Learning Material"
            )

            material_id = save_material_to_db(
                material_text,
                st.session_state.material_name
            )

            if material_id:
                st.session_state.material_id = material_id

            st.success("✅ Learning material saved successfully!")

    st.markdown("---")

    if st.session_state.material_text:

        st.success(
            f"Material ready: **{st.session_state.material_name}**"
        )

        if st.button(
            "➡️ NEXT: Generate Questions",
            use_container_width=True
        ):
            go_to_step(2)


# ============================================================
# STEP 2 — GENERATE QUESTIONS
# ============================================================

elif sidebar_page == "📝 Generate Questions":

    st.title("📝 Step 2 — Generate Questions")

    if not st.session_state.material_text:

        st.warning(
            "Please add learning material before generating questions."
        )

        if st.button("⬅️ Go to Learning Material"):
            go_to_step(1)

    else:

        st.success(
            f"📚 Material: **{st.session_state.material_name}**"
        )

        question_count = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=20,
            value=5
        )

        st.write(
            "AIStat Learn will generate MCQs from your learning material."
        )

        if st.button(
            "🧠 Generate Questions",
            use_container_width=True
        ):

            with st.spinner("Generating questions..."):

                try:
                    generated_questions = generate_mcqs(
                        st.session_state.material_text,
                        question_count
                    )

                    if generated_questions:

                        st.session_state.questions = generated_questions
                        st.session_state.quiz_submitted = False
                        st.session_state.assessment_answers = {}
                        st.session_state.score = 0
                        st.session_state.total_questions = len(
                            generated_questions
                        )

                        # Try saving to database.
                        st.session_state.quiz_id = save_quiz_to_db(
                            generated_questions
                        )

                        st.success(
                            f"✅ {len(generated_questions)} questions generated!"
                        )

                    else:
                        st.error(
                            "No questions were generated. "
                            "Please provide more detailed learning material."
                        )

                except Exception as e:
                    st.error(
                        f"Error generating questions: {e}"
                    )

        # ----------------------------------------------------
        # Preview questions
        # ----------------------------------------------------

        if st.session_state.questions:

            st.markdown("---")

            st.subheader("📋 Generated Questions Preview")

            for i, question in enumerate(
                st.session_state.questions,
                start=1
            ):

                with st.expander(
                    f"Question {i}: {get_question_text(question)}"
                ):

                    options = get_options(question)

                    for option in options:
                        st.write(
                            f"• {option['label']}"
                        )

                    st.caption(
                        f"Topic: {get_question_topic(question)}"
                    )

            st.markdown("---")

            if st.button(
                "➡️ NEXT: Take Assessment",
                use_container_width=True
            ):
                go_to_step(3)


# ============================================================
# STEP 3 — TAKE ASSESSMENT
# ============================================================

elif sidebar_page == "✍️ Take Assessment":

    st.title("✍️ Step 3 — Take Assessment")

    if not st.session_state.questions:

        st.warning(
            "No quiz is available. Please generate questions first."
        )

        if st.button("⬅️ Generate Questions"):
            go_to_step(2)

    else:

        total_questions = len(st.session_state.questions)

        # ====================================================
        # BEFORE SUBMISSION
        # ====================================================

        if not st.session_state.quiz_submitted:

            st.info(
                f"📝 Answer all {total_questions} questions and then "
                f"submit the quiz."
            )

            st.markdown("---")

            for index, question in enumerate(
                st.session_state.questions,
                start=1
            ):

                st.markdown(
                    f"### Question {index} of {total_questions}"
                )

                st.write(
                    f"**{get_question_text(question)}**"
                )

                options = get_options(question)

                labels = [
                    option["label"]
                    for option in options
                    if option["label"]
                ]

                if not labels:
                    st.warning(
                        "This question has no valid options."
                    )
                    continue

                previous_answer = st.session_state.assessment_answers.get(
                    index
                )

                default_index = 0

                if previous_answer in labels:
                    default_index = labels.index(previous_answer)

                selected = st.radio(
                    "Choose your answer:",
                    labels,
                    index=default_index,
                    key=f"question_{index}"
                )

                st.session_state.assessment_answers[index] = selected

                st.markdown("---")

            if st.button(
                "📤 Submit Quiz",
                use_container_width=True
            ):

                unanswered = []

                for index in range(1, total_questions + 1):
                    if not st.session_state.assessment_answers.get(index):
                        unanswered.append(index)

                if unanswered:

                    st.error(
                        "Please answer all questions before submitting."
                    )

                else:

                    score = 0

                    for index, question in enumerate(
                        st.session_state.questions,
                        start=1
                    ):

                        user_answer = (
                            st.session_state.assessment_answers.get(index)
                        )

                        correct_answer = get_correct_answer(question)

                        if (
                            user_answer.strip().lower()
                            == correct_answer.strip().lower()
                        ):
                            score += 1

                    percentage = round(
                        (score / total_questions) * 100,
                        2
                    )

                    st.session_state.score = score
                    st.session_state.total_questions = total_questions
                    st.session_state.percentage = percentage
                    st.session_state.quiz_submitted = True

                    # Save assessment attempt.
                    save_attempt_to_db(
                        score,
                        total_questions,
                        percentage
                    )

                    st.rerun()


        # ====================================================
        # AFTER SUBMISSION
        # ====================================================

        else:

            score = st.session_state.score
            total = st.session_state.total_questions
            percentage = st.session_state.percentage

            performance, performance_message = calculate_performance(
                percentage
            )

            st.success("🎉 Quiz Submitted Successfully!")

            st.markdown("---")

            # =================================================
            # RESULT SUMMARY
            # =================================================

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
                    f"{percentage}%"
                )

            with col3:
                st.metric(
                    "Correct",
                    score
                )

            with col4:
                st.metric(
                    "Incorrect",
                    total - score
                )

            st.markdown(
                f"""
                <div class="result-card">
                    <h2>{performance}</h2>
                    <p>{performance_message}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            # =================================================
            # QUESTION-BY-QUESTION EXPLANATION
            # =================================================

            st.header("🔍 Detailed Answer Explanation")

            st.write(
                """
                Review every question below. AIStat Learn explains
                why the correct answer is correct and, whenever
                available, why each other option is incorrect.
                """
            )

            weak_topics = {}

            for index, question in enumerate(
                st.session_state.questions,
                start=1
            ):

                question_text = get_question_text(question)
                topic = get_question_topic(question)
                concept = get_question_concept(question)

                user_answer = (
                    st.session_state.assessment_answers.get(index, "")
                )

                correct_answer = get_correct_answer(question)

                is_correct = (
                    user_answer.strip().lower()
                    == correct_answer.strip().lower()
                )

                options = get_options(question)

                correct_option = find_correct_option(question)

                if not is_correct:
                    weak_topics[topic] = (
                        weak_topics.get(topic, 0) + 1
                    )

                # ---------------------------------------------
                # Question heading
                # ---------------------------------------------

                if is_correct:
                    st.markdown(
                        f"## 🟢 Question {index} — Correct"
                    )
                else:
                    st.markdown(
                        f"## 🔴 Question {index} — Incorrect"
                    )

                st.write(
                    f"**{question_text}**"
                )

                st.caption(
                    f"📚 Topic: {topic} | 🔑 Concept: {concept}"
                )

                # ---------------------------------------------
                # User answer
                # ---------------------------------------------

                if is_correct:

                    st.markdown(
                        f"""
                        <div class="correct-box">
                        <b>🟢 Your Answer:</b> {user_answer}<br>
                        <b>✅ Correct Answer:</b> {correct_answer}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="wrong-box">
                        <b>🔴 Your Answer:</b> {user_answer}<br>
                        <b>✅ Correct Answer:</b> {correct_answer}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ---------------------------------------------
                # WHY CORRECT ANSWER IS CORRECT
                # ---------------------------------------------

                st.markdown("### ✅ Why is this answer correct?")

                general_explanation = get_general_explanation(
                    question
                )

                if correct_option and correct_option.get("feedback"):

                    st.write(
                        correct_option["feedback"]
                    )

                elif general_explanation:

                    st.write(
                        general_explanation
                    )

                else:

                    st.write(
                        f"The correct answer is **{correct_answer}** "
                        f"because it satisfies the condition asked "
                        f"in the question and matches the concept "
                        f"being tested: **{concept}**."
                    )

                # ---------------------------------------------
                # WHY OTHER OPTIONS ARE INCORRECT
                # ---------------------------------------------

                st.markdown("### ❌ Why are the other options incorrect?")

                for option in options:

                    option_label = option["label"]

                    if not option_label:
                        continue

                    if (
                        option_label.strip().lower()
                        == correct_answer.strip().lower()
                    ):
                        continue

                    option_feedback = get_option_feedback(
                        question,
                        option
                    )

                    if option_feedback:

                        st.markdown(
                            f"**❌ {option_label}**"
                        )

                        st.write(
                            option_feedback
                        )

                    else:

                        st.markdown(
                            f"**❌ {option_label}**"
                        )

                        st.write(
                            explain_incorrect_option(
                                question,
                                option,
                                correct_option
                            )
                        )

                # ---------------------------------------------
                # TOPIC EXPLANATION
                # ---------------------------------------------

                with st.expander(
                    f"📚 Learn More About: {topic}",
                    expanded=True
                ):

                    create_topic_explanation(
                        question
                    )

                st.markdown("---")

            # =================================================
            # WEAK TOPICS
            # =================================================

            st.header("🎯 Topics to Review")

            if weak_topics:

                st.warning(
                    "These topics appeared in questions you answered incorrectly."
                )

                weak_data = []

                for topic, count in sorted(
                    weak_topics.items(),
                    key=lambda x: x[1],
                    reverse=True
                ):

                    weak_data.append({
                        "Topic": topic,
                        "Questions to Review": count
                    })

                st.dataframe(
                    pd.DataFrame(weak_data),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown(
                    """
                    ### 📖 What should you do?

                    1. Read the topic explanation above.
                    2. Review the important concepts.
                    3. Practice similar questions.
                    4. Take another assessment.
                    """
                )

            else:

                st.success(
                    "🎉 Excellent! You answered every question correctly. "
                    "No weak topics were detected."
                )

            # =================================================
            # OVERALL RECOMMENDATION
            # =================================================

            st.markdown("---")

            st.header("🤖 AI Learning Recommendation")

            if percentage >= 90:

                st.success(
                    """
                    🌟 Excellent performance!

                    You have demonstrated strong understanding of the
                    material. You can move to more advanced concepts
                    or attempt a harder assessment.
                    """
                )

            elif percentage >= 75:

                st.info(
                    """
                    👍 Good performance!

                    Your fundamentals are strong. Review the questions
                    you missed and then practice a few more questions
                    before moving to advanced topics.
                    """
                )

            elif percentage >= 50:

                st.warning(
                    """
                    📖 Moderate performance.

                    Some concepts need revision. Focus especially on
                    the weak topics identified above and take another
                    assessment after reviewing them.
                    """
                )

            else:

                st.error(
                    """
                    💪 More practice is recommended.

                    Start by reviewing the topic explanations carefully.
                    Understand the concepts with examples and then take
                    another assessment.
                    """
                )

            # =================================================
            # NEXT BUTTONS
            # =================================================

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "🔄 Take Assessment Again",
                    use_container_width=True
                ):

                    st.session_state.assessment_answers = {}
                    st.session_state.quiz_submitted = False
                    go_to_step(3)

            with col2:

                if st.button(
                    "➡️ View Progress",
                    use_container_width=True
                ):
                    go_to_step(4)


# ============================================================
# STEP 4 — PROGRESS
# ============================================================

elif sidebar_page == "📊 Progress":

    st.title("📊 Step 4 — Progress")

    score = st.session_state.score
    total = st.session_state.total_questions
    percentage = st.session_state.percentage

    if total > 0:

        st.subheader("Latest Assessment")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Latest Score",
                f"{score}/{total}"
            )

        with col2:
            st.metric(
                "Percentage",
                f"{percentage}%"
            )

        with col3:

            performance, _ = calculate_performance(
                percentage
            )

            st.metric(
                "Performance",
                performance
            )

    else:

        st.info(
            "Complete an assessment to see your progress."
        )

    st.markdown("---")

    st.subheader("📈 Learning Progress")

    history = load_quiz_history()

    if history:

        try:

            history_data = []

            for item in history:

                history_data.append({
                    "Date": item.get("created_at", ""),
                    "Score": item.get("score", 0),
                    "Total": item.get(
                        "total",
                        item.get("total_questions", 0)
                    ),
                    "Percentage": item.get("percentage", 0)
                })

            df = pd.DataFrame(history_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            if "Percentage" in df.columns:

                st.line_chart(
                    df["Percentage"]
                )

        except Exception:

            st.info(
                "Assessment history is available but could not be displayed."
            )

    else:

        st.info(
            "Your assessment history will appear here after completing quizzes."
        )

    st.markdown("---")

    if st.button(
        "➡️ Go to Learning Plan",
        use_container_width=True
    ):
        go_to_step(5)


# ============================================================
# STEP 5 — LEARNING PLAN
# ============================================================

elif sidebar_page == "📅 Learning Plan":

    st.title("📅 Step 5 — Personalized Learning Plan")

    percentage = st.session_state.percentage

    if percentage >= 90:

        st.success(
            """
            ### 🌟 Advanced Learning Plan

            You have a strong understanding of the current material.

            **Recommended next steps:**
            - Study advanced concepts.
            - Solve challenging problems.
            - Try higher-difficulty assessments.
            - Work on practical projects.
            """
        )

    elif percentage >= 75:

        st.info(
            """
            ### 👍 Strengthening Learning Plan

            Your fundamentals are good.

            **Recommended next steps:**
            - Review incorrect questions.
            - Practice intermediate questions.
            - Study examples and applications.
            - Take another assessment.
            """
        )

    elif percentage >= 50:

        st.warning(
            """
            ### 📖 Revision Learning Plan

            Some concepts need additional practice.

            **Recommended next steps:**
            - Review the topic explanations.
            - Focus on incorrect questions.
            - Practice basic and intermediate questions.
            - Retake the assessment.
            """
        )

    else:

        st.error(
            """
            ### 💪 Foundation Learning Plan

            Start by strengthening your fundamentals.

            **Recommended next steps:**
            - Read the learning material again.
            - Understand definitions and basic concepts.
            - Study examples.
            - Practice simple questions.
            - Retake the assessment.
            """
        )

    st.markdown("---")

    st.subheader("🎯 Suggested Study Cycle")

    st.markdown(
        """
        **Day 1:** Read and understand the learning material.

        **Day 2:** Review important concepts and examples.

        **Day 3:** Practice questions.

        **Day 4:** Review mistakes from the assessment.

        **Day 5:** Take another assessment.

        **Day 6:** Focus on weak topics.

        **Day 7:** Take a final revision assessment.
        """
    )


# ============================================================
# SYSTEM CHECK
# ============================================================

elif sidebar_page == "🔧 System Check":

    st.title("🔧 System Check")

    st.subheader("Database")

    if database_status == "Connected":
        st.success("✅ Supabase connection is working.")
    else:
        st.warning(
            "⚠️ Supabase is not connected. "
            "The app can still run using session data."
        )

    st.markdown("---")

    st.subheader("MCQ Generator")

    test_text = (
        "Python is a programming language. "
        "Python supports variables, loops, functions and lists. "
        "It is widely used for software development and data analysis."
    )

    if st.button(
        "🧪 Test Question Generator",
        use_container_width=True
    ):

        try:

            test_questions = generate_mcqs(
                test_text,
                3
            )

            if test_questions:

                st.success(
                    f"✅ MCQ Generator working. "
                    f"Generated {len(test_questions)} questions."
                )

                for i, question in enumerate(
                    test_questions,
                    start=1
                ):

                    st.write(
                        f"{i}. {get_question_text(question)}"
                    )

            else:

                st.error(
                    "❌ MCQ Generator returned no questions."
                )

        except Exception as e:

            st.error(
                f"❌ MCQ Generator error: {e}"
            )

    st.markdown("---")

    st.subheader("Session Information")

    st.write(
        f"User ID: `{st.session_state.user_id}`"
    )

    st.write(
        f"Current Step: `{st.session_state.current_step}`"
    )

    st.write(
        f"Questions Available: `{len(st.session_state.questions)}`"
    )

    st.write(
        f"Quiz Submitted: `{st.session_state.quiz_submitted}`"
    )
