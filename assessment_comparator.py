# ============================================================
# AIStat Learn
# Stage 12 - Reassessment Intelligence
# ============================================================


# ============================================================
# CALCULATE IMPROVEMENT
# ============================================================

def calculate_improvement(before, after):
    """
    Calculates the change in score between two assessments.
    """

    try:
        before = float(before)
    except:
        before = 0

    try:
        after = float(after)
    except:
        after = 0

    return round(after - before, 2)


# ============================================================
# DETERMINE PERFORMANCE STATUS
# ============================================================

def get_status(before, after):

    improvement = calculate_improvement(
        before,
        after
    )

    if improvement >= 20:

        return "Excellent Improvement"

    elif improvement >= 10:

        return "Good Improvement"

    elif improvement > 0:

        return "Slight Improvement"

    elif improvement == 0:

        return "No Change"

    else:

        return "Performance Decreased"


# ============================================================
# DETERMINE NEW LEVEL
# ============================================================

def get_level(score):

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
# COMPARE ONE TOPIC
# ============================================================

def compare_topic(before_topic, after_topic):

    topic = before_topic.get(
        "topic",
        after_topic.get(
            "topic",
            "Unknown Topic"
        )
    )

    before_score = before_topic.get(
        "percentage",
        before_topic.get(
            "score",
            0
        )
    )

    after_score = after_topic.get(
        "percentage",
        after_topic.get(
            "score",
            0
        )
    )

    improvement = calculate_improvement(
        before_score,
        after_score
    )

    status = get_status(
        before_score,
        after_score
    )

    before_level = get_level(
        before_score
    )

    after_level = get_level(
        after_score
    )

    return {

        "topic":
            topic,

        "before":
            round(float(before_score), 2),

        "after":
            round(float(after_score), 2),

        "improvement":
            improvement,

        "before_level":
            before_level,

        "after_level":
            after_level,

        "status":
            status
    }


# ============================================================
# FIND TOPIC DATA
# ============================================================

def find_topic(topic, topic_list):

    for item in topic_list:

        if not isinstance(
            item,
            dict
        ):
            continue

        item_topic = item.get(
            "topic",
            ""
        )

        if str(item_topic).strip().lower() == str(topic).strip().lower():

            return item

    return None


# ============================================================
# COMPARE ASSESSMENTS
# ============================================================

def compare_assessments(
    first_assessment,
    second_assessment
):

    if not first_assessment:

        return {

            "results": [],

            "summary":
                "The first assessment is not available.",

            "overall_before":
                0,

            "overall_after":
                0,

            "overall_improvement":
                0,

            "improved_topics": [],

            "unchanged_topics": [],

            "declined_topics": [],

            "remaining_weak_topics": []
        }


    if not second_assessment:

        return {

            "results": [],

            "summary":
                "The second assessment is not available.",

            "overall_before":
                0,

            "overall_after":
                0,

            "overall_improvement":
                0,

            "improved_topics": [],

            "unchanged_topics": [],

            "declined_topics": [],

            "remaining_weak_topics": []
        }


    results = []


    # --------------------------------------------------------
    # Compare topics from first assessment
    # --------------------------------------------------------

    for before_topic in first_assessment:

        if not isinstance(
            before_topic,
            dict
        ):
            continue

        topic = before_topic.get(
            "topic",
            ""
        )

        after_topic = find_topic(
            topic,
            second_assessment
        )

        if after_topic is None:

            continue

        result = compare_topic(
            before_topic,
            after_topic
        )

        results.append(
            result
        )


    # --------------------------------------------------------
    # Find topics that exist only in second assessment
    # --------------------------------------------------------

    for after_topic in second_assessment:

        if not isinstance(
            after_topic,
            dict
        ):
            continue

        topic = after_topic.get(
            "topic",
            ""
        )

        already_exists = find_topic(
            topic,
            first_assessment
        )

        if already_exists is None:

            score = after_topic.get(
                "percentage",
                after_topic.get(
                    "score",
                    0
                )
            )

            results.append(

                {

                    "topic":
                        topic,

                    "before":
                        0,

                    "after":
                        float(score),

                    "improvement":
                        float(score),

                    "before_level":
                        "Not Assessed",

                    "after_level":
                        get_level(score),

                    "status":
                        "New Topic"
                }
            )


    # ========================================================
    # OVERALL SCORES
    # ========================================================

    if results:

        overall_before = round(
            sum(
                item["before"]
                for item in results
            ) / len(results),
            2
        )

        overall_after = round(
            sum(
                item["after"]
                for item in results
            ) / len(results),
            2
        )

    else:

        overall_before = 0

        overall_after = 0


    overall_improvement = calculate_improvement(
        overall_before,
        overall_after
    )


    # ========================================================
    # CLASSIFY TOPICS
    # ========================================================

    improved_topics = []

    unchanged_topics = []

    declined_topics = []

    remaining_weak_topics = []


    for result in results:

        if result["improvement"] > 0:

            improved_topics.append(
                result
            )

        elif result["improvement"] == 0:

            unchanged_topics.append(
                result
            )

        else:

            declined_topics.append(
                result
            )


        if result["after"] < 50:

            remaining_weak_topics.append(
                result
            )


    # ========================================================
    # GENERATE SUMMARY
    # ========================================================

    if overall_improvement >= 20:

        summary = (
            "Excellent progress! Your overall performance "
            "has improved significantly after completing "
            "the personalized learning plan. Continue using "
            "the same learning approach while gradually "
            "increasing question difficulty."
        )

    elif overall_improvement >= 10:

        summary = (
            "Good progress! Your overall performance has "
            "improved after the learning plan. Continue "
            "practicing the weaker areas and revise concepts "
            "that still need improvement."
        )

    elif overall_improvement > 0:

        summary = (
            "Your performance has improved slightly. The "
            "learning plan is helping, but some concepts "
            "may require additional practice and revision."
        )

    elif overall_improvement == 0:

        summary = (
            "Your overall score has not changed. Review "
            "the learning strategy and spend more time on "
            "your weak topics before attempting another "
            "assessment."
        )

    else:

        summary = (
            "Your overall performance has decreased. Do not "
            "worry. Review the difficult concepts again, "
            "practice them carefully, and take another "
            "assessment after additional preparation."
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "results":
            results,

        "summary":
            summary,

        "overall_before":
            overall_before,

        "overall_after":
            overall_after,

        "overall_improvement":
            overall_improvement,

        "improved_topics":
            improved_topics,

        "unchanged_topics":
            unchanged_topics,

        "declined_topics":
            declined_topics,

        "remaining_weak_topics":
            remaining_weak_topics
    }


