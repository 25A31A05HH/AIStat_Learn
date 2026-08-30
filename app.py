
import os
import streamlit as st
import pandas as pd

from mcq_generator import generate_mcqs


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AIStat Learn",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "learning_material" not in st.session_state:
    st.session_state.learning_material = ""

if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

if "assessment_answers" not in st.session_state:
    st.session_state.assessment_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0

if "quiz_percentage" not in st.session_state:
    st.session_state.quiz_percentage = 0

if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

if "first_scores" not in st.session_state:
    st.session_state.first_scores = []

if "second_scores" not in st.session_state:
    st.session_state.second_scores = []


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
        "🔧 System Check"
    ]
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
        AIStat Learn helps students learn from their own
        study material, practice MCQs, analyze performance,
        identify weak topics and follow a personalized
        learning strategy.
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

            • 5 questions  
            • 10 questions  
            • 15 questions  
            • 20 questions  
            • 30 questions  
            • 40 questions  
            • 50 questions  
            • 60 questions  
            • 70 questions  
            • 75 questions  
            • 100 questions  
            • Submit Quiz  
            • Score  
            • Explanations
            """
        )

    st.divider()

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

    st.subheader("📤 Upload Learning Material")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "docx"]
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

                        text = paragraph.text.strip()

                        if text:

                            paragraphs.append(
                                text
                            )

                    extracted_text = "\n".join(
                        paragraphs
                    )

                if extracted_text.strip():

                    st.session_state.learning_material = (
                        extracted_text
                    )

                    st.session_state.generated_questions = []

                    st.session_state.assessment_answers = {}

                    st.session_state.quiz_submitted = False

                    st.success(
                        "✅ Learning material loaded successfully!"
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

    st.subheader("📋 Or Paste Learning Material")

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

            st.session_state.learning_material = (
                pasted_material
            )

            st.session_state.generated_questions = []

            st.session_state.assessment_answers = {}

            st.session_state.quiz_submitted = False

            st.success(
                "✅ Learning material saved!"
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

            st.session_state.learning_material = ""

            st.session_state.generated_questions = []

            st.session_state.assessment_answers = {}

            st.session_state.quiz_submitted = False

            st.rerun()


# ============================================================
# ASSESSMENT
# ============================================================

elif page == "📝 Assessment":

    st.title("📝 Intelligent Assessment")

    st.write(
        """
        Generate questions from your learning material,
        answer them and submit the quiz.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # MATERIAL CHECK
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # QUESTION COUNT
        # ----------------------------------------------------

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

                        st.session_state.quiz_percentage = 0

                        st.session_state.quiz_results = []

                        st.success(
                            f"✅ Generated {len(questions)} questions!"
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

                    selected = st.radio(
                        "Choose your answer:",
                        option_labels,
                        key=f"question_{question_number}",
                        index=None
                    )

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
                    )

                    st.session_state.quiz_submitted = True

                    st.session_state.quiz_score = score

                    st.session_state.quiz_total = total

                    st.session_state.quiz_percentage = (
                        percentage
                    )

                    st.session_state.quiz_results = results

                    # Store score for progress
                    st.session_state.first_scores.append(
                        {
                            "quiz":
                                len(
                                    st.session_state
                                    .first_scores
                                ) + 1,

                            "score":
                                percentage
                        }
                    )

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

                # ------------------------------------------------
                # RESULT TABLE
                # ------------------------------------------------

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

                # ------------------------------------------------
                # REVIEW
                # ------------------------------------------------

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

                    selected_letter = result[
                        "selected"
                    ]

                    correct_letter = result[
                        "correct"
                    ]

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

    st.title("📊 Progress Analysis")

    st.write(
        "Track your quiz performance and topic scores."
    )

    st.divider()

    if st.session_state.first_scores:

        st.subheader(
            "📝 Quiz History"
        )

        history_rows = []

        for item in (
            st.session_state.first_scores
        ):

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

        chart_df = pd.DataFrame(
            {
                "Quiz":
                    [
                        item["quiz"]
                        for item
                        in st.session_state.first_scores
                    ],

                "Score":
                    [
                        item["score"]
                        for item
                        in st.session_state.first_scores
                    ]
            }
        )

        chart_df = chart_df.set_index(
            "Quiz"
        )

        st.line_chart(
            chart_df
        )

        latest_score = (
            st.session_state
            .first_scores[-1]["score"]
        )

        st.metric(
            "Latest Score",
            f"{latest_score:.1f}%"
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

    # DAY 1
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

    # DAY 2
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

    # DAY 3
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

    # DAY 4
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

    # DAY 5
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

    # SCORE BASED ADVICE
    if st.session_state.first_scores:

        st.divider()

        latest_score = (
            st.session_state
            .first_scores[-1]["score"]
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

    st.title("🔧 System Check")

    st.write(
        "Check whether the project is configured correctly."
    )

    st.divider()

    project_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    st.subheader(
        "📁 Required Files"
    )

    required_files = [
        "app.py",
        "mcq_generator.py"
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

            st.error(
                f"❌ {filename} not found."
            )

    # --------------------------------------------------------
    # IMPORT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TEST QUESTIONS
    # --------------------------------------------------------

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

