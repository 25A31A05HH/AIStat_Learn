# ============================================================
# AIStat Learn
# Stage 14 - Smart Adaptive Recommendations
# ============================================================


# ============================================================
# DETERMINE LEARNING LEVEL
# ============================================================

def determine_level(score):

    try:
        score = float(score)
    except:
        score = 0

    if score < 50:
        return "Weak"

    elif score < 75:
        return "Developing"

    else:
        return "Strong"


# ============================================================
# DETERMINE LEARNING STRATEGY
# ============================================================

def determine_strategy(score):

    try:
        score = float(score)
    except:
        score = 0

    if score < 50:

        return {
            "level": "Weak",
            "strategy": "Concept Reinforcement",
            "difficulty": "Easy",
            "activity": "Learn concepts and solve basic questions",
            "revision": "High",
            "practice": "High"
        }

    elif score < 75:

        return {
            "level": "Developing",
            "strategy": "Practice and Application",
            "difficulty": "Medium",
            "activity": "Revise concepts and solve application-based questions",
            "revision": "Medium",
            "practice": "High"
        }

    else:

        return {
            "level": "Strong",
            "strategy": "Advanced Challenge",
            "difficulty": "Hard",
            "activity": "Solve challenging and application-based questions",
            "revision": "Low",
            "practice": "High"
        }


# ============================================================
# TOPIC RECOMMENDATION
# ============================================================

def recommend_for_topic(topic, score):

    strategy = determine_strategy(score)

    return {
        "topic": topic,
        "score": round(float(score), 2),
        "level": strategy["level"],
        "strategy": strategy["strategy"],
        "difficulty": strategy["difficulty"],
        "activity": strategy["activity"],
        "revision": strategy["revision"],
        "practice": strategy["practice"]
    }


# ============================================================
# GENERATE ADAPTIVE PLAN
# ============================================================

def generate_adaptive_plan(topic_scores):

    recommendations = []

    for item in topic_scores:

        if not isinstance(item, dict):
            continue

        topic = item.get(
            "topic",
            "Unknown Topic"
        )

        score = item.get(
            "percentage",
            item.get(
                "score",
                0
            )
        )

        try:
            score = float(score)
        except:
            score = 0

        recommendations.append(
            recommend_for_topic(
                topic,
                score
            )
        )

    return recommendations


# ============================================================
# PRIORITIZE TOPICS
# ============================================================

def prioritize_topics(recommendations):

    return sorted(
        recommendations,
        key=lambda x: x["score"]
    )


# ============================================================
# GENERATE PERSONALIZED MESSAGE
# ============================================================

def generate_topic_message(recommendation):

    topic = recommendation["topic"]

    score = recommendation["score"]

    level = recommendation["level"]

    strategy = recommendation["strategy"]

    difficulty = recommendation["difficulty"]

    activity = recommendation["activity"]


    if level == "Weak":

        return (
            f"{topic} needs focused attention because "
            f"your current score is {score}%. Start by "
            f"reviewing the fundamental concepts and then "
            f"practice easy questions. The recommended "
            f"strategy is {strategy}. Begin with {difficulty} "
            f"questions and gradually increase difficulty "
            f"after your understanding improves."
        )


    elif level == "Developing":

        return (
            f"{topic} is developing well with a score of "
            f"{score}%. You understand some of the concepts, "
            f"but additional practice is needed. The "
            f"recommended strategy is {strategy}. Focus on "
            f"{activity} and use medium-level questions to "
            f"strengthen your understanding."
        )


    else:

        return (
            f"{topic} is a strong area with a score of "
            f"{score}%. Basic revision can be reduced and "
            f"more challenging activities can be introduced. "
            f"The recommended strategy is {strategy}. "
            f"Try {difficulty}-level questions and "
            f"application-based problems to deepen your "
            f"understanding."
        )


# ============================================================
# GENERATE OVERALL RECOMMENDATION
# ============================================================

