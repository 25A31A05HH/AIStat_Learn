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
# CSS
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

    "material_saved": False,

    "last_uploaded_file": "",

    "quiz_history": []
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

    if (
        "SUPABASE_URL" in st.secrets
        and
        "SUPABASE_KEY" in st.secrets
    ):

        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

        db_status = "Connected"

    else:

        db_status = "Secrets not found"


except Exception as e:

    db_status = f"Connection error: {e}"


# =========================================================
# NAVIGATION
# =========================================================

def go_to_step(step):

    st.session_state.current_step = step

    st.rerun()


# =========================================================
# TEXT FUNCTIONS
# =========================================================

def clean_text(value):

    if value is None:

        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


# =========================================================
# QUESTION TEXT
# =========================================================

def get_question_text(question):

    if isinstance(question, dict):

        for key in [
            "question",
            "question_text",
            "text"
        ]:

            if key in question:

                return clean_text(
                    question[key]
                )

    return clean_text(question)


# =========================================================
# TOPIC
# =========================================================

def get_topic(question):

    if isinstance(question, dict):

        for key in [
            "topic",
            "subject",
            "category"
        ]:

            if key in question:

                return clean_text(
                    question[key]
                )

    return "General"


# =========================================================
# CONCEPT
# =========================================================

def get_concept(question):

    if isinstance(question, dict):

        for key in [
            "concept",
            "subtopic"
        ]:

            if key in question:

                return clean_text(
                    question[key]
                )

    return get_topic(question)


# =========================================================
# GET OPTIONS
# =========================================================

def get_options(question):

    if not isinstance(question, dict):

        return []

    raw_options = None

    # Try different possible names
    for key in [
        "options",
        "choices",
        "answers"
    ]:

        if key in question:

            raw_options = question[key]

            break

    if raw_options is None:

        return []

    # ---------------------------------------------
    # Dictionary
    # ---------------------------------------------

    if isinstance(raw_options, dict):

        options = []

        for letter in [
            "A",
            "B",
            "C",
            "D"
        ]:

            if letter in raw_options:

                options.append(
                    clean_text(
                        raw_options[letter]
                    )
                )

        if options:

            return options

        return [
            clean_text(value)
            for value in raw_options.values()
        ]

    # ---------------------------------------------
    # List
    # ---------------------------------------------

    if isinstance(
        raw_options,
        (list, tuple)
    ):

        return [
            clean_text(option)
            for option in raw_options
        ]

    return []


# =========================================================
# GET CORRECT ANSWER
# =========================================================

def get_correct_raw(question):

    if not isinstance(question, dict):

        return ""

    for key in [
        "correct_answer",
        "correct_option",
        "answer",
        "correct"
    ]:

        if key in question:

            return clean_text(
                question[key]
            )

    return ""


def get_correct_option(question):

    correct = get_correct_raw(
        question
    )

    options = get_options(
        question
    )

    if not correct:

        return ""

    # ---------------------------------------------
    # A / B / C / D
    # ---------------------------------------------

    if correct.upper() in [
        "A",
        "B",
        "C",
        "D"
    ]:

        index = (
            ord(correct.upper())
            -
            ord("A")
        )

        if index < len(options):

            return options[index]

    # ---------------------------------------------
    # "A. Queue"
    # ---------------------------------------------

    for i, option in enumerate(
        options
    ):

        letter = chr(
            65 + i
        )

        if correct.upper().startswith(
            letter + "."
        ):

            return option

        if correct.lower() == option.lower():

            return option

    return correct


# =========================================================
# GET EXPLANATION
# =========================================================

def get_explanation(question):

    if not isinstance(question, dict):

        return ""

    for key in [
        "explanation",
        "answer_explanation",
        "reason"
    ]:

        if key in question:

            return clean_text(
                question[key]
            )

    return ""


# =========================================================
# OPTION FEEDBACK
# =========================================================

