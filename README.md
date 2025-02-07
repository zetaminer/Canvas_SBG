# Canvas API Integration Guide 📚

Quick guide for students helping with the project, including steps to retrieve the **Course ID**, **User Token**, and get started with the code.

---

## Quick Start Guide 🚀

Follow these steps to download the project and get started:

### Clone the Repository

1. **Copy the Repository URL**
   - Visit the GitHub page for this project.
   - Click the green **Code** button and copy the HTTPS URL.

2. **Open a Terminal**
   Navigate to the directory where you want to clone the repository:
   ```sh
   cd /path/to/your/folder
   ```

3. **Clone the Repository**
   ```sh
   git clone https://github.com/zetaminer/Canvas_SBG.git
   ```
   

4. **Navigate to the Project Directory**
   ```sh
   cd your-repo
   ```

### Install Python

1. **Download Python**
   - Visit the [official Python website](https://www.python.org/downloads/).
   - Choose the latest version compatible with your operating system.
   - Download and run the installer.

2. **During Installation:**
   - Check the box that says **Add Python to PATH** (important).
   - Choose **Install Now** and follow the on-screen instructions.

3. **Verify Installation:**
   Open a terminal or command prompt and run:
   ```sh
   python --version
   ```
   This should display the installed Python version.

### Set Up the Environment

1. **Install Dependencies**
   Ensure you have Python installed. Then, install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

2. **Configure the Project**
   - Create a `config.json` file in the project directory.
   - Add the following:
     ```json
     {
       "TOKEN": "your-access-token-here",
       "COURSE_ID": "your-course-id-here"
     }
     ```

3. **Run the Project**
   Execute the script to test functionality or perform tasks:
   ```sh
   python GettingStartedWithCanvasAPI_2.py
   ```

---

## Resources

Here are helpful links for documentation and learning materials:

1. [Canvas Login | Instructure](https://canvas.instructure.com/)  
   Use this to log in to your Canvas instance.

2. [Canvas LMS REST API Documentation](https://canvas.instructure.com/doc/api/)  
   Official API documentation for working with Canvas LMS.

3. [CanvasAPI 3.2.0 Documentation](https://canvasapi.readthedocs.io/)  
   A Python wrapper for the Canvas API. Use this if you plan to interact with Canvas programmatically.

4. [Find Your Superpower - Learn Programming Using Canvas APIs (YouTube)](https://www.youtube.com/watch?v=6AEzuo7gElM)  
   A great video resource to understand how to use Canvas APIs effectively.

5. [Canvas APIs: Getting Started - Instructure Community](https://community.canvaslms.com/t5/Canvas-Developers-Group/Canvas-APIs-Getting-started-the-practical-ins-and-outs-gotchas/ba-p/263685)  
   A community resource for learning the practical ins and outs of using Canvas APIs.

---

## Prerequisites

Before you begin:
- Access to a Canvas LMS account.
- Admin or API access (if needed).
- Basic knowledge of REST APIs.

---

## How to Find the Course ID 🆔

The **Course ID** is a unique identifier for each course in Canvas. Here's how to locate it:

1. **Log in to Canvas LMS:**  
   Visit [Canvas Login](https://canvas.instructure.com/) and sign in.

2. **Navigate to the Course:**  
   Open the course you want the ID for.

3. **Check the URL:**  
   Look at the browser's address bar. The Course ID is the numeric part of the URL:
   ```
   https://canvas.instructure.com/courses/12345
   ```
   In this example, the **Course ID** is `12345`.

---

## How to Generate a User Token 🔑

A User Token is required to authenticate API requests.

1. **Log in to Canvas:**  
   Visit [Canvas Login](https://canvas.instructure.com/) and sign in.

2. **Access Profile Settings:**
   - Click your profile picture or initials in the top-right corner.
   - Go to **Settings**.

3. **Create a Token:**
   - Scroll to the **Approved Integrations** section.
   - Click **+ New Access Token**.
   - Enter a purpose (e.g., "API Integration") and expiration date.
   - Click **Generate Token**.

4. **Save the Token:**  
   Copy the token and save it securely. You’ll need it to authenticate API requests.

---

## Using the Canvas API 🚀

### Example: Retrieving Course Information
Here’s an example of how to retrieve course information using Python and the Canvas API:

```python
from canvasapi import Canvas

# Canvas API URL and Token
API_URL = "https://canvas.instructure.com"
API_TOKEN = "your-access-token-here"

# Initialize Canvas object
canvas = Canvas(API_URL, API_TOKEN)

# Get a course by its ID
course_id = 12345  # Replace with your Course ID
course = canvas.get_course(course_id)

# Print course details
print(f"Course Name: {course.name}")
print(f"Course Code: {course.course_code}")
```

---

## Troubleshooting

- **Missing Dependencies:** Ensure you’ve installed the packages from `requirements.txt`.
- **Invalid Token:** Double-check your token and ensure it hasn’t expired.
- **Course Not Found:** Verify that the Course ID in the URL is correct.

---

