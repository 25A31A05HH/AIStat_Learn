import re
import random


# ============================================================
# AIStat Learn - Intelligent MCQ Generator
# ============================================================


# ------------------------------------------------------------
# 1. CLEAN TEXT
# ------------------------------------------------------------

def clean_text(text):
    if not text:
        return ""

    text = str(text)

    text = text.replace("\x00", " ")
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------------------------
# 2. SPLIT INTO SENTENCES
# ------------------------------------------------------------

def get_sentences(text):

    text = clean_text(text)

    if not text:
        return []

    # Split even when punctuation is at the end of the text
    sentences = re.split(
        r"(?<=[.!?])\s+|(?<=[.!?])$",
        text
    )

    result = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        words = sentence.split()

        # Accept shorter sentences too
        if len(words) >= 5:

            if not sentence.isupper():

                result.append(sentence)

    # If sentence splitting produced nothing,
    # create chunks from the text.
    if not result:

        words = text.split()

        if len(words) >= 5:

            chunk_size = 25

            for i in range(
                0,
                len(words),
                chunk_size
            ):

                chunk = " ".join(
                    words[i:i + chunk_size]
                )

                if len(chunk.split()) >= 5:
                    result.append(chunk)

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
        concept
        + " "
        + sentence
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
        c
        for c in concepts
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
# 9. CREATE CORRECT ANSWER
# ------------------------------------------------------------

def create_correct_answer(
    concept,
    sentence,
    question_type
):

    sentence = sentence.strip()

    return (
        "The principle described in the passage should be "
        "understood in its broader context and applied by "
        "considering the meaning and purpose explained in "
        "the learning material. This interpretation is "
        "consistent with the idea presented in the passage."
    )


# ------------------------------------------------------------
# 10. CREATE WRONG ANSWERS
# ------------------------------------------------------------

def create_distractors(
    concept,
    concepts,
    question_type
):

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
            "depends mainly on comparison and "
            "competition with other people."
        ),

        (
            "The principle focuses exclusively on "
            "acquiring material resources and does not "
            "involve understanding or relationships."
        )

    ]

    distractors = []

    random.shuffle(patterns)

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

    return distractors[:3]


# ------------------------------------------------------------
# 11. CREATE OPTIONS
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

    # Guarantee 4 options
    while len(choices) < 4:

        choices.append(
            "The idea should be understood differently "
            "from the context presented in the material."
        )

    random.shuffle(choices)

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
        choices[:4]
    ):

        options[letter] = choice

        if choice == correct_answer:
            correct_letter = letter

    return options, correct_letter


# ------------------------------------------------------------
# 12. EXPLANATION
# ------------------------------------------------------------

def create_explanation(
    concept,
    sentence,
    question_type
):

    return (
        "The correct answer is supported by the context of "
        "the learning material. The passage discusses "
        + concept
        + " as part of a broader idea. The learner should "
        "therefore understand the complete meaning of the "
        "statement instead of relying only on individual "
        "keywords."
    )


# ------------------------------------------------------------
# 13. OPTION EXPLANATIONS
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
                "This option is consistent with the "
                "meaning and context of the learning material."
            )

        else:

            explanations[letter] = (
                "This option does not accurately represent "
                "the specific meaning presented in the "
                "learning material."
            )

    return explanations


# ------------------------------------------------------------
# 14. DIFFICULTY DISTRIBUTION
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
# 15. CREATE ONE MCQ
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
                "Key Takeaway: Understand the complete "
                "idea and its context rather than "
                "memorizing an individual word."
            ),

        "source_text":
            sentence,

        "related_concepts":
            related

    }


# ------------------------------------------------------------
# 16. DUPLICATE DETECTION
# ------------------------------------------------------------

def question_signature(question):

    text = question.lower()

    text = re.sub(
        r"[^a-z0-9 ]",
        "",
        text
    )

    words = text.split()

    stop_words = {
        "the",
        "a",
        "an",
        "of",
        "in",
        "is",
        "to",
        "and",
        "which",
        "what",
        "according",
        "passage"
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
# 17. GENERATE MCQs
# ------------------------------------------------------------

def generate_mcqs(
    text,
    number_of_questions=10
):

    text = clean_text(text)

    if not text:
        return []

    sentences = get_sentences(text)

    if not sentences:
        return []

    # --------------------------------------------------------
    # Find concepts
    # --------------------------------------------------------

    concepts = find_concepts(text)

    # Generic fallback concepts
    if not concepts:

        words = re.findall(
            r"\b[A-Za-z]{5,}\b",
            text
        )

        ignored = {
            "according",
            "following",
            "learning",
            "material",
            "education",
            "which",
            "should",
            "their",
            "there",
            "about",
            "these",
            "those"
        }

        words = [
            word
            for word in words
            if word.lower() not in ignored
        ]

        concepts = list(
            dict.fromkeys(
                words
            )
        )[:30]

    if not concepts:

        concepts = [
            "learning"
        ]

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
                pairs.append(pair)

    # Add general sentence pairs
    if len(pairs) < number_of_questions:

        for sentence in sentences:

            concept = random.choice(
                concepts
            )

            pair = (
                concept,
                sentence
            )

            if pair not in pairs:
                pairs.append(pair)

    # If still not enough pairs, reuse sentences
    if not pairs:

        for sentence in sentences:

            pairs.append(
                (
                    concepts[0],
                    sentence
                )
            )

    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    difficulties = create_difficulties(
        number_of_questions
    )

    # --------------------------------------------------------
    # Generate questions
    # --------------------------------------------------------

    questions = []

    used_signatures = set()

    attempts = 0

    maximum_attempts = (
        number_of_questions * 100
    )

    while (
        len(questions) < number_of_questions
        and attempts < maximum_attempts
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
