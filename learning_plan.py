# ============================================================
# AIStat Learn
# Adaptive 5-Day Personalized Learning Plan
# ============================================================


# ============================================================
# LEARNING STRATEGIES
# ============================================================

LEARNING_STRATEGIES = {

    1: {
        "name": "Concept Understanding",

        "description":
            "Start by building a clear conceptual foundation. "
            "Read the learning material carefully and identify "
            "the meaning, definitions, important principles, "
            "and relationships between concepts.",

        "activities": [
            "Read the selected topic carefully.",
            "Identify important definitions and principles.",
            "Write short notes using your own words.",
            "Identify the main idea of the topic."
        ]
    },


    2: {
        "name": "Active Recall",

        "description":
            "Retrieve information from memory without looking "
            "at the learning material. Active recall helps "
            "identify which concepts are understood and which "
            "ones still need attention.",

        "activities": [
            "Close the learning material.",
            "Recall the important concepts from memory.",
            "Explain the topic without looking at your notes.",
            "Write down everything you remember."
        ]
    },


    3: {
        "name": "Practice & Application",

        "description":
            "Apply the concepts through practice questions "
            "and examples. The goal is to move from remembering "
            "information to actually using the knowledge.",

        "activities": [
            "Solve practice questions.",
            "Work through examples related to the topic.",
            "Identify mistakes in your answers.",
            "Explain why the correct answer is correct."
        ]
    },


    4: {
        "name": "Analysis & Problem Solving",

        "description":
            "Develop deeper understanding by comparing ideas, "
            "analyzing situations, identifying relationships, "
            "and solving application-oriented problems.",

        "activities": [
            "Compare related concepts.",
            "Analyze practical examples.",
            "Identify relationships between concepts.",
            "Solve higher-level questions."
        ]
    },


    5: {
        "name": "Revision & Self Assessment",

        "description":
            "Consolidate everything learned during the previous "
            "days. Review weak areas and test your understanding "
            "with a short self-assessment.",

        "activities": [
            "Review important concepts.",
            "Revise previously difficult areas.",
            "Take a short practice assessment.",
            "Write down the concepts that still need revision."
        ]
    }
}


# ============================================================
# DETERMINE TOPIC LEVEL
# ============================================================

def get_topic_level(percentage):

    percentage = float(percentage)

    if percentage < 50:

        return "Weak"

    elif percentage < 75:

        return "Developing"

    else:

        return "Strong"


# ============================================================
# DETERMINE PRIORITY
# ============================================================

def get_priority(percentage):

    percentage = float(percentage)

    if percentage < 50:

        return "High"

    elif percentage < 75:

        return "Medium"

    else:

        return "Low"


# ============================================================
# STUDY TIME
# ============================================================

def get_study_time(level, day):

    if level == "Weak":

        if day <= 2:

            return "60 minutes"

        elif day <= 4:

            return "60–75 minutes"

        else:

            return "45–60 minutes"


    elif level == "Developing":

        if day <= 2:

            return "45 minutes"

        elif day <= 4:

            return "45–60 minutes"

        else:

            return "40–45 minutes"


    else:

        return "30–40 minutes"


# ============================================================
# DAY-SPECIFIC TITLE
# ============================================================

def get_day_title(day):

    titles = {

        1:
            "Build Your Concept Foundation",

        2:
            "Test Your Memory",

        3:
            "Practice What You Learned",

        4:
            "Think Deeper & Apply",

        5:
            "Revise & Test Yourself"
    }

    return titles.get(
        day,
        "Learning Session"
    )


# ============================================================
# DAY-SPECIFIC GOAL
# ============================================================

def get_day_goal(day, topic, level):

    if day == 1:

        return (
            f"Understand the fundamental ideas of "
            f"{topic} and create a clear conceptual foundation."
        )


    elif day == 2:

        return (
            f"Recall the important concepts of "
            f"{topic} without depending completely on your notes."
        )


    elif day == 3:

        return (
            f"Use your knowledge of {topic} "
            f"to solve practice questions and examples."
        )


    elif day == 4:

        return (
            f"Develop deeper understanding of {topic} "
            f"by analyzing relationships and applications."
        )


    else:

        return (
            f"Revise {topic}, identify remaining weak areas, "
            f"and check your understanding through self-assessment."
        )


