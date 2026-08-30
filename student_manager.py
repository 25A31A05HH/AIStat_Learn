import json
import os
import hashlib


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FOLDER = "student_data"


# ============================================================
# CREATE DATA FOLDER
# ============================================================

def create_data_folder():

    if not os.path.exists(DATA_FOLDER):

        os.makedirs(DATA_FOLDER)


# ============================================================
# CREATE STUDENT ID
# ============================================================

def create_student_id(name, student_id):

    text = (
        str(name).strip().lower()
        + "_"
        + str(student_id).strip().lower()
    )

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()[:12]


# ============================================================
# STUDENT FILE PATH
# ============================================================

def get_student_file(student_key):

    create_data_folder()

    return os.path.join(
        DATA_FOLDER,
        f"{student_key}.json"
    )


# ============================================================
# CREATE STUDENT PROFILE
# ============================================================

def create_student(
    name,
    student_id,
    course,
    year
):

    create_data_folder()

    student_key = create_student_id(
        name,
        student_id
    )

    student = {

        "student_key":
            student_key,

        "name":
            name.strip(),

        "student_id":
            student_id.strip(),

        "course":
            course,

        "year":
            year,

        "assessments": []
    }


    file_path = get_student_file(
        student_key
    )


    # Don't overwrite an existing student.

    if os.path.exists(file_path):

        return load_student(
            student_key
        )


    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            student,
            file,
            indent=4,
            ensure_ascii=False
        )


    return student


# ============================================================
# LOAD STUDENT
# ============================================================

def load_student(student_key):

    file_path = get_student_file(
        student_key
    )


    if not os.path.exists(file_path):

        return None


    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except Exception:

        return None


# ============================================================
# SAVE STUDENT
# ============================================================

def save_student(student):

    student_key = student.get(
        "student_key"
    )


    if not student_key:

        return False


    file_path = get_student_file(
        student_key
    )


    try:

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                student,
                file,
                indent=4,
                ensure_ascii=False
            )


        return True


    except Exception:

        return False


# ============================================================
# ADD ASSESSMENT TO STUDENT
# ============================================================

def add_student_assessment(
    student_key,
    assessment
):

    student = load_student(
        student_key
    )


    if student is None:

        return False


    if "assessments" not in student:

        student["assessments"] = []


    student["assessments"].append(
        assessment
    )


    return save_student(
        student
    )


# ============================================================
# GET STUDENT ASSESSMENTS
# ============================================================

def get_student_assessments(
    student_key
):

    student = load_student(
        student_key
    )


    if student is None:

        return []


    return student.get(
        "assessments",
        []
    )


# ============================================================
# GET LATEST STUDENT ASSESSMENT
# ============================================================

def get_latest_student_assessment(
    student_key
):

    assessments = get_student_assessments(
        student_key
    )


    if not assessments:

        return None


    return assessments[-1]


# ============================================================
# GET STUDENT PROFILE
# ============================================================

def get_student_profile(
    student_key
):

    return load_student(
        student_key
    )


# ============================================================
# UPDATE STUDENT PROFILE
# ============================================================

def update_student_profile(
    student_key,
    name=None,
    course=None,
    year=None
):

    student = load_student(
        student_key
    )


    if student is None:

        return False


    if name is not None:

        student["name"] = name.strip()


    if course is not None:

        student["course"] = course


    if year is not None:

        student["year"] = year


    return save_student(
        student
    )


# ============================================================
# LIST ALL STUDENTS
# ============================================================

def list_students():

    create_data_folder()

    students = []


    for filename in os.listdir(
        DATA_FOLDER
    ):

        if not filename.endswith(
            ".json"
        ):

            continue


        file_path = os.path.join(
            DATA_FOLDER,
            filename
        )


        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                student = json.load(
                    file
                )


                students.append(
                    student
                )


        except Exception:

            continue


    return students


# ============================================================
# DELETE STUDENT
# ============================================================

def delete_student(
    student_key
):

    file_path = get_student_file(
        student_key
    )


    if os.path.exists(file_path):

        os.remove(
            file_path
        )

        return True


    return False