def generate_overall_recommendation(
    recommendations
):

    if not recommendations:

        return (
            "Complete an assessment to receive "
            "personalized recommendations."
        )


    weak = [
        item
        for item in recommendations
        if item["level"] == "Weak"
    ]


    developing = [
        item
        for item in recommendations
        if item["level"] == "Developing"
    ]


    strong = [
        item
        for item in recommendations
        if item["level"] == "Strong"
    ]


    if weak:

        topics = [
            item["topic"]
            for item in weak
        ]

        return (
            "Your next learning cycle should focus mainly "
            "on the weak topics: "
            + ", ".join(topics)
            + ". Start with concept reinforcement and easy "
              "practice before moving to higher difficulty."
        )


    if developing:

        topics = [
            item["topic"]
            for item in developing
        ]

        return (
            "Your performance is developing. Focus on "
            "practice and application in: "
            + ", ".join(topics)
            + ". Medium-level questions should be used "
              "to strengthen your understanding."
        )


    if strong:

        return (
            "Your performance is strong across the assessed "
            "topics. Move toward challenging questions, "
            "application-based problems, and advanced "
            "learning activities."
        )


    return (
        "Continue regular learning and assessment."
    )


# ============================================================
# GENERATE 5-DAY ADAPTIVE PLAN
# ============================================================

def generate_5_day_adaptive_plan(
    recommendations
):

    prioritized = prioritize_topics(
        recommendations
    )

    plan = {

        "Day 1": [],
        "Day 2": [],
        "Day 3": [],
        "Day 4": [],
        "Day 5": []
    }


    if not prioritized:

        return plan


    # --------------------------------------------------------
    # Weak topics
    # --------------------------------------------------------

    weak = [
        item
        for item in prioritized
        if item["level"] == "Weak"
    ]


    developing = [
        item
        for item in prioritized
        if item["level"] == "Developing"
    ]


    strong = [
        item
        for item in prioritized
        if item["level"] == "Strong"
    ]


    # --------------------------------------------------------
    # Day 1 - Fundamentals
    # --------------------------------------------------------

    plan["Day 1"] = weak[:]


    # --------------------------------------------------------
    # Day 2 - Practice
    # --------------------------------------------------------

    plan["Day 2"] = (
        weak
        + developing[:1]
    )


    # --------------------------------------------------------
    # Day 3 - Application
    # --------------------------------------------------------

    plan["Day 3"] = (
        developing
        + weak[:1]
    )


    # --------------------------------------------------------
    # Day 4 - Mixed Practice
    # --------------------------------------------------------

    plan["Day 4"] = (
        weak
        + developing
        + strong[:1]
    )


    # --------------------------------------------------------
    # Day 5 - Challenge
    # --------------------------------------------------------

    plan["Day 5"] = (
        developing
        + strong
    )


    return plan


# ============================================================
# CREATE RECOMMENDATION REPORT
# ============================================================

def create_recommendation_report(
    topic_scores
):

    recommendations = generate_adaptive_plan(
        topic_scores
    )


    overall = generate_overall_recommendation(
        recommendations
    )


    five_day_plan = generate_5_day_adaptive_plan(
        recommendations
    )


    return {

        "recommendations":
            recommendations,

        "overall":
            overall,

        "five_day_plan":
            five_day_plan
    }


# ============================================================
# TEST MODULE
# ============================================================

if __name__ == "__main__":

    sample_scores = [

        {
            "topic":
                "Value Education",

            "percentage":
                40
        },

        {
            "topic":
                "Human Values",

            "percentage":
                65
        },

        {
            "topic":
                "Relationships",

            "percentage":
                85
        }
    ]


    report = create_recommendation_report(
        sample_scores
    )


    print()
    print("=" * 65)
    print(
        "AIStat Learn - ADAPTIVE RECOMMENDATION REPORT"
    )
    print("=" * 65)


    print()
    print("OVERALL RECOMMENDATION:")
    print(
        report["overall"]
    )


    print()
    print("-" * 65)
    print("TOPIC RECOMMENDATIONS")
    print("-" * 65)


    for item in report[
        "recommendations"
    ]:

        print()

        print(
            "Topic:",
            item["topic"]
        )

        print(
            "Score:",
            item["score"],
            "%"
        )

        print(
            "Level:",
            item["level"]
        )

        print(
            "Strategy:",
            item["strategy"]
        )

        print(
            "Difficulty:",
            item["difficulty"]
        )

        print(
            "Activity:",
            item["activity"]
        )

        print(
            "Recommendation:"
        )

        print(
            generate_topic_message(
                item
            )
        )


    print()
    print("=" * 65)
    print("5-DAY ADAPTIVE PLAN")
    print("=" * 65)


    for day, topics in report[
        "five_day_plan"
    ].items():

        print()
        print(day)

        if topics:

            for topic in topics:

                print(
                    "  •",
                    topic["topic"],
                    "-",
                    topic["strategy"]
                )

        else:

            print(
                "  No topics assigned."
            )


    print()
    print("=" * 65)