# ============================================================
# GET ACTIVITY
# ============================================================

def get_day_activity(day, topic, level):

    if day == 1:

        if level == "Weak":

            return (
                f"Read the learning material for {topic} slowly. "
                f"Focus on definitions, basic principles, and "
                f"examples before moving to difficult concepts."
            )

        elif level == "Developing":

            return (
                f"Review {topic} and create a concise summary "
                f"containing the important concepts and relationships."
            )

        else:

            return (
                f"Quickly review {topic}, focusing on concepts "
                f"that were missed or misunderstood in the assessment."
            )


    elif day == 2:

        return (
            f"Close your notes and explain {topic} from memory. "
            f"Write down important definitions, principles, and "
            f"examples. Then compare your response with the material."
        )


    elif day == 3:

        return (
            f"Solve practice questions related to {topic}. "
            f"After every mistake, identify the concept responsible "
            f"for the error and review it again."
        )


    elif day == 4:

        return (
            f"Analyze {topic} using examples or real situations. "
            f"Compare related concepts and explain how they are "
            f"connected. Try to solve application-based questions."
        )


    else:

        return (
            f"Review the complete topic of {topic}. Focus especially "
            f"on concepts that were difficult earlier, then complete "
            f"a short self-test to check your final understanding."
        )


# ============================================================
# CREATE ONE DAY
# ============================================================

def create_day_plan(
    day,
    topic,
    percentage,
    level,
    priority
):

    strategy = LEARNING_STRATEGIES[day]


    return {

        "day":
            day,

        "topic":
            topic,

        "percentage":
            percentage,

        "level":
            level,

        "priority":
            priority,

        "title":
            get_day_title(day),

        "strategy":
            strategy["description"],

        "activity":
            get_day_activity(
                day,
                topic,
                level
            ),

        "study_time":
            get_study_time(
                level,
                day
            ),

        "goal":
            get_day_goal(
                day,
                topic,
                level
            ),

        "activities":
            strategy["activities"]
    }


# ============================================================
# CREATE PERSONALIZED PLAN
# ============================================================