def get_option_feedback(
    question,
    option
):

    if not isinstance(question, dict):

        return ""

    feedback = question.get(
        "option_feedback",
        {}
    )

    if isinstance(
        feedback,
        dict
    ):

        if option in feedback:

            return clean_text(
                feedback[option]
            )

        for key, value in feedback.items():

            if clean_text(
                key
            ).lower() == option.lower():

                return clean_text(
                    value
                )

    return ""


# =========================================================
# WRONG OPTION EXPLANATION
# =========================================================

def explain_wrong_option(
    question,
    option
):

    correct = get_correct_option(
        question
    )

    topic = get_topic(
        question
    )

    question_text = get_question_text(
        question
    )

    if option.lower() == correct.lower():

        return "This is the correct answer."

    # Queue / FIFO
    if (
        "queue" in correct.lower()
        or
        "fifo" in question_text.lower()
    ):

        if "stack" in option.lower():

            return (
                "A Stack follows LIFO "
                "(Last In, First Out), "
                "not FIFO."
            )

        if "tree" in option.lower():

            return (
                "A Tree is mainly used to represent "
                "hierarchical relationships."
            )

        if "graph" in option.lower():

            return (
                "A Graph represents relationships "
                "between vertices and edges."
            )

    # Stack / LIFO
    if (
        "stack" in correct.lower()
        or
        "lifo" in question_text.lower()
    ):

        if "queue" in option.lower():

            return (
                "A Queue follows FIFO, whereas "
                "a Stack follows LIFO."
            )

    return (
        f"This option is incorrect because "
        f"it does not match the concept "
        f"being tested in {topic}. "
        f"The correct answer is "
        f"{correct}."
    )


# =========================================================
# TOPIC EXPLANATION
# =========================================================

def topic_explanation(topic):

    topic_lower = topic.lower()

    if "queue" in topic_lower:

        return """
### 📚 Queue

A **Queue** is a linear data structure that follows:

**FIFO — First In, First Out**

Think about a ticket counter.

The person who comes first gets served first.

#### Main operations

- **Enqueue** → Add an element
- **Dequeue** → Remove an element
- **Front / Peek** → View the first element

💡 **Remember: Queue = FIFO**
"""

    if "stack" in topic_lower:

        return """
### 📚 Stack

A **Stack** is a linear data structure that follows:

**LIFO — Last In, First Out**

Think about a stack of plates.

The last plate placed on top is removed first.

#### Main operations

- **Push** → Add an element
- **Pop** → Remove an element
- **Peek** → View the top element

💡 **Remember: Stack = LIFO**
"""

    if "array" in topic_lower:

        return """
### 📚 Array

An **Array** stores elements in an ordered collection.

Each element can be accessed using an index.

Example:

`[10, 20, 30, 40]`

The first element is at index `0`.

💡 **Remember: Array = Indexed collection**
"""

    if "linked list" in topic_lower:

        return """
### 📚 Linked List

A **Linked List** consists of nodes.

Each node contains:

- Data
- A link/reference to another node

The nodes are connected to form a sequence.

💡 **Remember: Linked List = Connected Nodes**
"""

    if "python" in topic_lower:

        return """
### 📚 Python

Python is a high-level programming language.

It is widely used for:

- Web development
- Data analysis
- Artificial intelligence
- Machine learning
- Automation

Python is popular because its syntax is simple and readable.

💡 **Remember: Python = Simple + Powerful**
"""

    if "data structure" in topic_lower:

        return """
### 📚 Data Structures

A data structure is a way of organizing and storing data.

Common data structures include:

- Arrays
- Linked Lists
- Stacks
- Queues
- Trees
- Graphs

Different data structures are useful for different problems.

💡 Choose a data structure based on the required operations.
"""

    return f"""
### 📚 {topic}

This question is related to **{topic}**.

Review the definition, properties, operations,
and applications of this topic.
"""


# =========================================================
# PERFORMANCE
# =========================================================

