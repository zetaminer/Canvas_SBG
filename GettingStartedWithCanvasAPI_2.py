import requests
import json
import random
from canvasapi import Canvas

# Canvas API Configuration
API_URL = 'https://morenetlab.instructure.com'

ACCOUNT_ID = 1

# Global Variables (Initialized in `initialize_canvas()`)
TOKEN = None
COURSE_ID = None
canvas = None


DATA_FILE = "canvas_data.json" # stores the student id and quiz ids so that they can be easily removed
DEFAULT_PASSWORD = "Pass123!"


# ==================== Utility Functions ==================== #


def initialize_canvas():
    """Loads the API token and course ID from config.json, then initializes the Canvas object."""
    global TOKEN, COURSE_ID, canvas, HEADERS  # Declare global variables

    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            TOKEN = config.get("TOKEN")
            COURSE_ID = config.get("COURSE_ID")

        if not TOKEN or not COURSE_ID:
            raise ValueError("Missing TOKEN or COURSE_ID in config.json")

        # Initialize Canvas API instance
        canvas = Canvas(API_URL, TOKEN)
        HEADERS = {"Authorization": f"Bearer {TOKEN}"}
        print("Canvas API initialized successfully.")

    except FileNotFoundError:
        print("Error: config.json not found.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def save_data_to_file(data):
    """Saves data to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {DATA_FILE}")

def load_data_from_file():
    """Loads data from a JSON file."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"students": [], "quizzes": []}


# ==================== Canvas API Functions ==================== #

def create_test_students():
    """Creates 3 test students and saves their details for later use."""
    account = canvas.get_account(ACCOUNT_ID)
    data = load_data_from_file()
    students = []

    for i in range(1, 4):
        name = f"Test Student{i}"
        email = f"teststudent{i}@example.com"

        student_pseudonym = {
            "unique_id": email,
            "password": DEFAULT_PASSWORD,
            "send_confirmation": False
        }

        student_info = {
            "user": {"name": name, "skip_registration": True},
            "communication_channel": {
                "type": "email",
                "address": email,
                "skip_confirmation": True
            }
        }

        try:
            new_student = account.create_user(pseudonym=student_pseudonym, **student_info)
            students.append({
                "id": new_student.id,
                "name": name,
                "email": email,
                "password": DEFAULT_PASSWORD
            })
            print(f"Created student: {name} (ID: {new_student.id})")
        except Exception as e:
            print(f"Failed to create student {name}: {e}")

    data["students"] = students
    save_data_to_file(data)

def enroll_students_to_course(course_id):
    """Enrolls the created test students into a given course and accepts invites."""
    course = canvas.get_course(course_id)
    data = load_data_from_file()

    for student in data["students"]:
        enrollment_data = {
            "user_id": student["id"],
            "type": "StudentEnrollment",
            "enrollment_state": "invited",
            "send_confirmation": False
        }
        try:
            course.enroll_user(student["id"], **enrollment_data)
            print(f"Enrolled {student['name']} (ID: {student['id']}) into Course {course_id}")

        except Exception as e:
            print(f"Failed to enroll {student['name']}: {e}")

    accept_all_course_invites(course_id)

def accept_all_course_invites(course_id):
    """Accepts all pending enrollment invitations for a given course."""
    course = canvas.get_course(course_id)
    enrollments = course.get_enrollments()
    pending_enrollments = [e for e in enrollments if e.enrollment_state == "invited"]

    for enrollment in pending_enrollments:
        student_id = enrollment.user_id
        enrollment_id = enrollment.id

        accept_url = f"{API_URL}/api/v1/courses/{course_id}/enrollments/{enrollment_id}/accept"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        params = {"as_user_id": student_id}

        response = requests.post(accept_url, headers=headers, params=params)

        if response.status_code == 200:
            print(f"Enrollment accepted for Student ID: {student_id}")
        else:
            print(f"Failed to accept enrollment for Student ID: {student_id}")

def remove_students_from_lab():
    """Completely deletes test students from the Canvas account."""
    data = load_data_from_file()
    account = canvas.get_account(ACCOUNT_ID)

    for student in data["students"]:
        try:
            # Use delete_user() to permanently remove the user
            deleted_user = account.delete_user(student["id"])
            print(f"Successfully deleted user: {student['name']} (ID: {student['id']})")

        except Exception as e:
            print(f"Failed to delete {student['name']}: {e}")

    # Clear student data from file
    data["students"] = []
    save_data_to_file(data)


# ==================== Quiz Functions ==================== #

def create_quiz_from_json(course_id, quiz_title, json_file='quiz_data.json'):
    """Creates a quiz in a Canvas course using data from a JSON file and saves quiz info."""
    with open(json_file, "r") as file:
        quiz_data = json.load(file)

    questions = quiz_data.pop("questions", [])
    quiz_data["title"] = quiz_title

    course = canvas.get_course(int(course_id))
    quiz = course.create_quiz(quiz=quiz_data)
    print(f"Quiz created: {quiz.title} (ID: {quiz.id})")

    for question in questions:
        formatted_question = {
            "question_name": question.get("question_name", "Default Name"),
            "question_text": question.get("question_text", ""),
            "question_type": question.get("question_type", "multiple_choice_question"),
            "points_possible": question.get("points_possible", 1),
            "answers": question.get("answers", [])
        }
        quiz.create_question(question=formatted_question)

    # Save quiz details to the file
    data = load_data_from_file()
    quiz_entry = {
        "id": quiz.id,
        "title": quiz.title,
        "course_id": course_id
    }
    data["quizzes"].append(quiz_entry)
    save_data_to_file(data)

    def delete_previous_quiz_and_create_new(course_id, quiz_title, json_file='quiz_data.json'):
        """
        Deletes the most recently created quiz and creates a new one.
        Saves new quiz details to canvas_data.json.
        """
        data = load_data_from_file()

        # Delete previous quiz
        if data["quizzes"]:
            last_quiz = data["quizzes"].pop()  # Get last quiz
            try:
                course = canvas.get_course(course_id)
                quiz = course.get_quiz(last_quiz["id"])
                quiz.delete()
                print(f"Deleted previous quiz: {last_quiz['title']} (ID: {last_quiz['id']})")
            except Exception as e:
                print(f"Failed to delete quiz {last_quiz['title']}: {e}")

        # Create new quiz
        try:
            with open(json_file, "r") as file:
                quiz_data = json.load(file)

            questions = quiz_data.pop("questions", [])
            quiz_data["title"] = quiz_title

            course = canvas.get_course(course_id)
            quiz = course.create_quiz(quiz=quiz_data)
            print(f"Created new quiz: {quiz.title} (ID: {quiz.id})")

            for question in questions:
                formatted_question = {
                    "question_name": question.get("question_name", "Default Name"),
                    "question_text": question.get("question_text", ""),
                    "question_type": question.get("question_type", "multiple_choice_question"),
                    "points_possible": question.get("points_possible", 1),
                    "answers": question.get("answers", [])
                }
                quiz.create_question(question=formatted_question)

            # Save new quiz details
            new_quiz_entry = {"id": quiz.id, "title": quiz.title, "course_id": course_id}
            data["quizzes"].append(new_quiz_entry)
            save_data_to_file(data)

        except Exception as e:
            print(f"Failed to create new quiz: {e}")

def check_quiz_type(course_id, quiz_id):
    """Checks if a quiz is a Classic Quiz or a New Quiz."""
    course = canvas.get_course(course_id)
    quiz = course.get_quiz(quiz_id)

    if hasattr(quiz, 'quiz_engine'):
        quiz_type = "New Quiz" if quiz.quiz_engine == 2 else "Classic Quiz"
        print(f"The quiz '{quiz.title}' is a {quiz_type}.")
    else:
        print("Could not determine quiz type.")

def get_quiz_answer_key(course_id, quiz_id):
    """
    Retrieve the correct answers for all quiz questions (requires instructor/admin token).
    """
    try:
        course = canvas.get_course(course_id)
        quiz = course.get_quiz(quiz_id)
        questions = quiz.get_questions()

        answer_key = {}

        for question in questions:
            question_id = question.id
            possible_answers = question.answers  # List of answer choices

            # Find the correct answer (weight = 100)
            correct_answer = next((ans for ans in possible_answers if ans.get("weight", 0) == 100), None)

            if correct_answer:
                answer_key[question_id] = correct_answer["id"]  # Store the correct answer ID

        print(f"✅ Retrieved answer key for Quiz {quiz_id}: {answer_key}")
        return answer_key

    except Exception as e:
        print(f"❌ Failed to get answer key for Quiz {quiz_id}: {e}")
        return None

def get_quiz(quiz_id, student_id):
    """Retrieve quiz details while masquerading as a student."""
    url = f"{API_URL}/courses/{COURSE_ID}/quizzes/{quiz_id}?as_user_id={student_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        quiz_data = response.json()
        print("Quiz Details:", quiz_data)
        return quiz_data
    else:
        print("Failed to fetch quiz:", response.text)
        return None

def start_quiz(course_id, quiz_id, student_id):
    """
    Start a quiz-taking session for a student using masquerading.

    :param course_id: The ID of the course.
    :param quiz_id: The ID of the quiz.
    :param student_id: The ID of the student.
    :return: QuizSubmission object or None if an error occurs.
    """
    try:
        course = canvas.get_course(course_id)
        quiz = course.get_quiz(quiz_id)

        # Start quiz attempt while masquerading
        submission = quiz.create_submission(as_user_id=student_id)

        print(f"✅ Started quiz {quiz_id} for Student {student_id}: {submission}")
        return submission
    except Exception as e:
        print(f"❌ Failed to start quiz for Student {student_id}: {e}")
        return None

def answer_quiz_questions(course_id, quiz_id, quiz_submission_id, student_id, answer_key, correct_questions):
    """
    Answer quiz questions using the instructor-provided answer key.
    """
    try:
        course = canvas.get_course(course_id)
        quiz = course.get_quiz(quiz_id)

        # ✅ Directly get submission instead of searching
        quiz_submission = quiz.get_quiz_submission(quiz_submission_id)

        if not quiz_submission:
            print(f"⚠️ Could not find submission {quiz_submission_id} for Student {student_id}.")
            return

        questions = quiz_submission.get_submission_questions()
        answers = []

        for i, question in enumerate(questions, start=1):
            question_id = question.id
            possible_answers = question.answers

            print(f"🔍 Debug: Question {i} Answers: {possible_answers}")

            if not possible_answers:
                print(f"⚠️ No answer choices found for Question {i}")
                continue

            # Determine if student should answer correctly
            if i in correct_questions:
                correct_answer_id = answer_key.get(question_id)  # Get correct answer ID
            else:
                incorrect_answers = [ans["id"] for ans in possible_answers if ans["id"] != answer_key.get(question_id)]
                correct_answer_id = incorrect_answers[0] if incorrect_answers else possible_answers[0]["id"]

            answers.append({"id": question_id, "answer": correct_answer_id})

        if answers:
            print(f"📤 Sending answers for Student {student_id}: {answers}")

            response = quiz_submission.answer_submission_questions(quiz_answers=answers)
            print(f"✅ Answers submitted for Student {student_id}, Response: {response}")

    except Exception as e:
        print(f"❌ Failed to submit answers for Student {student_id}: {e}")

def submit_quiz(course_id, quiz_id, quiz_submission, student_id):
    """
    Submit the quiz for grading.

    :param course_id: The ID of the course.
    :param quiz_id: The ID of the quiz.
    :param quiz_submission: The QuizSubmission object.
    :param student_id: The ID of the student.
    """
    try:
        quiz_submission.complete()
        print(f"✅ Quiz {quiz_id} submitted for Student {student_id}")
    except Exception as e:
        print(f"❌ Failed to submit quiz for Student {student_id}: {e}")

def complete_quiz_for_students_OLD(course_id, quiz_id, correct_answers_map):
    """
    Masquerades as each student and completes the quiz.
    """
    data = load_data_from_file()
    students = data["students"]

    # Retrieve the correct answer key (requires instructor/admin token)
    answer_key = get_quiz_answer_key(course_id, quiz_id)
    if not answer_key:
        print("❌ Failed to retrieve answer key. Exiting.")
        return

    for index, student in enumerate(students):
        student_id = student["id"]
        print(f"\n🚀 Masquerading as {student['name']} (ID: {student_id}) to take quiz {quiz_id}...")

        # Start the quiz and get the correct submission ID
        quiz_submission_id = start_quiz(course_id, quiz_id, student_id)
        if not quiz_submission_id:
            continue

        # Submit answers using the correct answer key
        correct_questions = correct_answers_map.get(index, [])
        answer_quiz_questions(course_id, quiz_id, quiz_submission_id, student_id, answer_key, correct_questions)

        # Submit quiz
        submit_quiz(course_id, quiz_id, quiz_submission_id, student_id)

        print(f"✅ Quiz {quiz_id} completed for {student['name']}\n")

def complete_quiz_for_students(course_id, quiz_id, correct_answers_map):
    """
    Masquerades as each student and completes the quiz.
    """
    data = load_data_from_file()
    students = data["students"]

    # Retrieve the correct answer key (requires instructor/admin token)
    answer_key = get_quiz_answer_key(course_id, quiz_id)
    if not answer_key:
        print("❌ Failed to retrieve answer key. Exiting.")
        return

    for index, student in enumerate(students):
        student_id = student["id"]
        print(f"\n🚀 Masquerading as {student['name']} (ID: {student_id}) to take quiz {quiz_id}...")

        # Start the quiz and get the correct submission ID
        quiz_submission_id = start_quiz(course_id, quiz_id, student_id)
        if not quiz_submission_id:
            continue

        # Prepare answers (only correct answers if specified)
        correct_questions = correct_answers_map.get(index, [])
        student_answers = {
            q_id: answer_key[q_id] if q_id in correct_questions else random.choice(list(answer_key.values()))
            for q_id in answer_key
        }

        # Submit answers using masquerading
        submit_answers_masquerading(course_id, quiz_id, quiz_submission_id, student_id, student_answers, TOKEN)

        # Submit quiz
        submit_quiz(course_id, quiz_id, quiz_submission_id, student_id)

        print(f"✅ Quiz {quiz_id} completed for {student['name']}\n")

def submit_answers_masquerading(course_id, quiz_id, quiz_submission_id, student_id, answers, admin_token):
    """
    Submit answers to a Canvas Quiz while masquerading as a student.

    :param course_id: The course ID
    :param quiz_id: The quiz ID
    :param quiz_submission_id: The student's quiz submission ID
    :param student_id: The student's ID (for masquerading)
    :param answers: A dictionary of question_id -> selected_answer_id
    :param admin_token: Your admin API token
    """

    # 🔹 Canvas API endpoint for submitting quiz answers (using API_URL dynamically)
    url = f"{API_URL}/api/v1/quiz_submissions/{quiz_submission_id}/questions"

    # 🔹 Authentication headers
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 🔹 Format request payload correctly
    payload = {
        "quiz_questions": [
            {"id": question_id, "answer": answer_id}
            for question_id, answer_id in answers.items()
        ]
    }

    # 🔹 Make the request with masquerading
    params = {"as_user_id": student_id}

    response = requests.post(url, json=payload, headers=headers, params=params)

    # 🔹 Handle response
    if response.status_code == 200:
        print(f"✅ Successfully submitted answers for Student {student_id}")
    else:
        print(f"❌ Failed to submit answers for Student {student_id}: {response.status_code} - {response.text}")


# ==================== Debugging & Testing Functions ==================== #

def test_get_courses():
    """Fetches and prints available courses."""
    courses = canvas.get_courses()
    print("Available Courses:")
    for course in courses:
        print(f"- {course.name} (ID: {course.id})")


def check_account_id():
    """Lists available accounts under the authenticated user."""
    accounts = canvas.get_accounts()
    for account in accounts:
        print(f"Account ID: {account.id} - Name: {account.name}")


def check_URL_Response():
    """Checks if the Canvas API URL is reachable."""
    response = requests.get(API_URL)
    print(f"API Response: {response.status_code}")


# ==================== Example Usage ==================== #

if __name__ == "__main__":

    initialize_canvas() # Call the function at the start of the script to ensure global values are set

    # Create and enroll students, then accept invites
    # create_test_students()
    # enroll_students_to_course(COURSE_ID)

    # Create a quiz and save details
    # create_quiz_from_json(COURSE_ID, "Test Quiz 4")

    correct_answers_map = {
        0: [1, 3],  # First student answers Q1, Q3 correctly
        1: [2, 4],  # Second student answers Q2, Q4 correctly
        2: [5, 6]  # Third student answers Q5, Q6 correctly
    }

    complete_quiz_for_students(course_id = COURSE_ID,quiz_id=808, correct_answers_map=correct_answers_map)

    # Uncomment to remove test students
    # remove_students_from_lab()