# ============================================================
# GENERATE RECOMMENDATION
# ============================================================

def generate_recommendation(comparison):

    if not comparison:

        return "Complete two assessments to receive a recommendation."


    weak_topics = comparison.get(
        "remaining_weak_topics",
        []
    )

    declined_topics = comparison.get(
        "declined_topics",
        []
    )

    improved_topics = comparison.get(
        "improved_topics",
        []
    )


    # --------------------------------------------------------
    # Remaining weak topics
    # --------------------------------------------------------

    if weak_topics:

        topic_names = [
            item["topic"]
            for item in weak_topics
        ]

        return (
            "Continue focusing on these weak topics: "
            + ", ".join(topic_names)
            + ". Review the concepts again, use active recall, "
              "solve practice questions, and complete another "
              "assessment."
        )


    # --------------------------------------------------------
    # Declining topics
    # --------------------------------------------------------

    if declined_topics:

        topic_names = [
            item["topic"]
            for item in declined_topics
        ]

        return (
            "Some topics showed a decrease in performance: "
            + ", ".join(topic_names)
            + ". Revisit the learning material and practice "
              "these topics before moving to more difficult "
              "content."
        )


    # --------------------------------------------------------
    # Strong improvement
    # --------------------------------------------------------

    if improved_topics:

        return (
            "Your performance is improving well. Continue "
            "with regular revision and gradually move toward "
            "medium and hard application-based questions."
        )


    return (
        "Continue studying regularly and complete another "
        "assessment to measure your progress."
    )


# ============================================================
# SIMPLE PROGRESS REPORT
# ============================================================

def generate_progress_report(comparison):

    if not comparison:

        return "No comparison data available."


    before = comparison.get(
        "overall_before",
        0
    )

    after = comparison.get(
        "overall_after",
        0
    )

    improvement = comparison.get(
        "overall_improvement",
        0
    )

    improved = len(
        comparison.get(
            "improved_topics",
            []
        )
    )

    unchanged = len(
        comparison.get(
            "unchanged_topics",
            []
        )
    )

    declined = len(
        comparison.get(
            "declined_topics",
            []
        )
    )


    report = (

        f"Overall Score Before: {before}%\n"

        f"Overall Score After: {after}%\n"

        f"Overall Improvement: {improvement} percentage points\n\n"

        f"Improved Topics: {improved}\n"

        f"Unchanged Topics: {unchanged}\n"

        f"Declined Topics: {declined}"
    )


    return report


# ============================================================
# TEST THE MODULE
# ============================================================

if __name__ == "__main__":

    first_assessment = [

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
                55
        },

        {
            "topic":
                "Relationships",

            "percentage":
                80
        }
    ]


    second_assessment = [

        {
            "topic":
                "Value Education",

            "percentage":
                75
        },

        {
            "topic":
                "Human Values",

            "percentage":
                70
        },

        {
            "topic":
                "Relationships",

            "percentage":
                82
        }
    ]


    comparison = compare_assessments(
        first_assessment,
        second_assessment
    )


    print("\n")
    print(
        "=" * 65
    )

    print(
        "AIStat Learn - REASSESSMENT REPORT"
    )

    print(
        "=" * 65
    )


    print(
        "\n"
        + comparison["summary"]
    )


    print(
        "\nOverall Before:",
        comparison["overall_before"],
        "%"
    )


    print(
        "Overall After:",
        comparison["overall_after"],
        "%"
    )


    print(
        "Overall Improvement:",
        comparison["overall_improvement"],
        "percentage points"
    )


    print(
        "\n"
        + "-" * 65
    )


    for result in comparison["results"]:

        print(
            f"\nTopic: {result['topic']}"
        )

        print(
            f"Before: {result['before']}%"
        )

        print(
            f"After: {result['after']}%"
        )

        print(
            f"Improvement: {result['improvement']}%"
        )

        print(
            f"Status: {result['status']}"
        )


    print(
        "\n"
        + "-" * 65
    )


    print(
        "\nRECOMMENDATION:"
    )

    print(
        generate_recommendation(
            comparison
        )
    )


    print(
        "\n"
        + "=" * 65
    )