def performance_level(
    percentage
):

    if percentage >= 90:

        return "Excellent 🌟"

    if percentage >= 75:

        return "Very Good 👍"

    if percentage >= 60:

        return "Good 🙂"

    if percentage >= 40:

        return "Needs Improvement 📚"

    return "Needs More Practice 💪"


# =========================================================
# DATABASE — MATERIAL
# =========================================================

def save_material_to_db(
    name,
    content
):

    if supabase is None:

        return None

    try:

        result = (
            supabase
            .table("learning_materials")
            .insert(
                {
                    "user_id":
                        st.session_state.user_id,

                    "material_name":
                        name,

                    "content":
                        content
                }
            )
            .execute()
        )

        if result.data:

            return result.data[0].get(
                "id"
            )

    except Exception as e:

        st.warning(
            f"Material could not be saved: {e}"
        )

    return None


# =========================================================
# DATABASE — QUIZ
# =========================================================

def save_quiz_to_db(
    questions
):

    if supabase is None:

        return None

    try:

        result = (
            supabase
            .table("quizzes")
            .insert(
                {
                    "user_id":
                        st.session_state.user_id,

                    "question_count":
                        len(questions)
                }
            )
            .execute()
        )

        if result.data:

            return result.data[0].get(
                "id"
            )

    except Exception as e:

        st.warning(
            f"Quiz could not be saved: {e}"
        )

    return None


# =========================================================
# DATABASE — ATTEMPT
# =========================================================

def save_attempt_to_db(
    quiz_id,
    score,
    total,
    percentage
):

    if supabase is None:

        return

    try:

        (
            supabase
            .table("quiz_attempts")
            .insert(
                {
                    "user_id":
                        st.session_state.user_id,

                    "quiz_id":
                        quiz_id,

                    "score":
                        score,

                    "total_questions":
                        total,

                    "percentage":
                        percentage
                }
            )
            .execute()
        )

    except Exception as e:

        st.warning(
            f"Attempt could not be saved: {e}"
        )


# =========================================================
# DATABASE — HISTORY
# =========================================================

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

st.sidebar.title(
    "🎓 AIStat Learn"
)

st.sidebar.caption(
    "AI-Powered Personalized Learning Platform"
)

st.sidebar.divider()

st.sidebar.subheader(
    "📌 Learning Progress"
)

steps = [
    "1️⃣ Learning Material",
    "2️⃣ Generate Questions",
    "3️⃣ Take Assessment",
    "4️⃣ Progress",
    "5️⃣ Learning Plan"
]

for i, step_name in enumerate(
    steps,
    start=1
):

    if (
        i
        <
        st.session_state.current_step
    ):

        st.sidebar.success(
            step_name
        )

    elif (
        i
        ==
        st.session_state.current_step
    ):

        st.sidebar.info(
            step_name
        )

    else:

        st.sidebar.write(
            step_name
        )


st.sidebar.divider()

st.sidebar.subheader(
    "Navigation"
)

navigation = [
    "🏠 Home",
    "📚 Learning Material",
    "📝 Generate Questions",
    "✍️ Take Assessment",
    "📊 Progress",
    "📅 Learning Plan",
    "🔧 System Check"
]


if st.session_state.current_step == 1:

    default_page = "📚 Learning Material"

elif st.session_state.current_step == 2:

    default_page = "📝 Generate Questions"

elif st.session_state.current_step == 3:

    default_page = "✍️ Take Assessment"

elif st.session_state.current_step == 4:

    default_page = "📊 Progress"

elif st.session_state.current_step == 5:

    default_page = "📅 Learning Plan"

else:

    default_page = "🏠 Home"


sidebar_page = st.sidebar.radio(
    "Go to",
    navigation,
    index=navigation.index(
        default_page
    )
)


st.sidebar.divider()

if db_status == "Connected":

    st.sidebar.success(
        "🗄️ Database Connected"
    )

