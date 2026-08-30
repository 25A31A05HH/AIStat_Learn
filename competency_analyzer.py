# ============================================================
# AIStat Learn - Competency Analyzer
# Stage 7
# ============================================================


# ============================================================
# CLASSIFY PERFORMANCE
# ============================================================

def classify_performance(percentage):

    if percentage < 50:
        return "Weak"

    elif percentage < 75:
        return "Developing"

    else:
        return "Strong"


# ============================================================
# GET PRIORITY
# ============================================================

def get_priority(percentage):

    if percentage < 50:
        return "High"

    elif percentage < 75:
        return "Medium"

    else:
        return "Low"


# ============================================================
# GET RECOMMENDATION
# ============================================================

def get_recommendation(
    topic,
    percentage,
    level
):

    if level == "Weak":

        return (
            f"You need to give more attention to "
            f"{topic}. Start by reviewing the basic "
            f"concepts and definitions. After understanding "
            f"the fundamentals, study examples and practice "
            f"questions related to this topic. Regular revision "
            f"will help strengthen your understanding."
        )

    elif level == "Developing":

        return (
            f"You have a developing understanding of "
            f"{topic}. Review the important concepts and "
            f"focus on areas where you made mistakes. "
            f"Practice additional questions and connect the "
            f"concepts with practical examples to improve "
            f"your confidence and accuracy."
        )

    else:

        return (
            f"You have demonstrated strong understanding "
            f"of {topic}. Continue reviewing the important "
            f"concepts and challenge yourself with higher-level "
            f"questions. You can also help reinforce your "
            f"knowledge by applying these concepts to practical "
            f"problems and real-world situations."
        )


# ============================================================
# ANALYZE ONE TOPIC
# ============================================================

def analyze_topic(
    topic,
    correct,
    total
):

    if total == 0:

        percentage = 0

    else:

        percentage = (
            correct / total
        ) * 100


    level = classify_performance(
        percentage
    )


    priority = get_priority(
        percentage
    )


    recommendation = get_recommendation(
        topic,
        percentage,
        level
    )


    return {

        "topic": topic,

        "correct": correct,

        "total": total,

        "percentage": round(
            percentage,
            2
        ),

        "level": level,

        "priority": priority,

        "recommendation": recommendation
    }


# ============================================================
# ANALYZE ASSESSMENT
# ============================================================

def analyze_assessment(
    mcqs,
    answers
):

    topic_data = {}


    # --------------------------------------------------------
    # PROCESS QUESTIONS
    # --------------------------------------------------------

    for index, mcq in enumerate(mcqs):

        topic = mcq.get(
            "topic",
            "General"
        )


        correct_answer = mcq.get(
            "correct_answer",
            ""
        )


        if topic not in topic_data:

            topic_data[topic] = {

                "correct": 0,

                "total": 0
            }


        topic_data[topic]["total"] += 1


        selected_answer = answers.get(
            index,
            ""
        )


        if selected_answer:

            selected_letter = (
                selected_answer[0]
            )


            if (
                selected_letter
                ==
                correct_answer
            ):

                topic_data[topic]["correct"] += 1


    # --------------------------------------------------------
    # CREATE ANALYSIS
    # --------------------------------------------------------

    results = []


    for topic, data in topic_data.items():

        result = analyze_topic(
            topic,
            data["correct"],
            data["total"]
        )


        results.append(
            result
        )


    # --------------------------------------------------------
    # SORT BY PERFORMANCE
    # --------------------------------------------------------

    results.sort(
        key=lambda x: x["percentage"]
    )


    return results


# ============================================================
# GET WEAK TOPICS
# ============================================================

def get_weak_topics(
    analysis
):

    return [

        item

        for item in analysis

        if item["level"] == "Weak"
    ]


# ============================================================
# GET DEVELOPING TOPICS
# ============================================================

def get_developing_topics(
    analysis
):

    return [

        item

        for item in analysis

        if item["level"] == "Developing"
    ]


# ============================================================
# GET STRONG TOPICS
# ============================================================

def get_strong_topics(
    analysis
):

    return [

        item

        for item in analysis

        if item["level"] == "Strong"
    ]


# ============================================================
# GET LEARNING GAPS
# ============================================================

def get_learning_gaps(
    analysis
):

    gaps = []


    for item in analysis:

        if item["level"] == "Weak":

            gaps.append({

                "topic":
                    item["topic"],

                "percentage":
                    item["percentage"],

                "priority":
                    "High",

                "reason":
                    (
                        "The student needs stronger "
                        "understanding of the fundamental "
                        "concepts in this topic."
                    )
            })


        elif item["level"] == "Developing":

            gaps.append({

                "topic":
                    item["topic"],

                "percentage":
                    item["percentage"],

                "priority":
                    "Medium",

                "reason":
                    (
                        "The student understands some "
                        "concepts but needs additional "
                        "practice and revision."
                    )
            })


    return gaps


# ============================================================
# GENERATE 5-DAY PLAN
# ============================================================

def generate_learning_plan(
    analysis
):

    if not analysis:

        return []


    # Weak topics first
    sorted_topics = sorted(
        analysis,
        key=lambda x: x["percentage"]
    )


    plan = []


    for day in range(1, 6):

        # Select topics using rotation
        selected_topics = []


        for i in range(
            min(3, len(sorted_topics))
        ):

            index = (
                (day - 1) * 2 + i
            ) % len(sorted_topics)


            selected_topics.append(
                sorted_topics[index]
            )


        # ----------------------------------------------------
        # DAY ACTIVITY
        # ----------------------------------------------------

        if day == 1:

            activity = (
                "Review fundamental concepts "
                "and definitions."
            )

        elif day == 2:

            activity = (
                "Study examples and important "
                "concepts."
            )

        elif day == 3:

            activity = (
                "Practice questions and identify "
                "mistakes."
            )

        elif day == 4:

            activity = (
                "Apply the concepts to practical "
                "problems."
            )

        else:

            activity = (
                "Revise all important concepts and "
                "prepare for reassessment."
            )


        day_data = {

            "day":
                day,

            "activity":
                activity,

            "topics": [

                {

                    "topic":
                        item["topic"],

                    "percentage":
                        item["percentage"],

                    "level":
                        item["level"],

                    "priority":
                        item["priority"]
                }

                for item
                in selected_topics
            ]
        }


        plan.append(
            day_data
        )


    return plan


# ============================================================
# COMPLETE COMPETENCY REPORT
# ============================================================

def generate_competency_report(
    mcqs,
    answers
):

    analysis = analyze_assessment(
        mcqs,
        answers
    )


    weak_topics = get_weak_topics(
        analysis
    )


    developing_topics = (
        get_developing_topics(
            analysis
        )
    )


    strong_topics = get_strong_topics(
        analysis
    )


    learning_gaps = get_learning_gaps(
        analysis
    )


    learning_plan = generate_learning_plan(
        analysis
    )


    return {

        "analysis":
            analysis,

        "weak_topics":
            weak_topics,

        "developing_topics":
            developing_topics,

        "strong_topics":
            strong_topics,

        "learning_gaps":
            learning_gaps,

        "learning_plan":
            learning_plan
    }