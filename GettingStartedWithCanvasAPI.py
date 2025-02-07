from venv import create

from canvasapi import Canvas
import requests
import json
import random
import string
from questions import question_data_list
from requests.auth import HTTPBasicAuth

API_URL = 'https://morenetlab.instructure.com'
TOKEN = 'YOURTOKENHERE'
API_KEY = TOKEN
DEV_KEY = 'YOURDEVKEYHERE'
canvas = Canvas(API_URL, TOKEN)
ACCOUNT_ID = 1
# account = canvas.get_account(ACCOUNT_ID)

def canvas_object_print():
    query = """
    {
      account(id: "1") {
        name
        id
      }
    }
    """

    # Execute the GraphQL query
    response = canvas.graphql(query)
    print(response)

def check_URL_Response():
    response = requests.get(API_URL)  # + '/api/v1/users/me', auth=HTTPBasicAuth(API_KEY))
    print(response)

def test_get_courses():
    courses = canvas.get_courses()
    print(courses)
    print(courses[0])
    course = canvas.get_course(515)

def get_course_by_name(target_course_name: str):
    """Finds and returns a course by name from Canvas API."""

    courses = canvas.get_courses()
    if not courses:
        print("No courses found.")
        return None

    for course in courses:
        if course.name.lower() == target_course_name.lower():
            print(f"Course found: {course.name} (ID: {course.id})")
            return course  # Return immediately when found

    print("Course not found.")
    return None  # Explicitly return None if no match is found

def create_quiz_from_json(course_id, quiz_title, json_file='quiz_data.json'):
    """
    Reads quiz data and questions from a JSON file and creates a quiz in a Canvas course
    with a custom title.

    :param course_id: The ID of the Canvas course.
    :param quiz_title: The title to set for the quiz.
    :param json_file: Path to the JSON file containing quiz data and questions.
    """
    # Load quiz data from JSON
    with open(json_file, "r") as file:
        quiz_data = json.load(file)

    # Extract questions from the JSON
    questions = quiz_data.pop("questions", [])  # Remove questions from quiz data

    # Override title with the provided quiz_title
    quiz_data["title"] = quiz_title

    # Get the course
    course = canvas.get_course(int(course_id))  # Ensure course_id is an integer

    # Create the quiz
    quiz = course.create_quiz(quiz=quiz_data)  # Use keyword arguments
    print(f"✅ Quiz created: {quiz.title} (ID: {quiz.id})")

    # Add questions to the quiz
    for question in questions:
        # Debugging: Print question data before sending
        # print(f"➡ Adding Question: {question['question_text']}")

        # Ensure field names match API expectations
        formatted_question = {
            "question_name": question.get("question_name", "Default Name"),
            "question_text": question.get("question_text", ""),
            "question_type": question.get("question_type", "multiple_choice_question"),
            "points_possible": question.get("points_possible", 1),
            "answers": question.get("answers", [])
        }

        # Debug: Show formatted question before API call
        # print(f"🔍 Formatted Question Data: {formatted_question}")

        quiz.create_question(question = formatted_question)  # Unpack dictionary into keyword arguments
        # print(f"✅ Added question: {formatted_question['question_text']}")

    print("🎉 Quiz setup complete!")

def check_quiz_type(course_id, quiz_id):
    """
    Checks if a quiz is a Classic Quiz or a New Quiz.

    :param course_id: The ID of the Canvas course.
    :param quiz_id: The ID of the quiz.
    """
    course = canvas.get_course(course_id)
    quiz = course.get_quiz(quiz_id)

    if hasattr(quiz, 'quiz_engine'):
        if quiz.quiz_engine == 2:
            print(f"✅ The quiz '{quiz.title}' is a New Quiz.")
        else:
            print(f"✅ The quiz '{quiz.title}' is a Classic Quiz.")
    else:
        print("❌ Could not determine quiz type.")

def accept_all_course_invites(course_id):
    """
    Accept all pending enrollment invitations for a given course.
    :param course_id: The Canvas course ID.
    """
    try:
        # ✅ Step 1: Get the Course
        course = canvas.get_course(course_id)
        print(f"🔍 Fetching enrollments for Course ID: {course_id}")

        # ✅ Step 2: Get all enrollments
        enrollments = course.get_enrollments()

        # ✅ Step 3: Filter pending invitations
        pending_enrollments = [e for e in enrollments if e.enrollment_state == "invited"]

        if not pending_enrollments:
            print("✅ No pending invitations found.")
            return

        print(f"📝 Found {len(pending_enrollments)} pending invitations.")

        # ✅ Step 4: Accept each invitation by masquerading as the student
        for enrollment in pending_enrollments:
            student_id = enrollment.user_id
            enrollment_id = enrollment.id

            print(f"➡ Masquerading as Student ID: {student_id} to accept enrollment.")

            # API Request to Accept Invitation with Masquerading
            accept_url = f"{API_URL}/api/v1/courses/{course_id}/enrollments/{enrollment_id}/accept"
            headers = {
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            }
            params = {"as_user_id": student_id}

            response = requests.post(accept_url, headers=headers, params=params)

            # ✅ Check response
            if response.status_code == 200:
                print(f"🎉 Enrollment Accepted for Student ID: {student_id}")
            else:
                print(f"❌ Failed to Accept Enrollment for Student ID: {student_id}: {response.json()}")

    except Exception as e:
        print(f"❌ Error accepting invitations: {e}")