else:

    st.sidebar.warning(
        f"🗄️ Database: {db_status}"
    )


# =========================================================
# HOME
# =========================================================

if sidebar_page == "🏠 Home":

    st.markdown(
        '<div class="main-title">'
        '🎓 AIStat Learn'
        '</div>',
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

📚 Upload learning material

🤖 Generate practice questions

✍️ Take assessments

💡 Understand correct and incorrect answers

📊 Track learning progress

📅 Get personalized recommendations
"""
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Questions Generated",
            len(
                st.session_state.questions
            )
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

    st.title(
        "📚 Step 1 — Learning Material"
    )

    st.write(
        "Upload a PDF or paste your learning material."
    )

    # =====================================================
    # PDF UPLOAD
    # =====================================================

    st.subheader(
        "📤 Upload PDF"
    )

    uploaded_file = st.file_uploader(
        "Choose your learning material",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if PdfReader is None:

            st.error(
                "❌ PyPDF2 is not installed."
            )

            st.code(
                "pip install PyPDF2"
            )

        else:

            if (
                st.session_state.last_uploaded_file
                != uploaded_file.name
            ):

                try:

                    reader = PdfReader(
                        uploaded_file
                    )

                    extracted_text = ""

                    for page in reader.pages:

                        page_text = (
                            page.extract_text()
                            or ""
                        )

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

                        st.session_state.last_uploaded_file = (
                            uploaded_file.name
                        )

                        st.success(
                            "✅ PDF uploaded successfully!"
                        )

                    else:

                        st.error(
                            "❌ No text could be extracted."
                        )

                        st.info(
                            "If the PDF is scanned, "
                            "paste the text manually."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Error reading PDF: {e}"
                    )

    # =====================================================
    # MATERIAL EDITOR
    # =====================================================

    st.divider()

    st.subheader(
        "✍️ Learning Material"
    )

    material_name = st.text_input(
        "Material Name",
        value=st.session_state.material_name,
        placeholder="Example: Python Basics"
    )

    material_text = st.text_area(
        "Material Text",
        value=st.session_state.material_text,
        height=350,
        placeholder="Paste your learning material here..."
    )

    st.caption(
        f"Word count: {len(material_text.split())}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Material",
            use_container_width=True
        ):

            if not material_text.strip():

                st.error(
                    "Please upload a PDF or enter text."
                )

            elif len(
                material_text.split()
            ) < 5:

                st.error(
                    "Please provide more learning material."
                )

            else:

                st.session_state.material_text = (
                    material_text.strip()
                )

                st.session_state.material_name = (
                    material_name.strip()
                    or
                    "Learning Material"
                )

                st.session_state.material_saved = True

                material_id = save_material_to_db(
                    st.session_state.material_name,
                    st.session_state.material_text
                )

                st.success(
                    "✅ Learning material saved!"
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
                    "Please upload a PDF or enter text."
                )

            elif len(
                material_text.split()
            ) < 5:

                st.error(
                    "Please provide more learning material."
                )

            else:

                st.session_state.material_text = (
                    material_text.strip()
                )

                st.session_state.material_name = (
                    material_name.strip()
                    or
                    "Learning Material"
                )

                go_to_step(2)


# =========================================================
# STEP 2 — GENERATE QUESTIONS
# =========================================================

elif sidebar_page == "📝 Generate Questions":

    st.title(
        "📝 Step 2 — Generate Questions"
    )

    if not st.session_state.material_text:

        st.warning(
            "⚠️ Please upload learning material first."
        )

        if st.button(
            "📚 Go to Learning Material"
        ):

            go_to_step(1)

    else:

        st.success(
            f"📚 Material: "
            f"{st.session_state.material_name}"
        )

        st.write(
            f"Words: "
            f"{len(st.session_state.material_text.split())}"
        )

        st.divider()

        question_count = st.slider(
            "Number of Questions",
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

                        st.session_state.questions = (
                            questions
                        )

                        st.session_state.total_questions = (
                            len(questions)
                        )

                        st.session_state.assessment_answers = {}

                        st.session_state.quiz_submitted = False

                        quiz_id = save_quiz_to_db(
                            questions
                        )

                        st.session_state.quiz_id = (
                            quiz_id
                        )

                        st.success(
                            f"✅ {len(questions)} questions generated!"
                        )

                    else:

                        st.error(
                            "❌ No questions were generated."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Error generating questions: {e}"
                    )

        # =================================================
        # QUESTION PREVIEW
        # =================================================

        if st.session_state.questions:

            st.divider()

            st.subheader(
                "👀 Question Preview"
            )

            for i, question in enumerate(
                st.session_state.questions,
                start=1
            ):

                st.markdown(
                    f"### Q{i}. "
                    f"{get_question_text(question)}"
                )

                options = get_options(
                    question
                )

                if options:

                    for j, option in enumerate(
                        options
                    ):

                        st.write(
                            f"**{chr(65+j)}.** {option}"
                        )

                else:

                    st.error(
                        "⚠️ Options are missing."
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

    st.title(
        "✍️ Step 3 — Take Assessment"
    )

    if not st.session_state.questions:

        st.warning(
            "⚠️ No questions available."
        )

        if st.button(
            "📝 Generate Questions"
        ):

            go_to_step(2)

    # =====================================================
    # BEFORE SUBMISSION
    # =====================================================

    elif not st.session_state.quiz_submitted:

        st.info(
            f"📝 Answer all "
            f"{len(st.session_state.questions)} questions."
        )

        st.divider()

        for i, question in enumerate(
            st.session_state.questions
        ):

            question_text = get_question_text(
                question
            )

            st.markdown(
                f"### Q{i + 1}. {question_text}"
            )

            options = get_options(
                question
            )

            # =================================================
            # CLICKABLE OPTIONS
            # =================================================

            if options:

                # Create A/B/C/D display
                display_options = []

                for j, option in enumerate(
                    options
                ):

                    letter = chr(
                        65 + j
                    )

                    display_options.append(
                        f"{letter}. {option}"
                    )

                selected = st.radio(
                    "Select one answer:",
                    display_options,
                    key=f"question_answer_{i}",
                    index=None
                )

                # Save selected option
                if selected:

                    selected_index = (
                        display_options.index(
                            selected
                        )
                    )

                    st.session_state.assessment_answers[
                        i
                    ] = options[
                        selected_index
                    ]

            else:

                st.error(
                    "❌ No options available for this question."
                )

            st.divider()

        # =====================================================
        # SUBMIT BUTTON
        # =====================================================

        if st.button(
            "✅ Submit Assessment",
            use_container_width=True
        ):

            unanswered = []

            for i in range(
                len(
                    st.session_state.questions
                )
            ):

                answer = (
                    st.session_state
                    .assessment_answers
                    .get(i)
                )

                if not answer:

                    unanswered.append(
                        i + 1
                    )

            if unanswered:

                st.error(
                    "⚠️ Please answer all questions."
                )

                st.write(
                    "Unanswered questions:",
                    ", ".join(
                        map(
                            str,
                            unanswered
                        )
                    )
                )

            else:

                score = 0

                for i, question in enumerate(
                    st.session_state.questions
                ):

                    user_answer = (
                        st.session_state
                        .assessment_answers[i]
                    )

                    correct_answer = (
                        get_correct_option(
                            question
                        )
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

                st.session_state.score = (
                    score
                )

                st.session_state.total_questions = (
                    total
                )

                st.session_state.percentage = (
                    percentage
                )

                st.session_state.quiz_submitted = (
                    True
                )

                save_attempt_to_db(
                    st.session_state.quiz_id,
                    score,
                    total,
                    percentage
                )

                st.rerun()

    # =====================================================
    # AFTER SUBMISSION
    # =====================================================

    else:

        st.success(
            "🎉 Assessment Submitted Successfully!"
        )

        score = st.session_state.score

        total = st.session_state.total_questions

        percentage = st.session_state.percentage

        st.divider()

        # =================================================
        # SCORE
        # =================================================

        st.subheader(
            "📊 Your Result"
        )

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

            st.metric(
                "Correct",
                score
            )

        with col4:

            st.metric(
                "Incorrect",
                total - score
            )

        st.info(
            f"Performance: "
            f"**{performance_level(percentage)}**"
        )

        st.divider()

        # =================================================
        # DETAILED REVIEW
        # =================================================

        st.subheader(
            "💡 Detailed Question Review"
        )

        topic_results = {}

        for i, question in enumerate(
            st.session_state.questions
        ):

            question_text = get_question_text(
                question
            )

            topic = get_topic(
                question
            )

            concept = get_concept(
                question
            )

            options = get_options(
                question
            )

            correct_answer = get_correct_option(
                question
            )

            user_answer = (
                st.session_state
                .assessment_answers
                .get(
                    i,
                    "Not answered"
                )
            )

            is_correct = (
                user_answer.strip().lower()
                ==
                correct_answer.strip().lower()
            )

            # Topic tracking
            if topic not in topic_results:

                topic_results[topic] = {
                    "correct": 0,
                    "total": 0
                }

            topic_results[topic]["total"] += 1

            if is_correct:

                topic_results[topic]["correct"] += 1

                st.success(
                    f"### Q{i+1}. ✅ Correct"
                )

            else:

                st.error(
                    f"### Q{i+1}. ❌ Incorrect"
                )

            st.write(
                f"**Question:** {question_text}"
            )

            st.write(
                f"**Topic:** {topic}"
            )

            st.write(
                f"**Concept:** {concept}"
            )

            st.write(
                f"**Your Answer:** {user_answer}"
            )

            st.write(
                f"**Correct Answer:** "
                f"{correct_answer}"
            )

            # =================================================
            # WHY CORRECT?
            # =================================================

            st.markdown(
                "#### ✅ Why is this answer correct?"
            )

            explanation = get_explanation(
                question
            )

            if explanation:

                st.info(
                    explanation
                )

            else:

                st.info(
                    f"**{correct_answer}** is correct "
                    f"because it matches the concept "
                    f"being tested in **{topic}**."
                )

            # =================================================
            # WHY WRONG?
            # =================================================

            st.markdown(
                "#### ❌ Why are the other options incorrect?"
            )

            for option in options:

                if (
                    option.lower()
                    ==
                    correct_answer.lower()
                ):

                    continue

                feedback = get_option_feedback(
                    question,
                    option
                )

                if not feedback:

                    feedback = explain_wrong_option(
                        question,
                        option
                    )

                st.write(
                    f"❌ **{option}** — "
                    f"{feedback}"
                )

            # =================================================
            # TOPIC EXPLANATION
            # =================================================

            with st.expander(
                f"📚 Learn More About: {topic}"
            ):

                st.markdown(
                    topic_explanation(
                        topic
                    )
                )

            st.divider()

        # =================================================
        # TOPIC PERFORMANCE
        # =================================================

        st.subheader(
            "📌 Topic-wise Performance"
        )

        topic_rows = []

        for topic, result in (
            topic_results.items()
        ):

            correct = result["correct"]

            topic_total = result["total"]

            topic_percentage = (
                correct
                /
                topic_total
                *
                100
                if topic_total
                else 0
            )

            topic_rows.append(
                {
                    "Topic": topic,

                    "Correct": correct,

                    "Total": topic_total,

                    "Performance":
                        f"{topic_percentage:.1f}%"
                }
            )

        if topic_rows:

            st.dataframe(
                pd.DataFrame(
                    topic_rows
                ),
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # WEAK TOPICS
        # =================================================

        st.subheader(
            "📌 Areas to Improve"
        )

        weak_topics = []

        for topic, result in (
            topic_results.items()
        ):

            topic_percentage = (
                result["correct"]
                /
                result["total"]
                *
                100
                if result["total"]
                else 0
            )

            if topic_percentage < 60:

                weak_topics.append(
                    topic
                )

        if weak_topics:

            st.warning(
                "📚 Revise these topics: "
                +
                ", ".join(
                    weak_topics
                )
            )

        else:

            st.success(
                "🌟 Great job! You performed well across the tested topics."
            )

        st.divider()

        # =================================================
        # NEXT ACTIONS
        # =================================================

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

                go_to_step(4)


# =========================================================
# STEP 4 — PROGRESS
# =========================================================

elif sidebar_page == "📊 Progress":

    st.title(
        "📊 Step 4 — Progress"
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
                performance_level(
                    st.session_state.percentage
                )
            )

    else:

        st.info(
            "Take an assessment to see your progress."
        )

    st.divider()

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
                        item.get(
                            "score",
                            "-"
                        ),

                    "Total":
                        item.get(
                            "total_questions",
                            "-"
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

    st.title(
        "📅 Step 5 — Personalized Learning Plan"
    )

    percentage = (
        st.session_state.percentage
    )

    if percentage >= 80:

        st.success(
            """
### 🌟 Strong Performance

Recommended plan:

1. Review concepts briefly.
2. Solve advanced questions.
3. Move to the next topic.
4. Take another assessment.
"""
        )

    elif percentage >= 60:

        st.info(
            """
### 👍 Good Progress

Recommended plan:

1. Review incorrect answers.
2. Practice medium-level questions.
3. Revise important concepts.
4. Retake the assessment.
"""
        )

    else:

        st.warning(
            """
### 📚 More Practice Recommended

Recommended plan:

1. Read the learning material again.
2. Focus on weak topics.
3. Practice basic questions.
4. Review explanations carefully.
5. Retake the assessment.
"""
        )

    st.divider()

    if st.session_state.questions:

        st.subheader(
            "📌 Topics Covered"
        )

        topics = []

        for question in (
            st.session_state.questions
        ):

            topic = get_topic(
                question
            )

            if topic not in topics:

                topics.append(
                    topic
                )

        for topic in topics:

            st.write(
                f"📖 **{topic}**"
            )

    st.divider()

    if st.button(
        "📚 Back to Learning Material",
        use_container_width=True
    ):

        go_to_step(1)


# =========================================================
# SYSTEM CHECK
# =========================================================

elif sidebar_page == "🔧 System Check":

    st.title(
        "🔧 System Check"
    )

    # Streamlit
    st.success(
        "✅ Streamlit is working"
    )

    # PyPDF2
    if PdfReader:

        st.success(
            "✅ PyPDF2 is installed"
        )

    else:

        st.error(
            "❌ PyPDF2 is not installed"
        )

        st.code(
            "pip install PyPDF2"
        )

    # MCQ generator
    try:

        test_questions = generate_mcqs(
            """
            Python is a programming language.
            Python supports variables, loops,
            functions and lists.
            """,
            2
        )

        if test_questions:

            st.success(
                f"✅ MCQ Generator is working "
                f"({len(test_questions)} questions)"
            )

            with st.expander(
                "🔍 View Generated Question Data"
            ):

                for question in test_questions:

                    st.json(
                        question
                    )

        else:

            st.error(
                "❌ MCQ Generator returned no questions."
            )

    except Exception as e:

        st.error(
            f"❌ MCQ Generator error: {e}"
        )

    # Supabase
    if supabase:

        st.success(
            "✅ Supabase connection initialized"
        )

    else:

        st.warning(
            "⚠️ Supabase is not connected"
        )

    st.divider()

    st.subheader(
        "📊 Current Application State"
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
        f"**Score:** "
        f"{st.session_state.score}/"
        f"{st.session_state.total_questions}"
    )