def create_personalized_plan(analysis):

    if not analysis:

        return {

            "summary":
                "Complete an assessment to generate "
                "your personalized learning plan.",

            "priority_topics": [],

            "plan": []
        }


    # ========================================================
    # NORMALIZE ANALYSIS
    # ========================================================

    topics = []


    for item in analysis:

        if not isinstance(
            item,
            dict
        ):

            continue


        topic = item.get(
            "topic",
            "General"
        )


        percentage = item.get(
            "percentage",
            item.get(
                "score",
                0
            )
        )


        try:

            percentage = float(
                percentage
            )

        except:

            percentage = 0


        level = item.get(
            "level",
            get_topic_level(
                percentage
            )
        )


        priority = get_priority(
            percentage
        )


        topics.append(
            {

                "topic":
                    topic,

                "percentage":
                    percentage,

                "level":
                    level,

                "priority":
                    priority
            }
        )


    # ========================================================
    # SORT FROM WEAKEST TO STRONGEST
    # ========================================================

    topics.sort(
        key=lambda x:
        x["percentage"]
    )


    if not topics:

        return {

            "summary":
                "No topic performance data is available.",

            "priority_topics": [],

            "plan": []
        }


    # ========================================================
    # PRIORITY TOPICS
    # ========================================================

    priority_topics = []


    for item in topics:

        if item["level"] in [
            "Weak",
            "Developing"
        ]:

            priority_topics.append(
                item
            )


    # ========================================================
    # IF EVERYTHING IS STRONG
    # ========================================================

    if not priority_topics:

        priority_topics = [
            topics[0]
        ]


    # ========================================================
    # CREATE FIVE-DAY PLAN
    # ========================================================

    plan = []


    # --------------------------------------------------------
    # Strategy:
    #
    # Day 1 → Weakest topic
    # Day 2 → Second weakest / same topic
    # Day 3 → Weakest topic practice
    # Day 4 → Developing topic / application
    # Day 5 → Revision + self assessment
    # --------------------------------------------------------


    weakest = topics[0]


    if len(topics) > 1:

        second_topic = topics[1]

    else:

        second_topic = weakest


    if len(topics) > 2:

        third_topic = topics[2]

    else:

        third_topic = weakest


    # ========================================================
    # DAY 1
    # ========================================================

    plan.append(
        create_day_plan(
            1,
            weakest["topic"],
            weakest["percentage"],
            weakest["level"],
            weakest["priority"]
        )
    )


    # ========================================================
    # DAY 2
    # ========================================================

    plan.append(
        create_day_plan(
            2,
            weakest["topic"],
            weakest["percentage"],
            weakest["level"],
            weakest["priority"]
        )
    )


    # ========================================================
    # DAY 3
    # ========================================================

    plan.append(
        create_day_plan(
            3,
            second_topic["topic"],
            second_topic["percentage"],
            second_topic["level"],
            second_topic["priority"]
        )
    )


    # ========================================================
    # DAY 4
    # ========================================================

    plan.append(
        create_day_plan(
            4,
            third_topic["topic"],
            third_topic["percentage"],
            third_topic["level"],
            third_topic["priority"]
        )
    )


    # ========================================================
    # DAY 5
    # ========================================================

    plan.append(
        create_day_plan(
            5,
            weakest["topic"],
            weakest["percentage"],
            weakest["level"],
            weakest["priority"]
        )
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    weak_count = sum(
        1
        for topic in topics
        if topic["level"] == "Weak"
    )


    developing_count = sum(
        1
        for topic in topics
        if topic["level"] == "Developing"
    )


    if weak_count > 0:

        summary = (
            f"Your plan focuses primarily on "
            f"{weak_count} weak topic(s) and "
            f"{developing_count} developing topic(s). "
            f"The five-day strategy gradually moves from "
            f"concept understanding to active recall, practice, "
            f"analysis, and final revision."
        )


    elif developing_count > 0:

        summary = (
            f"You have {developing_count} developing topic(s). "
            f"The plan focuses on strengthening these areas "
            f"while maintaining your stronger concepts."
        )


    else:

        summary = (
            "Your current performance is strong across the "
            "assessed topics. The five-day plan focuses on "
            "deeper understanding, application, and revision."
        )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "summary":
            summary,

        "priority_topics":
            priority_topics,

        "plan":
            plan,

        "total_topics":
            len(topics),

        "weak_topics":
            [
                topic
                for topic in topics
                if topic["level"] == "Weak"
            ],

        "developing_topics":
            [
                topic
                for topic in topics
                if topic["level"] == "Developing"
            ],

        "strong_topics":
            [
                topic
                for topic in topics
                if topic["level"] == "Strong"
            ]
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_analysis = [

        {
            "topic":
                "Need for Value Education",

            "percentage":
                35
        },

        {
            "topic":
                "Guidelines for Value Education",

            "percentage":
                62
        },

        {
            "topic":
                "Content of Value Education",

            "percentage":
                82
        }
    ]


    result = create_personalized_plan(
        sample_analysis
    )


    print("\n")
    print(
        "PERSONALIZED 5-DAY LEARNING PLAN"
    )

    print("=" * 60)


    print(
        result["summary"]
    )


    print("\n")


    for day in result["plan"]:

        print(
            f"DAY {day['day']}"
        )

        print(
            f"Topic: {day['topic']}"
        )

        print(
            f"Strategy: {day['strategy']}"
        )

        print(
            f"Activity: {day['activity']}"
        )

        print(
            f"Study Time: {day['study_time']}"
        )

        print(
            f"Goal: {day['goal']}"
        )

        print(
            "-" * 60
        )