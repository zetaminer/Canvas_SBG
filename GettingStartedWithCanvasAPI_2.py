import requests
import json
import random
from canvasapi import Canvas

# Canvas API Configuration
API_URL = 'https://morenetlab.instructure.com'
TOKEN = 'YOUR_TOKEN_HERE'
canvas = Canvas(API_URL, TOKEN)
ACCOUNT_ID = 1
COURSE_ID = 515
DATA_FILE = "canvas_data.json"
DEFAULT_PASSWORD = "Pass123!"


# ==================== Utility Functions ==================== #



def load_token():
    with open("config.json", "r") as file:
        config = json.load(file)
    return config["TOKEN"]


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


def check_quiz_type(course_id, quiz_id):
    """Checks if a quiz is a Classic Quiz or a New Quiz."""
    course = canvas.get_course(course_id)
    quiz = course.get_quiz(quiz_id)

    if hasattr(quiz, 'quiz_engine'):
        quiz_type = "New Quiz" if quiz.quiz_engine == 2 else "Classic Quiz"
        print(f"The quiz '{quiz.title}' is a {quiz_type}.")
    else:
        print("Could not determine quiz type.")


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
    TOKEN = load_token()  # load token from private json, if you hard code it you can remove this line
    # Create and enroll students, then accept invites
    # create_test_students()
    # enroll_students_to_course(COURSE_ID)

    # Create a quiz and save details
    # create_quiz_from_json(COURSE_ID, "Test Quiz")

    # Uncomment to remove test students
    # remove_students_from_lab()