def generate_secure_password():
    """Generates a strong password with at least 8 characters."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def check_account_id():
    accounts = canvas.get_accounts()
    for account in accounts:
        print(f"Account ID: {account.id} - Name: {account.name}")

def create_students():
    """
    Creates multiple student accounts in Canvas.
    """
    # Get the Canvas account
    account = canvas.get_account(ACCOUNT_ID)

    # Student list
    students = [
        {"name": "Test Student1", "email": "student1@example.com"},
        {"name": "Test Student2", "email": "student2@example.com"},
        {"name": "Test Student3", "email": "student3@example.com"},
    ]

    for student in students:
        try:
            # Generate a strong password
            password = 'Pass123!'

            # Ensure unique login ID by appending a random number
            # unique_email = student["email"].split("@")[0] + f"{random.randint(1000,9999)}@" + student["email"].split("@")[1]

            # Define student user and login information
            student_pseudonym = {
                "unique_id": student["email"],
                "password": password,
                "send_confirmation": False  # Set to True to email confirmation
            }

            student_info = {
                "user": {
                    "name": student["name"],
                    "skip_registration": True,},
                "communication_channel": {
                    "type": "email",
                    "address": student["email"],
                    "skip_confirmation": True
                }
            }

            # ✅ Corrected call to `create_user()`
            new_student = account.create_user(pseudonym=student_pseudonym, **student_info)

            print(f"✅ Created student: {new_student.name} (ID: {new_student.id}) - Email: {student["email"]}")

        except Exception as e:
            print(f"❌ Failed to create student {student['name']}: {e}")

def enroll_students(course_id):
    courses = canvas.get_courses()
    course = canvas.get_course(course_id)
    student_ids = [612, 613, 614]

    for student_id in student_ids:
        enrollment_data = {
            "user_id": student_id,
            "type": "StudentEnrollment",  # This ensures they are added as a student
            "enrollment_state": "active",  # Makes sure they are enrolled immediately
            "send_confirmation": False,
            "skip_registration": True,
            "notify":False

        }
        try:
            enrollment = course.enroll_user(student_id, **enrollment_data)
            # enrollment.accept()
            print(f"✅ Enrolled User ID: {student_id}")
        except Exception as e:
            print(f"❌ Failed to enroll User ID {student_id}: {e}")

def submit_quiz_for_student(course_id, quiz_id, student_id, num_correct):
    """
    Submits a quiz for a student with a set number of questions answered correctly.
    :param course_id: The Canvas course ID.
    :param quiz_id: The Quiz ID.
    :param student_id: The student's Canvas user ID.
    :param num_correct: Number of questions to answer correctly.
    """
    try:
        # ✅ Step 1: Start the quiz submission as the student (Masquerading)
        start_quiz_url = f"{API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        params = {"as_user_id": student_id}  # Masquerading

        response = requests.post(start_quiz_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"❌ Failed to start quiz for student {student_id}: {response.json()}")
            return

        submission_data = response.json()
        submission_id = submission_data["quiz_submissions"][0]["id"]
        print(f"✅ Started quiz submission (Submission ID: {submission_id})")

        # ✅ Step 2: Get quiz questions (Use Admin ID, Not Masquerading)
        questions_url = f"{API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions"
        response = requests.get(questions_url, headers=headers)  # ❌ No Masquerading Here

        if response.status_code != 200:
            print(f"❌ Failed to fetch quiz questions: {response.json()}")
            return

        questions = response.json()
        print(f"📋 Retrieved {len(questions)} quiz questions.")

        if num_correct > len(questions):
            print(f"⚠ Requested {num_correct} correct answers, but quiz only has {len(questions)} questions.")
            num_correct = len(questions)

        # ✅ Step 3: Select random questions to answer correctly
        selected_correct_questions = random.sample(questions, num_correct)
        correct_answers_map = {}

        for question in selected_correct_questions:
            question_id = question["id"]
            if "answers" in question:
                # Find the correct answer
                correct_answer = next((a["id"] for a in question["answers"] if a["weight"] == 100), None)
                if correct_answer:
                    correct_answers_map[question_id] = correct_answer

        # ✅ Step 4: Submit answers (Masquerade Again)
        answer_url = f"{API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/questions"
        params = {"as_user_id": student_id}  # ✅ Switch Back to Student ID

        answers_payload = {
            "attempt": submission_id,
            "questions": []
        }

        for question in questions:
            question_id = question["id"]
            answer_choice = correct_answers_map.get(question_id, None)  # Correct answer if selected, otherwise None

            if answer_choice:
                answers_payload["questions"].append({
                    "id": question_id,
                    "answer": answer_choice  # Submit the correct answer
                })

        response = requests.post(answer_url, headers=headers, params=params, json=answers_payload)

        if response.status_code != 200:
            print(f"❌ Failed to submit answers: {response.json()}")
            return

        print(f"✅ Successfully answered {num_correct} quiz questions correctly.")

        # ✅ Step 5: Submit the quiz (Masquerade Again)
        submit_url = f"{API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/complete"
        response = requests.post(submit_url, headers=headers, params=params)

        if response.status_code == 200:
            print(f"🎉 Successfully submitted the quiz for Student ID: {student_id}")
        else:
            print(f"❌ Failed to submit quiz: {response.json()}")

    except Exception as e:
        print(f"❌ Error: {e}")






student_ids = [612, 613, 614]
canvas_object_print()
# get_course_by_name('Integrated Algebra I')
# create_quiz_from_json(515, 'Quiz 2')
# check_quiz_type(515, 805)
# create_students()
# check_account_id()
# enroll_students(515)
# accept_all_course_invites(515)
# submit_quiz_for_student(515,806,612,5)