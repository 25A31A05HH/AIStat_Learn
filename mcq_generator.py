import re
import random


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Clean and normalize input text."""
    if not text:
        return ""

    text = str(text)

    # Remove null characters
    text = text.replace("\x00", " ")

    # Replace new lines and tabs with spaces
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SENTENCE EXTRACTION
# ============================================================

def get_sentences(text):
    """Extract usable sentences from the text."""

    text = clean_text(text)

    if not text:
        return []

    # Split at ., ! or ?
    sentences = re.split(r"(?<=[.!?])\s+", text)

    result = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        words = sentence.split()

        # Accept sentences with 5 or more words
        if len(words) >= 5:
            result.append(sentence)

    # If there are no proper sentences,
    # create chunks from the text.
    if not result:
        words = text.split()

        if len(words) >= 5:
            chunk_size = 25

            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])

                if len(chunk.split()) >= 5:
                    result.append(chunk)

    return result


# ============================================================
# CONCEPTS
# ============================================================

CONCEPTS = [
    "python",
    "programming",
    "variables",
    "loops",
    "functions",
    "lists",
    "data",
    "algorithm",
    "software",
    "computer",
    "technology",
    "learning",
    "education",
    "database",
    "artificial intelligence",
    "machine learning",
    "cloud computing",
    "cyber security",
    "data science",
    "communication",
    "problem solving"
]


def find_concepts(sentence):
    """Find known concepts in a sentence."""

    sentence_lower = sentence.lower()

    found = []

    for concept in CONCEPTS:
        if concept.lower() in sentence_lower:
            found.append(concept)

    return found


# ============================================================
# TOPIC DETECTION
# ============================================================

def determine_topic(text):
    """Determine a simple topic from the text."""

    text_lower = text.lower()

    topic_keywords = {
        "Python": [
            "python",
            "variables",
            "lists",
            "tuples",
            "dictionary",
            "function",
            "loop"
        ],
        "Programming": [
            "programming",
            "code",
            "software",
            "algorithm"
        ],
        "Artificial Intelligence": [
            "artificial intelligence",
            "ai",
            "intelligent system"
        ],
        "Machine Learning": [
            "machine learning",
            "model",
            "training",
            "dataset"
        ],
        "Data Science": [
            "data science",
            "data analysis",
            "statistics",
            "visualization"
        ],
        "Cloud Computing": [
            "cloud",
            "aws",
            "azure",
            "google cloud"
        ],
        "Cyber Security": [
            "cyber",
            "security",
            "encryption",
            "hacking"
        ]
    }

    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return topic

    return "General Learning"


# ============================================================
# RELATED CONCEPTS
# ============================================================

def get_related_concepts(concept):
    """Return related concepts."""

    relationships = {
        "python": ["programming", "variables", "functions", "loops", "lists"],
        "programming": ["python", "algorithm", "software", "functions"],
        "variables": ["python", "data", "programming"],
        "loops": ["python", "programming", "algorithm"],
        "functions": ["python", "programming", "software"],
        "lists": ["python", "data", "variables"],
        "artificial intelligence": ["machine learning", "data science"],
        "machine learning": ["artificial intelligence", "data science"],
        "data science": ["statistics", "machine learning", "data"],
        "cloud computing": ["software", "technology", "data"],
        "cyber security": ["technology", "software", "data"]
    }

    return relationships.get(
        concept.lower(),
        ["learning", "education", "problem solving"]
    )


# ============================================================
# QUESTION TYPES
# ============================================================

QUESTION_TYPES = [
    "concept",
    "understanding",
    "application",
    "purpose",
    "identification",
    "knowledge",
    "reasoning",
    "true_statement",
    "best_description",
    "practical"
]


# ============================================================
# CORRECT ANSWER CREATION
# ============================================================

def create_correct_answer(sentence, concept, question_type):
    """Create a correct answer based on the source sentence."""

    sentence = sentence.strip()

    if question_type == "concept":
        return sentence

    if question_type == "understanding":
        return f"{concept.capitalize()} is explained in the context of: {sentence}"

    if question_type == "application":
        return f"It can be applied according to the idea described in the sentence."

    if question_type == "purpose":
        return f"It is used for the purpose described in the given learning material."

    if question_type == "identification":
        return f"The statement is mainly related to {concept}."

    if question_type == "knowledge":
        return sentence

    if question_type == "reasoning":
        return f"The statement correctly explains the relationship involving {concept}."

    if question_type == "true_statement":
        return sentence

    if question_type == "best_description":
        return sentence

    if question_type == "practical":
        return f"A practical example follows the concept described in the learning material."

    return sentence


# ============================================================
# DISTRACTORS
# ============================================================

def create_distractors(sentence, concept, question_type):
    """Create incorrect but reasonable answer options."""

    distractors = [
        f"{concept.capitalize()} is unrelated to the topic.",
        f"{concept.capitalize()} is used only for entertainment.",
        f"{concept.capitalize()} does not have any practical use.",
        f"The statement describes a completely different concept.",
        f"The concept is applicable only outside technology.",
        f"The concept cannot be used in programming or learning.",
        f"The statement is mainly about an unrelated subject.",
        f"{concept.capitalize()} is used only for storing images.",
        f"The concept has no connection with the given material.",
        f"The statement provides no useful information about the topic."
    ]

    # Remove any accidental duplicate of the correct answer
    clean_sentence = sentence.lower().strip()

    result = []

    for item in distractors:
        if item.lower().strip() != clean_sentence:
            if item not in result:
                result.append(item)

    return result


# ============================================================
# OPTIONS
# ============================================================

def create_options(correct_answer, distractors):
    """Create four shuffled options."""

    options = [correct_answer]

    for distractor in distractors:
        if distractor not in options:
            options.append(distractor)

        if len(options) == 4:
            break

    # Safety fallback
    while len(options) < 4:
        options.append(
            "None of the other statements correctly describe the concept."
        )

    random.shuffle(options)

    letters = ["A", "B", "C", "D"]

    option_dict = {}

    correct_letter = None

    for letter, option in zip(letters, options):
        option_dict[letter] = option

        if option == correct_answer:
            correct_letter = letter

    return option_dict, correct_letter


# ============================================================
# EXPLANATION
# ============================================================

def create_explanation(sentence, concept, correct_answer):
    """Create explanation for the correct answer."""

    return (
        f"The correct answer is based on the learning material. "
        f"The sentence explains the concept of {concept}. "
        f"Therefore, the selected answer matches the information "
        f"provided in the source material."
    )


# ============================================================
# BUILD ONE MCQ
# ============================================================

def build_mcq(sentence, concept, question_type, question_id):
    """Build one complete MCQ."""

    topic = determine_topic(sentence)

    correct_answer = create_correct_answer(
        sentence,
        concept,
        question_type
    )

    distractors = create_distractors(
        sentence,
        concept,
        question_type
    )

    options, correct_letter = create_options(
        correct_answer,
        distractors
    )

    # Different question wording
    if question_type == "concept":
        question = (
            f"Which statement best represents the concept discussed "
            f"in the following learning material?\n\n{sentence}"
        )

    elif question_type == "understanding":
        question = (
            f"Which option best explains the following statement?\n\n"
            f"{sentence}"
        )

    elif question_type == "application":
        question = (
            f"How can the idea described in the following statement "
            f"be understood in practice?\n\n{sentence}"
        )

    elif question_type == "purpose":
        question = (
            f"What is the main purpose or role described in the "
            f"following statement?\n\n{sentence}"
        )

    elif question_type == "identification":
        question = (
            f"Which concept is mainly represented by the following "
            f"statement?\n\n{sentence}"
        )

    elif question_type == "knowledge":
        question = (
            f"According to the learning material, which statement "
            f"is correct?\n\n{sentence}"
        )

    elif question_type == "reasoning":
        question = (
            f"Which answer provides the best reasoning for the "
            f"following statement?\n\n{sentence}"
        )

    elif question_type == "true_statement":
        question = (
            f"Which of the following is the correct statement based "
            f"on the learning material?\n\n{sentence}"
        )

    elif question_type == "best_description":
        question = (
            f"Which option gives the best description of the idea "
            f"presented below?\n\n{sentence}"
        )

    else:
        question = (
            f"Which option represents a practical interpretation of "
            f"the following learning material?\n\n{sentence}"
        )

    explanation = create_explanation(
        sentence,
        concept,
        correct_answer
    )

    return {
        "id": question_id,
        "topic": topic,
        "concept": concept,
        "difficulty": "Medium",
        "question_type": question_type,
        "question": question,
        "options": options,
        "correct_answer": correct_letter,
        "explanation": explanation,
        "option_explanations": {
            "A": "Review the learning material carefully.",
            "B": "Review the learning material carefully.",
            "C": "Review the learning material carefully.",
            "D": "Review the learning material carefully."
        },
        "takeaway": (
            f"Remember the main idea related to {concept} "
            f"from the learning material."
        ),
        "source_text": sentence,
        "related_concepts": get_related_concepts(concept)
    }


# ============================================================
# MAIN MCQ GENERATOR
# ============================================================

def generate_mcqs(text, num_questions=10):
    """
    Generate MCQs from learning material.

    Parameters:
        text: learning material as a string
        num_questions: number of MCQs required

    Returns:
        List of MCQ dictionaries
    """

    # Clean input
    text = clean_text(text)

    if not text:
        return []

    # Get sentences
    sentences = get_sentences(text)

    # Emergency fallback for very short text
    if not sentences:
        words = text.split()

        if len(words) >= 3:
            sentences = [text]

    if not sentences:
        return []

    # Detect topic
    topic = determine_topic(text)

    # Find concepts from all sentences
    all_concepts = []

    for sentence in sentences:
        concepts = find_concepts(sentence)

        for concept in concepts:
            if concept not in all_concepts:
                all_concepts.append(concept)

    # Fallback concept
    if not all_concepts:
        all_concepts = [topic]

    questions = []

    # Generate questions
    question_id = 1

    # We deliberately cycle through sentences and question types.
    # This guarantees that the requested number of questions can
    # be generated even when the input contains only a few sentences.

    for i in range(num_questions):

        sentence = sentences[i % len(sentences)]

        concepts_in_sentence = find_concepts(sentence)

        if concepts_in_sentence:
            concept = concepts_in_sentence[i % len(concepts_in_sentence)]
        else:
            concept = all_concepts[i % len(all_concepts)]

        question_type = QUESTION_TYPES[
            i % len(QUESTION_TYPES)
        ]

        mcq = build_mcq(
            sentence,
            concept,
            question_type,
            question_id
        )

        questions.append(mcq)

        question_id += 1

    return questions


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_text = """
    Python is a programming language.
    Python supports variables, loops, functions and lists.
    Functions help programmers organize reusable code.
    Lists are used to store multiple values in Python.
    """

    questions = generate_mcqs(test_text, 5)

    print("=" * 60)
    print("MCQ GENERATOR TEST")
    print("=" * 60)

    print("Questions generated:", len(questions))

    for q in questions:
        print("\nQuestion:", q["question"])
        print("Options:")

        for letter, option in q["options"].items():
            print(f"{letter}. {option}")

        print("Correct Answer:", q["correct_answer"])
        print("Explanation:", q["explanation"])
        print("-" * 60)
