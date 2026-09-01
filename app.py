import os
import uuid
import json
import streamlit as st
import pandas as pd

from mcq_generator import generate_mcqs


# ============================================================
# AIStat Learn
# Step-by-step learning flow with automatic Next navigation
# ============================================================

st.set_page_config(
    page_title="AIStat Learn",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

def get_supabase_client():
    """Create Supabase client using Streamlit secrets."""
    try:
        from supabase import create_client

        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")

        if not url or not key:
            return None

        return create_client(url, key)

    except Exception:
        return None


supabase = get_supabase_client()


# ============================================================
# USER ID
# ============================================================

def get_user_id():
    """
    Keep a browser-level user ID in the URL.
    This allows saved data to be recovered after refresh.
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
            st.session_state.local_user_id = str(uuid.uuid4())

        return st.session_state.local_user_id


USER_ID = get_user_id()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {

    # Material
    "learning_material": "",
    "material_id": None,
    "material_title": "",

    # Quiz
    "generated_questions": [],
    "quiz_id": None,

    # Assessment
    "assessment_answers": {},
    "quiz_submitted": False,
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_percentage": 0.0,
    "quiz_results": [],

    # History
    "first_scores": [],
    "second_scores": [],

    # Database
    "loaded_from_database": False,

    # Current step
    "current_step": 1,

    # Question count
    "number_of_questions": 10,
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# STEP NAVIGATION
# ============================================================

def go_to_step(step_number):
    """
    Move automatically to another step.
    """

    st.session_state.current_step = step_number
    st.rerun()


# ============================================================
# DATABASE STATUS
# ============================================================

def db_available():
    return supabase is not None


# ============================================================
# SAVE MATERIAL
# ============================================================

def save_material_to_db(title, content):

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


# ============================================================
# LOAD MATERIAL
# ============================================================

def load_latest_material():

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

    except Exception:
        pass

    return None


# ============================================================
# SAVE QUIZ
# ============================================================

def save_quiz_to_db(material_id, questions):

    if not db_available():
        return None

    try:

        quiz_response = (
            supabase
            .table("quizzes")
            .insert(
                {
                    "user_id": USER_ID,
                    "material_id": material_id,
                    "question_count": len(questions),
                }
            )
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


# ============================================================
# LOAD QUIZ
# ============================================================

def load_latest_quiz():

    if not db_available():
        return None

    try:

        quiz_response = (
            supabase
            .table("quizzes")
            .select("*")
            .eq("user_id", USER_ID)
            .order("created_at", desc=True)
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
            .eq("quiz_id", quiz["id"])
            .order("question_number")
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
                    "id": f"Q{int(row['question_number']):03d}",
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


# ============================================================
# SAVE QUIZ ATTEMPT
# ============================================================

def save_attempt_to_db(
    quiz_id,
    score,
    total,
    percentage,
    results
):

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

        # Topic progress
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


# ============================================================
# LOAD HISTORY
# ============================================================

def load_quiz_history():

    if not db_available():
        return []

    try:

        response = (
            supabase
            .table("quiz_attempts")
            .select("*")
            .eq("user_id", USER_ID)
            .order("submitted_at")
            .execute()
        )

        return response.data or []

    except Exception:
        return []


# ============================================================
# CLEAR DATABASE DATA
# ============================================================

def clear_database_data():

    if not db_available():
        return False

    try:

        supabase.table(
            "quiz_attempts"
        ).delete().eq(
            "user_id",
            USER_ID
        ).execute()

        supabase.table(
            "learning_materials"
        ).delete().eq(
            "user_id",
            USER_ID
        ).execute()

        return True

    except Exception:
        return False


# ============================================================
# RESTORE DATA
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
            latest_material.get("id")
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


# Show current progress

st.sidebar.subheader("📍 Your Progress")

current_step = st.session_state.current_step

steps = [
    "📚 Learning Material",
    "📝 Generate Questions",
    "✍️ Take Assessment",
    "📊 Progress",
    "📅 Learning Plan",
]

for index, step_name in enumerate(
    steps,
    start=1
):

    if index < current_step:

        st.sidebar.success(
            f"✅ {step_name}"
        )

    elif index == current_step:

        st.sidebar.info(
            f"▶️ {step_name}"
        )

    else:

        st.sidebar.write(
            f"🔒 {step_name}"
        )


st.sidebar.divider()


# Database status

if db_available():

    st.sidebar.success(
        "🗄️ Database Connected"
    )

else:

    st.sidebar.warning(
        "🗄️ Database Not Connected"
    )


# ============================================================
# OPTIONAL SIDEBAR NAVIGATION
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("Navigation")

sidebar_page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "📚 Learning Material",
        "📝 Assessment",
        "📊 Progress",
        "📅 Learning Plan",
        "🔧 System Check",
    ],
    index=(
        1 if current_step == 1
        else 2 if current_step in [2, 3]
        else 3 if current_step == 4
        else 4 if current_step == 5
        else 0
    )
)


# ============================================================
# HOME
# ============================================================

if sidebar_page == "🏠 Home":

    st.title("🎓 AIStat Learn")

    st.subheader(
        "AI-Powered Personalized Learning Platform"
    )

    st.write(
        """
        AIStat Learn helps students learn from their own
        study material, practice MCQs, analyze performance,
        identify weak topics and follow a personalized
        learning strategy.
        """
    )

    st.divider()

    st.header("🚀 Your Learning Journey")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.markdown("## 📚")
        st.write("**Learn**")
        st.caption("Study your material.")

    with col2:

        st.markdown("## 🤖")
        st.write("**Generate**")
        st.caption("Create MCQs.")

    with col3:

        st.markdown("## 📝")
        st.write("**Assess**")
        st.caption("Take the quiz.")

    with col4:

        st.markdown("## 📊")
        st.write("**Analyze**")
        st.caption("Check performance.")

    with col5:

        st.markdown("## 📅")
        st.write("**Improve**")
        st.caption("Follow your plan.")

    st.divider()

    st.info(
        "👉 Start with 📚 Learning Material."
    )


# ============================================================
# STEP 1
# LEARNING MATERIAL
# ============================================================

elif sidebar_page == "📚 Learning Material":

    st.title("📚 Step 1 — Learning Material")

    st.write(
        "Upload your study material or paste your notes."
    )

    st.divider()

    st.subheader("📤 Upload Learning Material")

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

                filename = uploaded_file.name.lower()

                extracted_text = ""

                # TXT
                if filename.endswith(".txt"):

                    extracted_text = (
                        uploaded_file
                        .read()
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )

                # PDF
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

                # DOCX
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
                            "☁️ Material saved to Supabase."
                        )

                    st.info(
                        f"📝 Word count: "
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


    # ========================================================
    # PASTE MATERIAL
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Or Paste Learning Material"
    )

    pasted_material = st.text_area(
        "Paste your notes here",
        height=300,
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
                    "☁️ Material saved to Supabase."
                )

        else:

            st.warning(
                "⚠️ Please paste some material."
            )


    # ========================================================
    # CURRENT MATERIAL
    # ========================================================

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


        # ====================================================
        # NEXT BUTTON
        # ====================================================

        st.divider()

        st.success(
            "🎉 Step 1 completed!"
        )

        st.write(
            "Your learning material is ready."
        )

        if st.button(
            "➡️ NEXT: Generate Questions",
            use_container_width=True,
            type="primary"
        ):

            go_to_step(2)


# ============================================================
# STEP 2
# GENERATE QUESTIONS
# ============================================================

elif sidebar_page == "📝 Assessment":

    st.title(
        "📝 Step 2 — Generate Questions"
    )

    if not st.session_state.learning_material:

        st.warning(
            "⚠️ Please complete Step 1 first."
        )

        if st.button(
            "⬅️ Back to Learning Material",
            use_container_width=True
        ):

            go_to_step(1)

    else:

        st.success(
            "✅ Learning material is ready."
        )

        st.divider()

        st.subheader(
            "🎯 Choose Number of Questions"
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

        st.session_state.number_of_questions = (
            number_of_questions
        )

        st.divider()

        if st.button(
            "🚀 Generate Questions",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                f"Generating "
                f"{number_of_questions} questions..."
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

                        st.session_state.quiz_id = (
                            quiz_id
                        )

                        st.success(
                            f"✅ Generated "
                            f"{len(questions)} questions!"
                        )

                        if quiz_id:

                            st.success(
                                "☁️ Quiz saved to database."
                            )

                    else:

                        st.warning(
                            "⚠️ No questions were generated."
                        )

                except Exception as error:

                    st.error(
                        f"❌ Error generating questions: "
                        f"{error}"
                    )


        # ====================================================
        # QUESTIONS GENERATED
        # ====================================================

        if st.session_state.generated_questions:

            st.divider()

            st.success(
                f"🎉 Step 2 completed! "
                f"{len(st.session_state.generated_questions)} "
                f"questions are ready."
            )

            st.write(
                "Click Next to start your assessment."
            )

            if st.button(
                "➡️ NEXT: Take Assessment",
                use_container_width=True,
                type="primary"
            ):

                go_to_step(3)


# ============================================================
# STEP 3
# TAKE ASSESSMENT
# ============================================================

elif sidebar_page == "✍️ Take Assessment":

    st.title(
        "✍️ Step 3 — Take Assessment"
    )

    questions = (
        st.session_state.generated_questions
    )

    if not questions:

        st.warning(
            "⚠️ No questions available."
        )

        if st.button(
            "⬅️ Back to Generate Questions",
            use_container_width=True
        ):

            go_to_step(2)

    else:

        st.success(
            f"📝 {len(questions)} questions ready."
        )

        st.info(
            "Answer all questions and submit the quiz."
        )

        st.divider()


        # ====================================================
        # QUESTIONS
        # ====================================================

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
                        f"{letter}. "
                        f"{options[letter]}"
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


        # ====================================================
        # SUBMIT
        # ====================================================

        st.header(
            "🚀 Submit Quiz"
        )

        if st.button(
            "✅ SUBMIT QUIZ",
            use_container_width=True,
            type="primary"
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
                    f"⚠️ You have not answered "
                    f"{len(unanswered)} questions."
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

                st.session_state.quiz_score = (
                    score
                )

                st.session_state.quiz_total = (
                    total
                )

                st.session_state.quiz_percentage = (
                    percentage
                )

                st.session_state.quiz_results = (
                    results
                )

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


        # ====================================================
        # RESULT
        # ====================================================

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


            # =================================================
            # QUESTION-WISE RESULT
            # =================================================

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


            # =================================================
            # REVIEW
            # =================================================

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
                        f"Question {question_number} "
                        f"— ✅ Correct"
                    )

                else:

                    st.error(
                        f"Question {question_number} "
                        f"— ❌ Incorrect"
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
                        f"{options.get(
                            selected_letter,
                            ''
                        )}"
                    )

                st.write(
                    f"**Correct Answer:** "
                    f"{correct_letter}. "
                    f"{options.get(
                        correct_letter,
                        ''
                    )}"
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


            # =================================================
            # NEXT TO PROGRESS
            # =================================================

            st.success(
                "🎉 Step 3 completed!"
            )

            if st.button(
                "➡️ NEXT: View Progress",
                use_container_width=True,
                type="primary"
            ):

                go_to_step(4)


# ============================================================
# STEP 4
# PROGRESS
# ============================================================

elif sidebar_page == "📊 Progress":

    st.title(
        "📊 Step 4 — Progress Analysis"
    )

    st.write(
        "Track your quiz performance and improvement."
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
                        f"{float(
                            item.get(
                                'percentage',
                                0
                            )
                        ):.1f}%",
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

        st.subheader(
            "📈 Performance"
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

        if latest_score >= 75:

            st.success(
                "🎉 Your performance is good!"
            )

        elif latest_score >= 50:

            st.warning(
                "📚 Keep practicing and revise weak topics."
            )

        else:

            st.error(
                "⚠️ More revision is recommended."
            )


        # ====================================================
        # NEXT
        # ====================================================

        st.divider()

        st.success(
            "🎉 Step 4 completed!"
        )

        if st.button(
            "➡️ NEXT: Learning Plan",
            use_container_width=True,
            type="primary"
        ):

            go_to_step(5)

    else:

        st.info(
            "No quiz history yet."
        )


# ============================================================
# STEP 5
# LEARNING PLAN
# ============================================================

elif sidebar_page == "📅 Learning Plan":

    st.title(
        "📅 Step 5 — Personalized Learning Plan"
    )

    st.write(
        "Your personalized 5-day learning strategy."
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

        **Goal:** Build a strong foundation.
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

        **Goal:** Move beyond memorization.
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

        **Goal:** Learn how to use the concept.
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

        **Goal:** Improve accuracy.
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

        **Goal:** Measure improvement.
        """
    )


    # ========================================================
    # PERSONALIZED RECOMMENDATION
    # ========================================================

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

                Spend more time on fundamentals
                and basic concept understanding.
                """
            )

        elif latest_score < 75:

            st.warning(
                f"""
                🟡 Your latest score is
                **{latest_score:.1f}%**.

                Focus on application and
                scenario-based questions.
                """
            )

        else:

            st.success(
                f"""
                🟢 Your latest score is
                **{latest_score:.1f}%**.

                Focus on advanced reasoning
                and higher-order questions.
                """
            )


    st.divider()

    st.success(
        "🎉 Congratulations! You completed the AIStat Learn journey."
    )


# ============================================================
# SYSTEM CHECK
# ============================================================

elif sidebar_page == "🔧 System Check":

    st.title(
        "🔧 System Check"
    )

    st.write(
        "Check whether AIStat Learn is configured correctly."
    )

    st.divider()

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

    st.subheader(
        "🗄️ Supabase Connection"
    )

    if db_available():

        st.success(
            "✅ Supabase client connected."
        )

        st.write(
            f"Browser User ID: `{USER_ID}`"
        )

    else:

        st.error(
            """
            ❌ Supabase is not connected.

            Check SUPABASE_URL and SUPABASE_KEY
            in .streamlit/secrets.toml.
            """
        )


    st.divider()

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


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎓 AIStat Learn | "
    "Learn → Generate → Assess → Analyze → Improve"
)
