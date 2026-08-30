# ============================================================
# AIStat Learn - Progress Tracker
# Stage 10
# Topic-wise Progress Tracking
# ============================================================

from collections import defaultdict


# ============================================================
# CALCULATE TOPIC PERFORMANCE
# ============================================================

def calculate_topic_performance(assessments):

    topic_data = defaultdict(list)

    for assessment in assessments:

        for result in assessment.get(
            "topic_results",
            []
        ):

            topic = result.get(
                "topic",
                "General"
            )

            percentage = float(
                result.get(
                    "percentage",
                    0
                )
            )

            topic_data[topic].append(
                percentage
            )

    return dict(topic_data)


# ============================================================
# GET LATEST TOPIC SCORES
# ============================================================

def get_latest_topic_scores(assessments):

    topic_scores = {}

    for assessment in assessments:

        for result in assessment.get(
            "topic_results",
            []
        ):

            topic = result.get(
                "topic",
                "General"
            )

            topic_scores[topic] = float(
                result.get(
                    "percentage",
                    0
                )
            )

    return topic_scores


# ============================================================
# GET FIRST TOPIC SCORES
# ============================================================

def get_first_topic_scores(assessments):

    topic_scores = {}

    if not assessments:

        return topic_scores

    first_assessment = assessments[0]

    for result in first_assessment.get(
        "topic_results",
        []
    ):

        topic = result.get(
            "topic",
            "General"
        )

        topic_scores[topic] = float(
            result.get(
                "percentage",
                0
            )
        )

    return topic_scores


# ============================================================
# CALCULATE IMPROVEMENT
# ============================================================

def calculate_improvement(
    first_score,
    latest_score
):

    return latest_score - first_score


# ============================================================
# GET TOPIC STATUS
# ============================================================

def get_topic_status(percentage):

    if percentage < 50:

        return "Weak"

    elif percentage < 75:

        return "Developing"

    else:

        return "Strong"


# ============================================================
# CREATE TOPIC PROGRESS
# ============================================================

def create_topic_progress(
    first_score,
    latest_score
):

    improvement = calculate_improvement(
        first_score,
        latest_score
    )

    status = get_topic_status(
        latest_score
    )


    if improvement > 0:

        trend = "Improving"

    elif improvement < 0:

        trend = "Declining"

    else:

        trend = "No Change"


    return {

        "first_score":
            first_score,

        "latest_score":
            latest_score,

        "improvement":
            improvement,

        "status":
            status,

        "trend":
            trend
    }


# ============================================================
# BUILD COMPLETE PROGRESS REPORT
# ============================================================

def generate_progress_report(
    assessments
):

    if not assessments:

        return {

            "topics": {},

            "improving_topics": [],

            "declining_topics": [],

            "weak_topics": [],

            "strong_topics": []
        }


    first_scores = (
        get_first_topic_scores(
            assessments
        )
    )

    latest_scores = (
        get_latest_topic_scores(
            assessments
        )
    )


    all_topics = set(
        first_scores.keys()
    ) | set(
        latest_scores.keys()
    )


    topic_progress = {}


    for topic in all_topics:

        first = first_scores.get(
            topic,
            0
        )

        latest = latest_scores.get(
            topic,
            first
        )


        topic_progress[topic] = (
            create_topic_progress(
                first,
                latest
            )
        )


    improving = []

    declining = []

    weak = []

    strong = []


    for topic, data in topic_progress.items():

        if data["improvement"] > 0:

            improving.append(
                topic
            )

        elif data["improvement"] < 0:

            declining.append(
                topic
            )


        if data["status"] == "Weak":

            weak.append(
                topic
            )

        elif data["status"] == "Strong":

            strong.append(
                topic
            )


    return {

        "topics":
            topic_progress,

        "improving_topics":
            improving,

        "declining_topics":
            declining,

        "weak_topics":
            weak,

        "strong_topics":
            strong
    }


# ============================================================
# OVERALL IMPROVEMENT
# ============================================================

def calculate_overall_improvement(
    assessments
):

    if len(assessments) < 2:

        return 0


    first = float(
        assessments[0].get(
            "percentage",
            0
        )
    )

    latest = float(
        assessments[-1].get(
            "percentage",
            0
        )
    )


    return latest - first


# ============================================================
# GET PROGRESS MESSAGE
# ============================================================

def get_progress_message(
    assessments
):

    if not assessments:

        return (
            "Complete your first assessment "
            "to start tracking progress."
        )


    if len(assessments) == 1:

        return (
            "Your first assessment has been recorded. "
            "Complete another assessment after your "
            "learning plan to measure improvement."
        )


    improvement = (
        calculate_overall_improvement(
            assessments
        )
    )


    if improvement > 10:

        return (
            f"Excellent progress! Your overall "
            f"performance has improved by "
            f"{improvement:.1f} percentage points."
        )


    elif improvement > 0:

        return (
            f"Good progress! Your overall "
            f"performance has improved by "
            f"{improvement:.1f} percentage points."
        )


    elif improvement < 0:

        return (
            f"Your overall score has decreased by "
            f"{abs(improvement):.1f} percentage points. "
            "Review your weak topics before the next "
            "assessment."
        )


    return (
        "Your overall score has remained the same. "
        "Focus on your weak and developing topics "
        "to improve in the next assessment."
    )