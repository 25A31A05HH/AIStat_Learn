import os
import uuid
import json
import streamlit as st
import pandas as pd

from mcq_generator import generate_mcqs


# ============================================================
# AIStat Learn - Persistent Version
# ============================================================

st.set_page_config(
    page_title="AIStat Learn",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

supabase = None
supabase_error = None


def get_supabase_client():
    """
    Create Supabase client using Streamlit secrets.
    """

    global supabase_error

    try:
        from supabase import create_client

        # Read secrets
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        # Validate values
        if not url:
            supabase_error = "SUPABASE_URL is empty."
            return None

        if not key:
            supabase_error = "SUPABASE_KEY is empty."
            return None

        # Create Supabase client
        client = create_client(
            url,
            key
        )

        return client

    except KeyError as error:
        supabase_error = (
            f"Missing Streamlit secret: {error}"
        )
        return None

    except Exception as error:
        supabase_error = str(error)
        return None


supabase = get_supabase_client()


# ============================================================
# DATABASE STATUS
# ============================================================

def db_available():
    """
    Returns True when the Supabase client was created.
    """

    return supabase is not None


def test_database_connection():
    """
    Test the actual Supabase database.

    Returns:
        (True, message) if successful
        (False, error message) if unsuccessful
    """

    if supabase is None:
        return False, supabase_error or "Supabase client is not available."

    try:
        # Test the learning_materials table.
        response = (
            supabase
            .table("learning_materials")
            .select("id")
            .limit(1)
            .execute()
        )

        return True, "Supabase database connection is working."

    except Exception as error:
        return False, str(error)


# ============================================================
# USER / SESSION ID
# ============================================================

def get_user_id():
    """
    Keep a browser-level user id in the URL so the same browser
    can recover its data after a Streamlit refresh.
    """

    try:
        existing_id = st.query_params.get("user_id")

        if existing_id:
            return str(existing_id)

        new_id = str(uuid.uuid4())

        st.query_params["user_id"] = new_id

        return new_id

    except Exception:

        if "local_user_id" not in st.session_state:
            st.session_state.local_user_id = str(
                uuid.uuid4()
            )

        return st.session_state.local_user_id


USER_ID = get_user_id()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "learning_material": "",
    "material_id": None,
    "material_title": "",
    "generated_questions": [],
    "quiz_id": None,
    "assessment_answers": {},
    "quiz_submitted": False,
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_percentage": 0.0,
    "quiz_results": [],
    "first_scores": [],
    "second_scores": [],
    "loaded_from_database": False,
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATABASE HELPERS
# ============================================================

def save_material_to_db(title, content):
    """
    Save learning material and return its database id.
    """

    if not db_available():
        return None

    try:

        response = (
            supabase
            .table("learning_materials")
            .insert(
                {
                    "user_id": USER_ID,
                    "title": title,
                    "content": content,
                }
            )
            .execute()
        )

        if response.data:
            return response.data[0]["id"]

    except Exception as error:

        st.warning(
            f"Database could not save the material: {error}"
        )

    return None


def load_latest_material():
    """
    Load the most recent material belonging to this browser.
    """

    if not db_available():
        return None

    try:

        response = (
            supabase
            .table("learning_materials")
            .select("*")
            .eq("user_id", USER_ID)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception as error:

        # Don't crash the application.
        return None

    return None


def save_quiz_to_db(material_id, questions):
    """
    Save quiz and all generated questions.
    """

    if not db_available():
        return None

    try:

        quiz_data = {
            "user_id": USER_ID,
            "question_count": len(questions),
        }

        # material_id may be None if material was not saved.
        if material_id:
            quiz_data["material_id"] = material_id

        quiz_response = (
            supabase
            .table("quizzes")
            .insert(quiz_data)
            .execute()
        )

        if not quiz_response.data:
            return None

        quiz_id = quiz_response.data[0]["id"]

        question_rows = []

        for index, question in enumerate(
            questions,
            start=1
        ):

            options = question.get(
                "options",
                {}
            )

            question_rows.append(
                {
                    "quiz_id": quiz_id,
                    "question_number": index,
                    "topic": str(
                        question.get(
                            "topic",
                            "General"
                        )
                    ),
                    "concept": str(
                        question.get(
                            "concept",
                            ""
                        )
                    ),
                    "difficulty": str(
                        question.get(
                            "difficulty",
                            "Medium"
                        )
                    ),
                    "question_type": str(
                        question.get(
                            "question_type",
                            ""
                        )
                    ),
                    "question": str(
                        question.get(
                            "question",
                            ""
                        )
                    ),
                    "options": options,
                    "correct_answer": str(
                        question.get(
                            "correct_answer",
                            ""
                        )
                    ),
                    "explanation": str(
                        question.get(
                            "explanation",
                            ""
                        )
                    ),
                    "source_text": str(
                        question.get(
                            "source_text",
                            ""
                        )
                    ),
                }
            )

        if question_rows:

            (
                supabase
                .table("questions")
                .insert(question_rows)
                .execute()
            )

        return quiz_id

    except Exception as error:

        st.warning(
            f"Database could not save the quiz: {error}"
        )

        return None


def load_latest_quiz():
    """
    Load the latest quiz for this browser.
    """

    if not db_available():
        return None

    try:

        quiz_response = (
            supabase
            .table("quizzes")
            .select("*")
            .eq("user_id", USER_ID)
            .order(
                "created_at",
                desc=True
            )
            .limit(1)
            .execute()
        )

        if not quiz_response.data:
            return None

        quiz = quiz_response.data[0]

        question_response = (
            supabase
            .table("questions")
            .select("*")
            .eq(
                "quiz_id",
                quiz["id"]
            )
            .order(
                "question_number"
            )
            .execute()
        )

        if not question_response.data:
            return None

        questions = []

        for row in question_response.data:

            options = row.get(
                "options",
                {}
            )

            if isinstance(options, str):

                try:
                    options = json.loads(options)

                except Exception:
                    options = {}

            questions.append(
                {
                    "id": (
                        f"Q"
                        f"{int(row['question_number']):03d}"
                    ),
                    "topic": row.get(
                        "topic",
                        "General"
                    ),
                    "concept": row.get(
                        "concept",
                        ""
                    ),
                    "difficulty": row.get(
                        "difficulty",
                        "Medium"
                    ),
                    "question_type": row.get(
                        "question_type",
                        ""
                    ),
                    "question": row.get(
                        "question",
                        ""
                    ),
                    "options": options,
                    "correct_answer": row.get(
                        "correct_answer",
                        ""
                    ),
                    "explanation": row.get(
                        "explanation",
                        ""
                    ),
                    "source_text": row.get(
                        "source_text",
                        ""
                    ),
                    "related_concepts": [],
                }
            )

        return {
            "quiz": quiz,
            "questions": questions,
        }

    except Exception:

        return None


def save_attempt_to_db(
    quiz_id,
    score,
    total,
    percentage,
    results
):
    """
    Save quiz submission and every selected answer.
    """

    if not db_available() or not quiz_id:
        return False

    try:

        attempt_response = (
            supabase
            .table("quiz_attempts")
            .insert(
                {
                    "user_id": USER_ID,
                    "quiz_id": quiz_id,
                    "score": score,
                    "total_questions": total,
                    "percentage": round(
                        float(percentage),
                        2
                    ),
                }
            )
            .execute()
        )

        if not attempt_response.data:
            return False

        attempt_id = attempt_response.data[0]["id"]

        question_response = (
            supabase
            .table("questions")
            .select(
                "id, question_number"
            )
            .eq(
                "quiz_id",
                quiz_id
            )
            .order(
                "question_number"
            )
            .execute()
        )

        question_id_map = {}

        if question_response.data:

            for row in question_response.data:

                question_id_map[
                    int(row["question_number"])
                ] = row["id"]

        answer_rows = []

        for result in results:

            question_number = int(
                result["question"]
            )

            answer_rows.append(
                {
                    "attempt_id": attempt_id,
                    "question_id":
                        question_id_map.get(
                            question_number
                        ),
                    "selected_answer":
                        result["selected"],
                    "is_correct":
                        bool(
                            result["result"]
                        ),
                }
            )

        answer_rows = [
            row
            for row in answer_rows
            if row["question_id"] is not None
        ]

        if answer_rows:

            (
                supabase
                .table("quiz_answers")
                .insert(answer_rows)
                .execute()
            )

        # ----------------------------------------------------
        # Topic-level progress
        # ----------------------------------------------------

        topics = {}

        for index, question in enumerate(
            st.session_state.generated_questions,
            start=1
        ):

            topic = question.get(
                "topic",
                "General"
            )

            result = results[index - 1]["result"]

            if topic not in topics:

                topics[topic] = {
                    "correct": 0,
                    "total": 0
                }

            topics[topic]["total"] += 1

            if result:
                topics[topic]["correct"] += 1

        for topic, data in topics.items():

            topic_score = (
                data["correct"]
                /
                data["total"]
                *
                100
                if data["total"]
                else 0
            )

            (
                supabase
                .table("learning_progress")
                .insert(
                    {
                        "user_id": USER_ID,
                        "topic": topic,
                        "score": round(
                            topic_score,
                            2
                        ),
                        "attempts": 1,
                    }
                )
                .execute()
            )

        return True

    except Exception as error:

        st.warning(
            f"Quiz result could not be saved: {error}"
        )

        return False


def load_quiz_history():
    """
    Load all saved quiz attempts.
    """

    if not db_available():
        return []

    try:

        response = (
            supabase
            .table("quiz_attempts")
            .select("*")
            .eq(
                "user_id",
                USER_ID
            )
            .order(
                "submitted_at"
            )
            .execute()
        )

        return response.data or []

    except Exception:

        return []


def clear_database_data():
    """
    Delete this browser's saved data.
    """

    if not db_available():
        return False

    try:

        # Delete answers belonging to this user's attempts
        attempts_response = (
            supabase
            .table("quiz_attempts")
            .select("id")
            .eq(
                "user_id",
                USER_ID
            )
            .execute()
        )

        if attempts_response.data:

            attempt_ids = [
                row["id"]
                for row in attempts_response.data
            ]

            for attempt_id in attempt_ids:

                (
                    supabase
                    .table("quiz_answers")
                    .delete()
                    .eq(
                        "attempt_id",
                        attempt_id
                    )
                    .execute()
                )

        # Delete attempts
        (
            supabase
            .table("quiz_attempts")
            .delete()
            .eq(
                "user_id",
                USER_ID
            )
            .execute()
        )

        # Delete learning materials
        (
            supabase
            .table("learning_materials")
            .delete()
            .eq(
                "user_id",
                USER_ID
            )
            .execute()
        )

        return True

    except Exception:

        return False


# ============================================================
# RESTORE DATA AFTER REFRESH
# ============================================================

if not st.session_state.loaded_from_database:

    st.session_state.loaded_from_database = True

    latest_material = load_latest_material()

    if latest_material:

        st.session_state.learning_material = (
            latest_material.get(
                "content",
                ""
            )
        )

        st.session_state.material_id = (
            latest_material.get(
                "id"
            )
        )

        st.session_state.material_title = (
            latest_material.get(
                "title",
                ""
            )
        )

    latest_quiz = load_latest_quiz()

    if latest_quiz:

        st.session_state.quiz_id = (
            latest_quiz["quiz"]["id"]
        )

        st.session_state.generated_questions = (
            latest_quiz["questions"]
        )

        st.session_state.quiz_total = len(
            latest_quiz["questions"]
        )


# ============================================================
# LOAD HISTORY
# ============================================================

if db_available():

    history = load_quiz_history()

    if history:

        st.session_state.first_scores = [

            {
                "quiz": index,
                "score": float(
                    item.get(
                        "percentage",
                        0
                    )
                )
            }

            for index, item in enumerate(
                history,
                start=1
            )
        ]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 AIStat Learn")

st.sidebar.write(
    "AI-Powered Personalized Learning Platform"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📚 Learning Material",
        "📝 Assessment",
        "📊 Progress",
        "📅 Learning Plan",
        "🔧 System Check",
    ]
)

if db_available():

    st.sidebar.success(
        "🗄️ Database Client Connected"
    )

else:

    st.sidebar.error(
        "🗄️ Database Not Connected"
    )


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.title("🎓 AIStat Learn")

    st.subheader(
        "AI-Powered Personalized Learning Platform"
    )

    st.write(
        """
        AIStat Learn helps students learn from their own study
        material, practice MCQs, analyze performance, identify
        weak topics and follow a personalized learning strategy.
        """
    )

    st.divider()

    st.header("🚀 Learning Journey")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown("## 📚")
        st.subheader("Learn")
        st.write(
            "Upload or paste your learning material."
        )

    with col2:

        st.markdown("## 📝")
        st.subheader("Assess")
        st.write(
            "Generate 5 to 100 MCQs."
        )

    with col3:

        st.markdown("## 📊")
        st.subheader("Analyze")
        st.write(
            "Check your performance."
        )

    with col4:

        st.markdown("## 🤖")
        st.subheader("Improve")
        st.write(
            "Follow a personalized learning plan."
        )

    st.divider()

    st.header("✨ Features")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            ### 📚 Learning Material

            • Upload PDF
            • Upload TXT
            • Upload DOCX
            • Paste notes
            • Preview material
            • Word count
            """
        )

    with col2:

        st.markdown(
            """
            ### 📝 Assessment

            • 5 to 100 questions
            • Submit Quiz
            • Score
            • Question-wise result
            • Explanations
            • Persistent quiz session
            """
        )

    st.divider()

    if db_available():

        st.success(
            "☁️ Your learning data is connected to Supabase."
        )

    else:

        st.warning(
            "⚠️ Supabase is not connected. "
            "Open System Check to see the exact error."
        )

    st.info(
        "👉 Start with 📚 Learning Material."
    )


# ============================================================
# LEARNING MATERIAL
# ============================================================

elif page == "📚 Learning Material":

    st.title("📚 Learning Material")

    st.write(
        "Upload your material or paste your notes."
    )

    st.divider()

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    st.subheader(
        "📤 Upload Learning Material"
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=[
            "pdf",
            "txt",
            "docx"
        ]
    )

    if uploaded_file is not None:

        st.write(
            f"📄 Selected: **{uploaded_file.name}**"
        )

        if st.button(
            "📥 Load Uploaded File",
            use_container_width=True
        ):

            try:

                filename = (
                    uploaded_file.name.lower()
                )

                extracted_text = ""

                if filename.endswith(".txt"):

                    extracted_text = (
                        uploaded_file
                        .read()
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )

                elif filename.endswith(".pdf"):

                    import PyPDF2

                    reader = PyPDF2.PdfReader(
                        uploaded_file
                    )

                    pages = []

                    for pdf_page in reader.pages:

                        page_text = (
                            pdf_page.extract_text()
                        )

                        if page_text:
                            pages.append(
                                page_text
                            )

                    extracted_text = "\n".join(
                        pages
                    )

                elif filename.endswith(".docx"):

                    from docx import Document

                    document = Document(
                        uploaded_file
                    )

                    paragraphs = []

                    for paragraph in document.paragraphs:

                        text = (
                            paragraph.text.strip()
                        )

                        if text:
                            paragraphs.append(
                                text
                            )

                    extracted_text = "\n".join(
                        paragraphs
                    )

                if extracted_text.strip():

                    material_id = (
                        save_material_to_db(
                            uploaded_file.name,
                            extracted_text
                        )
                    )

                    st.session_state.learning_material = (
                        extracted_text
                    )

                    st.session_state.material_id = (
                        material_id
                    )

                    st.session_state.material_title = (
                        uploaded_file.name
                    )

                    # Reset quiz
                    st.session_state.generated_questions = []
                    st.session_state.quiz_id = None
                    st.session_state.assessment_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_results = []

                    st.success(
                        "✅ Learning material loaded successfully!"
                    )

                    if material_id:

                        st.success(
                            "☁️ Learning material saved to database."
                        )

                    else:

                        if db_available():

                            st.warning(
                                "⚠️ Material loaded, "
                                "but it could not be saved to the database."
                            )

                    st.info(
                        f"Word count: "
                        f"{len(extracted_text.split())}"
                    )

                else:

                    st.warning(
                        "⚠️ No readable text found."
                    )

            except Exception as error:

                st.error(
                    f"❌ Error reading file: {error}"
                )

    # --------------------------------------------------------
    # PASTE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Or Paste Learning Material"
    )

    pasted_material = st.text_area(
        "Paste your notes here",
        height=350,
        placeholder=(
            "Paste your learning material here..."
        )
    )

    if st.button(
        "💾 Save Pasted Material",
        use_container_width=True
    ):

        if pasted_material.strip():

            material_id = (
                save_material_to_db(
                    "Pasted Learning Material",
                    pasted_material
                )
            )

            st.session_state.learning_material = (
                pasted_material
            )

            st.session_state.material_id = (
                material_id
            )

            st.session_state.material_title = (
                "Pasted Learning Material"
            )

            st.session_state.generated_questions = []
            st.session_state.quiz_id = None
            st.session_state.assessment_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = []

            st.success(
                "✅ Learning material saved!"
            )

            if material_id:

                st.success(
                    "☁️ Material permanently saved to database."
                )

            elif db_available():

                st.warning(
                    "⚠️ Material was loaded locally, "
                    "but database saving failed."
                )

        else:

            st.warning(
                "⚠️ Please paste some material."
            )

    # --------------------------------------------------------
    # CURRENT MATERIAL
    # --------------------------------------------------------

    if st.session_state.learning_material:

        st.divider()

        st.subheader(
            "📖 Current Learning Material"
        )

        material = (
            st.session_state.learning_material
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "📝 Words",
                len(material.split())
            )

        with col2:

            st.metric(
                "🔤 Characters",
                len(material)
            )

        with st.expander(
            "👁️ Preview Material"
        ):

            st.write(material)

        if st.button(
            "🗑️ Clear Material",
            use_container_width=True
        ):

            if clear_database_data():

                st.success(
                    "☁️ Saved database data cleared."
                )

            st.session_state.learning_material = ""
            st.session_state.material_id = None
            st.session_state.material_title = ""
            st.session_state.generated_questions = []
            st.session_state.quiz_id = None
            st.session_state.assessment_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = []

            st.rerun()


# ============================================================
# ASSESSMENT
# ============================================================

elif page == "📝 Assessment":

    st.title(
        "📝 Intelligent Assessment"
    )

    st.write(
        """
        Generate questions from your learning material,
        answer them and submit the quiz.
        """
    )

    st.divider()

    if not st.session_state.learning_material:

        st.warning(
            """
            ⚠️ No learning material found.

            Go to 📚 Learning Material first.
            """
        )

    else:

        st.success(
            "✅ Learning material is ready."
        )

        st.subheader(
            "🎯 Number of Questions"
        )

        question_options = [
            5,
            10,
            15,
            20,
            30,
            40,
            50,
            60,
            70,
            75,
            100
        ]

        number_of_questions = st.selectbox(
            "Select number of questions",
            question_options,
            index=1
        )

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        if st.button(
            "🚀 Generate Questions",
            use_container_width=True
        ):

            with st.spinner(
                f"Generating {number_of_questions} questions..."
            ):

                try:

                    questions = generate_mcqs(
                        st.session_state.learning_material,
                        number_of_questions
                    )

                    if questions:

                        st.session_state.generated_questions = (
                            questions
                        )

                        st.session_state.assessment_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_score = 0
                        st.session_state.quiz_total = len(
                            questions
                        )
                        st.session_state.quiz_percentage = 0.0
                        st.session_state.quiz_results = []

                        quiz_id = save_quiz_to_db(
                            st.session_state.material_id,
                            questions
                        )

                        st.session_state.quiz_id = quiz_id

                        st.success(
                            f"✅ Generated {len(questions)} questions!"
                        )

                        if quiz_id:

                            st.success(
                                "☁️ Quiz saved. "
                                "It will remain after refresh."
                            )

                        elif db_available():

                            st.warning(
                                "⚠️ Questions were generated, "
                                "but the database could not save the quiz."
                            )

                    else:

                        st.warning(
                            "⚠️ No questions were generated."
                        )

                except Exception as error:

                    st.error(
                        f"❌ Error generating questions: {error}"
                    )

        # ----------------------------------------------------
        # QUESTIONS
        # ----------------------------------------------------

        questions = (
            st.session_state.generated_questions
        )

        if questions:

            st.divider()

            st.header(
                f"📝 Quiz — {len(questions)} Questions"
            )

            if st.session_state.quiz_id:

                st.success(
                    "☁️ This quiz is saved and can be restored after refresh."
                )

            st.info(
                """
                Answer every question and click
                **SUBMIT QUIZ** at the bottom.
                """
            )

            for index, question in enumerate(
                questions
            ):

                question_number = index + 1

                st.markdown(
                    f"### Question {question_number}"
                )

                topic = question.get(
                    "topic",
                    "General"
                )

                difficulty = question.get(
                    "difficulty",
                    "Medium"
                )

                st.caption(
                    f"📚 {topic} | 🎯 {difficulty}"
                )

                st.write(
                    question.get(
                        "question",
                        "Question unavailable"
                    )
                )

                options = question.get(
                    "options",
                    {}
                )

                option_labels = []

                for letter in [
                    "A",
                    "B",
                    "C",
                    "D"
                ]:

                    if letter in options:

                        option_labels.append(
                            f"{letter}. {options[letter]}"
                        )

                if option_labels:

                    previous_answer = (
                        st.session_state
                        .assessment_answers
                        .get(
                            question_number
                        )
                    )

                    previous_index = None

                    if previous_answer in option_labels:

                        previous_index = (
                            option_labels.index(
                                previous_answer
                            )
                        )

                    selected = st.radio(
                        "Choose your answer:",
                        option_labels,
                        key=(
                            f"question_"
                            f"{question_number}"
                        ),
                        index=previous_index
                    )

                    if selected:

                        st.session_state.assessment_answers[
                            question_number
                        ] = selected

                st.divider()

            # ------------------------------------------------
            # SUBMIT
            # ------------------------------------------------

            st.header(
                "🚀 Submit Quiz"
            )

            if st.button(
                "✅ SUBMIT QUIZ",
                use_container_width=True
            ):

                unanswered = []

                for question_number in range(
                    1,
                    len(questions) + 1
                ):

                    answer = (
                        st.session_state
                        .assessment_answers
                        .get(
                            question_number
                        )
                    )

                    if not answer:

                        unanswered.append(
                            question_number
                        )

                if unanswered:

                    st.warning(
                        f"""
                        ⚠️ You have not answered
                        **{len(unanswered)} questions**.

                        Questions:
                        **{', '.join(map(str, unanswered))}**

                        Please answer all questions.
                        """
                    )

                else:

                    score = 0

                    results = []

                    for index, question in enumerate(
                        questions
                    ):

                        question_number = index + 1

                        selected_answer = (
                            st.session_state
                            .assessment_answers
                            .get(
                                question_number
                            )
                        )

                        selected_letter = ""

                        if selected_answer:

                            selected_letter = (
                                selected_answer
                                .split(
                                    ".",
                                    1
                                )[0]
                                .strip()
                                .upper()
                            )

                        correct_letter = str(
                            question.get(
                                "correct_answer",
                                ""
                            )
                        ).strip().upper()

                        is_correct = (
                            selected_letter
                            ==
                            correct_letter
                        )

                        if is_correct:
                            score += 1

                        results.append(
                            {
                                "question":
                                    question_number,
                                "selected":
                                    selected_letter,
                                "correct":
                                    correct_letter,
                                "result":
                                    is_correct
                            }
                        )

                    total = len(questions)

                    percentage = (
                        score
                        /
                        total
                        *
                        100
                        if total
                        else 0
                    )

                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_score = score
                    st.session_state.quiz_total = total
                    st.session_state.quiz_percentage = percentage
                    st.session_state.quiz_results = results

                    if st.session_state.quiz_id:

                        saved = save_attempt_to_db(
                            st.session_state.quiz_id,
                            score,
                            total,
                            percentage,
                            results
                        )

                        if saved:

                            st.success(
                                "☁️ Quiz result saved permanently."
                            )

                    history = load_quiz_history()

                    if history:

                        st.session_state.first_scores = [

                            {
                                "quiz": index,
                                "score": float(
                                    item.get(
                                        "percentage",
                                        0
                                    )
                                )
                            }

                            for index, item in enumerate(
                                history,
                                start=1
                            )
                        ]

                    st.rerun()

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            if st.session_state.quiz_submitted:

                st.divider()

                st.header(
                    "🎉 Quiz Result"
                )

                score = (
                    st.session_state.quiz_score
                )

                total = (
                    st.session_state.quiz_total
                )

                percentage = (
                    st.session_state.quiz_percentage
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "✅ Correct",
                        score
                    )

                with col2:

                    st.metric(
                        "❌ Incorrect",
                        total - score
                    )

                with col3:

                    st.metric(
                        "📊 Score",
                        f"{percentage:.1f}%"
                    )

                if percentage >= 90:

                    st.success(
                        "🏆 Excellent performance!"
                    )

                elif percentage >= 75:

                    st.success(
                        "🎉 Very good performance!"
                    )

                elif percentage >= 50:

                    st.warning(
                        "📚 Good attempt. Revise weak areas."
                    )

                else:

                    st.error(
                        "⚠️ More revision is needed."
                    )

                st.subheader(
                    "📋 Question-wise Result"
                )

                rows = []

                for result in (
                    st.session_state.quiz_results
                ):

                    rows.append(
                        {
                            "Question":
                                result["question"],

                            "Your Answer":
                                result["selected"],

                            "Correct Answer":
                                result["correct"],

                            "Result":
                                (
                                    "✅ Correct"
                                    if result["result"]
                                    else "❌ Incorrect"
                                )
                        }
                    )

                result_df = pd.DataFrame(
                    rows
                )

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                st.header(
                    "📖 Review Answers"
                )

                for index, question in enumerate(
                    questions
                ):

                    question_number = index + 1

                    result = (
                        st.session_state
                        .quiz_results[index]
                    )

                    if result["result"]:

                        st.success(
                            f"Question {question_number} — ✅ Correct"
                        )

                    else:

                        st.error(
                            f"Question {question_number} — ❌ Incorrect"
                        )

                    st.write(
                        question.get(
                            "question",
                            ""
                        )
                    )

                    options = question.get(
                        "options",
                        {}
                    )

                    selected_letter = (
                        result["selected"]
                    )

                    correct_letter = (
                        result["correct"]
                    )

                    if selected_letter:

                        st.write(
                            f"**Your Answer:** "
                            f"{selected_letter}. "
                            f"{options.get(selected_letter, '')}"
                        )

                    st.write(
                        f"**Correct Answer:** "
                        f"{correct_letter}. "
                        f"{options.get(correct_letter, '')}"
                    )

                    explanation = question.get(
                        "explanation",
                        ""
                    )

                    if explanation:

                        with st.expander(
                            "💡 Explanation"
                        ):

                            st.write(
                                explanation
                            )

                    st.divider()


# ============================================================
# PROGRESS
# ============================================================

elif page == "📊 Progress":

    st.title(
        "📊 Progress Analysis"
    )

    st.write(
        "Track your quiz performance and topic scores."
    )

    st.divider()

    history = load_quiz_history()

    if history:

        history_rows = []

        for index, item in enumerate(
            history,
            start=1
        ):

            history_rows.append(
                {
                    "Quiz":
                        index,

                    "Score":
                        f"{float(item.get('percentage', 0)):.1f}%",

                    "Correct":
                        item.get(
                            "score",
                            0
                        ),

                    "Total":
                        item.get(
                            "total_questions",
                            0
                        ),

                    "Submitted":
                        str(
                            item.get(
                                "submitted_at",
                                ""
                            )
                        )[:19]
                }
            )

        history_df = pd.DataFrame(
            history_rows
        )

        st.subheader(
            "📝 Quiz History"
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        chart_df = pd.DataFrame(
            {
                "Quiz":
                    [
                        index
                        for index, _ in enumerate(
                            history,
                            start=1
                        )
                    ],

                "Score":
                    [
                        float(
                            item.get(
                                "percentage",
                                0
                            )
                        )

                        for item in history
                    ]
            }
        )

        chart_df = chart_df.set_index(
            "Quiz"
        )

        st.line_chart(
            chart_df
        )

        latest_score = float(
            history[-1].get(
                "percentage",
                0
            )
        )

        st.metric(
            "Latest Score",
            f"{latest_score:.1f}%"
        )

    elif st.session_state.first_scores:

        history_rows = []

        for item in st.session_state.first_scores:

            history_rows.append(
                {
                    "Quiz":
                        item["quiz"],

                    "Score":
                        f"{item['score']:.1f}%"
                }
            )

        history_df = pd.DataFrame(
            history_rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            """
            No quiz history yet.

            Go to 📝 Assessment and complete a quiz.
            """
        )


# ============================================================
# LEARNING PLAN
# ============================================================

elif page == "📅 Learning Plan":

    st.title(
        "📅 Personalized 5-Day Learning Plan"
    )

    st.write(
        """
        Your learning strategy changes throughout the week
        instead of repeating exactly the same activity every day.
        """
    )

    st.divider()

    st.header(
        "📅 Day 1 — Learn"
    )

    st.info(
        """
        📖 Study the learning material carefully.

        Focus on:
        • Definitions
        • Important concepts
        • Basic principles
        • Key terms

        Goal: Build a strong foundation.
        """
    )

    st.header(
        "📅 Day 2 — Understand"
    )

    st.info(
        """
        🧠 Focus on understanding.

        • Compare related concepts
        • Understand relationships
        • Write short notes
        • Explain concepts in your own words

        Goal: Move beyond memorization.
        """
    )

    st.header(
        "📅 Day 3 — Apply"
    )

    st.info(
        """
        🎯 Apply your knowledge.

        • Solve examples
        • Practice application questions
        • Practice scenario questions
        • Connect theory with real situations

        Goal: Learn how to use the concept.
        """
    )

    st.header(
        "📅 Day 4 — Practice"
    )

    st.info(
        """
        📝 Test yourself.

        • Attempt MCQs
        • Solve difficult questions
        • Review incorrect answers
        • Identify weak areas

        Goal: Improve accuracy.
        """
    )

    st.header(
        "📅 Day 5 — Revise & Reassess"
    )

    st.success(
        """
        🔄 Final revision.

        • Review weak topics
        • Review incorrect questions
        • Revise important notes
        • Take a fresh assessment
        • Compare your score

        Goal: Measure improvement.
        """
    )

    history = load_quiz_history()

    if history:

        st.divider()

        latest_score = float(
            history[-1].get(
                "percentage",
                0
            )
        )

        st.subheader(
            "🤖 Personalized Recommendation"
        )

        if latest_score < 50:

            st.error(
                f"""
                🔴 Your latest score is
                **{latest_score:.1f}%**.

                Spend more time on fundamentals and
                basic concept understanding.
                """
            )

        elif latest_score < 75:

            st.warning(
                f"""
                🟡 Your latest score is
                **{latest_score:.1f}%**.

                Focus on application and scenario-based
                questions.
                """
            )

        else:

            st.success(
                f"""
                🟢 Your latest score is
                **{latest_score:.1f}%**.

                Focus on advanced reasoning and
                higher-order questions.
                """
            )


# ============================================================
# SYSTEM CHECK
# ============================================================

elif page == "🔧 System Check":

    st.title(
        "🔧 System Check"
    )

    st.write(
        "Check whether the project is configured correctly."
    )

    st.divider()

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    project_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    st.subheader(
        "📁 Required Files"
    )

    required_files = [
        "app.py",
        "mcq_generator.py",
        "requirements.txt"
    ]

    for filename in required_files:

        filepath = os.path.join(
            project_folder,
            filename
        )

        if os.path.exists(filepath):

            st.success(
                f"✅ {filename} found."
            )

        else:

            st.warning(
                f"⚠️ {filename} not found locally."
            )

    st.divider()

    # --------------------------------------------------------
    # STREAMLIT SECRETS
    # --------------------------------------------------------

    st.subheader(
        "🔐 Streamlit Secrets"
    )

    try:

        secret_url = st.secrets.get(
            "SUPABASE_URL",
            None
        )

        secret_key = st.secrets.get(
            "SUPABASE_KEY",
            None
        )

        if secret_url:

            st.success(
                "✅ SUPABASE_URL found."
            )

        else:

            st.error(
                "❌ SUPABASE_URL not found."
            )

        if secret_key:

            st.success(
                "✅ SUPABASE_KEY found."
            )

        else:

            st.error(
                "❌ SUPABASE_KEY not found."
            )

    except Exception as error:

        st.error(
            f"❌ Could not read Streamlit secrets: {error}"
        )

    st.divider()

    # --------------------------------------------------------
    # SUPABASE CLIENT
    # --------------------------------------------------------

    st.subheader(
        "🗄️ Supabase Client"
    )

    if db_available():

        st.success(
            "✅ Supabase client created successfully."
        )

        st.write(
            f"Browser User ID: `{USER_ID}`"
        )

    else:

        st.error(
            "❌ Supabase client could not be created."
        )

        if supabase_error:

            st.code(
                supabase_error
            )

    st.divider()

    # --------------------------------------------------------
    # ACTUAL DATABASE TEST
    # --------------------------------------------------------

    st.subheader(
        "🔌 Actual Database Test"
    )

    if st.button(
        "🧪 Test Supabase Database",
        use_container_width=True
    ):

        connected, message = (
            test_database_connection()
        )

        if connected:

            st.success(
                f"✅ {message}"
            )

        else:

            st.error(
                "❌ Database test failed."
            )

            st.code(
                message
            )

            st.info(
                """
                If the error mentions a missing table,
                the Supabase connection itself may be working,
                but the required database tables have not been
                created yet.
                """
            )

    st.divider()

    # --------------------------------------------------------
    # MCQ GENERATOR
    # --------------------------------------------------------

    st.subheader(
        "🐍 MCQ Generator Test"
    )

    try:

        if callable(generate_mcqs):

            st.success(
                "✅ generate_mcqs() is available."
            )

    except Exception as error:

        st.error(
            f"❌ Error: {error}"
        )

    test_material = """
    Value education helps human beings understand their
    basic aspirations. Human beings seek happiness and
    prosperity. Self-exploration helps a person understand
    natural acceptance and develop right understanding.
    Human relationships are based on trust and respect.
    """

    if st.button(
        "🧪 Test Generate 5 Questions",
        use_container_width=True
    ):

        try:

            test_questions = generate_mcqs(
                test_material,
                5
            )

            if test_questions:

                st.success(
                    f"✅ Successfully generated "
                    f"{len(test_questions)} questions."
                )

            else:

                st.warning(
                    "⚠️ No questions generated."
                )

        except Exception as error:

            st.error(
                f"❌ Generator error: {error}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎓 AIStat Learn | "
    "Learn → Understand → Apply → Practice → Reassess"
)
