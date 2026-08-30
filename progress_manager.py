import json
import os


# ============================================================
# FILE CONFIGURATION
# ============================================================

PROGRESS_FILE = "student_progress.json"


# ============================================================
# LOAD STUDENT PROGRESS
# ============================================================

def load_progress():

    if not os.path.exists(PROGRESS_FILE):

        return {
            "assessments": []
        }

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        if "assessments" not in data:

            data["assessments"] = []


        return data


    except Exception:

        return {
            "assessments": []
        }


# ============================================================
# SAVE STUDENT PROGRESS
# ============================================================

def save_progress(data):

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# ADD NEW ASSESSMENT
# ============================================================

def add_assessment(
    score,
    total,
    percentage,
    topic_results
):

    data = load_progress()


    assessment_number = (
        len(data["assessments"]) + 1
    )


    assessment = {

        "assessment_number":
            assessment_number,

        "score":
            score,

        "total":
            total,

        "percentage":
            percentage,

        "topic_results": []
    }


    # --------------------------------------------------------
    # SAVE TOPIC RESULTS
    # --------------------------------------------------------

    for topic, performance, level in topic_results:

        assessment[
            "topic_results"
        ].append({

            "topic":
                topic,

            "performance":
                performance,

            "level":
                level
        })


    data[
        "assessments"
    ].append(
        assessment
    )


    save_progress(data)


    return assessment


# ============================================================
# GET ALL ASSESSMENTS
# ============================================================

def get_assessments():

    data = load_progress()

    return data.get(
        "assessments",
        []
    )


# ============================================================
# GET LATEST ASSESSMENT
# ============================================================

def get_latest_assessment():

    assessments = get_assessments()


    if not assessments:

        return None


    return assessments[-1]


# ============================================================
# GET PREVIOUS ASSESSMENT
# ============================================================

def get_previous_assessment():

    assessments = get_assessments()


    if len(assessments) < 2:

        return None


    return assessments[-2]


# ============================================================
# CALCULATE OVERALL IMPROVEMENT
# ============================================================

def get_overall_improvement():

    assessments = get_assessments()


    if len(assessments) < 2:

        return None


    previous = assessments[-2]

    current = assessments[-1]


    improvement = (
        current["percentage"]
        - previous["percentage"]
    )


    return improvement


# ============================================================
# GET TOPIC PROGRESS
# ============================================================

def get_topic_progress():

    assessments = get_assessments()


    if len(assessments) < 2:

        return []


    previous = assessments[-2]

    current = assessments[-1]


    previous_topics = {

        item["topic"]:
            item["performance"]

        for item in previous[
            "topic_results"
        ]
    }


    current_topics = {

        item["topic"]:
            item["performance"]

        for item in current[
            "topic_results"
        ]
    }


    all_topics = sorted(
        set(previous_topics.keys())
        |
        set(current_topics.keys())
    )


    results = []


    for topic in all_topics:

        before = previous_topics.get(
            topic,
            0
        )

        after = current_topics.get(
            topic,
            0
        )


        improvement = (
            after - before
        )


        results.append({

            "topic":
                topic,

            "before":
                before,

            "after":
                after,

            "improvement":
                improvement
        })


    return results


# ============================================================
# GET WEAK TOPICS
# ============================================================

def get_weak_topics():

    latest = get_latest_assessment()


    if latest is None:

        return []


    weak_topics = []


    for item in latest[
        "topic_results"
    ]:

        if item["performance"] < 50:

            weak_topics.append(
                item
            )


    return weak_topics


# ============================================================
# GET DEVELOPING TOPICS
# ============================================================

def get_developing_topics():

    latest = get_latest_assessment()


    if latest is None:

        return []


    developing_topics = []


    for item in latest[
        "topic_results"
    ]:

        if (
            item["performance"] >= 50
            and
            item["performance"] < 75
        ):

            developing_topics.append(
                item
            )


    return developing_topics


# ============================================================
# GET STRONG TOPICS
# ============================================================

def get_strong_topics():

    latest = get_latest_assessment()


    if latest is None:

        return []


    strong_topics = []


    for item in latest[
        "topic_results"
    ]:

        if item["performance"] >= 75:

            strong_topics.append(
                item
            )


    return strong_topics