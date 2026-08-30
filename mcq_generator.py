import re
import random


# ============================================================
# AIStat Learn - Intelligent MCQ Generator
# ============================================================


# ------------------------------------------------------------
# 1. CLEAN PDF TEXT
# ------------------------------------------------------------

def clean_text(text):
    text = text.replace("\x00", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ------------------------------------------------------------
# 2. SPLIT INTO SENTENCES
# ------------------------------------------------------------

def get_sentences(text):
    text = clean_text(text)

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    result = []

    for sentence in sentences:

        sentence = sentence.strip()

        words = sentence.split()

        if 8 <= len(words) <= 80:

            # Ignore headings and useless fragments
            if not sentence.isupper():

                result.append(sentence)

    return result


# ------------------------------------------------------------
# 3. IMPORTANT CONCEPTS
# ------------------------------------------------------------

CONCEPTS = [
    "human values",
    "value education",
    "values",
    "human beings",
    "human aspirations",
    "human",
    "happiness",
    "prosperity",
    "aspiration",
    "self-exploration",
    "self exploration",
    "natural acceptance",
    "relationship",
    "relationships",
    "facility",
    "facilities",
    "physical facilities",
    "education",
    "skills",
    "harmony",
    "trust",
    "respect",
    "understanding",
    "responsibility",
    "fulfilment",
    "fulfillment",
    "need",
    "purpose",
    "acceptance",
    "acceptable",
    "feeling",
    "feelings",
    "continuous happiness",
    "continuous happiness and prosperity"
]


def find_concepts(text):

    lower_text = text.lower()

    found = []

    # Longer concepts first
    concepts_sorted = sorted(
        CONCEPTS,
        key=len,
        reverse=True
    )

    for concept in concepts_sorted:

        if concept.lower() in lower_text:

            if concept not in found:

                found.append(concept)

    return found


# ------------------------------------------------------------
# 4. FIND SENTENCES FOR A CONCEPT
# ------------------------------------------------------------

def concept_sources(
    concept,
    sentences
):

    results = []

    for sentence in sentences:

        if concept.lower() in sentence.lower():

            results.append(sentence)

    return results


# ------------------------------------------------------------
# 5. TOPIC IDENTIFICATION
# ------------------------------------------------------------

def determine_topic(
    concept,
    sentence
):

    text = (
        concept + " " + sentence
    ).lower()

    if (
        "self-exploration" in text
        or "self exploration" in text
    ):
        return "Self-Exploration"

    if "natural acceptance" in text:
        return "Natural Acceptance"

    if (
        "relationship" in text
        or "trust" in text
        or "respect" in text
    ):
        return "Human Relationships"

    if (
        "facility" in text
        or "facilities" in text
        or "physical facilities" in text
    ):
        return "Physical Facilities"

    if (
        "happiness" in text
        or "prosperity" in text
    ):
        return (
            "Continuous Happiness and "
            "Prosperity as Basic Human Aspirations"
        )

    if (
        "aspiration" in text
        or "aspire" in text
    ):
        return "Basic Human Aspirations"

    if "value education" in text:
        return "Introduction to Value Education"

    if "education" in text:
        return "Need for Value Education"

    if "value" in text:
        return "Human Values"

    return "Learning Material"


# ------------------------------------------------------------
# 6. RELATED CONCEPTS
# ------------------------------------------------------------

def get_related_concepts(
    concept,
    concepts
):

    others = [
        c for c in concepts
        if c.lower() != concept.lower()
    ]

    random.shuffle(others)

    return others[:4]


# ------------------------------------------------------------
# 7. QUESTION TYPES
# ------------------------------------------------------------

QUESTION_TYPES = [

    "understanding",

    "application",

    "scenario",

    "comparison",

    "cause_effect",

    "reasoning",

    "example",

    "interpretation",

    "assertion",

    "higher_order"

]


# ------------------------------------------------------------
# 8. QUESTION TEMPLATES
# ------------------------------------------------------------

TEMPLATES = {

    "understanding": [

        "Which statement best explains the idea presented in the passage?",

        "What is the most appropriate interpretation of the passage?",

        "Which statement correctly reflects the meaning of the passage?"

    ],

    "application": [

        "How can the principle described in the passage be applied in everyday life?",

        "Which situation best demonstrates the principle discussed in the passage?",

        "A learner wants to apply the idea discussed above. Which action would be most appropriate?"

    ],

    "scenario": [

        "A student is facing a situation related to the idea described above. Which response best reflects the learning material?",

        "Consider the following situation. A person encounters a challenge related to the idea discussed above. Which approach is most consistent with the learning material?",

        "Suppose a learner encounters the situation described in the passage. Which decision would best reflect the principle discussed?"

    ],

    "comparison": [

        "Which statement best distinguishes the idea in the passage from a purely material or superficial understanding?",

        "Which comparison most accurately reflects the idea presented in the learning material?",

        "Which statement correctly contrasts the principle in the passage with an incomplete understanding of it?"

    ],

    "cause_effect": [

        "According to the learning material, what is the most appropriate consequence of applying the idea discussed in the passage?",

        "What relationship between the ideas in the passage is most accurately represented by the following option?",

        "Which outcome is most consistent with the principle described in the passage?"

    ],

    "reasoning": [

        "Why is the idea discussed in the passage important according to the learning material?",

        "Which reasoning best supports the idea presented in the passage?",

        "What is the strongest reason for the principle discussed in the passage?"

    ],

    "example": [

        "Which of the following situations is the best example of the idea discussed in the passage?",

        "Which example most clearly demonstrates the principle described in the learning material?",

        "Which situation represents an appropriate application of the idea presented above?"

    ],

    "interpretation": [

        "Which interpretation most accurately captures the deeper meaning of the passage?",

        "What can reasonably be understood from the passage?",

        "Which option demonstrates a correct understanding of the context presented?"

    ],

    "assertion": [

        "Which statement is most consistent with the learning material?",

        "Which of the following statements can be supported by the passage?",

        "Which statement correctly represents the principle discussed?"

    ],

    "higher_order": [

        "Which conclusion can be logically drawn from the idea presented in the passage?",

        "Which option demonstrates the deepest understanding of the principle described?",

        "Which conclusion would be most appropriate when the principle is applied to a new situation?"

    ]

}


# ------------------------------------------------------------
# 9. REMOVE CONCEPT-AS-ANSWER PROBLEM
# ------------------------------------------------------------

def forbidden_answer(
    answer,
    concept
):

    answer_lower = answer.lower().strip()

    concept_lower = concept.lower().strip()

    # Never allow a one-word concept as an answer
    if answer_lower == concept_lower:
        return True

    return False


# ------------------------------------------------------------
# 10. CREATE CORRECT ANSWER
# ------------------------------------------------------------

def create_correct_answer(
    concept,
    sentence,
    question_type
):

    sentence = sentence.strip()

    if question_type == "application":

        return (
            "The principle described in the passage should be "
            "understood in its broader context and applied by "
            "considering the purpose and meaning explained in "
            "the learning material. The situation is therefore "
            "best handled in a way that is consistent with the "
            "ideas presented in the passage."
        )

    if question_type == "scenario":

        return (
            "The appropriate response is the one that follows "
            "the understanding developed in the learning material. "
            "Rather than reacting only to the immediate situation, "
            "the learner should apply the underlying principle "
            "described in the passage and consider its broader "
            "meaning."
        )

    if question_type == "comparison":

        return (
            "The correct interpretation recognizes that the idea "
            "described in the passage is broader than a narrow or "
            "purely material interpretation. The learning material "
            "places the idea within a wider framework of understanding "
            "and human development."
        )

    if question_type == "cause_effect":

        return (
            "The passage suggests that understanding and applying "
            "the principle can influence the way a person thinks, "
            "responds, and makes decisions. The consequence must "
            "therefore be understood in relation to the broader "
            "context presented in the learning material."
        )

    if question_type == "reasoning":

        return (
            "The idea is important because the learning material "
            "presents it as part of a broader process of understanding "
            "human aspirations, values, relationships, and responsible "
            "living. Its importance therefore extends beyond simply "
            "remembering a definition."
        )

    if question_type == "example":

        return (
            "The correct example is the situation that demonstrates "
            "the principle in practice. It should reflect the meaning "
            "and context of the learning material rather than merely "
            "containing a similar keyword."
        )

    if question_type == "higher_order":

        return (
            "The conclusion follows from the broader principle "
            "presented in the passage. It requires the learner to "
            "connect the information in the material with a new "
            "situation instead of simply recalling an isolated term."
        )

    return (
        "The passage presents this idea as part of the broader "
        "discussion in the learning material. Understanding the "
        "statement requires considering its context and the "
        "relationship between the different ideas presented. "
        "The correct interpretation therefore reflects the "
        "overall meaning of the passage rather than simply "
        "matching a keyword."
    )


# ------------------------------------------------------------
# 11. CREATE WRONG ANSWERS
# ------------------------------------------------------------

def create_distractors(
    concept,
    concepts,
    question_type
):

    distractors = []

    other_concepts = [
        c for c in concepts
        if c.lower() != concept.lower()
    ]

    random.shuffle(other_concepts)

    # Wrong answers should be complete ideas,
    # not just concept names.

    patterns = [

        (
            "The idea is concerned only with "
            "{concept} and does not require "
            "any broader understanding."
        ),

        (
            "The principle suggests that external "
            "facilities alone are sufficient to "
            "achieve the desired outcome."
        ),

        (
            "The statement means that a person should "
            "accept information without examining or "
            "understanding it."
        ),

        (
            "The idea indicates that personal success "
            "depends mainly on comparison and competition "
            "with other people."
        ),

        (
            "The principle focuses exclusively on acquiring "
            "material resources and does not involve "
            "understanding or relationships."
        )

    ]

    for pattern in patterns:

        if len(distractors) >= 3:
            break

        distractor = pattern.format(
            concept=concept
        )

        if distractor not in distractors:

            distractors.append(
                distractor
            )

    # If needed, create additional contextual distractors

    for other in other_concepts:

        if len(distractors) >= 3:
            break

        distractor = (
            "The passage is primarily suggesting that "
            + other
            + " alone should be treated as the complete "
            "solution to the situation."
        )

        if distractor not in distractors:

            distractors.append(
                distractor
            )

    return distractors[:3]


# ------------------------------------------------------------
# 12. CREATE OPTIONS
# ------------------------------------------------------------

def create_options(
    correct_answer,
    distractors
):

    choices = [
        correct_answer
    ]

    choices.extend(
        distractors
    )

    random.shuffle(
        choices
    )

    letters = [
        "A",
        "B",
        "C",
        "D"
    ]

    options = {}

    correct_letter = ""

    for letter, choice in zip(
        letters,
        choices
    ):

        options[letter] = choice

        if choice == correct_answer:

            correct_letter = letter

    return options, correct_letter


# ------------------------------------------------------------
# 13. LONG EXPLANATION
# ------------------------------------------------------------

def create_explanation(
    concept,
    sentence,
    question_type
):

    explanation = (

        "The correct answer is supported by the context of the "
        "learning material rather than by the presence of a single "
        "keyword. The passage explains the idea in the following "
        "context: "

        + sentence.strip()

        + " "

        "This context is important because the learning material "
        "presents the idea as part of a broader discussion rather "
        "than as an isolated definition. The learner therefore "
        "needs to understand how the idea relates to the surrounding "
        "concepts and the purpose of the discussion. "

        "In this question, the important point is to recognize "
        "the meaning conveyed by the complete statement and apply "
        "that meaning to the question. Simply identifying a word "
        "that appears in the passage would not demonstrate the "
        "required understanding. "

        "The principle is connected with the concept of "

        + concept

        + ", but the answer is based on the meaning of the "
        "passage and its context. This type of understanding helps "
        "the learner apply the knowledge to unfamiliar situations "
        "instead of relying only on memorization."

    )

    return explanation


# ------------------------------------------------------------
# 14. OPTION EXPLANATIONS
# ------------------------------------------------------------

def create_option_explanations(
    options,
    correct_letter
):

    explanations = {}

    for letter in [
        "A",
        "B",
        "C",
        "D"
    ]:

        if letter == correct_letter:

            explanations[letter] = (
                "Correct. This option is consistent with the "
                "meaning and context of the learning material. "
                "It demonstrates understanding of the principle "
                "rather than simply matching a keyword."
            )

        else:

            explanations[letter] = (
                "Incorrect. Although this option may appear "
                "related to the general subject, it does not "
                "accurately represent the specific meaning or "
                "context presented in the learning material."
            )

    return explanations


# ------------------------------------------------------------
# 15. DIFFICULTY DISTRIBUTION
# ------------------------------------------------------------

def create_difficulties(total):

    easy_count = round(
        total * 0.40
    )

    medium_count = round(
        total * 0.35
    )

    hard_count = (
        total
        - easy_count
        - medium_count
    )

    difficulties = (
        ["Easy"] * easy_count
        + ["Medium"] * medium_count
        + ["Hard"] * hard_count
    )

    random.shuffle(
        difficulties
    )

    return difficulties


# ------------------------------------------------------------
# 16. CREATE ONE MCQ
# ------------------------------------------------------------

def build_mcq(
    number,
    concept,
    sentence,
    difficulty,
    question_type,
    concepts
):

    template = random.choice(
        TEMPLATES[question_type]
    )

    question = (
        template
        + "\n\n"
        + '"'
        + sentence.strip()
        + '"'
    )

    correct_answer = create_correct_answer(
        concept,
        sentence,
        question_type
    )

    # Safety check
    if forbidden_answer(
        correct_answer,
        concept
    ):

        correct_answer = (
            "The passage should be understood within "
            "the broader context presented by the learning "
            "material and applied according to the principle "
            "explained in the discussion."
        )

    distractors = create_distractors(
        concept,
        concepts,
        question_type
    )

    options, correct_letter = create_options(
        correct_answer,
        distractors
    )

    explanation = create_explanation(
        concept,
        sentence,
        question_type
    )

    option_explanations = create_option_explanations(
        options,
        correct_letter
    )

    topic = determine_topic(
        concept,
        sentence
    )

    related = get_related_concepts(
        concept,
        concepts
    )

    return {

        "id":
            "Q"
            + str(number).zfill(3),

        "topic":
            topic,

        "concept":
            concept.title(),

        "difficulty":
            difficulty,

        "question_type":
            question_type,

        "question":
            question,

        "options":
            options,

        "correct_answer":
            correct_letter,

        "explanation":
            explanation,

        "option_explanations":
            option_explanations,

        "takeaway":
            (
                "Key Takeaway: Understand the complete idea "
                "and its context rather than memorizing an "
                "individual word."
            ),

        "source_text":
            sentence,

        "related_concepts":
            related
    }


# ------------------------------------------------------------
# 17. DUPLICATE DETECTION
# ------------------------------------------------------------

def question_signature(
    question
):

    text = question.lower()

    text = re.sub(
        r"[^a-z0-9 ]",
        "",
        text
    )

    words = text.split()

    # Remove very common words
    stop_words = {
        "the",
        "a",
        "an",
        "of",
        "in",
        "is",
        "to",
        "and",
        "the",
        "which",
        "what",
        "according"
    }

    words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(
        words[:25]
    )


# ------------------------------------------------------------
# 18. GENERATE MCQS
# ------------------------------------------------------------

def generate_mcqs(
    text,
    number_of_questions=100
):

    text = clean_text(
        text
    )

    sentences = get_sentences(
        text
    )

    if not sentences:

        return []


    concepts = find_concepts(
        text
    )

    # Fallback if predefined concepts aren't found

    if not concepts:

        words = re.findall(
            r"\b[A-Za-z]{6,}\b",
            text
        )

        words = [
            word
            for word in words
            if word.lower()
            not in {
                "according",
                "following",
                "learning",
                "material",
                "education"
            }
        ]

        concepts = list(
            dict.fromkeys(
                words
            )
        )[:30]


    # --------------------------------------------------------
    # Create source pairs
    # --------------------------------------------------------

    pairs = []

    for concept in concepts:

        sources = concept_sources(
            concept,
            sentences
        )

        for source in sources:

            pair = (
                concept,
                source
            )

            if pair not in pairs:

                pairs.append(
                    pair
                )


    # Add general sentences if required

    if len(pairs) < number_of_questions:

        shuffled_sentences = sentences.copy()

        random.shuffle(
            shuffled_sentences
        )

        for sentence in shuffled_sentences:

            concept = random.choice(
                concepts
            )

            pairs.append(
                (
                    concept,
                    sentence
                )
            )


    if not pairs:

        return []


    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    difficulties = create_difficulties(
        number_of_questions
    )


    questions = []

    used_signatures = set()

    used_pairs = set()


    # --------------------------------------------------------
    # Generate questions
    # --------------------------------------------------------

    attempts = 0

    maximum_attempts = (
        number_of_questions * 50
    )


    while (
        len(questions)
        < number_of_questions
        and attempts
        < maximum_attempts
    ):

        attempts += 1

        concept, sentence = random.choice(
            pairs
        )

        difficulty = difficulties[
            len(questions)
        ]

        question_type = random.choice(
            QUESTION_TYPES
        )

        pair_key = (
            concept,
            sentence,
            question_type
        )

        if pair_key in used_pairs:

            continue

        used_pairs.add(
            pair_key
        )

        mcq = build_mcq(

            len(questions) + 1,

            concept,

            sentence,

            difficulty,

            question_type,

            concepts
        )

        signature = question_signature(
            mcq["question"]
        )

        if signature in used_signatures:

            continue

        used_signatures.add(
            signature
        )

        questions.append(
            mcq
        )


    # --------------------------------------------------------
    # Final numbering
    # --------------------------------------------------------

    for index, question in enumerate(
        questions,
        start=1
    ):

        question["id"] = (
            "Q"
            + str(index).zfill(3)
        )


    return questions